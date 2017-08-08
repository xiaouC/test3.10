-- ./app/platform/game/game_common/game_msg_ids.lua
require 'app.platform.common.common'

-- 0-100 system
-- 100-200 game station user action and common
-- 200-300 majiang
-- 300-400 poker
game_msg_ids = table.readOnly({
    EVENT_GAME_NOTIFY                               = 10001,                 --游戏主id

-------------------------------------------------------------UI行为类型----------------
    DATA_ACTION_TYPE_GET = 1,                            --UI 读取数据
    DATA_ACTION_TYPE_SEND = 2,                           --UI send msg to server
    LOGIC_ACTION_TYPE_GET = 3,                           --逻辑 读取数据
    DATA_ACTION_TYPE_SET  = 4,                           --设置


--------------------------------------USER用户自定义的在从10001开始--------------------------------------------------------------
    ACTION_PLAY_DICE                                 = 10001,                 -- 请求打骰
    ACTION_OUT_CARD                                  = 10002,                 -- 请求摸牌
    ACTION_BLOCK_OPREATE                             = 10003,                 -- 请求拦牌
    ACTION_GET_ONESELF_USERINFO                      = 10004,                 -- 获取自己用户信息
    ACTION_GET_ONESELF_DESK_POSITION                 = 10005,                 -- 获取自己坐位号
    ACTION_DATA_USER_INFO                            = 10006,                 -- 玩家信息 
    ACTION_SWAP_WALL_CARD                            = 10007,                 -- 请求换牌
    ACTION_DATA_USER_AGREE                           = 10008,                 -- 同意请求 
    ACTION_USER_FREE_GAME                            = 10009,                 -- 解散游戏
    ACTION_APPLY_GAME_INFO                           = 10010,                 -- 申请更新游戏信息 
    ACTION_APPLY_GAME_CONFIG                         = 10011,                 -- 申请游戏配置
    ACTION_RESET_GAME_STATION						 = 10012,				  -- 申请游戏状态


    -- 0 - 100 system
    -- 预留

    -- 100 - 200 game station user action and common
    EVENT_GAME_NOTIFY_GAME_STATE                    = 101,                   -- 游戏配置 
    EVENT_GAME_NOTIFY_USER_SIT                      = 102,                   -- 用户坐下
    EVENT_GAME_NOTIFY_USER_COME                     = 102,                   -- 玩家进来
    EVENT_GAME_NOTIFY_USER_UP                       = 103,                   -- 用户站起
    EVENT_GAME_NOTIFY_USER_READY                    = 104,                   -- 游戏准备 
    EVENT_GAME_NOTIFY_NOTIFY_GAME_CHAT_MSG          = 105,                   -- 游戏玩家聊天消息
    EVENT_GAME_NOTIFY_USER_CUT                      = 106,                   -- 用户断线
    EVENT_GAME_NOTIFY_USER_FREE_OPERATE             = 107,                   -- 玩家申请解散游戏
    EVENT_GAME_NOTIFY_USER_FREE_RESULT              = 108,                   -- 玩家解散游戏结果
    EVENT_GAME_NOTIFY_FORCE_LEAVE                   = 109,                   -- 剔除信息
    EVENT_GAME_NOTIFY_GPS_RESULT	        	    = 110,                   -- 通知定位结果
    EVENT_GAME_NOTIFY_USER_SIT_FAIL                 = 111,                   -- 用户坐下失败

    -- 200 - 300 mahjong
    EVENT_GAME_NOTIFY_MAKER_INFO                    = 201,                  -- 定庄消息
    EVENT_GAME_NOTIFY_DICE_INFO                     = 202,                  -- 打骰子
    EVENT_GAME_NOTIFY_CARD_INFO                     = 203,                  -- 发牌消息
    EVENT_GAME_NOTIFY_OUT_CARD                      = 204,                  -- 玩家出牌
    EVENT_GAME_NOTIFY_GET_CARD                      = 205,                  -- 玩家摸牌
    EVENT_GAME_NOTIFY_BLOCK_INFO                    = 206,                  -- 拦牌消息
    EVENT_GAME_NOTIFY_BLOCK_RESULT                  = 207,                  -- 拦牌操作结果
    EVENT_GAME_NOTIFY_NOTIFY_OUT_CARD               = 208,                  -- 通知玩家出牌
    EVENT_GAME_NOTIFY_NOTIFY_NOTIFY_WAIT_BLOCK      = 209,                  -- 等待拦牌操作消息
    EVENT_GAME_NOTIFY_NOTIFY_GAME_RESULT            = 210,                  -- 游戏结束，一把
    EVENT_GAME_NOTIFY_NOTIFY_TING                   = 211,                  -- 听牌
    EVENT_GAME_NOTIFY_NOTIFY_GAME_RESULT_OVER       = 212,                  -- 游戏结束,所有局数
    EVENT_GAME_NOTIFY_NOTIFY_GAME_RESULT_ONE        = 213,                  -- 单局记录
    EVENT_GAME_NOTIFY_FAST_OUT_INOF					= 214,                  -- 快速出牌信息
    EVENT_GAME_NOTIFY_KING_CARD_INFO                = 215,                  -- 鬼牌

    -- 300 - 400 poker
})

