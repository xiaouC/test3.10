-- ./app/platform/game/game_common/game_scene_manager_base.lua

RequestAction = {
    DATA_ACTION_TYPE_GET                    = 1,
    DATA_ACTION_TYPE_SEND                   = 2,
    LOGIC_ACTION_TYPE_GET                   = 3,
    DATA_ACTION_TYPE_SET                    = 4,

    ACTION_PLAY_DICE                        = 10001,                 --请求打骰
    ACTION_OUT_CARD                         = 10002,                 --请求摸牌
    ACTION_BLOCK_OPREATE                    = 10003,                 --请求拦牌
    ACTION_GET_ONESELF_USERINFO             = 10004,                 --获取自己用户信息
    ACTION_GET_ONESELF_DESK_POSITION        = 10005,                 --获取自己坐位号
    ACTION_DATA_USER_INFO                   = 10006,                 --玩家信息 
    ACTION_SWAP_WALL_CARD                   = 10007,                 --请求换牌
    ACTION_DATA_USER_AGREE                  = 10008,                 --同意请求 
    ACTION_USER_FREE_GAME                   = 10009,                 --解散游戏
    ACTION_APPLY_GAME_INFO                  = 10010,                 --申请更新游戏信息 
    ACTION_APPLY_GAME_CONFIG                = 10011,                 --申请游戏配置
    ACTION_RESET_GAME_STATION               = 10012,				 --申请游戏状态
    ACTION_USER_TIAN_TING                   = 10013,				 --玩家天听操作
    ACTION_USER_RUN_SCORE                   = 10014,				 --玩家跑分操作
}

-------------------------------------------------------------------------------------------------------------------------------------
local GameSceneManagerBase = class('GameSceneManagerBase')
function GameSceneManagerBase:ctor()
    self.game_scene = nil

    self.request_actions = {
        [RequestAction.DATA_ACTION_TYPE_GET] = {},
        [RequestAction.DATA_ACTION_TYPE_SEND] = {},
    }
end

function GameSceneManagerBase:init_module(game_handle_impl)
    self.game_handle_impl = game_handle_impl

    -- 
    self.request_actions[RequestAction.DATA_ACTION_TYPE_SEND] = {
        [RequestAction.ACTION_PLAY_DICE]            = function(param) self:do_play_dice(param) end,
        [RequestAction.ACTION_OUT_CARD]             = function(param) self:do_out_card(param) end,
        [RequestAction.ACTION_BLOCK_OPREATE]        = function(param) self:do_block_opreate(param) end,
        [RequestAction.ACTION_SWAP_WALL_CARD]       = function(param) self:do_swap_wall_card(param) end,
        [RequestAction.ACTION_DATA_USER_AGREE]      = function(param) self:do_user_agree(param) end,
        [RequestAction.ACTION_USER_FREE_GAME]       = function(param) self:do_user_free_game(param) end,
        [RequestAction.ACTION_APPLY_GAME_INFO]      = function(param) self:do_user_apply_game_info(param) end,
        [RequestAction.ACTION_APPLY_GAME_CONFIG]    = function(param) self:do_get_game_config(param) end,
        [RequestAction.ACTION_RESET_GAME_STATION]   = function(param) self:do_request_game_station(param) end,
    }

    self.request_actions[RequestAction.DATA_ACTION_TYPE_GET] = {
        [RequestAction.ACTION_GET_ONESELF_USERINFO]      = function(param) self:do_get_self_info(param) end,
        [RequestAction.ACTION_GET_ONESELF_DESK_POSITION] = function(param) self:do_get_self_desk_station(param) end,
        [RequestAction.ACTION_DATA_USER_INFO]            = function(param) self:do_get_user_info_by_id(param) end,
    }
end

function GameSceneManagerBase:leave_game_scene()
end

function GameSceneManagerBase:data_notify(id, data)
    if tolua.cast(self.game_scene, 'Node') then self.game_scene:data_notify(id, data) end
end

function GameSceneManagerBase:request_action(event_type, action_id, param)
    local ra = self.request_actions[event_type]
    if ra then
        local action_func = ra[action_id]
        if action_func then
            return action_func(param)
        end
    end
end

return GameSceneManagerBase
