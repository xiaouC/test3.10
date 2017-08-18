-- ./win/Fight/object.lua
require 'utils.class'
require 'utils.stack'
require 'utils.random_number'
require 'win.Fight.verify_skill_system'
require 'win.Fight.verify_skill'

local HERO_USEFOR_FIGHT = 0
local ITEM_TYPE_MONEY = 8
local ITEM_TYPE_SOUL = 16

-------------------------------------------------------------------------------------------------------------------------------------
__verify_base_object = class( 'verify_base_object' )
function __verify_base_object:ctor( obj_info, pos_index )
    self.obj_info = obj_info
    self.death = false
    self.pos_index = pos_index
    self.origin_pos_index = pos_index

    -- 死亡回调
    self.death_call_back_func = {}

    self.random_index = self.obj_info.random_index or 1
end

function __verify_base_object:init()
end

function __verify_base_object:destroy()
end

function __verify_base_object:addDeathCallBackFunc( call_back_func )
    self.death_call_back_func[call_back_func] = 1
end

function __verify_base_object:removeDeathCallBackFunc( call_back_func )
    self.death_call_back_func[call_back_func] = nil
end

function __verify_base_object:doDeath()
    -- 已经死过一次了，不用再死一次了
    if self.death then return end

    self.death = true

    self:playDeathEffect( function()
        -- 其他的回调
        for func,_ in pairs( self.death_call_back_func ) do func() end

        local drop_list = {}
        for _,v in ipairs( self.obj_info.drop2 or {} ) do
            if v.type ~= ITEM_TYPE_MONEY and v.type ~= ITEM_TYPE_SOUL then
                table.insert( drop_list, v )
            end
        end
        verify_fight_manager:gainDropReward( self, drop_list )

        local grid_item = verify_fight_manager:getGridItemByPosIndex( self.pos_index )
        if grid_item then
            -- 其他恢复的，不需要
            if self.obj_info.type == 'player' or self.obj_info.type == 'enemy' then
                if grid_item.grid_obj and grid_item.grid_obj.obj_info.type == 'stone' then
                    grid_item.grid_obj.grid_obj = nil
                else
                    grid_item.grid_obj = nil
                end
            end
        end

        if self.obj_info.type == 'player' or self.obj_info.type == 'enemy' then
            verify_fight_manager.dying_fight_objs:pop( self.obj_info.entity_id )
            verify_fight_manager:tryNextFightState()
        end

        -- 
        self:destroy()
    end)
end

function __verify_base_object:playDeathEffect( call_back_func )
    call_back_func()
end

function __verify_base_object:initModel()
end

function __verify_base_object:createModel()
end

function __verify_base_object:addEffect( effect_name, loop, call_back_func )
end

function __verify_base_object:addEffectEx( effect_name, loop )
end

function __verify_base_object:stopEffect( handle )
end

function __verify_base_object:setCurHP( hp )
    self.cur_hp = hp
    if self.cur_hp > self.max_hp then self.cur_hp = self.max_hp end
end

function __verify_base_object:realFloatText( txt, anim_mcName )
end

function __verify_base_object:canMoveTo( target_grid_obj )
    -- 如果已经死亡的话，可以移动到
    if target_grid_obj.death then return true end
    return false
end

function __verify_base_object:effective( grid_obj )
end

function __verify_base_object:isEnemy( grid_obj )
    return false
end

function __verify_base_object:isTeammate( grid_obj )
    return ( self.obj_info.type == grid_obj.obj_info.type ) and true or false
end

function __verify_base_object:isDelaySkill()
    return self.normal_skill and self.normal_skill:isDelaySkill() or false
end

-- 防御
function __verify_base_object:getRealTimeDef()
    return self.def
end

function __verify_base_object:getRealTimeAtk()
    return self.atk
end

function __verify_base_object:setPosition( x, y )
end

function __verify_base_object:shock()
end

function __verify_base_object:getRandomNumber( min, max )
    local ret_num, next_index = pseudo_random( self.random_index, min, max )

    self.random_index = next_index

    return ret_num
end

-------------------------------------------------------------------------------------------------------------------------------------
__verify_fight_object = class( 'verify_fight_object', __verify_base_object )
function __verify_fight_object:ctor( obj_info, pos_index )
    __verify_base_object.ctor( self, obj_info, pos_index )
    self.anim_rad = 0
    self.dead_sound = fight_const.fight_enemy_dead
    self.attack_combo_mc = {}
    self.total_damage = 0       -- 攻击别人的伤害总和
    self.used_skill_ids = {}    -- 使用过的技能 ID
    self.attack_max_combo = 0   -- 受到的最大的连击数
    self.total_round = 1
    self.hurt_float_list = stack.new()
    self.restore_float_list = stack.new()

    -- 
    self.origin_max_hp = obj_info.base_attr._hp + obj_info.faction_attr._hp + obj_info.equip_attr._hp + obj_info.buff_attr._hp
    self.max_hp = self.origin_max_hp

    local origin_hp = table.hasKey( obj_info, 'origin_hp' ) and obj_info.origin_hp or self.max_hp
    __verify_base_object.setCurHP( self, origin_hp )

    self.atk   = obj_info.base_attr._atk   + obj_info.faction_attr._atk   + obj_info.equip_attr._atk   + obj_info.buff_attr._atk  
    self.def   = obj_info.base_attr._def   + obj_info.faction_attr._def   + obj_info.equip_attr._def   + obj_info.buff_attr._def  
    self.crit  = obj_info.base_attr._crit  + obj_info.faction_attr._crit  + obj_info.equip_attr._crit  + obj_info.buff_attr._crit 
    self.dodge = obj_info.base_attr._dodge + obj_info.faction_attr._dodge + obj_info.equip_attr._dodge + obj_info.buff_attr._dodge

    self.mvRgeTL = self.obj_info.mvRgeTL
    self.mvRgeT = self.obj_info.mvRgeT
    self.mvRgeTR = self.obj_info.mvRgeTR
    self.mvRgeR = self.obj_info.mvRgeR
    self.mvRgeBR = self.obj_info.mvRgeBR
    self.mvRgeB = self.obj_info.mvRgeB
    self.mvRgeBL = self.obj_info.mvRgeBL
    self.mvRgeL = self.obj_info.mvRgeL

    -- __fight_skill 
    self:resetSkills( self.obj_info.skill_ids )

    -- buff & debuff
    self.aura_buff = {}
    self.aura_debuff = {}

    self.trigger_buff = {}
    self.trigger_debuff = {}

    self.buff_debuff_index = stack.new()
    self.next_buff_debuff_id = 1

    -- item buff
    self.buff_item_effective = {}

    -- 亡语回调的次数
    self.death_cb_count = stack.new()

    -- 清理所有的光环效果
    self:addDeathCallBackFunc( function()
        for _,grid_obj in ipairs( verify_fight_manager:getAllFighterObjects() ) do
            grid_obj:removeAuraEffect( self.obj_info.entity_id )
        end
    end)
end

function __verify_fight_object:createModel()
end

function __verify_fight_object:showModelDetail( model_mc_flag )
end

function __verify_fight_object:hideModelDetail( model_mc_flag )
end

function __verify_fight_object:reliveClear()
    -- buff & debuff
    self.aura_buff = {}
    self.aura_debuff = {}

    for _,v in ipairs( self.trigger_buff ) do if v.remove_effect_func then v.remove_effect_func() end end
    self.trigger_buff = {}

    for _,v in ipairs( self.trigger_debuff ) do if v.remove_effect_func then v.remove_effect_func() end end
    self.trigger_debuff = {}

    self.buff_debuff_index:clear()
    self.next_buff_debuff_id = 1

    -- item buff
    self.buff_item_effective = {}

    -- 
    self:destroy()
end

function __verify_fight_object:destroy()
    __verify_base_object.destroy( self )
end

function __verify_fight_object:createDropDragModel()
end

function __verify_fight_object:dropDragStart()
end

function __verify_fight_object:dropDragEnd()
end

function __verify_fight_object:resetSkills( skill_ids )
    self.all_fight_skill = {}
    for _,v in ipairs( skill_ids ) do
        local f_skill = __verify_fight_skill.new( self, v.id, v.level )
        table.insert( self.all_fight_skill, f_skill )
    end
end

function __verify_fight_object:getFightSkill( skill_id )
    for _,skill in ipairs( self.all_fight_skill ) do
        if skill.skill_id == skill_id then return skill end
    end
end

-- buff, debuff 加入的时机，在刷新的时候，需要严格控制
-- 根据当前的 verify_fight_manager.fight_state，在哪个阶段添加上去的 buff 或者 debuff，就应该在这个阶段刷新剩余回合数
function __verify_fight_object:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, add_effect_func, effect_func, remove_effect_func, call_back_func )
    local function __get_buff_debuff__()
        local param = se_info.param or se_info.abs_param or 0
        local is_debuff = param < 0
        if se_type == 'aura' then
            return is_debuff and self.aura_debuff or self.aura_buff, nil, is_debuff
        else
            local buff_debuff_id = self.next_buff_debuff_id
            self.next_buff_debuff_id = self.next_buff_debuff_id + 1

            return is_debuff and self.trigger_debuff or self.trigger_buff, buff_debuff_id, is_debuff
        end
    end

    local info, buff_debuff_id, is_debuff = __get_buff_debuff__()
    if is_debuff and self:isInvincible() then return call_back_func() end     -- 如果魔免的话，所有施放在其身上的 DEBUFF 都不起作用

    local fight_state = verify_fight_manager.fight_state
    local first_check = true
    if fight_state == 'player_attacking' then
        fight_state = 'player_round_end'
        first_check = false
    end
    if fight_state == 'monster_attacking' then
        fight_state = 'monster_round_end'
        first_check = false
    end

    table.insert( info, {
        buff_debuff_id = buff_debuff_id,
        se_info = se_info,
        skill_level = skill_level,
        src_entity_id = src_grid_obj.obj_info.entity_id,
        remain_round = se_info.round,
        start_round = verify_fight_manager.player_total_round,
        effect_attr = effect_attr,
        effect_param = effect_param or 1.0,
        effect_func = effect_func,
        remove_effect_func = remove_effect_func,
        fight_state = fight_state,
        first_check = first_check,
    })

    -- 
    if add_effect_func then add_effect_func() end

    if buff_debuff_id then
        self.buff_debuff_index:push( buff_debuff_id )
        self:updateBuffDebuffState()
    end

    self:updatePoisonState()

    -- 附带击退效果
    if v.beak_back_index then
        self:beakBack( src_grid_obj, v.beak_back_index, call_back_func )
    else
        call_back_func()
    end
end

function __verify_fight_object:collectEffectFuncByKind( kind, all_effect_func )
    local function __has_kind_type__( v ) if v.se_info.kind == kind then table.insert( all_effect_func, v.effect_func ) end end

    for _,v in ipairs( self.aura_buff ) do __has_kind_type__( v ) end
    for _,v in ipairs( self.aura_debuff ) do __has_kind_type__( v ) end
    for _,v in ipairs( self.trigger_buff ) do __has_kind_type__( v ) end
    for _,v in ipairs( self.trigger_debuff ) do __has_kind_type__( v ) end
end

function __verify_fight_object:addBuffItemEffective( buff_type, effect_name, last_round, param, add_effect_func, effect_func, remove_effect_func )
    self.buff_item_effective[buff_type] = {
        remain_round = last_round,
        param = param,
        effect_func = effect_func,
        remove_effect_func = remove_effect_func,
        fight_state = verify_fight_manager.fight_state,
    }

    if add_effect_func then add_effect_func( self ) end
end

function __verify_fight_object:refreshBuffDebuff()
    local temp_trigger_buff = {}
    for _,v in ipairs( self.trigger_buff ) do
        if v.remain_round > 0 and v.fight_state == verify_fight_manager.fight_state then
            if v.first_check then
                v.remain_round = v.remain_round - 1
            else
                v.first_check = true
            end
        end

        -- 等于 0 的，就是要被移除的
        if v.remain_round ~= 0 then
            table.insert( temp_trigger_buff, v )
        else
            -- 
            if v.remove_effect_func then v.remove_effect_func() end

            -- 
            self.buff_debuff_index:pop( v.buff_debuff_id )
        end
    end
    self.trigger_buff = temp_trigger_buff

    local temp_trigger_debuff = {}
    for _,v in ipairs( self.trigger_debuff ) do
        if v.remain_round > 0 and v.fight_state == verify_fight_manager.fight_state then
            if v.first_check then
                v.remain_round = v.remain_round - 1
            else
                v.first_check = true
            end
        end

        -- 等于 0 的，就是要被移除的
        if v.remain_round ~= 0 then
            table.insert( temp_trigger_debuff, v )
        else
            -- 
            if v.remove_effect_func then v.remove_effect_func() end

            -- 
            self.buff_debuff_index:pop( v.buff_debuff_id )
        end
    end
    self.trigger_debuff = temp_trigger_debuff

    self:updateBuffDebuffState()

    -- 物品 BUFF 
    local rm_types = {}
    for buff_type, b_info in pairs( self.buff_item_effective ) do
        if b_info.fight_state == verify_fight_manager.fight_state then
            b_info.remain_round = b_info.remain_round - 1
            if b_info.effect_func then b_info.effect_func( self ) end
            if b_info.remain_round <= 0 then table.insert( rm_types, buff_type ) end
        end
    end
    for _,buff_type in ipairs( rm_types ) do
        if self.buff_item_effective[buff_type].remove_effect_func then self.buff_item_effective[buff_type].remove_effect_func( self ) end
        self.buff_item_effective[buff_type] = nil
    end

    self:updatePoisonState()
end

function __verify_fight_object:checkTriggerSkill( all_src_entity_id, all_target_entity_id, action, param_tbl )
    for _,f_skill in ipairs( self.all_fight_skill ) do
        local func = f_skill:isTrigger( all_src_entity_id, all_target_entity_id, action, param_tbl )
        if func then
            table.insert( verify_fight_manager.all_trigger_skill_func, func )

            -- 等待亡语的回调后，才真的死亡
            if action == trigger_action.death then self.death_cb_count:push( 1 ) end
        end
    end
end

function __verify_fight_object:hasKindType( kind )
    local function __has_kind_type__( v ) return v.se_info.kind == kind end

    for _,v in ipairs( self.aura_buff ) do if __has_kind_type__( v ) then return true end end
    for _,v in ipairs( self.aura_debuff ) do if __has_kind_type__( v ) then return true end end
    for _,v in ipairs( self.trigger_buff ) do if __has_kind_type__( v ) then return true end end
    for _,v in ipairs( self.trigger_debuff ) do if __has_kind_type__( v ) then return true end end
    return false
end

function __verify_fight_object:hasKindTypeNegative( kind, negative )
    local function __has_kind_type_negative__( v )
        if v.se_info.kind == kind then return negative * v.se_info.param >= 0 end
        return false
    end

    for _,v in ipairs( self.aura_buff ) do if __has_kind_type_negative__( v ) then return true end end
    for _,v in ipairs( self.aura_debuff ) do if __has_kind_type_negative__( v ) then return true end end
    for _,v in ipairs( self.trigger_buff ) do if __has_kind_type_negative__( v ) then return true end end
    for _,v in ipairs( self.trigger_debuff ) do if __has_kind_type_negative__( v ) then return true end end
    return false
end

function __verify_fight_object:hasKindAnyNegative( negative )
    local function __has_kind_any_negative__( v ) return negative * v.se_info.param >= 0 end
    for _,v in ipairs( self.trigger_buff ) do if __has_kind_any_negative__( v ) then return true end end
    for _,v in ipairs( self.trigger_debuff ) do if __has_kind_any_negative__( v ) then return true end end
    return false
end

function __verify_fight_object:disperseAllKind( src_grid_obj, disperse_type, beak_back_index, call_back_func )
    local __disperse_type__ = {
        function()      -- 驱散全部正面 BUFF
            for _,v in ipairs( self.trigger_buff ) do
                if v.remove_effect_func then v.remove_effect_func() end
                self.buff_debuff_index:pop( v.buff_debuff_id )
            end
            self.trigger_buff = {}
        end,
        function()      -- 驱散全部负面 BUFF
            for _,v in ipairs( self.trigger_debuff ) do
                if v.remove_effect_func then v.remove_effect_func() end
                self.buff_debuff_index:pop( v.buff_debuff_id )
            end
            self.trigger_debuff = {}
        end,
        function()      -- 驱散全部正面负面 BUFF
            for _,v in ipairs( self.trigger_buff ) do
                if v.remove_effect_func then v.remove_effect_func() end
            end
            self.trigger_buff = {}

            for _,v in ipairs( self.trigger_debuff ) do
                if v.remove_effect_func then v.remove_effect_func() end
            end
            self.trigger_debuff = {}
            self.buff_debuff_index:clear()
        end,
    }

    __disperse_type__[disperse_type]()

    self:updateBuffDebuffState()
    self:updatePoisonState()

    if beak_back_index then
        self:beakBack( src_grid_obj, beak_back_index, call_back_func )
    else
        if call_back_func then call_back_func() end
    end
end

function __verify_fight_object:checkAttrState( attr_check_info, sort_param )
    local __get_attr__ = {
        [1] = function() return self.max_hp end,
        [2] = function() return attr_check_info.relative and ( self.cur_hp / self.max_hp ) * 100 or self.cur_hp end,
        [3] = function() return self:getBaseAtk() end,
        [4] = function() return self:getBaseDef() end,
        [5] = function() return self:getBaseCriticalRate() end,
        [6] = function() return self:getBaseDodgeRate() end,
    }

    -- 
    if not attr_check_info.attr_type or not __get_attr__[attr_check_info.attr_type] then return false end

    local attr_param = math.floor( __get_attr__[attr_check_info.attr_type]() )

    local __compare_func__ = {
        [1] = function() return attr_param > attr_check_info.param end,
        [2] = function() return attr_param >= attr_check_info.param end,
        [3] = function() return attr_param == attr_check_info.param end,
        [4] = function() return attr_param < attr_check_info.param end,
        [5] = function() return attr_param <= attr_check_info.param end,
        [6] = function() return attr_param ~= attr_check_info.param end,
    }

    -- 
    if attr_check_info.compare_type then return __compare_func__[attr_check_info.compare_type]() end

    -- 
    if attr_check_info.sort_type then
        if not sort_param[attr_param] then sort_param[attr_param] = {} end

        local attr_param_pos_index = sort_param[attr_param]
        table.insert( attr_param_pos_index, self.pos_index )

        return true
    end

    return false
end

-- 物理伤害免疫
function __verify_fight_object:isImmunityPhysical()
    if hasAbilityImmunityPhysical( self.obj_info.ability ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.ImmunityPhysical.value )
end

-- 魔法免疫
function __verify_fight_object:isImmunityMagic()
    if hasAbilityImmunityMagic( self.obj_info.ability ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.ImmunityMagic.value )
end

-- 技能伤害免疫
function __verify_fight_object:isImmunitySkillHurt()
    if hasAbilityImmunitySkillHurt( self.obj_info.ability ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.ImmunitySkillHurt.value )
end

-- 免疫眩晕
function __verify_fight_object:isImmunityDizziness()
    if hasAbilityImmunityDizziness( self.obj_info.ability ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.ImmunityDizziness.value )
end

-- 免疫沉默
function __verify_fight_object:isImmunitySilence()
    if hasAbilityImmunitySilence( self.obj_info.ability ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.ImmunitySilence.value )
end

-- 免疫中毒
function __verify_fight_object:isImmunityPoison()
    if hasAbilityImmunityPoison( self.obj_info.ability ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.ImmunityPoison.value )
end

-- 免疫驱散
function __verify_fight_object:isImmunityDisperse()
    if hasAbilityImmunityDisperse( self.obj_info.ability ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.ImmunityDisperse.value )
end

-- 无敌
function __verify_fight_object:isInvincible()
    if self.buff_item_effective['buff_invincible'] then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.Invincible.value )
end

function __verify_fight_object:isForbidMove()
    -- 不允许移动或者被眩晕了
    if self:hasKindType( verify_skill_system.__kind_type__.ForbidMove.value ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.Paralysis.value )
end

function __verify_fight_object:isForbidAttack()
    -- 不允许攻击或者被眩晕了
    if self:hasKindType( verify_skill_system.__kind_type__.ForbidAttack.value ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.Paralysis.value )
end

function __verify_fight_object:isSilence()
    return self:hasKindType( verify_skill_system.__kind_type__.Silence.value )
end

function __verify_fight_object:calculateBuffDebuff( src_grid_obj, target_grid_obj, cur_num, kind )
    local function __cal_( v )
        if v.se_info.kind == kind then
            local temp = verify_skill_system.getRelativeParam( src_grid_obj, target_grid_obj, v.se_info, v.skill_level )
            cur_num = cur_num + temp * v.effect_param
        end
    end

    for _,v in ipairs( self.aura_buff ) do __cal_( v ) end
    for _,v in ipairs( self.aura_debuff ) do __cal_( v ) end
    for _,v in ipairs( self.trigger_buff ) do __cal_( v ) end
    for _,v in ipairs( self.trigger_debuff ) do __cal_( v ) end

    return cur_num
end

function __verify_fight_object:getCriticalValue( target_grid_obj, base_crit_rate )
    local ret_crit_rate = base_crit_rate

    local ret_crit_rate_2 = base_crit_rate
    local function __crit_value_( v )
        if v.se_info.kind == verify_skill_system.__kind_type__.CritVal.value then
            local se_param = v.se_info.param + ( ( v.skill_level - 1 ) * v.se_info.lv_param ) / 100
            if v.se_info.relative == 0 then
                ret_crit_rate = ret_crit_rate * se_param / 100 * v.effect_param
            else
                local temp_crit_rate = se_param / 100 * v.effect_param
                if temp_crit_rate > ret_crit_rate_2 then ret_crit_rate_2 = temp_crit_rate end
            end
        end
    end

    for _,v in ipairs( self.aura_buff ) do __crit_value_( v ) end
    for _,v in ipairs( self.aura_debuff ) do __crit_value_( v ) end
    for _,v in ipairs( self.trigger_buff ) do __crit_value_( v ) end
    for _,v in ipairs( self.trigger_debuff ) do __crit_value_( v ) end

    return ret_crit_rate > ret_crit_rate_2 and ret_crit_rate or ret_crit_rate_2
end

function __verify_fight_object:getBaseCriticalRate()
    return self.crit
end

function __verify_fight_object:isCritical( target_grid_obj, base_critical_rate )
    local base_crit = self:getBaseCriticalRate()

    -- 物品暴击
    if self.buff_item_effective['buff_critical'] then base_crit = base_crit + self.buff_item_effective['buff_critical'].param end

    -- BUFF 和 DEBUFF
    base_crit = math.floor( self:calculateBuffDebuff( self, target_grid_obj, base_crit, verify_skill_system.__kind_type__.CritUp.value ) )

    local is_crit = self:getRandomNumber( 0, 1000 ) < base_crit

    if is_crit then return is_crit, self:getCriticalValue( target_grid_obj, base_critical_rate ) end

    return is_crit, base_critical_rate
end

function __verify_fight_object:getBaseDodgeRate( damage )
    return self.dodge
end

function __verify_fight_object:isDodge( src_grid_obj, damage )
    local base_dodge = self:getBaseDodgeRate( damage )

    -- 物品闪避
    if self.buff_item_effective['buff_dodge'] then base_dodge = base_dodge + self.buff_item_effective['buff_dodge'].param end

    -- BUFF 和 DEBUFF
    base_dodge = math.floor( self:calculateBuffDebuff( src_grid_obj, self, base_dodge, verify_skill_system.__kind_type__.DodgeUp.value ) )

    return self:getRandomNumber( 0, 1000 ) < base_dodge
end

function __verify_fight_object:hasAbilityFly()
    if self.buff_item_effective['buff_fly'] then return true end
    if hasAbilityFly( self.obj_info.ability ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.AbilityFly.value )
end

function __verify_fight_object:hasAbilityShare()
    if self.buff_item_effective['buff_share'] then return true end
    if hasAbilityShare( self.obj_info.ability ) then return true end
    return self:hasKindType( verify_skill_system.__kind_type__.AbilityShare.value )
end

-- 治疗效果的参数，可能是增量治疗效果，也可能是降低治疗效果
function __verify_fight_object:getRestoreParam()
    local cur_param, cur_abs_param = 100, 0
    local function __update_restore_param__( v )
        if v.se_info.kind == verify_skill_system.__kind_type__.ReduceRestore.value then
            cur_param = cur_param + ( v.se_info.param + ( ( v.skill_level - 1 ) * v.se_info.lv_param ) / 100 )
            cur_abs_param = cur_abs_param + ( v.se_info.abs_param + ( v.skill_level - 1 ) * v.se_info.lv_abs_param )
        end
    end

    for _,v in ipairs( self.aura_buff ) do __update_restore_param__( v ) end
    for _,v in ipairs( self.aura_debuff ) do __update_restore_param__( v ) end
    for _,v in ipairs( self.trigger_buff ) do __update_restore_param__( v ) end
    for _,v in ipairs( self.trigger_debuff ) do __update_restore_param__( v ) end

    local ret_param = cur_param / 100
    return ret_param > 0 and ret_param or 0, cur_abs_param
end

-- 技能伤害的效果参数，可能是增加，也可能是减少
function __verify_fight_object:getSkillHurtParam( kind )
    local cur_param, cur_abs_param = 0, 0
    local function __update_restore_param__( v )
        if v.se_info.kind == kind then
            cur_param = cur_param + ( v.se_info.param + ( ( v.skill_level - 1 ) * v.se_info.lv_param ) / 100 )
            cur_abs_param = cur_abs_param + ( v.se_info.abs_param + ( v.skill_level - 1 ) * v.se_info.lv_abs_param )
        end
    end

    for _,v in ipairs( self.aura_buff ) do __update_restore_param__( v ) end
    for _,v in ipairs( self.aura_debuff ) do __update_restore_param__( v ) end
    for _,v in ipairs( self.trigger_buff ) do __update_restore_param__( v ) end
    for _,v in ipairs( self.trigger_debuff ) do __update_restore_param__( v ) end

    return cur_param, cur_abs_param
end

function __verify_fight_object:updateBuffDebuffState()
end

function __verify_fight_object:addAuraEffect( all_target_grid_obj )
    for _,f_skill in ipairs( self.all_fight_skill ) do
        f_skill:addAuraEffect( all_target_grid_obj )
    end
end

function __verify_fight_object:removeAuraEffect( entity_id )
    local temp_buff = {}
    for _,v in ipairs( self.aura_buff ) do
        if v.src_entity_id ~= entity_id then table.insert( temp_buff, v ) end
    end
    self.aura_buff = temp_buff

    local temp_debuff = {}
    for _,v in ipairs( self.aura_debuff ) do
        if v.src_entity_id ~= entity_id then table.insert( temp_debuff, v ) end
    end
    self.aura_debuff = temp_debuff
end

-- 返回占的格子索引，BOSS 就会返回 4 个索引
function __verify_fight_object:getAllPosIndex()
    return { self.pos_index }
end

function __verify_fight_object:getPosition()
end

-- 这个用于强设坐标，在 verify_fight_manager:moveTo 中被调用到
function __verify_fight_object:setPosition( x, y )
end

function __verify_fight_object:getShadowOffsetY()
end

-- 这个目前来说，只用于 AI 移动
function __verify_fight_object:smoothMoveTo( o_x, o_y, t_x, t_y, call_back_func )
    if call_back_func then call_back_func() end
end

function __verify_fight_object:beakBack( src_grid_obj, beak_back_index, call_back_func )
    if not beak_back_index then return call_back_func() end

    local src_grid_item = verify_fight_manager:getGridItemByPosIndex( self.pos_index )
    local target_grid_item = verify_fight_manager:getGridItemByPosIndex( beak_back_index )

    -- 
    local target_grid_item = verify_fight_manager:getGridItemByPosIndex( beak_back_index )

    verify_fight_manager:setTo( self, beak_back_index, function() end )

    -- 被击退将触发移动
    local all_src_entity_id = { src_grid_obj.obj_info.entity_id }
    local all_target_entity_id = { self.obj_info.entity_id }
    local mv_count = verify_fight_manager:getMoveGridCount( self.pos_index, beak_back_index )
    local param_tbl = { [self.obj_info.entity_id] = {} }
    param_tbl[self.obj_info.entity_id][src_grid_obj.obj_info.entity_id] = { mv_count = mv_count }
    self:checkTriggerSkill( all_src_entity_id, all_target_entity_id, trigger_action.move, param_tbl )
    call_back_func()
    --processVerifyTriggerSkillFunc( call_back_func )
end

function __verify_fight_object:modelDetailFollow( is_follow )
end

-- 这是一个理论值
function __verify_fight_object:collectMovePosIndex( pos_index )
    -- 麻痹了，就哪也去不了
    if self:isForbidMove() then return {} end

    -- 这是一个不可达的位置
    if pos_index < 1 or pos_index > verify_fight_manager.grid_count_per_page then return {} end

    -- 
    local ret_pos_index = {}

    local row = math.floor( ( pos_index - 1 ) / 4 )
    local col = ( pos_index - 1 ) % 4

    -- 左上
    if self.mvRgeTL == 1 then               -- 单
        if col > 0 and row > 0 then table.insert( ret_pos_index, pos_index - 5 ) end
    elseif self.mvRgeTL == 2 then         -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while r > 0 and c > 0 do
            table.insert( ret_pos_index, temp_pos_index - 5 )

            r = r - 1
            c = c - 1
            temp_pos_index = temp_pos_index - 5
        end
    end

    -- 上
    if self.mvRgeT == 1 then                    -- 单
        if row > 0 then table.insert( ret_pos_index, pos_index - 4 ) end
    elseif self.mvRgeT == 2 then              -- 双
        local r = row
        local temp_pos_index = pos_index

        while r > 0 do
            table.insert( ret_pos_index, temp_pos_index - 4 )

            r = r - 1
            temp_pos_index = temp_pos_index - 4
        end
    end

    -- 右上
    if self.mvRgeTR == 1 then              -- 单
        if col < 3 and row > 0 then table.insert( ret_pos_index, pos_index - 3 ) end
    elseif self.mvRgeTR == 2 then        -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c < 3 and r > 0 do
            table.insert( ret_pos_index, temp_pos_index - 3 )

            r = r - 1
            c = c + 1
            temp_pos_index = temp_pos_index - 3
        end
    end

    -- 右
    if self.mvRgeR == 1 then                  -- 单
        if col < 3 then table.insert( ret_pos_index, pos_index + 1 ) end
    elseif self.mvRgeR == 2 then            -- 双
        local c = col
        local temp_pos_index = pos_index

        while c < 3 do
            table.insert( ret_pos_index, temp_pos_index + 1 )

            c = c + 1
            temp_pos_index = temp_pos_index + 1
        end
    end

    -- 右下
    if self.mvRgeBR == 1 then           -- 单
        if col < 3 and row < 3 then table.insert( ret_pos_index, pos_index + 5 ) end
    elseif self.mvRgeBR == 2 then     -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c < 3 and r < 3 do
            table.insert( ret_pos_index, temp_pos_index + 5 )

            r = r + 1
            c = c + 1
            temp_pos_index = temp_pos_index + 5
        end
    end

    -- 下
    if self.mvRgeB == 1 then                 -- 单
        if row < 3 then table.insert( ret_pos_index, pos_index + 4 ) end
    elseif self.mvRgeB == 2 then           -- 双
        local r = row
        local temp_pos_index = pos_index

        while r < 3 do
            table.insert( ret_pos_index, temp_pos_index + 4 )

            r = r + 1
            temp_pos_index = temp_pos_index + 4
        end
    end

    -- 左下
    if self.mvRgeBL == 1 then            -- 单
        if col > 0 and row < 3 then table.insert( ret_pos_index, pos_index + 3 ) end
    elseif self.mvRgeBL == 2 then      -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c > 0 and r < 3 do
            table.insert( ret_pos_index, temp_pos_index + 3 )

            c = c - 1
            r = r + 1
            temp_pos_index = temp_pos_index + 3
        end
    end

    -- 左
    if self.mvRgeL == 1 then               -- 单
        if col > 0 then table.insert( ret_pos_index, pos_index - 1 ) end
    elseif self.mvRgeL == 2 then         -- 双
        local c = col
        local temp_pos_index = pos_index

        while c > 0 do
            table.insert( ret_pos_index, temp_pos_index - 1 )

            c = c - 1
            temp_pos_index = temp_pos_index - 1
        end
    end

    return ret_pos_index
end

-- 这是一个根据当前状态，所能真实可达的
function __verify_fight_object:collectValidMovePosIndex()
    -- 麻痹了，就哪也去不了
    if self:isForbidMove() then return {} end

    local pos_index = self.pos_index
    local mv_pos_index = self:collectMovePosIndex( pos_index )

    -- 
    local ret_pos_index = {}

    local row = math.floor( ( pos_index - 1 ) / 4 )
    local col = ( pos_index - 1 ) % 4

    -- 左上
    if self.mvRgeTL == 1 then               -- 单
        if row > 0 and col > 0 and self:isValidMovePosIndex( pos_index - 5, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index - 5, show_pos_index = { pos_index - 5 } } )
        end
    elseif self.mvRgeTL == 2 then         -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while r > 0 and c > 0 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index - 5, mv_pos_index )

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index - 5, show_pos_index = { temp_pos_index - 5 } } )
            end

            if not can_pass then break end

            r = r - 1
            c = c - 1
            temp_pos_index = temp_pos_index - 5
        end
    end

    -- 上
    if self.mvRgeT == 1 then                    -- 单
        if row > 0 and self:isValidMovePosIndex( pos_index - 4, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index - 4, show_pos_index = { pos_index - 4 } } )
        end
    elseif self.mvRgeT == 2 then              -- 双
        local r = row
        local temp_pos_index = pos_index

        while r > 0 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index - 4, mv_pos_index )

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index - 4, show_pos_index = { temp_pos_index - 4 } } )
            end

            if not can_pass then break end

            r = r - 1
            temp_pos_index = temp_pos_index - 4
        end
    end

    -- 右上
    if self.mvRgeTR == 1 then              -- 单
        if col < 3 and row > 0 and self:isValidMovePosIndex( pos_index - 3, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index - 3, show_pos_index = { pos_index - 3 } } )
        end
    elseif self.mvRgeTR == 2 then        -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c < 3 and r > 0 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index - 3, mv_pos_index )

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index - 3, show_pos_index = { temp_pos_index - 3 } } )
            end

            if not can_pass then break end

            r = r - 1
            c = c + 1
            temp_pos_index = temp_pos_index - 3
        end
    end

    -- 右
    if self.mvRgeR == 1 then                  -- 单
        if col < 3 and self:isValidMovePosIndex( pos_index + 1, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index + 1, show_pos_index = { pos_index + 1 } } )
        end
    elseif self.mvRgeR == 2 then            -- 双
        local c = col
        local temp_pos_index = pos_index

        while c < 3 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index + 1, mv_pos_index )

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index + 1, show_pos_index = { temp_pos_index + 1 } } )
            end

            if not can_pass then break end

            c = c + 1
            temp_pos_index = temp_pos_index + 1
        end
    end

    -- 右下
    if self.mvRgeBR == 1 then           -- 单
        if col < 3 and row < 3 and self:isValidMovePosIndex( pos_index + 5, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index + 5, show_pos_index = { pos_index + 5 } } )
        end
    elseif self.mvRgeBR == 2 then     -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c < 3 and r < 3 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index + 5, mv_pos_index )

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index + 5, show_pos_index = { temp_pos_index + 5 } } )
            end

            if not can_pass then break end

            r = r + 1
            c = c + 1
            temp_pos_index = temp_pos_index + 5
        end
    end

    -- 下
    if self.mvRgeB == 1 then                 -- 单
        if row < 3 and self:isValidMovePosIndex( pos_index + 4, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index + 4, show_pos_index = { pos_index + 4 } } )
        end
    elseif self.mvRgeB == 2 then           -- 双
        local r = row
        local temp_pos_index = pos_index

        while r < 3 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index + 4, mv_pos_index )

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index + 4, show_pos_index = { temp_pos_index + 4 } } )
            end

            if not can_pass then break end

            r = r + 1
            temp_pos_index = temp_pos_index + 4
        end
    end

    -- 左下
    if self.mvRgeBL == 1 then            -- 单
        if col > 0 and row < 3 and self:isValidMovePosIndex( pos_index + 3, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index + 3, show_pos_index = { pos_index + 3 } } )
        end
    elseif self.mvRgeBL == 2 then      -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c > 0 and r < 3 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index + 3, mv_pos_index )

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index + 3, show_pos_index = { temp_pos_index + 3 } } )
            end

            if not can_pass then break end

            c = c - 1
            r = r + 1
            temp_pos_index = temp_pos_index + 3
        end
    end

    -- 左
    if self.mvRgeL == 1 then               -- 单
        if col > 0 and self:isValidMovePosIndex( pos_index - 1, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index - 1, show_pos_index = { pos_index - 1 } } )
        end
    elseif self.mvRgeL == 2 then         -- 双
        local c = col
        local temp_pos_index = pos_index

        while c > 0 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index - 1, mv_pos_index )

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index - 1, show_pos_index = { temp_pos_index - 1 } } )
            end

            if not can_pass then break end

            c = c - 1
            temp_pos_index = temp_pos_index - 1
        end
    end

    return ret_pos_index
end

function __verify_fight_object:isValidMovePosIndex( target_pos_index, mv_pos_index )
    -- 不是一个有效的位置，不能移动过去
    local target_grid_item = verify_fight_manager:getGridItemByPosIndex( target_pos_index )
    if not target_grid_item then return false, false end

    -- 在这个位置上已经有了，不能移动过去，以后添加飞行的时候，需要更细致的判断
    if target_grid_item.grid_obj then
        return self:canMoveTo( target_grid_item.grid_obj )
    end

    -- 遍历所有可以移动的位置，看是否有 target_pos_index
    for _,pos_index in ipairs( mv_pos_index ) do
        -- target_pos_index 在可移动列表中，这是一个有效的可移动的位置
        if pos_index == target_pos_index then return true, true end
    end

    -- 找不到，不可移动
    return false, false
end

function __verify_fight_object:isValidMovePosIndex_real( target_pos_index )
    local move_pos_index = self:collectValidMovePosIndex()
    for _,v in ipairs( move_pos_index ) do
        for _,pos_index in ipairs( v.show_pos_index ) do
            if pos_index == target_pos_index then return true end
        end
    end
    return false
end

-- return can_mv_to, can_pass
function __verify_fight_object:canMoveTo( target_grid_obj )
    if not __verify_base_object.canMoveTo( self, target_grid_obj ) then
        -- 自己的同伴的位置，不能移动过去
        if self.obj_info.type == target_grid_obj.obj_info.type then return false, true end

        -- 敌人的位置，不能移动过去
        if self:isEnemy( target_grid_obj ) then
            -- 不能飞的话，回去洗洗睡吧
            if not self:hasAbilityFly() then return false, false end
            return false, true
        end

        -- 障碍物，除非你能飞
        if target_grid_obj.obj_info.type == 'stone' then
            -- 不能飞的话，回去洗洗睡吧
            if not self:hasAbilityFly() then return false, false end
            -- 如果障碍物上已经有一个 grid_obj 了，那么只能穿过不能停留
            if target_grid_obj.grid_obj then return false, true end
        end
    end

    return true, true
end

function __verify_fight_object:getAllAttackPosIndex( pos_index )
    -- 这是一个不可达的位置
    if pos_index < 1 or pos_index > verify_fight_manager.grid_count_per_page then return {} end

    -- 
    local ret_pos_index = {}

    local row = math.floor( ( pos_index - 1 ) / 4 )
    local col = ( pos_index - 1 ) % 4

    -- 攻击的次数，与其星级相关
    --local combo = ATK_COUNT_BY_RARITY[self.obj_info.rarity]
    local combo = 1

    -- 左上，不管单还是双，都只能攻击最近的一个位置
    if self.mvRgeTL == 1 or self.mvRgeTL == 2 then               -- 单
        if col > 0 and row > 0 then table.insert( ret_pos_index, { index = pos_index - 5, combo = combo, atk_dir = 'mvRgeTL' } ) end
    end

    -- 上，不管单还是双，都只能攻击最近的一个位置
    if self.mvRgeT == 1 or self.mvRgeT == 2 then                    -- 单
        if row > 0 then table.insert( ret_pos_index, { index = pos_index - 4, combo = combo, atk_dir = 'mvRgeT' } ) end
    end

    -- 右上，不管单还是双，都只能攻击最近的一个位置
    if self.mvRgeTR == 1 or self.mvRgeTR == 2 then              -- 单
        if col < 3 and row > 0 then table.insert( ret_pos_index, { index = pos_index - 3, combo = combo, atk_dir = 'mvRgeTR' } ) end
    end

    -- 右
    if self.mvRgeR == 1 or self.mvRgeR == 2 then                  -- 单
        if col < 3 then table.insert( ret_pos_index, { index = pos_index + 1, combo = combo, atk_dir = 'mvRgeR' } ) end
    end

    -- 右下
    if self.mvRgeBR == 1 or self.mvRgeBR == 2 then           -- 单
        if col < 3 and row < 3 then table.insert( ret_pos_index, { index = pos_index + 5, combo = combo, atk_dir = 'mvRgeBR' } ) end
    end

    -- 下
    if self.mvRgeB == 1 or self.mvRgeB == 2 then                 -- 单
        if row < 3 then table.insert( ret_pos_index, { index = pos_index + 4, combo = combo, atk_dir = 'mvRgeB' } ) end
    end

    -- 左下
    if self.mvRgeBL == 1 or self.mvRgeBL == 2 then            -- 单
        if col > 0 and row < 3 then table.insert( ret_pos_index, { index = pos_index + 3, combo = combo, atk_dir = 'mvRgeBL' } ) end
    end

    -- 左
    if self.mvRgeL == 1 or self.mvRgeL == 2 then               -- 单
        if col > 0 then table.insert( ret_pos_index, { index = pos_index - 1, combo = combo, atk_dir = 'mvRgeL' } ) end
    end

    return ret_pos_index
end

function __verify_fight_object:canAttack( src_pos_index, target_pos_index )
    local all_atk_pos = self:getAllAttackPosIndex( src_pos_index )
    for _,v in ipairs( all_atk_pos ) do
        if v.index == target_pos_index then
            return true, v.atk_dir
        end
    end
    return false
end

function __verify_fight_object:doNormalHurt( src_grid_obj, restrain, attack_info, additional_se )
    -- 更新生命值
    if self.cur_hp > 0 then self:setCurHP( self.cur_hp - attack_info.real_damage ) end
end

function __verify_fight_object:doSkillHurt( src_grid_obj, damage_info, call_back_func )
    -- 造成的总伤害累加
    src_grid_obj.total_damage = src_grid_obj.total_damage + damage_info.real_damage

    -- 更新生命值
    if self.cur_hp > 0 then self:setCurHP( self.cur_hp - damage_info.real_damage ) end

    -- 附带击退效果
    if damage_info.beak_back_index then
        self:beakBack( src_grid_obj, damage_info.beak_back_index, call_back_func )
    else
        if call_back_func then call_back_func() end
    end
end

function __verify_fight_object:floatText( float_type, s_x, s_y, num, is_crit )
end

function __verify_fight_object:restore( src_grid_obj, hp, beak_back_index, call_back_func )
    local param_1, param_2 = self:getRestoreParam()
    local real_restore_hp = math.floor( hp * param_1 + param_2 )

    -- 更新生命值
    if self.cur_hp > 0 then self:setCurHP( self.cur_hp + real_restore_hp ) end

    if beak_back_index then
        self:beakBack( src_grid_obj, beak_back_index, call_back_func )
    else
        if call_back_func then call_back_func() end
    end
end

function __verify_fight_object:setCurHP( hp )
    __verify_base_object.setCurHP( self, hp )

    if self.death_event then
        self.death_cb_count:push( 1 )
        --self:tryDoDeath()
    end
end

function __verify_fight_object:declareDeath()
    if not self.death_event then
        verify_fight_manager.dying_fight_objs:push( self.obj_info.entity_id )

        self.death_event = true

        local all_src_entity_id = { self.obj_info.entity_id }
        local all_target_entity_id = { self.obj_info.entity_id }
        verify_fight_manager:triggerSkill( all_src_entity_id, all_target_entity_id, self, trigger_action.death, {}, verify_fight_manager.death_trigger_func, {} )
    end
end

function __verify_fight_object:tryDoDeath()
    if not self.death and self.death_cb_count:getElementCount() == 0 and self.cur_hp <= 0 then self:doDeath() end
end

function __verify_fight_object:doDeath()
    __verify_base_object.doDeath( self )
end

function __verify_fight_object:playDeathEffect( call_back_func )
    if call_back_func then call_back_func() end
end

function __verify_fight_object:getBaseDef()
    return self.def
end

function __verify_fight_object:receiveAttack( src_grid_obj, damage )
    -- 防御
    local base_def = self:getBaseDef()

    -- 物品防御
    if self.buff_item_effective['buff_def'] then base_def = base_def + self.buff_item_effective['buff_def'].param end

    local temp_def = math.floor( self:calculateBuffDebuff( src_grid_obj, self, base_def, verify_skill_system.__kind_type__.DefUp.value ) )
    damage = damage - temp_def

    -- 如果最后伤害小于 1 的话，就直接等于 1
    if damage < 1 then damage = 1 end

    return damage
end

function __verify_fight_object:receiveSkillAttack( damage )
    -- 如果最后伤害小于 1 的话，就直接等于 1
    if damage < 1 then damage = 1 end

    return damage
end

function __verify_fight_object:getBaseAtk()
    return self.atk
end

-- return damage, is_crit, is_miss
function __verify_fight_object:calculateNormalAttackTargetInfo( target_grid_obj )
    -- 如果闪避的话，后面不用计算了
    local is_miss = target_grid_obj:isDodge( self )
    if is_miss then return 0, false, true end

    -- 暴击
    local is_crit, crit_rate = self:isCritical( target_grid_obj, fight_const.critical_rate )

    -- 材料怪，都只掉 1 点血
    if target_grid_obj.obj_info.mtype ~= HERO_USEFOR_FIGHT then return 1, is_crit, false end

    local base_atk = self:getBaseAtk()

    -- 物品 BUFF 
    if self.buff_item_effective['buff_atk'] then base_atk = base_atk + self.buff_item_effective['buff_atk'].param end

    -- AtkUp
    local damage = math.floor( self:calculateBuffDebuff( self, target_grid_obj, base_atk, verify_skill_system.__kind_type__.AtkUp.value ) )
    damage = math.floor( self:calculateBuffDebuff( self, target_grid_obj, damage, verify_skill_system.__kind_type__.AtkAttr.value ) )

    damage = target_grid_obj:receiveAttack( self, damage )

    if is_crit then damage = damage * crit_rate end

    -- 属性相克关系
    restrain = attrRestrain( self, target_grid_obj )
    if restrain == 2 then
        damage = damage * self.obj_info.restrain_2
    elseif restrain == 0 then
        damage = damage * self.obj_info.restrain_0
    end

    -- 正常情况下，伤害至少是 1
    if damage < 1 then damage = 1 end

    -- 物免的话，伤害为 0
    if target_grid_obj:isInvincible() then damage = 0 end

    return math.floor( damage ), is_crit, false
end

function __verify_fight_object:getSkillAtk( target_grid_obj, damage )
    if target_grid_obj:isInvincible() then return 0 end
    if target_grid_obj.obj_info.mtype == HERO_USEFOR_FIGHT then
        -- 属性相克关系
        local restrain = attrRestrain( self, target_grid_obj )
        if restrain == 2 then
            damage = damage * self.obj_info.restrain_2
        elseif restrain == 0 then
            damage = damage * self.obj_info.restrain_0
        end

        return damage >= 1 and math.floor( damage ) or 1
    else
        return 1
    end
end

function __verify_fight_object:showAttackArrowAnimation( atk_dirs )
end

function __verify_fight_object:getNormalAttackTargets()
    local ret_attack_grid_objs = {}

    local all_attack_pos_index = self:getAllAttackPosIndex( self.pos_index )
    local function __is_valid_target__( target_grid_obj )
        -- 有可能技能已经把它打死了，只是还在播放血条扣血的动画，所以状态还活着，但正常来说，已经不可能攻击它了
        if target_grid_obj.death_event then return {} end

        -- 
        local atk_dirs = {}
        local all_pos_index = target_grid_obj:getAllPosIndex()
        for _,pos_info in ipairs( all_attack_pos_index ) do
            for _,pos_index in ipairs( all_pos_index ) do
                if pos_info.index == pos_index then table.insert( atk_dirs, pos_info.atk_dir ) end
            end
        end
        return atk_dirs
    end

    for _,grid_obj in ipairs( self.obj_info.type == 'enemy' and verify_fight_manager:getAllPetObjects() or verify_fight_manager:getAllMonsterObjects() ) do
        local atk_dirs = __is_valid_target__( grid_obj )
        if #atk_dirs > 0 then table.insert( ret_attack_grid_objs, { grid_obj = grid_obj, atk_dirs = atk_dirs } ) end
    end

    return ret_attack_grid_objs
end

function __verify_fight_object:getAttackPositionInfo( target_grid_obj, next_target_grid_obj )
    local attack_info = { target_grid_obj = target_grid_obj }

    return attack_info
end

function __verify_fight_object:startNormalAttack( call_back_func )
    if self:isForbidAttack() then return call_back_func() end

    local all_target_grid_objs = self:getNormalAttackTargets()

    if #all_target_grid_objs == 0 then return call_back_func() end

    --
    local all_src_entity_id = { self.obj_info.entity_id }
    local all_target_entity_id = {}
    local param_tbl = { [self.obj_info.entity_id] = {} }

    local atk_dirs = {}

    local ignore_trigger_entity_ids = {}
    local attack_list = { targets = {}, shadow_offset_y = self:getShadowOffsetY(), deadly_attack = false }
    for i,v in ipairs( all_target_grid_objs ) do
        local target_grid_obj = v.grid_obj

        for _,atk_dir in ipairs( v.atk_dirs ) do atk_dirs[atk_dir] = 1 end

        table.insert( all_target_entity_id, target_grid_obj.obj_info.entity_id )

        -- 
        local next_target_grid_obj = ( i + 1 <= #all_target_grid_objs and all_target_grid_objs[i+1].grid_obj or nil )
        local attack_info = self:getAttackPositionInfo( target_grid_obj, next_target_grid_obj )

        -- 伤害，暴击，丢失
        attack_info.real_damage, attack_info.is_crit, attack_info.is_miss = self:calculateNormalAttackTargetInfo( target_grid_obj )
        param_tbl[self.obj_info.entity_id][target_grid_obj.obj_info.entity_id] = { damage = attack_info.real_damage }

        -- 如果没有物理免疫的话
        if not target_grid_obj:isImmunityPhysical() then
            -- 暴击触发
            if attack_info.is_crit then
                local all_target_entity_id = { target_grid_obj.obj_info.entity_id }
                verify_fight_manager:triggerSkill( all_src_entity_id, all_target_entity_id, self, trigger_action.crit, {}, {} )
            end

            -- 闪避触发
            if attack_info.is_miss then
                local all_target_entity_id = { target_grid_obj.obj_info.entity_id }
                verify_fight_manager:triggerSkill( all_src_entity_id, all_target_entity_id, self, trigger_action.dodge, {}, {} )
            end

            -- 没有触发闪避，伤害致命，直接宣告死亡
            if not attack_info.is_miss and target_grid_obj.cur_hp <= attack_info.real_damage then target_grid_obj:declareDeath() end
        else
            attack_info.real_damage = 0
            table.insert( ignore_trigger_entity_ids, target_grid_obj.obj_info.entity_id )
        end

        -- 
        table.insert( attack_list.targets, attack_info )
    end

    verify_fight_manager:isDeadlyAttackAction( self.obj_info.type == 'player', attack_list )

    -- 伤害触发
    verify_fight_manager:triggerSkill( all_src_entity_id, all_target_entity_id, self, trigger_action.normal_attack, param_tbl, ignore_trigger_entity_ids )

    -- 
    self:beginNormalAttack( attack_list, function()
        self:normalAttackTarget( 1, attack_list, function()
            self:endNormalAttack( attack_list, function()
                processVerifyTriggerSkillFunc( call_back_func )
            end)
        end)
    end)
end

function __verify_fight_object:beginNormalAttack( attack_list, call_back_func )
    if call_back_func then call_back_func() end
end

function __verify_fight_object:normalAttackTarget( index, attack_list, call_back_func )
    local attack_info = attack_list.targets[index]
    if not attack_info then return call_back_func() end

    local function __real_attack__()
        self:hitTarget( attack_info )

        self:normalAttackTarget( index + 1, attack_list, call_back_func )
    end

    __real_attack__()
end

function __verify_fight_object:hitTarget( attack_info )
    if not attack_info.target_grid_obj:isImmunityPhysical() then
        -- 伤害
        attack_info.target_grid_obj:doNormalHurt( self, 0, attack_info, true )
    end
end

function __verify_fight_object:endNormalAttack( attack_list, call_back_func )
    if call_back_func then call_back_func() end
end

function __verify_fight_object:getHurtFloatPosition()
end

function __verify_fight_object:getRestoreFloatPosition()
end

function __verify_fight_object:getFloatPosition()
end

function __verify_fight_object:getSkillEffectNameFloatPosition()
end

function __verify_fight_object:getSkillNameFloatPosition()
end

function __verify_fight_object:updatePoisonState()
end

function __verify_fight_object:setAttrMaxLimit( attr_type, percent )
    local __attributes__ = {
        ['HP'] = function()
            local hp = math.floor( self.origin_max_hp * percent )
            self.max_hp = self.max_hp + hp
            if hp > 0 then self.cur_hp = self.cur_hp + hp end
            if self.cur_hp > self.max_hp then self.cur_hp = self.max_hp end
            self:setCurHP( self.cur_hp )
        end,
    }

    __attributes__[attr_type]()
end

function __verify_fight_object:playSkillAnimation( loop_count, call_back_func_1, call_back_func_2 )
    if call_back_func_1 then call_back_func_1() end
    if call_back_func_2 then call_back_func_2() end
end

function __verify_fight_object:playSkillSound()
end

function __verify_fight_object:showAttackArrow( v )
end

-------------------------------------------------------------------------------------------------------------------------------------
__verify_monster_object = class( 'verify_monster_object', __verify_fight_object )
function __verify_monster_object:ctor( obj_info, pos_index )
    __verify_fight_object.ctor( self, obj_info, pos_index )

    self.mvRgeTL = self.obj_info.mvRgeTR
    self.mvRgeTR = self.obj_info.mvRgeTL
    self.mvRgeR = self.obj_info.mvRgeL
    self.mvRgeL = self.obj_info.mvRgeR
    self.mvRgeBR = self.obj_info.mvRgeBL
    self.mvRgeBL = self.obj_info.mvRgeBR

    self:addDeathCallBackFunc( function() verify_fight_manager.monster_death_count = verify_fight_manager.monster_death_count + 1 end )
end

function __verify_monster_object:initModel()
end

function __verify_monster_object:setCurHP( hp )
    __verify_fight_object.setCurHP( self, hp )
end

function __verify_monster_object:isEnemy( grid_obj )
    return ( grid_obj.obj_info.type == 'player' ) and true or false
end

-------------------------------------------------------------------------------------------------------------------------------------
__verify_pet_object = class( 'verify_pet_object', __verify_fight_object )
function __verify_pet_object:ctor( obj_info, pos_index )
    __verify_fight_object.ctor( self, obj_info, pos_index )

    self:addDeathCallBackFunc( function() verify_fight_manager.player_death_count = verify_fight_manager.player_death_count + 1 end )
end

function __verify_pet_object:setCurHP( hp )
    __verify_fight_object.setCurHP( self, hp )
end

function __verify_pet_object:isEnemy( grid_obj )
    return ( grid_obj.obj_info.type == 'enemy' ) and true or false
end

function __verify_pet_object:modelDetailFollow( is_follow )
end

function __verify_pet_object:playSkillSound()
end

-------------------------------------------------------------------------------------------------------------------------------------
__verify_stone_object = class( 'verify_stone_object', __verify_base_object )
function __verify_stone_object:ctor( obj_info, pos_index )
    __verify_base_object.ctor( self, obj_info, pos_index )
end

function __verify_stone_object:initModel()
end

function __verify_stone_object:createModel()
end

function __verify_stone_object:canMoveTo()
    return true
end

function __verify_stone_object:effective( grid_obj )
    self.grid_obj = grid_obj
    grid_obj.grid_obj = self
end

function __verify_stone_object:playDeathEffect( call_back_func )
    if call_back_func then call_back_func() end
end

function __verify_stone_object:isEnemy( grid_obj )
    if self.grid_obj then return self.grid_obj:isEnemy( grid_obj ) end
    return false
end

function __verify_stone_object:canAttack( src_pos_index, target_pos_index )
    if self.grid_obj then return self.grid_obj:canAttack( src_pos_index, target_pos_index ) end
end

function __verify_stone_object:collectMovePosIndex( pos_index )
    if self.grid_obj then return self.grid_obj:collectMovePosIndex( pos_index ) end
end

function __verify_stone_object:isValidMovePosIndex( target_pos_index, mv_pos_index )
    if self.grid_obj then return self.grid_obj:isValidMovePosIndex( target_pos_index, mv_pos_index ) end
end

-------------------------------------------------------------------------------------------------------------------------------------
__verify_boss_object = class( 'verify_boss_object', __verify_monster_object )
function __verify_boss_object:ctor( obj_info, pos_index )
    __verify_monster_object.ctor( self, obj_info, pos_index )
    self.boss_name = ''
    self.large_skill_id = nil
    self.large_skill_prob = 0
    self.last_large_config = nil            -- 上一次使用的配置
    self.last_large_config_index = nil      -- 上一次配置对应的索引，可能是 1 ，也可能是 2 
    self.is_big_boss = true
end

function __verify_boss_object:initModel()
    __verify_monster_object.initModel( self )
end

-- 这是一个理论值
function __verify_boss_object:collectMovePosIndex( pos_index )
    -- 麻痹了，就哪也去不了
    if self:isForbidMove() then return {} end

    -- 这是一个不可达的位置
    if pos_index < 1 or pos_index > verify_fight_manager.grid_count_per_page then return {} end

    -- 
    local ret_pos_index = {}

    local row = math.floor( ( pos_index - 1 ) / 4 )
    local col = ( pos_index - 1 ) % 4

    -- 左上
    if self.mvRgeTL == 1 then               -- 单
        if col > 0 and row > 0 then table.insert( ret_pos_index, pos_index - 5 ) end
    elseif self.mvRgeTL == 2 then         -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while r > 0 and c > 0 do
            table.insert( ret_pos_index, temp_pos_index - 5 )

            r = r - 1
            c = c - 1
            temp_pos_index = temp_pos_index - 5
        end
    end

    -- 上
    if self.mvRgeT == 1 then                    -- 单
        if row > 0 then table.insert( ret_pos_index, pos_index - 4 ) end
    elseif self.mvRgeT == 2 then              -- 双
        local r = row
        local temp_pos_index = pos_index

        while r > 0 do
            table.insert( ret_pos_index, temp_pos_index - 4 )

            r = r - 1
            temp_pos_index = temp_pos_index - 4
        end
    end

    -- 右上
    if self.mvRgeTR == 1 then              -- 单
        if col < 2 and row > 0 then table.insert( ret_pos_index, pos_index - 3 ) end
    elseif self.mvRgeTR == 2 then        -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c < 2 and r > 0 do
            table.insert( ret_pos_index, temp_pos_index - 3 )

            r = r - 1
            c = c + 1
            temp_pos_index = temp_pos_index - 3
        end
    end

    -- 右
    if self.mvRgeR == 1 then                  -- 单
        if col < 2 then table.insert( ret_pos_index, pos_index + 1 ) end
    elseif self.mvRgeR == 2 then            -- 双
        local c = col
        local temp_pos_index = pos_index

        while c < 2 do
            table.insert( ret_pos_index, temp_pos_index + 1 )

            c = c + 1
            temp_pos_index = temp_pos_index + 1
        end
    end

    -- 右下
    if self.mvRgeBR == 1 then           -- 单
        if col < 2 and row < 2 then table.insert( ret_pos_index, pos_index + 5 ) end
    elseif self.mvRgeBR == 2 then     -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c < 2 and r < 2 do
            table.insert( ret_pos_index, temp_pos_index + 5 )

            r = r + 1
            c = c + 1
            temp_pos_index = temp_pos_index + 5
        end
    end

    -- 下
    if self.mvRgeB == 1 then                 -- 单
        if row < 2 then table.insert( ret_pos_index, pos_index + 4 ) end
    elseif self.mvRgeB == 2 then           -- 双
        local r = row
        local temp_pos_index = pos_index

        while r < 2 do
            table.insert( ret_pos_index, temp_pos_index + 4 )

            r = r + 1
            temp_pos_index = temp_pos_index + 4
        end
    end

    -- 左下
    if self.mvRgeBL == 1 then            -- 单
        if col > 0 and row < 2 then table.insert( ret_pos_index, pos_index + 3 ) end
    elseif self.mvRgeBL == 2 then      -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c > 0 and r < 2 do
            table.insert( ret_pos_index, temp_pos_index + 3 )

            c = c - 1
            r = r + 1
            temp_pos_index = temp_pos_index + 3
        end
    end

    -- 左
    if self.mvRgeL == 1 then               -- 单
        if col > 0 then table.insert( ret_pos_index, pos_index - 1 ) end
    elseif self.mvRgeL == 2 then         -- 双
        local c = col
        local temp_pos_index = pos_index

        while c > 0 do
            table.insert( ret_pos_index, temp_pos_index - 1 )

            c = c - 1
            temp_pos_index = temp_pos_index - 1
        end
    end

    return ret_pos_index
end

-- 这是一个根据当前状态，所能真实可达的
function __verify_boss_object:collectValidMovePosIndex()
    -- 麻痹了，就哪也去不了
    if self:isForbidMove() then return {} end

    local pos_index = self.pos_index
    local mv_pos_index = self:collectMovePosIndex( pos_index )

    -- 
    local ret_pos_index = {}

    local row = math.floor( ( pos_index - 1 ) / 4 )
    local col = ( pos_index - 1 ) % 4

    -- 左上
    if self.mvRgeTL == 1 then               -- 单
        if self:isValidMovePosIndex( pos_index - 5, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index - 5, show_pos_index = { pos_index - 5, pos_index - 4, pos_index - 1 } } )
        end
    elseif self.mvRgeTL == 2 then         -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while r > 0 and c > 0 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index - 5, mv_pos_index )
            if not can_mv_to and not can_pass then break end

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index - 5, show_pos_index = { temp_pos_index - 5, temp_pos_index - 4, temp_pos_index - 1 } } )
            end

            r = r - 1
            c = c - 1
            temp_pos_index = temp_pos_index - 5
        end
    end

    -- 上
    if self.mvRgeT == 1 then                    -- 单
        if self:isValidMovePosIndex( pos_index - 4, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index - 4, show_pos_index = { pos_index - 4, pos_index - 3 } } )
        end
    elseif self.mvRgeT == 2 then              -- 双
        local r = row
        local temp_pos_index = pos_index

        while r > 0 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index - 4, mv_pos_index )
            if not can_mv_to and not can_pass then break end

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index - 4, show_pos_index = { temp_pos_index - 4, temp_pos_index - 3 } } )
            end

            r = r - 1
            temp_pos_index = temp_pos_index - 4
        end
    end

    -- 右上
    if self.mvRgeTR == 1 then              -- 单
        if self:isValidMovePosIndex( pos_index - 3, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index - 3, show_pos_index = { pos_index - 3, pos_index - 2, pos_index + 2 } } )
        end
    elseif self.mvRgeTR == 2 then        -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c < 2 and r > 0 do
            local can_mv_to, can_pass = verify_fight_manager:isValidBigMovePosIndex( self, temp_pos_index - 3 )
            if not can_mv_to and not can_pass then break end

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index - 3, show_pos_index = { temp_pos_index - 3, temp_pos_index - 2, temp_pos_index + 2 } } )
            end

            r = r - 1
            c = c + 1
            temp_pos_index = temp_pos_index - 3
        end
    end

    -- 右
    if self.mvRgeR == 1 then                  -- 单
        if self:isValidMovePosIndex( pos_index + 1, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index + 1, show_pos_index = { pos_index + 2, pos_index + 6 } } )
        end
    elseif self.mvRgeR == 2 then            -- 双
        local c = col
        local temp_pos_index = pos_index

        while c < 3 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index + 1, mv_pos_index )
            if not can_mv_to and not can_pass then break end

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index + 1, show_pos_index = { temp_pos_index + 2, temp_pos_index + 6 } } )
            end

            c = c + 1
            temp_pos_index = temp_pos_index + 1
        end
    end

    -- 右下
    if self.mvRgeBR == 1 then           -- 单
        if self:isValidMovePosIndex( pos_index + 5, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index + 5, show_pos_index = { pos_index + 6, pos_index + 9, pos_index + 10 } } )
        end
    elseif self.mvRgeBR == 2 then     -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c < 2 and r < 2 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index + 5, mv_pos_index )
            if not can_mv_to and not can_pass then break end

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index + 5, show_pos_index = { temp_pos_index + 6, temp_pos_index + 9, temp_pos_index + 10 } } )
            end

            r = r + 1
            c = c + 1
            temp_pos_index = temp_pos_index + 5
        end
    end

    -- 下
    if self.mvRgeB == 1 then                 -- 单
        if self:isValidMovePosIndex( pos_index + 4, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index + 4, show_pos_index = { pos_index + 8, pos_index + 9 } } )
        end
    elseif self.mvRgeB == 2 then           -- 双
        local r = row
        local temp_pos_index = pos_index

        while r < 2 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index + 4, mv_pos_index )
            if not can_mv_to and not can_pass then break end

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index + 4, show_pos_index = { temp_pos_index + 8, temp_pos_index + 9 } } )
            end

            r = r + 1
            temp_pos_index = temp_pos_index + 4
        end
    end

    -- 左下
    if self.mvRgeBL == 1 then            -- 单
        if self:isValidMovePosIndex( pos_index + 3, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index + 3, show_pos_index = { pos_index + 3, pos_index + 7, pos_index + 8 } } )
        end
    elseif self.mvRgeBL == 2 then      -- 双
        local r,c = row,col
        local temp_pos_index = pos_index

        while c > 0 and r < 3 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index + 3, mv_pos_index )
            if not can_mv_to and not can_pass then break end

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index + 3, show_pos_index = { temp_pos_index + 3, temp_pos_index + 7, temp_pos_index + 8 } } )
            end

            c = c - 1
            r = r + 1
            temp_pos_index = temp_pos_index + 3
        end
    end

    -- 左
    if self.mvRgeL == 1 then               -- 单
        if self:isValidMovePosIndex( pos_index - 1, mv_pos_index ) then
            table.insert( ret_pos_index, { target_pos_index = pos_index - 1, show_pos_index = { pos_index - 1, pos_index + 3 } } )
        end
    elseif self.mvRgeL == 2 then         -- 双
        local c = col
        local temp_pos_index = pos_index

        while c > 0 do
            local can_mv_to, can_pass = self:isValidMovePosIndex( temp_pos_index - 1, mv_pos_index )
            if not can_mv_to and not can_pass then break end

            if can_mv_to then
                table.insert( ret_pos_index, { target_pos_index = temp_pos_index - 1, show_pos_index = { temp_pos_index - 1, temp_pos_index + 3 } } )
            end

            c = c - 1
            temp_pos_index = temp_pos_index - 1
        end
    end

    return ret_pos_index
end

function __verify_boss_object:isValidMovePosIndex( target_pos_index, mv_pos_index )
    -- 不是一个有效的位置，不能移动过去
    local target_grid_item_1 = verify_fight_manager:getGridItemByPosIndex( target_pos_index )
    if not target_grid_item_1 then return false, false end
    local target_grid_item_2 = verify_fight_manager:getGridItemByPosIndex( target_pos_index + 1 )
    if not target_grid_item_2 then return false, false end
    local target_grid_item_3 = verify_fight_manager:getGridItemByPosIndex( target_pos_index + 4 )
    if not target_grid_item_3 then return false, false end
    local target_grid_item_4 = verify_fight_manager:getGridItemByPosIndex( target_pos_index + 5 )
    if not target_grid_item_4 then return false, false end

    --
    local can_mv_to, can_pass = true, true

    -- 在这个位置上已经有东西了
    if target_grid_item_1.grid_obj then
        local can_mv_to_1, can_pass_1 = self:canMoveTo( target_grid_item_1.grid_obj )
        if not can_mv_to_1 then can_mv_to = false end
        if not can_pass_1 then can_pass = false end
    end
    if target_grid_item_2.grid_obj then
        local can_mv_to_2, can_pass_2 = self:canMoveTo( target_grid_item_2.grid_obj )
        if not can_mv_to_2 then can_mv_to = false end
        if not can_pass_2 then can_pass = false end
    end
    if target_grid_item_3.grid_obj then
        local can_mv_to_3, can_pass_3 = self:canMoveTo( target_grid_item_3.grid_obj )
        if not can_mv_to_3 then can_mv_to = false end
        if not can_pass_3 then can_pass = false end
    end
    if target_grid_item_4.grid_obj then
        local can_mv_to_4, can_pass_4 = self:canMoveTo( target_grid_item_4.grid_obj )
        if not can_mv_to_4 then can_mv_to = false end
        if not can_pass_4 then can_pass = false end
    end

    if can_mv_to then
        -- 遍历所有可以移动的位置，看是否有 target_pos_index
        for _,pos_index in ipairs( mv_pos_index ) do
            -- target_pos_index 在可移动列表中，这是一个有效的可移动的位置
            if pos_index == target_pos_index then return true, can_pass end
        end

        return false, can_pass
    end

    -- 找不到，不可移动
    return can_mv_to, can_pass
end

function __verify_boss_object:canMoveTo( target_grid_obj )
    if not __verify_monster_object.canMoveTo( self, target_grid_obj ) then
        -- 自己的同伴的位置，不能移动过去
        if self.obj_info.type == target_grid_obj.obj_info.type then
            -- 如果是自己的话可以移动穿越
            if target_grid_obj == self then return true, true end
            -- 可以穿越不可移动
            return false, true
        end

        -- 敌人的位置，不能移动过去
        if self:isEnemy( target_grid_obj ) then return false, false end

        -- 障碍物，除非你能飞
        if target_grid_obj.obj_info.type == 'stone' and not self:hasAbilityFly() then return false, false end
    end

    return true, true
end

function __verify_boss_object:getAllAttackPosIndex( pos_index )
    -- 这是一个不可达的位置
    if pos_index < 1 or pos_index > verify_fight_manager.grid_count_per_page then return {} end

    -- 
    local ret_pos_index = {}

    local row = math.floor( ( pos_index - 1 ) / 4 )
    local col = ( pos_index - 1 ) % 4

    -- 攻击的次数，与其星级相关
    --local combo = ATK_COUNT_BY_RARITY[self.obj_info.rarity]
    local combo = 1

    -- 左上，不管单还是双，都只能攻击最近的一个位置
    if self.mvRgeTL == 1 or self.mvRgeTL == 2 then               -- 单
        if col > 0 and row > 0 then table.insert( ret_pos_index, { index = pos_index - 5, combo = combo, atk_dir = 'mvRgeTL' } ) end
    end

    -- 上，不管单还是双，都只能攻击最近的一个位置
    if self.mvRgeT == 1 or self.mvRgeT == 2 then                    -- 单
        if row > 0 then
            table.insert( ret_pos_index, { index = pos_index - 4, combo = combo, atk_dir = 'mvRgeT' } )
            table.insert( ret_pos_index, { index = pos_index - 3, combo = combo, atk_dir = 'mvRgeT' } )
        end
    end

    -- 右上，不管单还是双，都只能攻击最近的一个位置
    if self.mvRgeTR == 1 or self.mvRgeTR == 2 then              -- 单
        if col < 2 and row > 0 then table.insert( ret_pos_index, { index = pos_index - 2, combo = combo, atk_dir = 'mvRgeTR' } ) end
    end

    -- 右
    if self.mvRgeR == 1 or self.mvRgeR == 2 then                  -- 单
        if col < 2 then
            table.insert( ret_pos_index, { index = pos_index + 2, combo = combo, atk_dir = 'mvRgeR' } )
            table.insert( ret_pos_index, { index = pos_index + 6, combo = combo, atk_dir = 'mvRgeR' } )
        end
    end

    -- 右下
    if self.mvRgeBR == 1 or self.mvRgeBR == 2 then           -- 单
        if col < 2 and row < 2 then table.insert( ret_pos_index, { index = pos_index + 10, combo = combo, atk_dir = 'mvRgeBR' } ) end
    end

    -- 下
    if self.mvRgeB == 1 or self.mvRgeB == 2 then                 -- 单
        if row < 2 then
            table.insert( ret_pos_index, { index = pos_index + 8, combo = combo, atk_dir = 'mvRgeB' } )
            table.insert( ret_pos_index, { index = pos_index + 9, combo = combo, atk_dir = 'mvRgeB' } )
        end
    end

    -- 左下
    if self.mvRgeBL == 1 or self.mvRgeBL == 2 then            -- 单
        if col > 0 and row < 2 then table.insert( ret_pos_index, { index = pos_index + 7, combo = combo, atk_dir = 'mvRgeBL' } ) end
    end

    -- 左
    if self.mvRgeL == 1 or self.mvRgeL == 2 then               -- 单
        if col > 0 then
            table.insert( ret_pos_index, { index = pos_index - 1, combo = combo, atk_dir = 'mvRgeL' } )
            table.insert( ret_pos_index, { index = pos_index + 3, combo = combo, atk_dir = 'mvRgeL' } )
        end
    end

    return ret_pos_index
end

function __verify_boss_object:switchMode()
    local mode_flag = {
        function( large_config )            -- 完全随机的
            return self:getRandomNumber( 0, 100 ) <= large_config.flgPrm1
        end,
        function( large_config )            -- HP 低于一定百分比
            return ( self.cur_hp / self.max_hp ) <= ( large_config.flgPrm1 / 100 )
        end,
        function( large_config )            -- 攻击别人的伤害总和
            return self.total_damage > large_config.flgPrm1
        end,
        function( large_config )            -- 使用过某个技能
            return table.hasValue( self.used_skill_ids, large_config.flgPrm1 )
        end,
        function( large_config )            -- 受到的最大连击
            return self.attack_max_combo > large_config.flgPrm1
        end,
    }

    -- 切换模式，默认使用第一个，当然第一个也可能没有
    local mode_index = 1
    for i,large_config in ipairs( self.obj_info.all_large_config ) do
        if mode_flag[large_config.flg]( large_config ) then
            mode_index = i

            break
        end
    end

    self:setBossMode( mode_index )
end

function __verify_boss_object:setBossMode( mode_index )
    local sel_large_config = self.obj_info.all_large_config[mode_index]
    if sel_large_config then
        -- 有可能只有一个
        local index = ( sel_large_config.cmd2 == '0.0' and 1 or math.floor( self:getRandomNumber( 1, 2 ) ) )
        if sel_large_config ~= self.last_large_config or index ~= self.last_large_config_index then
            self.last_large_config = sel_large_config

            -- boss name
            self.boss_name = sel_large_config[string.format('cmd%d',index)]

            -- large skill
            self.large_skill = nil
            self.large_skill_id = sel_large_config[string.format('skill%d',index)]
            self.large_skill_prob = sel_large_config[string.format('prob%d',index)]
            if self.large_skill_id ~= 0 then self.large_skill = __fight_skill.new( self, self.large_skill_id ) end

            -- 攻击和移动的箭头
            self.mvRgeTL = sel_large_config[string.format('mvRge%dTL',index)]
            self.mvRgeT = sel_large_config[string.format('mvRge%dT',index)]
            self.mvRgeTR = sel_large_config[string.format('mvRge%dTR',index)]
            self.mvRgeR = sel_large_config[string.format('mvRge%dR',index)]
            self.mvRgeBR = sel_large_config[string.format('mvRge%dBR',index)]
            self.mvRgeB = sel_large_config[string.format('mvRge%dB',index)]
            self.mvRgeBL = sel_large_config[string.format('mvRge%dBL',index)]
            self.mvRgeL = sel_large_config[string.format('mvRge%dL',index)]

            -- 重新创建
            self:recreateModelDetail()
        end
    end
end

function __verify_boss_object:recreateModelDetail()
end

function __verify_boss_object:useLargeSkill( call_back_func )
    -- 放技能
    if self.large_skill and self:getRandomNumber( 0, 10000 ) < self.large_skill_prob then
        local all_src_entity_id = { self.obj_info.entity_id }
        local all_target_entity_id = {}
        for _,grid_obj in ipairs( verify_fight_manager:getAllPetObjects() ) do table.insert( all_target_entity_id, grid_obj.obj_info.entity_id ) end
        self.large_skill:playSkillEffect( all_src_entity_id, all_target_entity_id, {}, call_back_func )
    else
        if call_back_func then call_back_func() end
    end
end

-- 返回占的格子索引，BOSS 就会返回 4 个索引
function __verify_boss_object:getAllPosIndex()
    return { self.pos_index, self.pos_index + 1, self.pos_index + 4, self.pos_index + 5 }
end

function __verify_boss_object:getPosition()
end

function __verify_boss_object:doDeath()
    self:_realDoDeath()
end

function __verify_boss_object:_realDoDeath()
    -- 已经死过一次了，不用再死一次了
    if self.death then return end

    self.death = true

    self:playDeathEffect( function()
        -- 其他的回调
        for func,_ in pairs( self.death_call_back_func ) do func() end

        local drop_list = {}
        for _,v in ipairs( self.obj_info.drop2 or {} ) do
            if v.type ~= ITEM_TYPE_MONEY and v.type ~= ITEM_TYPE_SOUL then
                table.insert( drop_list, v )
            end
        end
        verify_fight_manager:gainDropReward( self, drop_list )

        local grid_item = verify_fight_manager:getGridItemByPosIndex( self.pos_index )
        if grid_item then
            -- 其他恢复的，不需要
            if self.obj_info.type == 'player' or self.obj_info.type == 'enemy' then
                if grid_item.grid_obj and grid_item.grid_obj.obj_info.type == 'stone' then
                    grid_item.grid_obj.grid_obj = nil
                else
                    grid_item.grid_obj = nil
                end
            end
        end

        verify_fight_manager.dying_fight_objs:pop( self.obj_info.entity_id )
        verify_fight_manager:tryNextFightState()

        -- 
        self:destroy()
    end)
end

-------------------------------------------------------------------------------------------------------------------------------------
__verify_buff_object = class( 'verify_buff_object', __verify_base_object )
function __verify_buff_object:ctor( obj_info, pos_index )
    __verify_base_object.ctor( self, obj_info, pos_index )

    self.buff_type = obj_info.type
    self.add_effect_func = nil
    self.effect_func = nil
    self.remove_effect_func = nil
end

function __verify_buff_object:canMoveTo()
    return true
end

function __verify_buff_object:createModel()
end

function __verify_buff_object:playDeathEffect( call_back_func )
    verify_fight_manager.buff_item = nil
    if call_back_func then call_back_func() end
end

function __verify_buff_object:effective( grid_obj )
    if grid_obj:hasAbilityShare() then
        local all_ally_objects = verify_fight_manager:getAllAllyObjects( grid_obj )
        for _,target_grid_obj in ipairs( all_ally_objects ) do
            self:realEffective( target_grid_obj )
        end
    else
        self:realEffective( grid_obj )
    end

    self:doDeath()
end

function __verify_buff_object:realEffective( target_grid_obj )
    local param = self:getEffectiveParam( target_grid_obj )
    target_grid_obj:addBuffItemEffective( self.buff_type, self.effect_name, self.obj_info.last_round, param, self.add_effect_func, self.effect_func, self.remove_effect_func )
end

function __verify_buff_object:getEffectiveParam( target_grid_obj )
    return math.floor( self:calculateEffectiveParam( self:getEffectiveSrcParam( target_grid_obj ) ) )
end

function __verify_buff_object:getEffectiveSrcParam( target_grid_obj )
    return 0
end

function __verify_buff_object:calculateEffectiveParam( src_param )
    if self.obj_info.kind == 0 then return self.obj_info.val end
    if self.obj_info.kind == 1 then return src_param * self.obj_info.val / 100 end
    return self.obj_info.val + src_param
end

-- 攻击
__verify_buff_atk_object = class( 'verify_buff_atk_object', __verify_buff_object )
function __verify_buff_atk_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
    self.buff_type = 'buff_atk'
end

function __verify_buff_atk_object:getEffectiveSrcParam( target_grid_obj )
    return target_grid_obj.atk
end

-- 防御
__verify_buff_def_object = class( 'verify_buff_def_object', __verify_buff_object )
function __verify_buff_def_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
    self.buff_type = 'buff_def'
end

function __verify_buff_def_object:getEffectiveSrcParam( target_grid_obj )
    return target_grid_obj.def
end

-- 移动
__verify_buff_mv_object = class( 'verify_buff_mv_object', __verify_buff_object )
function __verify_buff_mv_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )

    self.add_effect_func = function( target_grid_obj )
        target_grid_obj.mvRgeTL = 2
        target_grid_obj.mvRgeT = 2
        target_grid_obj.mvRgeTR = 2
        target_grid_obj.mvRgeR = 2
        target_grid_obj.mvRgeBR = 2
        target_grid_obj.mvRgeB = 2
        target_grid_obj.mvRgeBL = 2
        target_grid_obj.mvRgeL = 2
    end
    self.remove_effect_func = function( target_grid_obj )
        target_grid_obj.mvRgeT   = target_grid_obj.obj_info.mvRgeT
        target_grid_obj.mvRgeB   = target_grid_obj.obj_info.mvRgeB
        target_grid_obj.mvRgeTL  = ( target_grid_obj.obj_info.type == 'player' and target_grid_obj.obj_info.mvRgeTL or target_grid_obj.obj_info.mvRgeTR )
        target_grid_obj.mvRgeTR  = ( target_grid_obj.obj_info.type == 'player' and target_grid_obj.obj_info.mvRgeTR or target_grid_obj.obj_info.mvRgeTL )
        target_grid_obj.mvRgeR   = ( target_grid_obj.obj_info.type == 'player' and target_grid_obj.obj_info.mvRgeR or target_grid_obj.obj_info.mvRgeL )
        target_grid_obj.mvRgeBR  = ( target_grid_obj.obj_info.type == 'player' and target_grid_obj.obj_info.mvRgeBR or target_grid_obj.obj_info.mvRgeBL )
        target_grid_obj.mvRgeBL  = ( target_grid_obj.obj_info.type == 'player' and target_grid_obj.obj_info.mvRgeBL or target_grid_obj.obj_info.mvRgeBR )
        target_grid_obj.mvRgeL   = ( target_grid_obj.obj_info.type == 'player' and target_grid_obj.obj_info.mvRgeL or target_grid_obj.obj_info.mvRgeR )
    end
end

-- 暴击
__verify_buff_crit_object = class( 'verify_buff_crit_object', __verify_buff_object )
function __verify_buff_crit_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
end

function __verify_buff_crit_object:calculateEffectiveParam( src_param )
    return self.obj_info.val
end

-- 无敌
__verify_buff_inv_object = class( 'verify_buff_inv_object', __verify_buff_object )
function __verify_buff_inv_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
end

-- 恢复
__verify_buff_restore_object = class( 'verify_buff_restore_object', __verify_buff_object )
function __verify_buff_restore_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
end

function __verify_buff_restore_object:getEffectiveSrcParam( target_grid_obj )
    return target_grid_obj.max_hp
end

function __verify_buff_restore_object:calculateEffectiveParam( src_param )
    local param = math.floor( __verify_buff_object.calculateEffectiveParam( self, src_param ) )
    if param < 1 then param = 1 end
    return param
end

function __verify_buff_restore_object:realEffective( target_grid_obj )
    local param = self:getEffectiveParam( target_grid_obj )
    target_grid_obj:restore( nil, param )
end

-- 飞行
__verify_buff_fly_object = class( 'verify_buff_fly_object', __verify_buff_object )
function __verify_buff_fly_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
end

-- 共享
__verify_buff_share_object = class( 'verify_buff_share_object', __verify_buff_object )
function __verify_buff_share_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
end

-- 回合数
__verify_buff_round_object = class( 'verify_buff_round_object', __verify_buff_object )
function __verify_buff_round_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
end

function __verify_buff_round_object:effective( grid_obj )
    verify_fight_manager.verify_fight_control:setCurLastRound( verify_fight_manager.verify_fight_control.cur_last_round + self.obj_info.val )

    self:doDeath()
end

-- 破坏障碍物(就是石块)
__verify_buff_stone_broken_object = class( 'verify_buff_stone_broken_object', __verify_buff_object )
function __verify_buff_stone_broken_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
end

function __verify_buff_stone_broken_object:effective( grid_obj )
    local all_stone_grid_items = {}
    for _,grid_item in ipairs( verify_fight_manager.all_grid_items ) do
        if grid_item.grid_obj and grid_item.grid_obj.obj_info.type == 'stone' then
            table.insert( all_stone_grid_items, grid_item )
        end
    end

    -- 如果有石块的话
    if #all_stone_grid_items > 0 then
        local index = math.floor( verify_fight_manager:getRandomNumber( 1, #all_stone_grid_items ) )
        local grid_item = all_stone_grid_items[index]
        local stone_grid_obj = grid_item.grid_obj

        -- 石块上有HERO
        if stone_grid_obj.grid_obj then
            grid_item.grid_obj = stone_grid_obj.grid_obj
            grid_item.grid_obj.grid_obj = nil
        else
            grid_item.grid_obj = nil
        end

        stone_grid_obj:doDeath()
    end

    -- 
    self:doDeath()
end

-- 奖励
__verify_buff_reward_object = class( 'verify_buff_reward_object', __verify_buff_object )
function __verify_buff_reward_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
end

function __verify_buff_reward_object:effective( target_grid_obj )
    if target_grid_obj.obj_info.type == 'player' then
        verify_fight_manager.verify_fight_control:gainReward( v )
        self.player_gain_reward = true
    end

    self:doDeath()
end

-- 箱子
__verify_buff_chest_object = class( 'verify_buff_chest_object', __verify_buff_object )
function __verify_buff_chest_object:ctor( obj_info, pos_index )
    __verify_buff_object.ctor( self, obj_info, pos_index )
end

function __verify_buff_chest_object:effective( target_grid_obj )
    verify_fight_manager.verify_fight_control.end_treasure.gain_chest = true

    self:doDeath()
end

