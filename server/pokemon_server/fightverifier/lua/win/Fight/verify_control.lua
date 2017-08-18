-- ./win/fight/verify_control.lua
require 'win.Fight.verify_manager'

__verify_fight_control = class( 'verify_fight_control' )
function __verify_fight_control:ctor( call_back_func )
    self.call_back_func = function( result )
        if call_back_func then call_back_func( result ) end
    end

    self.fight_state_change = {}
end

function __verify_fight_control:getFightProp()
end

function __verify_fight_control:getBackgroundID()
    return 1
end

function __verify_fight_control:getAreaInfo()
end

function __verify_fight_control:getPlayerFighters()
end

function __verify_fight_control:getFightType()
end

function __verify_fight_control:getFightIsNew()
end

function __verify_fight_control:generateBuffItem()
end

function __verify_fight_control:getGuideType()
end

function __verify_fight_control:checkIsWin()
    return false, false
end

function __verify_fight_control:getRandomIndex()
    if not self.random_index then self.random_index = math.random( 1, #pseudo_random_number ) end
    return self.random_index
end

function __verify_fight_control:startFight()
    local prop = self:getFightProp()
    local bg_id = self:getBackgroundID()
    local fight_type = self:getFightType()
    local is_new = self:getFightIsNew()
    local player_fighters = self:getPlayerFighters()
    local area_info, stone_num = self:getAreaInfo()
    local random_index = self:getRandomIndex()

    verify_fight_manager.verify_fight_control = self
    verify_fight_manager:prepareFighting( prop, bg_id, fight_type, is_new, player_fighters, area_info, stone_num, random_index, function()
        self.fight_end_call_back_func = function( result )
            verify_fight_manager:finish()
            if self.call_back_func then self.call_back_func( result ) end
        end

        -- 
        verify_fight_manager:start( 'init',
            -- 战斗状态切换时候的回调
            function( fight_state, is_front, call_back_func )
                return self:fightStateChange( fight_state, is_front, call_back_func )
            end,
            function( switch_type, area_info, area_index, call_back_func )
                return self:switchPageCallbackFunc( switch_type, area_info, area_index, call_back_func )
        end)
    end)
end

local pet_pos_index = { 15, 16, 12, 8 }
function __verify_fight_control:getPlayerFighterBornPosIndex( team_pos_index )
    return pet_pos_index[team_pos_index]
end

local enemy_pos_index = { 2, 1, 5, 9 }
function __verify_fight_control:getBornPosIndex( team_pos_index, is_enemy )
    if not is_enemy then return self:getPlayerFighterBornPosIndex( team_pos_index ) end
    return enemy_pos_index[team_pos_index]
end

function __verify_fight_control:fightStateChange( fight_state, is_front, call_back_func )
    local fsc = self.fight_state_change[fight_state]
    if fsc then
        if is_front then
            if fsc.front_func then
                fsc.front_func( call_back_func )
            else
                call_back_func()
            end
        else
            if fsc.post_func then fsc.post_func() end
        end
    else
        if is_front then call_back_func() end
    end
end

function __verify_fight_control:switchPageCallbackFunc( switch_type, area_info, area_index, call_back_func )
    if call_back_func then call_back_func() end
end

function __verify_fight_control:setFightStateChangeFrontFunc( fight_state, front_func )
    if not self.fight_state_change[fight_state] then self.fight_state_change[fight_state] = {} end
    self.fight_state_change[fight_state].front_func = front_func
end

function __verify_fight_control:getFightStateChangeFrontFunc( fight_state )
    if not self.fight_state_change[fight_state] then return nil end
    return self.fight_state_change[fight_state].front_func
end

function __verify_fight_control:setFightStateChangePostFunc( fight_state, post_func )
    if not self.fight_state_change[fight_state] then self.fight_state_change[fight_state] = {} end
    self.fight_state_change[fight_state].post_func = post_func
end

function __verify_fight_control:getFightStateChangePostFunc( fight_state )
    if not self.fight_state_change[fight_state] then return nil end
    return self.fight_state_change[fight_state].post_func
end

