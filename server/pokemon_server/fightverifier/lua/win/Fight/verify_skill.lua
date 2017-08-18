-- ./win/Fight/skill.lua
require 'win.Fight.verify_skill_system'

--------------------------------------------------------------------------------------------------------------------------------------------------------
-- 技能是否触发的条件 ----------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------
-- action
trigger_action = {
    ['fight_turn_front']                        = 1,                    -- 战斗回合开始
    ['fight_turn_end']                          = 2,                    -- 战斗回合结束
    ['player_turn_front']                       = 3,                    -- 玩家回合开始
    ['player_turn_end']                         = 4,                    -- 玩家回合结束
    ['enemy_turn_front']                        = 5,                    -- 怪物回合开始
    ['enemy_turn_end']                          = 6,                    -- 怪物回合结束
    ['normal_attack']                           = 7,                    -- 普通攻击 被击 xyz
    ['crit']                                    = 8,                    -- 暴击 xyz
    ['dodge']                                   = 9,                    -- 闪避 xyz
    ['skill_hurt']                              = 10,                   -- 技能伤害 xyz
    ['skill_restore']                           = 11,                   -- 技能治疗 xyz
    ['skill_beak_back']                         = 12,                   -- 技能击退 xyz
    ['skill_atk_up']                            = 13,                   -- 技能 BUFF atk up
    ['skill_atk_down']                          = 14,                   -- 技能 BUFF atk down
    ['skill_def_up']                            = 15,                   -- 技能 BUFF def up
    ['skill_def_down']                          = 16,                   -- 技能 BUFF def down
    ['skill_crit_up']                           = 17,                   -- 技能 BUFF crit up
    ['skill_crit_down']                         = 18,                   -- 技能 BUFF crit down
    ['skill_crit_val_up']                       = 19,                   -- 技能 BUFF crit value up
    ['skill_crit_val_down']                     = 20,                   -- 技能 BUFF crit value down
    ['skill_dodge_up']                          = 21,                   -- 技能 BUFF dodge up
    ['skill_dodge_down']                        = 22,                   -- 技能 BUFF dodge down
    ['skill_poison']                            = 23,                   -- 技能 BUFF poison
    ['skill_atk_attr_up']                       = 24,                   -- 技能 BUFF atk up
    ['skill_atk_attr_down']                     = 25,                   -- 技能 BUFF atk down
    ['skill_def_attr_up']                       = 26,                   -- 技能 BUFF def up
    ['skill_def_attr_down']                     = 27,                   -- 技能 BUFF def down
    ['skill_immunity_physics']                  = 28,                   -- 技能 BUFF 物理伤害免疫
    ['skill_immunity_magic']                    = 29,                   -- 技能 BUFF 魔法免疫
    ['skill_paralysis']                         = 30,                   -- 技能 BUFF 麻痹
    ['death']                                   = 31,                   -- 死亡 xyz
    ['move']                                    = 32,                   -- 移动
    ['attack_front']                            = 33,                   -- 攻击前 xyz
    ['skill_antiInjury']                        = 34,                   -- 技能反伤触发
    ['normal_attack_antiInjury']                = 35,                   -- 普通攻击反伤触发
    ['skill_hp_limit']                          = 36,                   -- 技能 BUFF 生命值上限
    ['skill_silence']                           = 37,                   -- 技能 BUFF 沉默
    ['skill_fly']                               = 38,                   -- 技能 BUFF 飞行
    ['skill_share']                             = 39,                   -- 技能 BUFF 共享
    ['skill_immunity_dizziness']                = 40,                   -- 技能 BUFF 免疫眩晕
    ['skill_immunity_silence']                  = 41,                   -- 技能 BUFF 免疫沉默
    ['skill_immunity_skill_hurt']               = 42,                   -- 技能 BUFF 免疫技能伤害
    ['skill_immunity_poison']                   = 43,                   -- 技能 BUFF 免疫中毒
    ['skill_immunity_disperse']                 = 44,                   -- 技能 BUFF 免疫驱散
    ['skill_invincible']                        = 45,                   -- 技能 BUFF 无敌
    ['skill_reduce_restore']                    = 46,                   -- 技能 BUFF 降低任意的治疗效果
    ['skill_forbid_move']                       = 47,                   -- 技能 BUFF 禁止移动
    ['skill_forbid_attack']                     = 48,                   -- 技能 BUFF 禁止攻击
    ['skill_hurt_up']                           = 49,                   -- 技能 BUFF 释放的技能伤害增加或减少
    ['skill_hurt_down']                         = 50,                   -- 技能 BUFF 受到的技能伤害增加或减少
}

-- 关系
local trigger_relationship = {
    { is_valid = function( skill_grid_obj, grid_obj ) return true end, },                                       -- 任意     = 1
    { is_valid = function( skill_grid_obj, grid_obj ) return skill_grid_obj:isTeammate( grid_obj ) end, },      -- 队友     = 2
    { is_valid = function( skill_grid_obj, grid_obj ) return not skill_grid_obj:isTeammate( grid_obj ) end, },  -- 敌人     = 3
}

local trigger_rge = {
    {       -- 全部          = 1
        is_valid_pos_index = function( skill_pos_index, pos_index )
            return true
        end,
    },
    {       -- 自己         = 2
        is_valid_pos_index = function( skill_pos_index, pos_index )
            return skill_pos_index == pos_index
        end,
    },
    {       -- 横向   = 3
        is_valid_pos_index = function( skill_pos_index, pos_index )
            local skill_grid_item = verify_fight_manager:getGridItemByPosIndex( skill_pos_index )
            if not skill_grid_item then return false end
            local grid_item = verify_fight_manager:getGridItemByPosIndex( pos_index )
            if not grid_item then return false end
            return skill_grid_item.row == grid_item.row
        end,
    },
    {       -- 纵向     = 4
        is_valid_pos_index = function( skill_pos_index, pos_index )
            local skill_grid_item = verify_fight_manager:getGridItemByPosIndex( skill_pos_index )
            if not skill_grid_item then return false end
            local grid_item = verify_fight_manager:getGridItemByPosIndex( pos_index )
            if not grid_item then return false end
            return skill_grid_item.col == grid_item.col
        end,
    },
    {       -- 边缘一格       = 5
        is_valid_pos_index = function( skill_pos_index, pos_index )
            local edge_pos_index = {}
            local function __append__( index ) if index >= 1 and index <= 16 then table.insert( edge_pos_index, index ) end end

            __append__( skill_pos_index - 5 )
            __append__( skill_pos_index - 4 )
            __append__( skill_pos_index - 3 )
            __append__( skill_pos_index - 1 )
            __append__( skill_pos_index - 0 )
            __append__( skill_pos_index + 1 )
            __append__( skill_pos_index + 3 )
            __append__( skill_pos_index + 4 )
            __append__( skill_pos_index + 5 )

            return table.hasValue( edge_pos_index, pos_index )
        end,
    },
}

local trigger_attr = {
    { is_valid_attr = function( skill_grid_obj, grid_obj ) return true end, },                                              -- 无       = 1
    { is_valid_attr = function( skill_grid_obj, grid_obj ) return grid_obj.obj_info.attr == hero_attr_fire end, },     -- 火       = 2
    { is_valid_attr = function( skill_grid_obj, grid_obj ) return grid_obj.obj_info.attr == hero_attr_water end, },    -- 水       = 3
    { is_valid_attr = function( skill_grid_obj, grid_obj ) return grid_obj.obj_info.attr == hero_attr_wood end, },     -- 木       = 4
    { is_valid_attr = function( skill_grid_obj, grid_obj ) return grid_obj.obj_info.attr == hero_attr_light end, },    -- 光       = 5
    { is_valid_attr = function( skill_grid_obj, grid_obj ) return grid_obj.obj_info.attr == hero_attr_dark end, },     -- 暗       = 6
    { is_valid_attr = function( skill_grid_obj, grid_obj ) return attrRestrain( skill_grid_obj, grid_obj ) == 2 end, },     -- 相克     = 7
    { is_valid_attr = function( skill_grid_obj, grid_obj ) return attrRestrain( skill_grid_obj, grid_obj ) == 1 end, },     -- 被克     = 8
    { is_valid_attr = function( skill_grid_obj, grid_obj ) return attrRestrain( skill_grid_obj, grid_obj ) == 0 end, },     -- 中性     = 9
}

local trigger_state = {
    { is_valid_state = function( grid_obj ) return true end, },                                                                         -- 不判断状态       = 1
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.AtkUp.value, 1 ) end, },    -- 攻击提升         = 2
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.AtkUp.value, -1 ) end, },   -- 攻击下降         = 3
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.DefUp.value, 1 ) end, },    -- 防御提升         = 4
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.DefUp.value, -1 ) end, },   -- 防御下降         = 5
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.CritUp.value, 1 ) end, },   -- 暴击提升         = 6
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.CritUp.value, -1 ) end, },  -- 暴击下降         = 7
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.CritVal.value, 1 ) end, },  -- 暴伤提升         = 8
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.CritVal.value, -1 ) end, }, -- 暴伤下降         = 9
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.DodgeUp.value, 1 ) end, },  -- 闪避提升         = 10
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.DodgeUp.value, -1 ) end, }, -- 闪避下降         = 11
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindType( verify_skill_system.__kind_type__.Poison.value ) end, },              -- 中毒             = 12
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.AtkAttr.value, 1 ) end, },  -- 属性攻击提升     = 13
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.AtkAttr.value, -1 ) end, }, -- 属性攻击下降     = 14
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.DefAttr.value, 1 ) end, },  -- 属性防御提升     = 15
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.DefAttr.value, -1 ) end, }, -- 属性防御下降     = 16
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindTypeNegative( verify_skill_system.__kind_type__.DefAttr.value, -1 ) end, }, -- 属性防御下降     = 17
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindType( verify_skill_system.__kind_type__.ImmunityPhysical.value ) end, },    -- 物免             = 18
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindType( verify_skill_system.__kind_type__.ImmunityMagic.value ) end, },       -- 魔免             = 19
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindType( verify_skill_system.__kind_type__.Paralysis.value ) end, },           -- 麻痹             = 20
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindAnyNegative( 1 ) end, },                                             -- 正面效果         = 21
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindAnyNegative( -1 ) end, },                                            -- 负面效果         = 22
    { is_valid_state = function( grid_obj ) return grid_obj:hasKindAnyNegative( 0 ) end, },                                             -- 正负面效果       = 23
}

---------------------------------------------------------------------------------------------------------------------------------------------
__verify_fight_skill = class( 'verify_fight_skill' )
function __verify_fight_skill:ctor( src_grid_obj, skill_id, skill_level )
    self.src_grid_obj = src_grid_obj

    self.skill_id = skill_id
    self.skill_level = skill_level
    self.skill_info = verify_fight_manager:getSkillInfo( skill_id )

    -- 
    local function __convert__( str )
        local text = 'return {' .. str .. '}'
        local fn = loadstring( text )
        return ( fn ~= nil ) and fn() or {}
    end

    self.effects = __convert__( self.skill_info.effects )           -- 技能效果
    if self.skill_info.attr_type ~= 0 then
        self.attr_check_info = {
            attr_type = self.skill_info.attr_type,
            relative = self.skill_info.relative,
            param = self.skill_info.param,
            compare_type = self.skill_info.compare_type,
        }
    end

    --self:getPlaySkillInfo()
end

function __verify_fight_skill:getKindValue( kind )
    local ret_value, ret_round = nil, 0

    for _,se_id in ipairs( self.effects ) do
        local se_info = verify_fight_manager:getSEInfo( se_id )
        if se_info.kind == kind then
            ret_value = se_info.value
            ret_round = se_info.round
        end
    end

    return ret_value, ret_round
end

function __verify_fight_skill:showAffectPos( effect_pos_index, effect_type )
end

function __verify_fight_skill:calculateSkillEffect( all_src_entity_id, all_target_entity_id, param_tbl )
    local ret_effect_pos_index = {}

    for _,se_id in ipairs( self.effects ) do
        local se_info = verify_fight_manager:getSEInfo( se_id )
        local ret_pos_index = verify_calculate_skill_effect( self.src_grid_obj, all_src_entity_id, all_target_entity_id, se_info, self.skill_level, param_tbl )
        table.insert( ret_effect_pos_index, ret_pos_index )
    end

    return ret_effect_pos_index
end

-- is_special, special_effect_name, special_rge_type, special_rge, is_show_pos_effect, is_play_animation, play_effect_name, play_effect_name_2
-- 是否特殊      特殊技能光效      特殊技能光效类型    范围          是否显示光圈      是否播放起手动作    起手光效         起手光效的持续光效
function __verify_fight_skill:getPlaySkillInfo()
    local effect_attr = self.src_grid_obj.obj_info.attr

    -- 是否显示范围位置光圈
    self.is_show_pos_effect = true

    self.is_play_animation = true

    -- 特殊的技能表现
    self.is_special = false
    self.special_rge_type = 'POINT'
    self.special_rge = nil
    self.special_effect_name = '60300/60300'
    self.play_effect_delay = 0.8
    self.effect_sound = nil
    self.special_effect_name_2 = nil
    for i=1,#self.effects do
        local se_id = self.effects[i]
        local se_info = verify_fight_manager:getSEInfo( se_id )

        -- 伤害性的，不显示范围位置光圈
        -- 非伤害性的，全屏范围才不显示光圈
        if se_info.kind == verify_skill_system.__kind_type__.Hurt.value then
            self.special_rge_type = verify_skill_system.getHurtSkillEffectRangeType( se_info )

            self.is_show_pos_effect = ( self.special_rge_type == 'BOX' and true or false )
            self.special_effect_name = ATTR_NAME[effect_attr].special_effect_name[self.special_rge_type][1]
            self.play_effect_delay = ATTR_NAME[effect_attr].special_effect_name[self.special_rge_type][2]
            self.effect_sound = ATTR_NAME[effect_attr].special_effect_name[self.special_rge_type][3]
            self.special_effect_name_2 = ATTR_NAME[effect_attr].special_effect_name_2
            self.is_special = ( self.special_rge_type ~= 'POINT' and true or false )
            self.special_rge = se_info.rge
        else
            self.is_play_animation = false

            if bit.band( se_info.rge, verify_skill_system.__se_range.ALL.value ) ~= 0 then
                self.is_show_pos_effect = false
            else
                self.is_show_pos_effect = true
            end
        end
    end

    self.play_effect_name, self.play_effect_name_2, self.play_sound = '60207/60207', nil, nil
end

function __verify_fight_skill:playOneSkillEffect( all_src_entity_id, all_target_entity_id, param_tbl, index, call_back_func )
    if index > #self.effects then return call_back_func() end

    -- 技能效果
    local se_param = self.skill_effect_param[index]

    -- 
    if self.skill_info.is_additional == 1 then
        local effect_attr = self.src_grid_obj.obj_info.attr
        verify_play_skill_effect( 'trigger', se_param.t_se_info, self.skill_level, self.src_grid_obj, se_param.effect_pos_index, false, effect_attr, param_tbl, function()
            self:playOneSkillEffect( all_src_entity_id, all_target_entity_id, param_tbl, index + 1, call_back_func )
        end)
    else
        local effect_attr = self.src_grid_obj.obj_info.attr
        verify_play_skill_effect( 'trigger', se_param.t_se_info, self.skill_level, self.src_grid_obj, se_param.effect_pos_index, false, effect_attr, param_tbl, function()
            self:playOneSkillEffect( all_src_entity_id, all_target_entity_id, param_tbl, index + 1, call_back_func )
        end)
    end
end

function __verify_fight_skill:playSkillEffect( all_src_entity_id, all_target_entity_id, param_tbl, call_back_func )
    self.skill_effect_param = nil
    local function __cal_skill_effect_param__()
        local se_damages = {}
        local function __set_target_grid_obj_damage__( target_grid_obj, damage )
            for _,v in ipairs( se_damages ) do
                if v.grid_obj == target_grid_obj then
                    v.damage = v.damage + damage
                    return
                end
            end
            table.insert( se_damages, { grid_obj = target_grid_obj, damage = damage } )
        end

        self.skill_effect_param = {}
        for i=1,#self.effects do
            -- 技能效果
            local se_id = self.effects[i]
            local t_se_info = verify_fight_manager:getSEInfo( se_id )
            local effect_pos_index = verify_calculate_skill_effect( self.src_grid_obj, all_src_entity_id, all_target_entity_id, t_se_info, self.skill_level, param_tbl )

            -- 如果这是一个反伤技能的话，不能反伤自己
            local src_entity_id = self.src_grid_obj.obj_info.entity_id
            if t_se_info.kind == verify_skill_system.__kind_type__.AntiInjury.value then
                for round, v in ipairs( effect_pos_index ) do
                    local target_grid_obj = fight_manager:getFightObjectByPosIndex( v.pos_index )
                    if target_grid_obj and target_grid_obj.obj_info.entity_id == src_entity_id then v.has_target = false end
                end
            end

            -- 
            local ignore_trigger_entity_ids = {}
            if t_se_info.kind == verify_skill_system.__kind_type__.Hurt.value or t_se_info.kind == verify_skill_system.__kind_type__.AntiInjury.value then
                for round, v in ipairs( effect_pos_index ) do
                    if v.has_target and v.buff_check and v.attr_check and v.max_count_check and v.hit_check and v.param then
                        local target_grid_obj = verify_fight_manager:getFightObjectByPosIndex( v.pos_index )
                        if target_grid_obj then
                            -- 如果目标魔免，或者免疫技能伤害的话，就不会把伤害计算进去
                            if not target_grid_obj:isImmunityMagic() and not target_grid_obj:isImmunitySkillHurt() then
                                __set_target_grid_obj_damage__( target_grid_obj, v.param )
                            else
                                table.insert( ignore_trigger_entity_ids, target_grid_obj.obj_info.entity_id )
                            end
                        end
                    end
                end
            end

            -- 技能伤害触发
            if t_se_info.additional == 1 then
                local all_src_entity_id = { src_entity_id }
                local all_target_entity_id = {}
                local trigger_param_tbl = { [src_entity_id] = {} }

                for _,v in ipairs( effect_pos_index ) do
                    if v.has_target and v.buff_check and v.attr_check and v.max_count_check then
                        local grid_obj = verify_fight_manager:getFightObjectByPosIndex( v.pos_index )
                        if grid_obj and not table.hasValue( all_target_entity_id, grid_obj.obj_info.entity_id ) then
                            table.insert( all_target_entity_id, grid_obj.obj_info.entity_id )
                            trigger_param_tbl[src_entity_id][grid_obj.obj_info.entity_id] = {
                                damage = v.param,
                                mv_count = v.count,
                            }
                        end
                    end
                end

                local kt, kt_info = get_verify_kind_type_info( t_se_info.kind )
                local action_type = kt_info.get_action_type( t_se_info )
                verify_fight_manager:triggerSkill( all_src_entity_id, all_target_entity_id, self.src_grid_obj, trigger_action[action_type], trigger_param_tbl, ignore_trigger_entity_ids )
            end

            -- 
            table.insert( self.skill_effect_param, {
                t_se_info = t_se_info,
                effect_pos_index = effect_pos_index,
            })
        end

        -- 看看谁要死
        for _,v in ipairs( se_damages ) do
            if v.grid_obj.cur_hp <= v.damage then v.grid_obj:declareDeath() end
        end
    end

    -- 开始前，先算出所有的数值
    __cal_skill_effect_param__()

    -- 
    self:playOneSkillEffect( all_src_entity_id, all_target_entity_id, param_tbl, 1, call_back_func )
    --self:playOneSkillEffect( all_src_entity_id, all_target_entity_id, param_tbl, 1, function()
    --    processVerifyTriggerSkillFunc( call_back_func )
    --end)
end

function __verify_fight_skill:isTrigger( all_src_entity_id, all_target_entity_id, action, param_tbl )
    -- 光环技能的话，不能被触发
    if self.skill_info.is_aura ~= 0 then return end

    -- trigger action
    if self.skill_info.action ~= action then return end

    -- 被沉默了，不能触发
    if self.src_grid_obj:isSilence() then return end

    -- 监听者的位置属性状态判断
    local function __check_pos__()
        for _,entity_id in ipairs( self.skill_info.active == 1 and all_src_entity_id or all_target_entity_id ) do
            local grid_obj = verify_fight_manager:getGridObjByEntityID( entity_id )
            if grid_obj and trigger_rge[self.skill_info.rge].is_valid_pos_index( self.src_grid_obj.pos_index, grid_obj.pos_index ) then return true end
        end
        return false
    end
    if not __check_pos__() then return end

    -- trigger attr
    if not trigger_attr[self.skill_info.attr].is_valid_attr( self.src_grid_obj, nil ) then return end

    -- trigger state
    if not trigger_state[self.skill_info.state].is_valid_state( self.src_grid_obj ) then return end

    -- 
    if not __verify_check_attr_state__( self.src_grid_obj, self.attr_check_info ) then return end

    -- 攻击方的属性状态判断
    local function __check_src__()
        for _,entity_id in ipairs( all_src_entity_id ) do
            local grid_obj = verify_fight_manager:getGridObjByEntityID( entity_id )
            if grid_obj then
                if trigger_relationship[self.skill_info.src_relationship].is_valid( self.src_grid_obj, grid_obj ) then -- trigger relationship
                    if trigger_attr[self.skill_info.src_attr].is_valid_attr( self.src_grid_obj, grid_obj ) then
                        if trigger_state[self.skill_info.src_state].is_valid_state( grid_obj ) then
                            -- 不需要属性值判断的话，就已经算是通过了
                            if self.skill_info.src_attr_type == 0 then return true end

                            -- 属性值判断
                            local attr_check_info = {
                                attr_type = self.skill_info.src_attr_type,
                                relative = self.skill_info.src_relative,
                                param = self.skill_info.src_param,
                                compare_type = self.skill_info.src_compare_type,
                            }
                            if __verify_check_attr_state__( grid_obj, attr_check_info ) then
                                -- 所有判断都通过了，就算通过了
                                return true
                            end
                        end
                    end
                end
            end
        end
        return false
    end
    if not __check_src__() then return end

    -- 被击方的属性状态判断
    local function __check_target__()
        for _,entity_id in ipairs( all_target_entity_id ) do
            local grid_obj = verify_fight_manager:getGridObjByEntityID( entity_id )
            if grid_obj then
                if trigger_relationship[self.skill_info.target_relationship].is_valid( self.src_grid_obj, grid_obj ) then
                    if trigger_attr[self.skill_info.target_attr].is_valid_attr( self.src_grid_obj, grid_obj ) then
                        if trigger_state[self.skill_info.target_state].is_valid_state( grid_obj ) then
                            -- 不需要属性值判断的话，就已经算是通过了
                            if self.skill_info.target_attr_type == 0 then return true end

                            -- 属性值判断
                            local attr_check_info = {
                                attr_type = self.skill_info.target_attr_type,
                                relative = self.skill_info.target_relative,
                                param = self.skill_info.target_param,
                                compare_type = self.skill_info.target_compare_type,
                            }
                            if __verify_check_attr_state__( grid_obj, attr_check_info ) then
                                -- 所有判断都通过了，就算通过了
                                return true
                            end
                        end
                    end
                end
            end
        end
        return false
    end
    if not __check_target__() then return end

    -- 判断触发的技能是否有目标，没有的话，就不触发
    local function __skill_has_target__()
        local all_effect_pos_index = self:calculateSkillEffect( all_src_entity_id, all_target_entity_id, param_tbl )
        for _,effect_pos_index in ipairs( all_effect_pos_index ) do
            for _,v in ipairs( effect_pos_index ) do
                --if v.has_target and v.buff_check and v.attr_check and v.max_count_check and v.hit_check then return true end
                if v.has_target and v.buff_check and v.attr_check and v.max_count_check then return true end
            end
        end
    end

    -- 没有 CD 的技能
    if self.skill_info.round == 0 then
        -- 概率触发
        if ( self.skill_info.probability or 100 ) < self.src_grid_obj:getRandomNumber( 0, 100 ) then return end

        -- 没有目标
        if not __skill_has_target__() then return end
    else
        -- cd
        if self.skill_info.in_cd == 1 and self.src_grid_obj.total_round == 1 then return end
        if self.skill_info.in_cd ~= 0 or self.src_grid_obj.total_round ~= 1 then
            local temp_round = self.src_grid_obj.total_round
            if self.skill_info.in_cd == 0 then temp_round = temp_round - 1 end
            if temp_round % self.skill_info.round ~= 0 then return end
        end
    end

    -- 
    local trigger_entity_id = self.src_grid_obj.obj_info.entity_id
    return function( call_back_func )
        local is_win, is_lost = verify_fight_manager.verify_fight_control:checkIsWin()

        -- 如果在最后 BOSS 关卡赢的话，就不需要再施放了
        if is_win and verify_fight_manager.cur_page == 1 then return call_back_func() end

        -- 如果战斗分出胜负的话，触发的有目标的技能可以继续施放
        -- 如果是一个没有 CD 的技能的话，需要有目标才能施放
        if ( is_win or is_lost or self.skill_info.round == 0 ) and not __skill_has_target__() then return call_back_func() end

        -- 
        local grid_obj = verify_fight_manager:getGridObjByEntityID( trigger_entity_id )
        if grid_obj then
            -- 已经死亡了，不触发技能
            if grid_obj.death then return call_back_func() end
            -- 眩晕的话，不能施放技能
            if action ~= trigger_action.death and grid_obj:hasKindType( verify_skill_system.__kind_type__.Paralysis.value ) then return call_back_func() end
            -- 如果已经宣告死亡，触发的技能又不是死亡才触发的话，不触发技能
            if grid_obj.death_event and action ~= trigger_action.death then return call_back_func() end

            -- 
            self:playSkillEffect( all_src_entity_id, all_target_entity_id, param_tbl, function()
                local function __is_src_trigger_entity__()
                    for _,entity_id in ipairs( all_src_entity_id ) do if entity_id == trigger_entity_id then return true end end
                    return false
                end

                -- 如果是亡语的话，就在触发完了后，尝试死亡了
                if action == trigger_action.death and __is_src_trigger_entity__() then
                    grid_obj.death_cb_count:popEnd()
                    grid_obj:tryDoDeath()
                end

                call_back_func()
            end)
        else
            call_back_func()
        end
    end
end

-- 添加光环效果
function __verify_fight_skill:addAuraEffect( all_target_grid_obj )
    -- 如果不是光环技能的话，就直接返回
    if self.skill_info.is_aura == 0 then return end

    -- 
    for _,se_id in ipairs( self.effects ) do
        local se_info = verify_fight_manager:getSEInfo( se_id )
        local effect_pos_index = verify_calculate_skill_effect( self.src_grid_obj, {}, {}, se_info, self.skill_level )

        local function __is_valid_target__( target_grid_obj )
            for _, v in ipairs( effect_pos_index ) do
                if v.has_target and v.pos_index == target_grid_obj.pos_index then return v end
            end
        end

        for _,grid_obj in ipairs( all_target_grid_obj ) do
            local v = __is_valid_target__( grid_obj )
            if v then verify_play_skill_effect( 'aura', se_info, self.skill_level, self.src_grid_obj, { v }, false, self.src_grid_obj.obj_info.attr, {}, function() end ) end
        end
    end
end

