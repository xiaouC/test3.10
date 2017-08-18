-- ./win/Fight/interactive.lua
require 'win.Fight.verify_control'

local HERO_ATTR_PVP = 7

__verify_fight_interactive = class( 'verify_fight_interactive', __verify_fight_control )
function __verify_fight_interactive:ctor( fr, call_back_func )
    __verify_fight_control.ctor( self, call_back_func )

    self.fr = fr
    self.skip_flag = false
    self.action_index = 1

    self.buff_group_index = self.fr.buff_group_index
    self.buff_index = 1

    self.initiate_turn = ( fr.is_player_turn and 'player_turn' or 'monster_turn' )

    self.max_last_round = self.fr.max_last_round
    self.cur_last_round = self.max_last_round
    self.round_fight_state = self.fr.round_fight_state

    -- init state
    self:setFightStateChangeFrontFunc( 'init', function( call_back_func )
        verify_fight_manager.replay_skill_info_list = {}
        for _,v in ipairs( self.fr.skill_list ) do verify_fight_manager.replay_skill_info_list[v.id] = v end

        verify_fight_manager.replay_se_info_list = {}
        for _,v in ipairs( self.fr.se_info_list ) do verify_fight_manager.replay_se_info_list[v.id] = v end

        if call_back_func then call_back_func() end
    end)
    self:setFightStateChangePostFunc( 'init', function()
        -- 开始战斗
        verify_fight_manager:setFightState( 'fight_start' )
    end)

    -- fight start state
    self:setFightStateChangePostFunc( 'fight_start', function()
        verify_fight_manager:setFightState( 'fight_turn' )
    end)

    self:setFightStateChangePostFunc( 'fight_turn', function() verify_fight_manager:setFightState( self.initiate_turn ) end )

    -- player turn
    self:setFightStateChangeFrontFunc( 'player_turn', function( call_back_func )
        verify_fight_manager.player_action_flag = false

        -- 玩家回合开始
        verify_fight_manager:debuffCheck( false, function() verify_fight_manager:fightObjectTurnFront( false, call_back_func ) end )
    end)
    self:setFightStateChangePostFunc( 'player_turn', function()
        -- 随机生成掉落
        self:generateBuffItem()
        verify_fight_manager:setFightState( 'player_attack' )
    end)

    self:setFightStateChangePostFunc( 'player_attack', function()
        self:nextAction( true )
    end)

    -- player round end
    self:setFightStateChangeFrontFunc( 'player_round_end', function( call_back_func )
        verify_fight_manager:fightObjectTurnEnd( false, call_back_func )
    end)
    self:setFightStateChangePostFunc( 'player_round_end', function()
        local next_fight_state = ( self.initiate_turn == 'monster_turn' and 'fight_turn_end' or 'monster_turn' )
        verify_fight_manager:setFightState( next_fight_state )
    end)

    -- monster turn
    self:setFightStateChangeFrontFunc( 'monster_turn', function( call_back_func )
        -- 敌方回合开始前
        verify_fight_manager:debuffCheck( true,  function() verify_fight_manager:fightObjectTurnFront( true, call_back_func ) end )
    end)
    self:setFightStateChangePostFunc( 'monster_turn', function()
        verify_fight_manager:setFightState( 'monster_skill' )
    end)

    -- monster skill
    self:setFightStateChangePostFunc( 'monster_skill', function()
        if verify_fight_manager:getFightState() ~= 'monster_attack' then
            verify_fight_manager:setFightState( 'monster_attack' )
        end
    end)

    -- monster attack
    self:setFightStateChangePostFunc( 'monster_attack', function()
        self:nextAction( false )
    end)

    -- monster round end
    self:setFightStateChangeFrontFunc( 'monster_round_end', function( call_back_func )
        verify_fight_manager:fightObjectTurnEnd( true, call_back_func )
    end)
    self:setFightStateChangePostFunc( 'monster_round_end', function()
        local next_fight_state = ( self.initiate_turn == 'player_turn' and 'fight_turn_end' or 'player_turn' )
        verify_fight_manager:setFightState( next_fight_state )
    end)

    self:setFightStateChangePostFunc( 'fight_turn_end', function()
        -- 不能在指定回合内结束
        if self.cur_last_round <= 0 then
            verify_fight_manager:setFightState( self.round_fight_state )
        else
            verify_fight_manager:setFightState( 'fight_turn' )
        end
    end)

    self:setFightStateChangePostFunc( 'fight_win', function()
    end)

    self:setFightStateChangePostFunc( 'fight_lost', function()
    end)
end

function __verify_fight_interactive:setCurLastRound( last_round )
    self.cur_last_round = last_round
    if self.cur_last_round > self.max_last_round then self.cur_last_round = self.max_last_round end
    if self.cur_last_round < 0 then self.cur_last_round = 0 end
end

function __verify_fight_interactive:getFightProp() return self.fr.prop end
function __verify_fight_interactive:getBackgroundID() return self.fr.bg_id end
function __verify_fight_interactive:getAreaInfo() return self.fr.areas, self.fr.stone_num, self.fr.buff_group_index end
function __verify_fight_interactive:getPlayerFighters() return self.fr.player_fighters end
function __verify_fight_interactive:getFightType() return self.fr.fight_type end
function __verify_fight_interactive:getFightIsNew() return self.fr.is_new end
function __verify_fight_interactive:checkIsWin()
    local is_win = true
    local is_lost = true

    -- 场上有怪物或者 BOSS 就没有胜利
    -- 场上没有了 pet 就是输了
    for _,grid_obj in ipairs( verify_fight_manager:getAllFighterObjects() ) do
        if grid_obj.obj_info.type == 'enemy' and not grid_obj.death then is_win = false end
        if grid_obj.obj_info.type == 'player' and not grid_obj.death then is_lost = false end
    end

    return is_win, is_lost
end
function __verify_fight_interactive:getRandomIndex() return self.fr.random_index end
function __verify_fight_interactive:generateBuffItem()
    if self.fr.buff_group_index ~= 0 then
        verify_fight_manager.area_index = 6

        local function __get_buff_info__()
            verify_fight_manager:getRandomNumber()
            local buff_info = self.fr.buff_info_list[self.buff_index]
            self.buff_index = self.buff_index + 1
            return buff_info
        end

        -- 如果当前区域没有 BUFF 物品，就随一下
        if not verify_fight_manager.buff_item and verify_fight_manager.cur_page > 1 then
            if verify_fight_manager:getRandomNumber( 0, 100 ) <= fight_const.buff_item_probability then
                verify_fight_manager.buff_item = true

                local buff_info = __get_buff_info__()
                local grid_item = verify_fight_manager:createGridObject( buff_info )
                grid_item.grid_obj:addDeathCallBackFunc( function() verify_fight_manager.buff_item = nil end )
            end
        end
    end
end

function __verify_fight_interactive:switchPageCallbackFunc( switch_type, area_info, area_index, call_back_func )
    -- 切换区域
    local function __switch_call_back()
        if area_index ~= verify_fight_manager.page_count then verify_fight_manager:setFightState( 'fight_turn' ) end

        if call_back_func then call_back_func() end
    end

    -- BOSS 区域，不会生成石板、石块、血心
    if area_index == 1 then
        if area_index ~= verify_fight_manager.page_count then
            verify_fight_manager.player_total_round = verify_fight_manager.player_total_round + 1
            verify_fight_manager.enemy_total_round = verify_fight_manager.enemy_total_round + 1
        end

        __switch_call_back()

        return
    end

    -- 石头障碍
    if verify_fight_manager.stone_num and verify_fight_manager.stone_num > 0 then
        verify_fight_manager:createStoneGridObject( verify_fight_manager.stone_num )
        __switch_call_back()
    else
        __switch_call_back()
    end
end

function __verify_fight_interactive:appendAction( action_type, entity_id, mv_index )
end

function __verify_fight_interactive:save()
end

function __verify_fight_interactive:initHelpButton()
end

function __verify_fight_interactive:getAI( is_player )
end

function __verify_fight_interactive:runAI( is_player )
end

function __verify_fight_interactive:nextAction( is_player )
    local next_fight_state = is_player and 'player_delay_skill' or 'monster_delay_skill'

    local action_info = self.fr.actions[self.action_index]
    self.action_index = self.action_index + 1

    if not action_info then
        verify_fight_manager:isWin()

        return false
    end

    local action_type = {
        attack = function()
            local grid_obj = verify_fight_manager:getGridObjByEntityID( action_info.entity_id )
            verify_fight_manager.normal_attack_first_grid_obj = grid_obj
            verify_fight_manager:setFightState( next_fight_state )
        end,
        move = function()
            local grid_obj = verify_fight_manager:getGridObjByEntityID( action_info.entity_id )
            verify_fight_manager.normal_attack_first_grid_obj = grid_obj
            verify_fight_manager:gridObjAction( grid_obj, action_info.mv_index, function()
                verify_fight_manager:setFightState( next_fight_state )
            end)
        end,
        relive = function()
            verify_fight_manager:setFightState( 'relive' )
        end,
    }

    action_type[action_info.action_type]()

    return true
end

