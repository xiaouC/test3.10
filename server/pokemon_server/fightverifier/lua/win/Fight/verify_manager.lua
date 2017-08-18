-- ./win/verify_fight_manager.lua
require 'utils.table'
require 'utils.stack'
require 'win.Fight.verify_object'
require 'win.Fight.verify_fight_config'
require 'win.Fight.fight_debug'
require 'utils.protobuf'

verify_fight_manager = {
    random_index = nil,                                     -- 伪随机索引
    is_fighting = false,
    call_back_func = nil,
    all_trigger_skill_func = {},
    death_trigger_func = {},
    dying_fight_objs = stack.new(),
    is_quit_fighting = true,
    account_ai_info = nil,
}

---------------------------------------------------------------------------------------------------------------------------------------------------------------
-- 战斗校验 
---------------------------------------------------------------------------------------------------------------------------------------------------------------
function verifyFightPlaybackWithFile( file_name )
    return verifyFightPlaybackWithData( getFileData(file_name) )
end

function verifyFightPlaybackWithData( data )
    local up_result = nil
    local fr = assert(protobuf.decode( 'poem.fightReplay', data ), 'decode fight reply failed')
    verifyFightPlayback( fr, function(result)
        up_result = result
    end)
    return up_result
end

function verifyFightPlayback( fr, call_back_func )
    require 'win.Fight.verify_interactive'
    local verify_fight = __verify_fight_interactive.new( fr, call_back_func )
    verify_fight:startFight()
end

---------------------------------------------------------------------------------------------------------------------------------------------------------------
function verify_fight_manager:prepareFighting( prop, bg_id, fight_type, is_new, player_fighters, areas, stone_num, random_index, prepare_call_back_func )
    -- 清理一下
    self:clear()

    self:init( prop, bg_id, fight_type, is_new, player_fighters, areas, stone_num, random_index )

    if prepare_call_back_func then prepare_call_back_func() end
end

function verify_fight_manager:getRandomNumber( min, max )
    local ret_num, next_index = pseudo_random( self.random_index, min, max )

    self.random_index = next_index

    return ret_num
end

function verify_fight_manager:getLineUp()
    local ret_line_up = {}

    for i,fighter_info in ipairs( self.player_fighters or {} ) do
        table.insert( ret_line_up, {
            entityID = fighter_info.real_entity_id,
            prototypeID = fighter_info.config_id,
            level = fighter_info.level,
            pos = fighter_info.pos,
        })
    end

    return ret_line_up
end

function verify_fight_manager:init( prop, bg_id, fight_type, is_new, player_fighters, areas, stone_num, random_index )
    -- 全部保存下来
    self.prop = prop
    self.bg_id = bg_id
    self.fight_type = fight_type
    self.is_new = is_new
    self.player_fighters = player_fighters
    self.areas = areas
    self.page_count = #areas
    self.stone_num = stone_num
    self.random_index = random_index

    -- 创建战斗使用的窗口
    if self.all_grid_items == nil then self:createFightWindow() end

    -- 重置
    self:reset()
end

function verify_fight_manager:finish()
    self:clear()
end

function verify_fight_manager:clear()
    self.all_grid_items = nil
    self.is_quit_fighting = true
end

function verify_fight_manager:start( fight_state, switch_fight_state_call_back_func, switch_page_call_back_func )
    self.switch_fight_state_call_back_func = switch_fight_state_call_back_func
    self.switch_page_call_back_func = switch_page_call_back_func
    self:setFightState( fight_state or 'init' )
end

function verify_fight_manager:createFightWindow()
    -- 格子的高宽
    self.grid_width, self.grid_height = 158, 158
    self.grid_count_per_page = fight_const.grid_row_per_page * fight_const.grid_col_per_page

    -- 所有的格子
    self.all_grid_items = {}
    for i=1,self.grid_count_per_page do
        local grid_item = {}

        grid_item.row = math.floor( ( i - 1 ) / 4 )
        grid_item.col = math.floor( ( i - 1 ) % 4 )
        grid_item.pos_index = i
        grid_item.grid_obj = nil

        table.insert( self.all_grid_items, grid_item )
    end
end

function verify_fight_manager:reset()
    self.dying_fight_objs:clear()

    self.relive_monsters_info = {}

    self.all_trigger_skill_func = {}
    self.death_trigger_func = {}

    -- 重播时候使用的技能和技能效果
    self.replay_skill_info_list = nil
    self.replay_se_info_list = nil
    self.replay_se_info_list_d = nil

    -- 
    self.player_total_round = 1
    self.enemy_total_round = 1

    self.player_death_count = 0
    self.monster_death_count = 0
end

function verify_fight_manager:getSkillInfo( skill_id )
    return self.replay_skill_info_list[skill_id]
end

function verify_fight_manager:getSEInfo( se_id )
    return self.replay_se_info_list[se_id]
end

function verify_fight_manager:setFightState( state )
    local fight_state_type = {
        ['init'] = function( call_back_func )
            self:switchPage( 'first_enter', self.page_count, call_back_func )
        end,
        ['fight_start'] = function( call_back_func )
            self.is_fighting = true

            -- 给所有的敌方添加技能影响
            local all_fighter_objs = self:getAllFighterObjects()
            for _,src_grid_obj in ipairs( self:getAllPetObjects() ) do src_grid_obj:addAuraEffect( all_fighter_objs ) end
            for _,src_grid_obj in ipairs( self:getAllMonsterObjects() ) do src_grid_obj:addAuraEffect( all_fighter_objs ) end

            if call_back_func then call_back_func() end
        end,
        ['fight_turn'] = function( call_back_func )
            local function __real_fight_turn__()
                self:refreshBuffDebuff()
                self:fightTurnFront( call_back_func )
            end

            if self.plot_play then
                self.plot_play = false
                local area_info = self.areas[self.cur_page]
                self:replaceFighterN( area_info.replace_list or {}, 1, __real_fight_turn__ )
            else
                __real_fight_turn__()
            end
        end,
        ['player_turn'] = function( call_back_func )
            self:refreshBuffDebuff()
            if call_back_func then call_back_func() end
        end,
        ['player_attack'] = function( call_back_func )
            self:refreshBuffDebuff()

            if call_back_func then call_back_func() end
        end,
        ['player_delay_skill'] = function( call_back_func )
            self:refreshBuffDebuff()

            for _,temp_grid_obj in ipairs( self:getAllPetObjects() ) do
                local all_src_entity_id = { temp_grid_obj.obj_info.entity_id }
                local all_target_entity_id = { temp_grid_obj.obj_info.entity_id }
                temp_grid_obj:checkTriggerSkill( all_src_entity_id, all_target_entity_id, trigger_action.attack_front, {} )
            end
            self:playDelaySkill( 'player_attacking', call_back_func )
        end,
        ['player_attacking'] = function( call_back_func )
            self:refreshBuffDebuff()

            self:playerNormalAttack( call_back_func )
        end,
        ['player_round_end'] = function( call_back_func )
            self:refreshBuffDebuff()

            self:updateRound( false )

            if call_back_func then call_back_func() end
        end,
        ['monster_turn'] = function( call_back_func )
            self:refreshBuffDebuff()

            if call_back_func then call_back_func() end
        end,
        ['monster_skill'] = function( call_back_func )
            self:refreshBuffDebuff()

            if self.is_big_boss then
                self:useLargeSkill( function() if call_back_func then call_back_func() end end )
            else
                if call_back_func then call_back_func() end
            end
        end,
        ['monster_attack'] = function( call_back_func )
            self:refreshBuffDebuff()

            if call_back_func then call_back_func() end
        end,
        ['monster_delay_skill'] = function( call_back_func )
            self:refreshBuffDebuff()

            for _,temp_grid_obj in ipairs( self:getAllMonsterObjects() ) do
                local all_src_entity_id = { temp_grid_obj.obj_info.entity_id }
                local all_target_entity_id = { temp_grid_obj.obj_info.entity_id }
                temp_grid_obj:checkTriggerSkill( all_src_entity_id, all_target_entity_id, trigger_action.attack_front, {} )
            end
            self:playDelaySkill( 'monster_attacking', call_back_func )
        end,
        ['monster_attacking'] = function( call_back_func )
            self:refreshBuffDebuff()
            self:monsterNormalAttack( call_back_func )
        end,
        ['monster_round_end'] = function( call_back_func )
            self:refreshBuffDebuff()

            -- 如果是大 BOSS 关卡的话，判断是否需要切换大 BOSS 的模式，包括攻击箭头的变更等
            if self.is_big_boss then self:switchBigBossMode() end

            self:updateRound( true )

            if call_back_func then call_back_func() end
        end,
        ['fight_turn_end'] = function( call_back_func )
            self:refreshBuffDebuff()
            self:fightTurnEnd( call_back_func )
        end,
        ['fight_win'] = function( call_back_func )
            self.is_fighting = false

            -- 校验成功
            self.verify_fight_control.fight_end_call_back_func( true )
        end,
        ['fight_lost'] = function( call_back_func )
            self.is_fighting = false

            -- 校验失败
            self.verify_fight_control.fight_end_call_back_func( false )
        end,
        ['relive'] = function( call_back_func )
            local function __clear_grid_obj__( grid_obj )
                grid_obj:reliveClear()

                --
                for _,pos_index in ipairs( grid_obj:getAllPosIndex() ) do
                    local grid_item = self:getGridItemByPosIndex( pos_index )
                    -- 如果这个格子上有石头，就石头自己清理自己了
                    if grid_item.grid_obj.obj_info.type == 'player' or grid_item.grid_obj.obj_info.type == 'enemy' then
                        grid_item.grid_obj = nil
                    end
                end
            end

            -- 清理所有的格子，并且记录下存活着的怪物的血量
            for _,grid_obj in ipairs( self:getAllMonsterObjects() ) do
                self.relive_monsters_info[grid_obj.obj_info.entity_id] = grid_obj.cur_hp
                __clear_grid_obj__( grid_obj )
            end
            for _,grid_obj in ipairs( self:getAllPetObjects() ) do
                __clear_grid_obj__( grid_obj )
            end
            for i=1,self.grid_count_per_page do
                local grid_item = self:getGridItemByPosIndex( i )
                if grid_item.grid_obj then
                    grid_item.grid_obj:destroy()
                    grid_item.grid_obj = nil
                end
            end

            self:relive()

            if call_back_func then call_back_func() end
        end,
    }

    local function changeState()
        -- 状态改变
        self.fight_state = state

        local func = fight_state_type[state]
        if func then
            func( function()
                -- 状态改变后
                if self.switch_fight_state_call_back_func then
                    self.switch_fight_state_call_back_func( state, false )
                end
            end)
        end
    end

    -- 状态改变前
    if self.switch_fight_state_call_back_func then
        self.switch_fight_state_call_back_func( state, true, changeState )
    else
        changeState()
    end
end

function verify_fight_manager:getFightState()
    return self.fight_state
end

function verify_fight_manager:playFightLostEffect( call_back_func )
end

function verify_fight_manager:refreshMonsterBuff()
    for _,grid_obj in ipairs( self:getAllMonsterObjects() ) do
        grid_obj:refreshBuffSkill()
    end
end

function verify_fight_manager:refreshMonsterDebuff()
    for _,grid_obj in ipairs( self:getAllMonsterObjects() ) do
        grid_obj:refreshDebuffSkill()
    end
end

function verify_fight_manager:refreshPetBuff()
    for _,grid_obj in ipairs( self:getAllPetObjects() ) do
        grid_obj:refreshBuffSkill()
    end
end

function verify_fight_manager:refreshPetDebuff()
    for _,grid_obj in ipairs( self:getAllPetObjects() ) do
        grid_obj:refreshDebuffSkill()
    end
end

function verify_fight_manager:switchPage( switch_type, page_index, call_back_func )
    local switch_page_type = {
        ['first_enter'] = function()
            self.is_big_boss = false                        -- 是否是大 BOSS 关卡
            self.cur_page = page_index                      -- 当前区域
            self.area_index = 5                             -- 怪物随机位置
            self.buff_item = nil                            -- 恢复性道具是否已经出现
            self.plot_play = self.is_new                    -- 剧情对白是否应该触发

            -- create player fighters
            for i,fighter_info in ipairs( self.player_fighters ) do
                self:createGridObject( fighter_info, fighter_info.pos_index )
            end

            -- 创建 monsters
            local area_info = self.areas[page_index]
            for _,m_fighter_info in ipairs( area_info.enemy_fighters or {} ) do
                self:createGridObject( m_fighter_info, m_fighter_info.pos_index )
            end

            self.switch_page_call_back_func( switch_type, area_info, page_index, call_back_func )
        end,
        ['next_page'] = function()
            -- 
            self.is_big_boss = false
            self.cur_page = page_index
            self.area_index = 1
            self.buff_item = nil
            self.plot_play = self.is_new

            -- 创建 monsters
            local area_info = self.areas[page_index]
            for _,m_fighter_info in ipairs( area_info.enemy_fighters or {} ) do
                self:createGridObject( m_fighter_info, m_fighter_info.pos_index, true )
                self.area_index = self.area_index + 1
            end

            -- 给所有的敌方添加技能影响
            local all_fighter_objs = self:getAllFighterObjects()
            local all_target_grid_objs = self:getAllMonsterObjects()
            for _,src_grid_obj in ipairs( self:getAllPetObjects() ) do src_grid_obj:addAuraEffect( all_target_grid_objs ) end
            for _,src_grid_obj in ipairs( self:getAllMonsterObjects() ) do src_grid_obj:addAuraEffect( all_fighter_objs ) end

            -- 
            self.switch_page_call_back_func( switch_type, area_info, page_index, call_back_func )
        end,
        ['boss_enter'] = function()
            local temp_grid_objs = {}
            for i=1,self.grid_count_per_page do
                local grid_obj = self:getFightObjectByPosIndex( i )
                if grid_obj and grid_obj.obj_info.type == 'player' then
                    grid_obj.grid_obj = nil

                    local grid_item = self:getGridItemByPosIndex( i )
                    grid_item.grid_obj = nil

                    table.insert( temp_grid_objs, grid_obj )
                end
            end

            self.is_big_boss = false
            self.cur_page = page_index
            self.area_index = 5
            self.buff_item = nil
            self.plot_play = self.is_new

            -- 创建 monsters
            local area_info = self.areas[page_index]
            for _,m_fighter_info in ipairs( area_info.enemy_fighters or {} ) do
                self:createGridObject( m_fighter_info, m_fighter_info.pos_index )
            end

            -- 重置玩家的HERO位置
            for _,grid_obj in ipairs( temp_grid_objs ) do
                local n_grid_item = self:getGridItemByPosIndex( grid_obj.origin_pos_index )

                n_grid_item.grid_obj = grid_obj
                grid_obj.pos_index = grid_obj.origin_pos_index
            end

            local all_fighter_objs = self:getAllFighterObjects()
            local all_pet_objs = self:getAllPetObjects()
            local all_monster_objs = self:getAllMonsterObjects()

            -- 给所有的敌方添加技能影响
            for _,src_grid_obj in ipairs( all_pet_objs ) do src_grid_obj:addAuraEffect( all_monster_objs ) end
            for _,src_grid_obj in ipairs( all_monster_objs ) do src_grid_obj:addAuraEffect( all_fighter_objs ) end

            self.switch_page_call_back_func( switch_type, area_info, page_index, call_back_func )
        end,
    }

    switch_page_type[switch_type]()
end

function verify_fight_manager:createGridObject( obj_info, pos_index, show_model_detail )
    -- 如果这个位置上有HERO了，就随机位置
    if pos_index then
        if pos_index == 0 or self:getFightObjectByPosIndex( pos_index ) then pos_index = nil end
    end

    -- 大 BOSS
    if obj_info.size == 1 then return self:createBigGridObject( obj_info, pos_index, show_model_detail ) end

    -- 位置
    pos_index = pos_index and pos_index or self:getFreePosIndex0()

    -- 坐标
    local grid_item = self:getGridItemByPosIndex( pos_index )

    -- 
    grid_item.grid_obj = verifyCreateGridObjByType( obj_info.type, obj_info, pos_index )

    return grid_item
end

function verify_fight_manager:createBigGridObject( obj_info, pos_index, show_model_detail )
    self.is_big_boss = true

    -- 位置
    pos_index = pos_index and pos_index or self:getFreePosIndex1()

    -- 坐标
    local grid_item_1 = self:getGridItemByPosIndex( pos_index )
    local grid_item_2 = self:getGridItemByPosIndex( pos_index + 1 )
    local grid_item_3 = self:getGridItemByPosIndex( pos_index + 4 )
    local grid_item_4 = self:getGridItemByPosIndex( pos_index + 5 )

    local grid_items = { grid_item_1, grid_item_2, grid_item_3, grid_item_4 }

    -- 
    local grid_obj = verifyCreateGridObjByType( 'boss', obj_info, pos_index )
    grid_obj:setBossMode( 1 )
    grid_item_1.grid_obj = grid_obj
    grid_item_2.grid_obj = grid_obj
    grid_item_3.grid_obj = grid_obj
    grid_item_4.grid_obj = grid_obj

    return grid_items
end

function verify_fight_manager:getGridItemByPosIndex( pos_index, grid_obj_alive )
    local grid_item = self.all_grid_items[pos_index]

    -- 没有要求的
    if not grid_obj_alive then return grid_item end

    -- 必须要活着的
    if grid_item.grid_obj and not grid_item.grid_obj.death then return grid_item end

    return nil
end

function verify_fight_manager:getFightObjectByPosIndex( pos_index )
    local grid_item = self:getGridItemByPosIndex( pos_index, true )
    if grid_item then
        local obj_type = grid_item.grid_obj.obj_info.type
        if obj_type == 'player' or obj_type == 'enemy' then return grid_item.grid_obj end
        if obj_type == 'stone' then return grid_item.grid_obj.grid_obj end
    end
end

function verify_fight_manager:getGridObjByEntityID( entity_id )
    for _, grid_obj in ipairs( self:getAllFighterObjects() ) do
        if entity_id == grid_obj.obj_info.entity_id then return grid_obj end
    end
end

-- 传递进来的是绝对的行号和绝对的列号
-- 而不是相对与当前页的行号和列号
function verify_fight_manager:getGridItemByRowCol( row, col, grid_obj_alive )
    local real_index = row * fight_const.grid_col_per_page + col + 1
    return self.all_grid_items[real_index]
end

function verify_fight_manager:getFreePosIndex0()
    local specify_pos_config = {
        [1] = {  1,  2,  5,  6 },
        [2] = {  3,  4,  7,  8 },
        [3] = {  9, 10, 13, 14 },
        [4] = { 11, 12, 15, 16 },
        [5] = {  1,  2,  5,  9 },
        [6] = {  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16 },
    }
  
    local specify_pos_index = specify_pos_config[self.area_index]

    -- 
    local free_pos_index = {}
    for _,pos_index in ipairs( specify_pos_index ) do
        local grid_item = self:getGridItemByPosIndex( pos_index )
        if grid_item.grid_obj == nil then table.insert( free_pos_index, pos_index ) end
    end

    if #free_pos_index > 0 then
        local index = math.floor( self:getRandomNumber( 1, #free_pos_index ) )

        return free_pos_index[index]
    else
        self.area_index = self.area_index + 1
        return self:getFreePosIndex0()
    end
end

function verify_fight_manager:getFreePosIndex1()
    local pos_config = { 1, 5 }

    local free_pos_index = {}
    for _,pos_index in ipairs( pos_config ) do
        -- 判断 4 个格子都没有东西，才是有效的位置
        local grid_item_1 = self:getGridItemByPosIndex( pos_index )
        if not grid_item_1.grid_obj then
            local grid_item_2 = self:getGridItemByPosIndex( pos_index + 1 )
            if not grid_item_2.grid_obj then
                local grid_item_3 = self:getGridItemByPosIndex( pos_index + 4 )
                if not grid_item_3.grid_obj then
                    local grid_item_4 = self:getGridItemByPosIndex( pos_index + 5 )
                    if not grid_item_4.grid_obj then table.insert( free_pos_index, pos_index ) end
                end
            end
        end
    end

    if #free_pos_index > 0 then
        local index = math.floor( self:getRandomNumber( 1, #free_pos_index ) )

        return free_pos_index[index]
    else
        return 1
    end
end

function verify_fight_manager:getStonePosIndex()
    local stone_pos_config = {
        [1] = {  6,  7, 10, 11 },
        [2] = {  5,  6,  7,  8,  9, 10, 11, 12 },
        [3] = {  6,  7,  8,  9, 10, 11 },
        [4] = {  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16 },
    }

    local index = math.floor( self:getRandomNumber( 1, #stone_pos_config ) )
    return stone_pos_config[index]
end

function verify_fight_manager:getAllFighterObjects()
    local all_fighter_objects = {}
    for i=1,self.grid_count_per_page do
        local grid_obj = self:getFightObjectByPosIndex( i )
        if grid_obj and not table.hasValue( all_fighter_objects, grid_obj ) then table.insert( all_fighter_objects, grid_obj ) end
    end
    return all_fighter_objects
end

function verify_fight_manager:getAllMonsterObjects()
    local all_monster_objects = {}
    for i=1,self.grid_count_per_page do
        local grid_obj = self:getFightObjectByPosIndex( i )
        if grid_obj and grid_obj.obj_info.type == 'enemy' then
            if not table.hasValue( all_monster_objects, grid_obj ) then
                table.insert( all_monster_objects, grid_obj )
            end
        end
    end

    return all_monster_objects
end

function verify_fight_manager:getAllAllyObjects( grid_obj )
    if grid_obj then
        if grid_obj.obj_info.type == 'player' then return self:getAllPetObjects() end
        if grid_obj.obj_info.type == 'enemy' then return self:getAllMonsterObjects() end
    end

    return {}
end

function verify_fight_manager:getAllPetObjects()
    local all_pet_objects = {}
    for i=1,self.grid_count_per_page do
        local grid_obj = self:getFightObjectByPosIndex( i )
        if grid_obj and grid_obj.obj_info.type == 'player' then table.insert( all_pet_objects, grid_obj ) end
    end

    return all_pet_objects
end

function verify_fight_manager:getGridObjectByType( type )
    for i=1,self.grid_count_per_page do
        local grid_item = self:getGridItemByPosIndex( i, true )
        if grid_item and grid_item.grid_obj.obj_info.type == type then
            return grid_item.grid_obj
        end
    end
end

function verify_fight_manager:gridObjAction( grid_obj, move_index, call_back_func )
    if not grid_obj then
        if call_back_func then call_back_func() end

        return
    end

    if move_index then
        self:moveTo( grid_obj, move_index, function()
            if call_back_func then call_back_func() end
        end)
    else
        if call_back_func then call_back_func() end
    end
end

function verify_fight_manager:moveTo( grid_obj, pos_index, call_back_func )
    if grid_obj then
        local grid_item = self:getGridItemByPosIndex( grid_obj.pos_index )
        if grid_item then
            local move_pos_index = grid_obj:collectMovePosIndex( grid_item.pos_index )
            if table.hasValue( move_pos_index, pos_index ) then
                self:setTo( grid_obj, pos_index )

                -- 移动后事件
                local all_src_entity_id = { grid_obj.obj_info.entity_id }
                local all_target_entity_id = { grid_obj.obj_info.entity_id }
                local mv_count = self:getMoveGridCount( grid_item.pos_index, pos_index )
                local param_tbl = { [grid_obj.obj_info.entity_id] = {} }
                param_tbl[grid_obj.obj_info.entity_id][grid_obj.obj_info.entity_id] = { mv_count = mv_count }
                grid_obj:checkTriggerSkill( all_src_entity_id, all_target_entity_id, trigger_action.move, param_tbl )
                processVerifyTriggerSkillFunc( call_back_func )
            else
                -- 把控制权交给玩家
                self:setFightState( 'monster_round_end' )
            end
        else
            -- 把控制权交给玩家
            self:setFightState( 'monster_round_end' )
        end
    else
        -- 把控制权交给玩家
        self:setFightState( 'monster_round_end' )
    end
end

function verify_fight_manager:setTo( grid_obj, pos_index )
    if grid_obj.obj_info.size == 1 then
        local src_grid_item_1 = self:getGridItemByPosIndex( grid_obj.pos_index )
        local src_grid_item_2 = self:getGridItemByPosIndex( grid_obj.pos_index + 1 )
        local src_grid_item_3 = self:getGridItemByPosIndex( grid_obj.pos_index + 4 )
        local src_grid_item_4 = self:getGridItemByPosIndex( grid_obj.pos_index + 5 )
        local target_grid_item_1 = self:getGridItemByPosIndex( pos_index )
        local target_grid_item_2 = self:getGridItemByPosIndex( pos_index + 1 )
        local target_grid_item_3 = self:getGridItemByPosIndex( pos_index + 4 )
        local target_grid_item_4 = self:getGridItemByPosIndex( pos_index + 5 )

        -- 踩到了一个物品，可能是石板或者恢复道具之类的
        local temp_grid_obj_1 = nil
        if target_grid_item_1.grid_obj and target_grid_item_1.grid_obj ~= grid_obj then temp_grid_obj_1 = target_grid_item_1.grid_obj end
        local temp_grid_obj_2 = nil
        if target_grid_item_2.grid_obj and target_grid_item_2.grid_obj ~= grid_obj then temp_grid_obj_2 = target_grid_item_2.grid_obj end
        local temp_grid_obj_3 = nil
        if target_grid_item_3.grid_obj and target_grid_item_3.grid_obj ~= grid_obj then temp_grid_obj_3 = target_grid_item_3.grid_obj end
        local temp_grid_obj_4 = nil
        if target_grid_item_4.grid_obj and target_grid_item_4.grid_obj ~= grid_obj then temp_grid_obj_4 = target_grid_item_4.grid_obj end

        -- 先清掉 src，然后再对 target 赋值
        grid_obj.pos_index = pos_index
        src_grid_item_1.grid_obj = nil
        src_grid_item_2.grid_obj = nil
        src_grid_item_3.grid_obj = nil
        src_grid_item_4.grid_obj = nil
        target_grid_item_1.grid_obj = grid_obj
        target_grid_item_2.grid_obj = grid_obj
        target_grid_item_3.grid_obj = grid_obj
        target_grid_item_4.grid_obj = grid_obj

        if temp_grid_obj_1 then temp_grid_obj_1:effective( grid_obj ) end
        if temp_grid_obj_2 then temp_grid_obj_2:effective( grid_obj ) end
        if temp_grid_obj_3 then temp_grid_obj_3:effective( grid_obj ) end
        if temp_grid_obj_4 then temp_grid_obj_4:effective( grid_obj ) end
    else
        local src_grid_item = self:getGridItemByPosIndex( grid_obj.pos_index )
        local target_grid_item = self:getGridItemByPosIndex( pos_index )

        -- 清理
        grid_obj.pos_index = pos_index
        grid_obj.grid_obj = nil
        if src_grid_item.grid_obj.obj_info.type == 'stone' then
            src_grid_item.grid_obj.grid_obj = nil
        else
            src_grid_item.grid_obj = nil
        end

        -- 
        if target_grid_item.grid_obj then
            local obj_type = target_grid_item.grid_obj.obj_info.type

            if obj_type == 'stone' then
                -- 踩到石块
                target_grid_item.grid_obj.grid_obj = grid_obj
                grid_obj.grid_obj = target_grid_item.grid_obj
            else
                -- 踩到其他道具
                local temp_grid_obj = target_grid_item.grid_obj
                target_grid_item.grid_obj = grid_obj

                temp_grid_obj:effective( grid_obj )
            end
        else
            target_grid_item.grid_obj = grid_obj
        end
    end
end

function verify_fight_manager:tryNextFightState()
    if self.try_flag and self.dying_fight_objs:getElementCount() == 0 then
        local next_fight_state = self.try_next_fight_state
        local cb = self.try_next_fight_state_cb

        self.try_flag = false
        self.try_next_fight_state = nil
        self.try_next_fight_state_cb = nil

        self:isWin( function()
            if cb then cb() end
            if next_fight_state then self:setFightState( next_fight_state ) end
        end)
    end
end

function verify_fight_manager:__realAttack( index, all_entity_ids )
    local entity_id = all_entity_ids[index]
    if not entity_id then
        self.try_flag = true
        return self:tryNextFightState()
    end

    local src_grid_obj = self:getGridObjByEntityID( entity_id )
    if not src_grid_obj then return self:__realAttack( index + 1, all_entity_ids ) end

    src_grid_obj:startNormalAttack( function() self:__realAttack( index + 1, all_entity_ids ) end )
end

function verify_fight_manager:playerNormalAttack( call_back_func )
    self.try_flag = false
    self.try_next_fight_state = 'player_round_end'
    self.try_next_fight_state_cb = call_back_func

    -- 通过 entity_id 来反查找 grid_obj 以防技能触发导致的 grid_obj 死亡
    local all_player_entity_ids = {}
    if self.normal_attack_first_grid_obj then table.insert( all_player_entity_ids, self.normal_attack_first_grid_obj.obj_info.entity_id ) end
    for _,grid_obj in ipairs( self:getAllPetObjects() ) do
        if grid_obj ~= self.normal_attack_first_grid_obj then
            table.insert( all_player_entity_ids, grid_obj.obj_info.entity_id )
        end
    end
    self.normal_attack_first_grid_obj = nil

    self:__realAttack( 1, all_player_entity_ids )
end

function verify_fight_manager:monsterNormalAttack( call_back_func )
    self.try_flag = false
    self.try_next_fight_state = 'monster_round_end'
    self.try_next_fight_state_cb = call_back_func

    -- 通过 entity_id 来反查找 grid_obj 以防技能触发导致的 grid_obj 死亡
    local all_monster_entity_ids = {}
    if self.normal_attack_first_grid_obj then table.insert( all_monster_entity_ids, self.normal_attack_first_grid_obj.obj_info.entity_id ) end
    for _,grid_obj in ipairs( self:getAllMonsterObjects() ) do
        if grid_obj ~= self.normal_attack_first_grid_obj then
            table.insert( all_monster_entity_ids, grid_obj.obj_info.entity_id )
        end
    end
    self.normal_attack_first_grid_obj = nil

    self:__realAttack( 1, all_monster_entity_ids )
end

function verify_fight_manager:playDelaySkill( next_fight_state, call_back_func )
    self.try_flag = false
    self.try_next_fight_state = next_fight_state
    self.try_next_fight_state_cb = call_back_func

    processVerifyTriggerSkillFunc( function()
        self.try_flag = true
        self:tryNextFightState()
    end)
end

function verify_fight_manager:fightTurnFront( call_back_func )
    self.try_flag = false
    self.try_next_fight_state = nil
    self.try_next_fight_state_cb = call_back_func

    -- 如果是玩家回合开始的话，也同样是战斗回合的开始
    -- 如果是玩家回合的话：触发玩家回合的 本方回合开始前的技能效果， 触发怪物回合的 敌方回合开始前的技能效果
    -- 如果是怪物回合的话：触发怪物回合的 本方回合开始前的技能效果， 触发玩家回合的 敌方回合开始前的技能效果
    self:triggerSkillSelf( trigger_action.fight_turn_front )
    processVerifyTriggerSkillFunc( function()
        self.try_flag = true
        self:tryNextFightState()
    end)
end

function verify_fight_manager:debuffCheck( is_enemy, call_back_func )
    local all_effect_func = {}
    for _,grid_obj in ipairs( is_enemy and self:getAllMonsterObjects() or self:getAllPetObjects() ) do
        grid_obj:collectEffectFuncByKind( verify_skill_system.__kind_type__.Poison.value, all_effect_func )
    end

    -- 没有任何 debuff 效果的话，直接返回
    local counter = #all_effect_func
    if counter <= 0 then return call_back_func() end

    self.try_flag = false
    self.try_next_fight_state = nil
    self.try_next_fight_state_cb = call_back_func

    for _,func in ipairs( all_effect_func ) do
        func( function()
            counter = counter - 1
            if counter <= 0 then
                processVerifyTriggerSkillFunc( function()
                    self.try_flag = true
                    self:tryNextFightState()
                end)
            end
        end)
    end
end

function verify_fight_manager:fightObjectTurnFront( is_enemy, call_back_func )
    self.try_flag = false
    self.try_next_fight_state = nil
    self.try_next_fight_state_cb = call_back_func

    self:triggerSkillSelf( is_enemy and trigger_action.enemy_turn_front or trigger_action.player_turn_front )
    processVerifyTriggerSkillFunc( function()
        self.try_flag = true
        self:tryNextFightState()
    end)
end

function verify_fight_manager:fightObjectTurnEnd( is_enemy, call_back_func )
    self.try_flag = false
    self.try_next_fight_state = nil
    self.try_next_fight_state_cb = call_back_func

    self:triggerSkillSelf( is_enemy and trigger_action.enemy_turn_end or trigger_action.player_turn_end )
    processVerifyTriggerSkillFunc( function()
        self.try_flag = true
        self:tryNextFightState()
    end)
end

function verify_fight_manager:fightTurnEnd( call_back_func )
    self.try_flag = false
    self.try_next_fight_state = nil
    self.try_next_fight_state_cb = call_back_func

    self:triggerSkillSelf( trigger_action.fight_turn_end )
    processVerifyTriggerSkillFunc( function()
        self.try_flag = true
        self:tryNextFightState()
    end)
end

function verify_fight_manager:updateRound( is_enemy_end )
    if is_enemy_end then
        self.enemy_total_round = self.enemy_total_round + 1

        for _,grid_obj in ipairs( self:getAllMonsterObjects() ) do
            grid_obj.total_round = grid_obj.total_round + 1
        end

        -- 剩余回合数递减
        if self.verify_fight_control.initiate_turn == 'player_turn' then
            self.verify_fight_control:setCurLastRound( self.verify_fight_control.cur_last_round - 1 )
        end
    else
        self.player_total_round = self.player_total_round + 1

        for _,grid_obj in ipairs( self:getAllPetObjects() ) do
            grid_obj.total_round = grid_obj.total_round + 1
        end

        -- 剩余回合数递减
        if self.verify_fight_control.initiate_turn == 'monster_turn' then
            self.verify_fight_control:setCurLastRound( self.verify_fight_control.cur_last_round - 1 )
        end
    end
end

function verify_fight_manager:refreshBuffDebuff()
    for _,grid_obj in ipairs( self:getAllFighterObjects() ) do
        grid_obj:refreshBuffDebuff()
    end
end

function verify_fight_manager:isValidMovePosIndex( grid_obj, target_pos_index, src_pos_index )
    src_pos_index = src_pos_index or grid_obj.pos_index
    local mv_pos_index = grid_obj:collectMovePosIndex( src_pos_index )
    return grid_obj:isValidMovePosIndex( target_pos_index, mv_pos_index )
end

function verify_fight_manager:isValidBigMovePosIndex( grid_obj, target_pos_index, src_pos_index )
    -- 无效的 grid_obj，无法移动
    local grid_item = self:getGridItemByPosIndex( grid_obj.pos_index )
    if not grid_item then return false, false end

    -- 不是一个有效的位置，不能移动过去
    local target_grid_item = self:getGridItemByPosIndex( target_pos_index )
    if not target_grid_item then return false, false end

    -- 在这个位置上已经有了，不能移动过去，以后添加飞行的时候，需要更细致的判断
    if target_grid_item.grid_obj then
        local can_mv_to, can_pass = grid_obj:canMoveTo( target_grid_item.grid_obj )
        if not can_mv_to then return can_mv_to ,can_pass end
    end

    -- 遍历所有可以移动的位置，看是否有 target_pos_index
    src_pos_index = src_pos_index or grid_item.pos_index
    for _,pos_index in ipairs( grid_obj:collectMovePosIndex( src_pos_index ) ) do
        -- target_pos_index 在可移动列表中，这是一个有效的可移动的位置
        if pos_index == target_pos_index then return true, true end
    end

    -- 找不到，不可移动
    return false, false
end

function verify_fight_manager:isValidBigMovePosIndex1( grid_obj, target_pos_index, mv_pos_index )
    -- 无效的 grid_obj，无法移动
    local grid_item = self:getGridItemByPosIndex( grid_obj.pos_index )
    if not grid_item then return false, false end

    -- 不是一个有效的位置，不能移动过去
    local target_grid_item = self:getGridItemByPosIndex( target_pos_index )
    if not target_grid_item then return false, false end

    -- 在这个位置上已经有了，不能移动过去，以后添加飞行的时候，需要更细致的判断
    if target_grid_item.grid_obj then
        local can_mv_to, can_pass = grid_obj:canMoveTo( target_grid_item.grid_obj )
        if not can_mv_to then return can_mv_to ,can_pass end
    end

    -- 遍历所有可以移动的位置，看是否有 target_pos_index
    src_pos_index = src_pos_index or grid_item.pos_index
    for _,pos_index in ipairs( grid_obj:collectMovePosIndex( src_pos_index ) ) do
        -- target_pos_index 在可移动列表中，这是一个有效的可移动的位置
        if pos_index == target_pos_index then return true, true end
    end

    -- 找不到，不可移动
    return false, false
end

function verify_fight_manager:realSwitchPage( switch_type, area_index, call_back_func )
    for i,grid_obj in ipairs( self:getAllRewardObjects() ) do
        local grid_item = self:getGridItemByPosIndex( grid_obj.pos_index )
        if grid_obj.obj_info.type == 'stone' then
            if grid_obj.grid_obj then
                grid_item.grid_obj = grid_obj.grid_obj
                grid_item.grid_obj.grid_obj = nil
            else
                grid_item.grid_obj = nil
            end
        else
            grid_item.grid_obj = nil
        end

        grid_obj:doDeath()
    end

    self:switchPage( switch_type, area_index, call_back_func )
end

function verify_fight_manager:isWin( call_back_func )
    local is_win, is_lost = self.verify_fight_control:checkIsWin()

    -- 如果失败了
    if is_lost then
        local is_enemy_end = true
        if self.fight_state == 'player_turn' or
            self.fight_state == 'player_attack' or
            self.fight_state == 'player_delay_skill' or
            self.fight_state == 'player_attacking' or
            self.fight_state == 'player_round_end' then
            is_enemy_end = false
        end
        self:updateRound( is_enemy_end )
        if not is_enemy_end then self:updateRound( true ) end

        return self:setFightState( 'fight_lost' )
    end

    -- 如果胜利了
    if is_win then
        -- 切页再战
        if self.cur_page > 1 then
            local is_enemy_end = true
            if self.fight_state == 'player_turn' or
               self.fight_state == 'player_attack' or
               self.fight_state == 'player_delay_skill' or
               self.fight_state == 'player_attacking' or
               self.fight_state == 'player_round_end' then
               is_enemy_end = false
            end
            self:updateRound( is_enemy_end )
            if not is_enemy_end then self:updateRound( true ) end

            return self:realSwitchPage( self.cur_page > 2 and 'next_page' or 'boss_enter', self.cur_page - 1, function() end )
        end

        return self:setFightState( 'fight_win' )
    end

    -- 既没有胜利，也没有失败的话，就执行回调函数，继续打下去
    if call_back_func then return call_back_func() end
end

function verify_fight_manager:relive()
    self.is_fighting = true

    -- 重置一些状态
    self.is_big_boss = false
    self.area_index = 5
    self.buff_item = nil

    -- 重新创建 player_fighters
    for i,pet_info in ipairs( self.player_fighters ) do
        self:createGridObject( pet_info, pet_info.pos_index )
    end

    -- 重新创建还存活的怪物
    local page_index = self.cur_page
    local area_info = self.areas[page_index]
    for _,m_fighter_info in ipairs( area_info.enemy_fighters or {} ) do
        local origin_hp = self.relive_monsters_info[m_fighter_info.entity_id]
        if origin_hp then
            -- 没有死亡的，将会重新创建
            self:createGridObject( m_fighter_info, m_fighter_info.pos_index )
            local grid_obj = self:getGridObjByEntityID( m_fighter_info.entity_id )
            __base_object.setCurHP( grid_obj, origin_hp )
        end
    end
    self.relive_monsters_info = {}

    -- 石头障碍
    if page_index > 1 and self.stone_num and self.stone_num > 0 then
        self:createStoneGridObject( self.stone_num )
    end

    self:setFightState( self.verify_fight_control.initiate_turn )
end

function verify_fight_manager:replaceFighterN( replace_list, index, call_back_func )
    local obj_info = replace_list[index]
    if not obj_info then return call_back_func() end

    -- 找到乱入的 grid_obj
    local lr_pos_index = nil
    for _,grid_obj in ipairs( obj_info.type == 'enemy' and self:getAllMonsterObjects() or self:getAllPetObjects() ) do
        if grid_obj.obj_info.team_pos_index == obj_info.team_pos_index then
            lr_pos_index = grid_obj.pos_index
            grid_obj:destroy()

            local grid_item = self:getGridItemByPosIndex( grid_obj.pos_index )
            grid_item.grid_obj = nil

            break
        end
    end

    local pos_index = lr_pos_index or obj_info.pos_index
    local origin_pos_index = self.verify_fight_control:getBornPosIndex( obj_info.team_pos_index, obj_info.type == 'enemy' )

    local grid_item = self:createGridObject( obj_info, pos_index or origin_pos_index )
    grid_item.grid_obj.origin_pos_index = origin_pos_index

    -- next 
    self:replaceFighterN( replace_list, index + 1, call_back_func )
end

function verify_fight_manager:gainDropReward( grid_obj, drop_list )
end

function verify_fight_manager:getAllRewardObjects()
    local all_reward_objects = {}
    for i=1,self.grid_count_per_page do
        local grid_item = self:getGridItemByPosIndex( i, true )
        if grid_item and grid_item.grid_obj.obj_info.type ~= 'enemy' and grid_item.grid_obj.obj_info.type ~= 'player' then
            if not table.hasValue( all_reward_objects, grid_item.grid_obj ) then
                table.insert( all_reward_objects, grid_item.grid_obj )
            end
        end
    end
    return all_reward_objects
end

function verify_fight_manager:useLargeSkill( call_back_func )
    if call_back_func then call_back_func() end
end

function verify_fight_manager:switchBigBossMode()
    -- 如果是大 BOSS 的话，一定只有一个
    local all_monster_objects = self:getAllMonsterObjects()
    local grid_obj = all_monster_objects[1]
    if grid_obj then grid_obj:switchMode() end
end

function verify_fight_manager:createStoneGridObject( stone_num )
    local stone_pos_index = self:getStonePosIndex()

    -- 所有可以放置的空闲的位置
    local free_pos_index = stack.new()
    for _,pos_index in ipairs( stone_pos_index ) do
        local grid_item = self:getGridItemByPosIndex( pos_index )
        if grid_item.grid_obj == nil then
            free_pos_index:push( pos_index )
        end
    end

    -- 如果有位置的话，就去放置
    for i=1,stone_num do
        while free_pos_index:getElementCount() > 0 do
            local index = math.floor( self:getRandomNumber( 1, free_pos_index:getElementCount() ) )
            local pos_index = free_pos_index:getAt( index )

            -- 不管这个位置能否放置石块，都要把这个位置从 free_pos_index 中去掉
            free_pos_index:pop( pos_index )

            -- 如果这个位置不会导致怪物或者宠物无法移动的话，那就可以放置了
            -- 如果这个位置不能放置，就随机另外一个位置
            if self:isValidStonePosIndex( pos_index ) then
                local item_type = 'stone'
                self:createGridObject( { type = item_type }, pos_index )

                break
            end
        end
    end
end

function verify_fight_manager:playerActionCallback()
end

function verify_fight_manager:isValidStonePosIndex( pos_index )
    for _,grid_obj in ipairs( self:getAllFighterObjects() ) do
        local temp_pos_index = {}
        for _,index in ipairs( grid_obj:collectValidMovePosIndex() ) do
            if index ~= pos_index then
                table.insert( temp_pos_index, index )
            end
        end

        -- 没有任何一个可移动的位置的话，不能放置石头
        if #temp_pos_index == 0 then return false end
    end

    return true
end

function verify_fight_manager:triggerSkill( all_src_entity_id, all_target_entity_id, priority_grid_obj, action, param_tbl, ignore_trigger_entity_ids )
    local function __is_ignore_id__( entity_id ) return table.hasValue( ignore_trigger_entity_ids, entity_id ) end

    if priority_grid_obj then
        priority_grid_obj:checkTriggerSkill( all_src_entity_id, all_target_entity_id, action, param_tbl )
    end
    for _,temp_grid_obj in ipairs( self:getAllFighterObjects() ) do
        if temp_grid_obj ~= priority_grid_obj and not __is_ignore_id__( temp_grid_obj.obj_info.entity_id ) then
            temp_grid_obj:checkTriggerSkill( all_src_entity_id, all_target_entity_id, action, param_tbl )
        end
    end
end

function verify_fight_manager:triggerSkillSelf( action )
    for _,temp_grid_obj in ipairs( self:getAllFighterObjects() ) do
        local all_src_entity_id = { temp_grid_obj.obj_info.entity_id }
        local all_target_entity_id = { temp_grid_obj.obj_info.entity_id }
        temp_grid_obj:checkTriggerSkill( all_src_entity_id, all_target_entity_id, action, {} )
    end
end

function verify_fight_manager:getMoveGridCount( from_pos_index, to_pos_index )
    if not from_pos_index or not to_pos_index then return nil end

    local from_grid_item = self:getGridItemByPosIndex( from_pos_index )
    if not from_grid_item then return nil end

    local to_grid_item = self:getGridItemByPosIndex( to_pos_index )
    if not to_grid_item then return nil end

    local row = math.abs( from_grid_item.row - to_grid_item.row )
    local col = math.abs( from_grid_item.col - to_grid_item.col )

    return math.max( row, col )
end

function verify_fight_manager:isDeadlyAttackAction( is_player, attack_list )
    attack_list.deadly_attack = false
end

