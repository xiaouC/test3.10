
local game_poker_config = import('.game_poker_config')
local game_scene_base = import('.game_scene_base')
local GameScenePoker = class('GameScenePoker', game_scene_base)
function GameScenePoker:ctor(game_id, self_user_id, scene_config)

    -- 
    local preload_plist = {
        'mahjong/common/mahjong_common.plist',
        'mahjong/game_card/game_card.plist',
        'mahjong/anim/anim_draw_card.plist'
    }

    game_scene_base.ctor(self, game_id, self_user_id, {
        background = scene_config.background or 'mahjong/mahjong_tablecloth.jpg',
        game_type = 'poker',
        game_name = scene_config.game_name,
        preload_plist = table.merge_append(scene_config.preload_plist or {}, preload_plist),
        listen_msg_ids = table.merge({
        }, scene_config.listen_msg_ids or {}),
        components = table.merge({
--            ['hand_card_self']              = { file_name = 'my_hand_card', args = { location_index = USER_LOCATION_SELF,   is_back = false } },    -- 手牌
--            ['hand_card_right']             = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_RIGHT,  is_back = true } },
--            ['hand_card_facing']            = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_FACING, is_back = true } },
--            ['hand_card_left']              = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_LEFT,   is_back = true } },
--            ['lei_card']                    = { file_name = 'lei_card', args = { is_back = true } },                                              -- 垒牌
--            ['out_card_self']               = { file_name = 'out_card', args = { location_index = USER_LOCATION_SELF } },                         -- 出牌
--            ['out_card_right']              = { file_name = 'out_card', args = { location_index = USER_LOCATION_RIGHT } },
--            ['out_card_facing']             = { file_name = 'out_card', args = { location_index = USER_LOCATION_FACING } },
--            ['out_card_left']               = { file_name = 'out_card', args = { location_index = USER_LOCATION_LEFT } },
--            ['tan_card_self']               = { file_name = 'tan_card', args = { location_index = USER_LOCATION_SELF } },                         -- 碰牌
--            ['tan_card_right']              = { file_name = 'tan_card', args = { location_index = USER_LOCATION_RIGHT } },
--            ['tan_card_facing']             = { file_name = 'tan_card', args = { location_index = USER_LOCATION_FACING } },
--            ['tan_card_left']               = { file_name = 'tan_card', args = { location_index = USER_LOCATION_LEFT } },
--            ['ting_card']                   = { file_name = 'ting_card', args = { x = 1230, y = 135, has_fan_count = true } },                               -- 听牌
--            ['on_block']                    = { file_name = 'on_block', },                                                              -- 拦牌操作
--            ['direction_room_info_view']    = { file_name = 'direction_room_info_view', },                                              -- 牌桌中间的那块区域，包括方位以及包间信息
--            ['roll_dice_view']              = { file_name = 'roll_dice_view', },                                                        -- 打骰子的动画界面
--            ['flop_card']                   = { file_name = 'flop_card', args = { flop_title = '鬼牌确定' } },                          -- 翻鬼牌的动画
            ['user_head_self']              = { file_name = 'user_head_view', args = { location_index = POKER_USER_LOCATION_SELF,   x = 140,   y = 160, chat_side = 'self' } },   -- 游戏过程中，在桌面显示的头像
            ['user_head_one']             = { file_name = 'user_head_view', args = { location_index = POKER_USER_LOCATION_ONE,  x = 1220, y = 460, chat_side = 'one' } },
            ['user_head_two']            = { file_name = 'user_head_view', args = { location_index = POKER_USER_LOCATION_TWO, x = 1045,  y = 630, chat_side = 'two' } },
            ['user_head_three']              = { file_name = 'user_head_view', args = { location_index = POKER_USER_LOCATION_THREE,   x = 235,   y = 630, chat_side = 'three' } },
            ['user_head_four']              = { file_name = 'user_head_view', args = { location_index = POKER_USER_LOCATION_FOUR,   x = 60,   y = 460, chat_side = 'four' } },
            ['normal_chat']                 = { file_name = 'normal_chat', args = { x = 1230, y = 275, }, },
            ['voice_chat']                  = { file_name = 'voice_chat', args = { x = 1230, y = 175 }, },            -- 语音聊天
--            ['next_round_ready']            = { file_name = 'next_round_ready', args = { { x = 640, y = 250 }, { x = 950, y = 380 }, { x = 640, y = 520 }, { x = 300, y = 380 } } },
--            ['free_game_second_confirmation'] = { file_name = 'free_game_second_confirmation', },           -- 申请解散包间的二次确认
--            ['free_game_waiting']           = { file_name = 'free_game_waiting', },                         -- 解散包间的等待界面
--            ['free_game_result']            = { file_name = 'free_game_result', },                          -- 解散包间结果确认界面
--            ['final_settle_view']           = { file_name = 'final_settle_view', },                         -- 大结算界面
--            ['block_result_effect']         = { file_name = 'block_result_effect', },                       -- 拦牌特效
--            ['fast_out_card_effect']        = { file_name = 'fast_out_card_effect', args = { { x = 210, y = 205 }, { x = 1080, y = 480 }, { x = 820, y = 620 }, { x = 210, y = 480 } } },        -- 快速出牌
--            ['out_card_guild']              = { file_name = 'out_card_guild', },            -- 滑动出牌引导
--            ['out_card_guild_line']         = { file_name = 'out_card_guild_line', },       -- 滑出此线出牌
--            ['out_card_tips']               = { file_name = 'out_card_tips', },
--            ['round_settle']                = { file_name = 'quick_settle', args = { draw_sprite_file = 'mahjong/common/game_result_draw_4.png' } },     -- 小局结算界面
--            ['warning_tips']                = { file_name = 'warning_tips', args = { x = 640, y = 170 }, },
             ['game_ready_view']     = { file_name = 'game_ready_view', args = {} },
             ['game_room_info_view']     = { file_name = 'game_room_info_view', args = {} },
        }, scene_config.components or {}),
        sound_text_list = scene_config.sound_text_list or {
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
        },
        emoji_type = scene_config.emoji_type or 'mahjong',
        has_ghost_card = scene_config.has_ghost_card,                                       -- 是否有鬼牌，这个决定了是否存在翻鬼牌这回事，影响的是打骰子到摸牌间的动画控制，必须要明确指定
        need_flop_anim = scene_config.need_flop_anim,                                       -- 是否需要翻鬼牌的动画，红中麻将，鬼牌是明确的，所以不需要动画
        ghost_card_name = scene_config.ghost_card_name,                                     -- 鬼牌的称谓，有些叫‘鬼牌’，有些叫‘混牌’等等
        ghost_subscript_file = scene_config.ghost_subscript_file or 'mahjong/common/mahjong_subscript_ghost.png',   -- 鬼牌使用的角标贴图
    })

    -- 
    self.all_user_info = {}
    self.local_index_to_server_index = {}
    self.server_index_to_local_index = {}

    self.my_server_index = nil                   -- 自己的 station
    self.my_local_index =  nil
    self.banker_server_index = nil               -- 庄家的 station

    ----------------------------------------------------------------------------------------------------------------------------------
    -- 控制动画的标识:
    -- 主要控制的是游戏开始的动画，具体如下：打骰子 =》 初始化手牌 =》 摸第一张手牌 =》 定鬼牌 =》 可以出牌
    -- 后续的过程，就是与服务器一来一回的交互了
    ----------------------------------------------------------------------------------------------------------------------------------

    -- 
    self.roll_dice_anim_end = false             -- 打骰子动画结束标识

    self.hand_card_data = nil                   -- 收到的服务器的数据
    self.init_hand_card_ended = false           -- 初始化手牌动画结束标识

    self.draw_card_data = nil                   -- 收到的服务器的数据
    self.draw_card_anim_end = false             -- 摸牌动画结束标识

    self.init_ghost_card_data = nil             -- 收到的服务器的数据
    self.ghost_card_anim_end = false            -- 翻鬼牌动画结束标识

    self.on_notify_out_card_data = nil          -- 收到的服务器数据

    -- 防止重复进入，因为出牌时常事，而翻鬼牌是一次的
    self.is_first_time_flop_flag = true

    -- 在这里记录下来，是因为有一些麻将，在小局结算的时候，服务器没有下发
    -- 而有一些，服务器却下发了，真是淡淡的忧伤啊
    self.block_cards = { {}, {}, {}, {} }
end

function GameScenePoker:check_game_state(data)
    if(nil == data.m_base_info ) then
        data.m_base_info = {}

        data.m_base_info.m_game_config = clone(data.m_gamerule)                     --游戏配置
        data.m_base_info.m_user_id = clone(data.m_otheruserid)                      --用户id
        data.m_base_info.m_privater_id = data.m_private_id                          --房主id
        data.m_base_info.m_private_station = data.m_private_station                 --房主位置号
        data.m_base_info.m_banker_station = data.m_bybankeruser                     --庄家位置
        data.m_base_info.m_cur_play_count = data.m_byGamePlayNum                    --当前第几局
        data.m_base_info.m_total_play_count = data.m_gamerule.m_iSetRoomCount       --总局数
        data.m_base_info.m_free_time = data.m_freeGametime                          --解散时间
        data.m_base_info.m_chair_id = data.m_chairid                                --自己当前位置
        data.m_base_info.m_user_score = clone(data.m_winmoney)                      --玩家分数
        data.m_base_info.m_user_cut = {}                                            --掉线用户
        data.m_base_info.m_fast_count = clone(data.m_fast_count)                    --快速出牌

        data.m_user_ready = clone(data.m_bagreeStation)                             --所有玩家准备状态
    end
end

function GameScenePoker:restart()
    game_scene_base.restart(self)

    self.fake_card_ids = {}
    self.really_card_ids = {}

    self:requestAction('user_agree', true)
end

function GameScenePoker:on_game_state(data)
    self:check_game_state(data)
    self.m_chair_id = data.m_base_info.m_chair_id + 1
    game_scene_base.on_game_state(self,data)
end

function GameScenePoker:on_reconn_game_state(data)
end

function GameScenePoker:convertStationToLocalIndex(server_index)
    -- local index coordinate, my local index is allways No.1.
    --              3
    --              |
    --              |
    --      4 ------------- 2
    --              |
    --              |
    --              1
    local count = 5 -- self.mahjong_config.count or 5
    return (server_index + count - self.my_server_index) % count + 1
end

function GameScenePoker:getRuleDetailConfig()
    return {
        {
            name = '基本玩法',
            help_contents = { string.format('%s/%d/rule_1.png', g_game_rules_url, self.game_id) },
        },
        {
            name = '基本牌型',
            help_contents = { string.format('%s/%d/rule_2.png', g_game_rules_url, self.game_id) },
        },
        {
            name = '特殊规则',
            help_contents = { string.format('%s/%d/rule_3.png', g_game_rules_url, self.game_id) },
        },
        {
            name = '结算规则',
            help_contents = { string.format('%s/%d/rule_4.png', g_game_rules_url, self.game_id) },
        },
    }
end

return GameScenePoker
