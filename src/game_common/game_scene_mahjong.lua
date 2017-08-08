-- ./app/platform/game/game_scene_mahjong.lua
local CURRENT_MODULE_NAME = ...
require 'app.platform.game.game_common.game_card_config'
require 'app.platform.game.game_common.mahjong_config'

local clientmain = import('...room.clientmain')

local game_scene_base = import('.game_scene_base')
local GameSceneMahjong = class('GameSceneMahjong', game_scene_base)
function GameSceneMahjong:ctor(game_id, self_user_id, scene_config)
    local preload_plist = {
        'mahjong/common/mahjong_common.plist',
        'mahjong/game_card/game_card.plist',
        'mahjong/anim/anim_draw_card.plist'
    }

    game_scene_base.ctor(self, game_id, self_user_id, {
        background = scene_config.background or 'mahjong/mahjong_tablecloth.jpg',
        game_type = 'mahjong',
        game_name = scene_config.game_name,
        preload_plist = table.merge_append(scene_config.preload_plist or {}, preload_plist),
        listen_msg_ids = table.merge({
        }, scene_config.listen_msg_ids or {}),
        components = table.merge({
            ['hand_card_self']              = { file_name = 'my_hand_card', args = { location_index = USER_LOCATION_SELF,   is_back = false } },    -- 手牌
            ['hand_card_right']             = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_RIGHT,  is_back = true } },
            ['hand_card_facing']            = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_FACING, is_back = true } },
            ['hand_card_left']              = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_LEFT,   is_back = true } },
            ['lei_card']                    = { file_name = 'lei_card', args = { is_back = true } },                                              -- 垒牌
            ['out_card_self']               = { file_name = 'out_card', args = { location_index = USER_LOCATION_SELF } },                         -- 出牌
            ['out_card_right']              = { file_name = 'out_card', args = { location_index = USER_LOCATION_RIGHT } },
            ['out_card_facing']             = { file_name = 'out_card', args = { location_index = USER_LOCATION_FACING } },
            ['out_card_left']               = { file_name = 'out_card', args = { location_index = USER_LOCATION_LEFT } },
            ['tan_card_self']               = { file_name = 'tan_card', args = { location_index = USER_LOCATION_SELF } },                         -- 碰牌
            ['tan_card_right']              = { file_name = 'tan_card', args = { location_index = USER_LOCATION_RIGHT } },
            ['tan_card_facing']             = { file_name = 'tan_card', args = { location_index = USER_LOCATION_FACING } },
            ['tan_card_left']               = { file_name = 'tan_card', args = { location_index = USER_LOCATION_LEFT } },
            ['ting_card']                   = { file_name = 'ting_card', args = { x = 1230, y = 135, has_fan_count = true } },                               -- 听牌
            ['on_block']                    = { file_name = 'on_block', },                                                              -- 拦牌操作
            ['direction_room_info_view']    = { file_name = 'direction_room_info_view', },                                              -- 牌桌中间的那块区域，包括方位以及包间信息
            ['roll_dice_view']              = { file_name = 'roll_dice_view', },                                                        -- 打骰子的动画界面
            ['flop_card']                   = { file_name = 'flop_card', args = { flop_title = '鬼牌确定' } },                          -- 翻鬼牌的动画
            ['user_head_self']              = { file_name = 'user_head', args = { location_index = USER_LOCATION_SELF,   x = 50,   y = 210, chat_side = 'right' } },   -- 游戏过程中，在桌面显示的头像
            ['user_head_right']             = { file_name = 'user_head', args = { location_index = USER_LOCATION_RIGHT,  x = 1230, y = 480, chat_side = 'left' } },
            ['user_head_facing']            = { file_name = 'user_head', args = { location_index = USER_LOCATION_FACING, x = 970,  y = 620, chat_side = 'left' } },
            ['user_head_left']              = { file_name = 'user_head', args = { location_index = USER_LOCATION_LEFT,   x = 50,   y = 480, chat_side = 'right' } },
            ['next_round_ready']            = { file_name = 'next_round_ready', args = { { x = 640, y = 250 }, { x = 950, y = 380 }, { x = 640, y = 520 }, { x = 300, y = 380 } } },
            ['free_game_second_confirmation'] = { file_name = 'free_game_second_confirmation', },           -- 申请解散包间的二次确认
            ['free_game_waiting']           = { file_name = 'free_game_waiting', },                         -- 解散包间的等待界面
            ['free_game_result']            = { file_name = 'free_game_result', },                          -- 解散包间结果确认界面
            ['final_settle_view']           = { file_name = 'final_settle_view', },                         -- 大结算界面
            ['block_result_effect']         = { file_name = 'block_result_effect', },                       -- 拦牌特效
            ['fast_out_card_effect']        = { file_name = 'fast_out_card_effect', args = { { x = 210, y = 205 }, { x = 1080, y = 480 }, { x = 820, y = 620 }, { x = 210, y = 480 } } },        -- 快速出牌
            ['out_card_guild']              = { file_name = 'out_card_guild', },            -- 滑动出牌引导
            ['out_card_guild_line']         = { file_name = 'out_card_guild_line', },       -- 滑出此线出牌
            ['out_card_tips']               = { file_name = 'out_card_tips', },
            ['round_settle']                = { file_name = 'quick_settle', args = { draw_sprite_file = 'mahjong/common/game_result_draw_4.png' } },     -- 小局结算界面
            ['warning_tips']                = { file_name = 'warning_tips', args = { x = 640, y = 170 }, },
            ['game_sound']                  = { file_name = 'game_sound', },
            ['win_type_effect']             = { file_name = 'win_type_effect', },
            ['round_settle_big_score_self'] = { file_name = 'round_settle_big_score',  args = { location_index = USER_LOCATION_SELF,   x = 200,   y = 210, } },
            ['round_settle_big_score_right']= { file_name = 'round_settle_big_score',  args = { location_index = USER_LOCATION_RIGHT,  x = 1050,   y = 480, } },
            ['round_settle_big_score_facing']= { file_name = 'round_settle_big_score', args = { location_index = USER_LOCATION_FACING, x = 800,   y = 620, } },
            ['round_settle_big_score_left'] = { file_name = 'round_settle_big_score',  args = { location_index = USER_LOCATION_LEFT,   x = 200,   y = 480, } },
        }, scene_config.components or {}),
        sound_text_list = scene_config.sound_text_list or {
            { text ='你的牌打得太好了！', index = 1 },
            { text ='和你合作真是太愉快了！', index = 2 },
            { text ='还让不让我摸牌了！', index = 3 },
            { text ='打一个来碰呗！', index = 4 },
            { text ='快点吧，我等到花都谢了！', index = 5 },
            { text ='呵呵！', index = 6 },
            { text ='哎呀呀，一不小心就胡了呀！', index = 7 },
            { text ='你这样，以后没朋友！', index = 8 },
            { text ='我有一百办法胡你，而你却无可奈何。', index = 9 },
            { text ='来啊，互相伤害啊！', index = 10 },
        },
        emoji_type = scene_config.emoji_type or 'mahjong',
        has_ghost_card = scene_config.has_ghost_card,                                       -- 是否有鬼牌，这个决定了是否存在翻鬼牌这回事，影响的是打骰子到摸牌间的动画控制，必须要明确指定
        need_flop_anim = scene_config.need_flop_anim,                                       -- 是否需要翻鬼牌的动画，红中麻将，鬼牌是明确的，所以不需要动画
        ghost_card_name = scene_config.ghost_card_name,                                     -- 鬼牌的称谓，有些叫‘鬼牌’，有些叫‘混牌’等等
        ghost_subscript_file = scene_config.ghost_subscript_file or 'mahjong/common/mahjong_subscript_ghost.png',   -- 鬼牌使用的角标贴图
    })

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

    -- 防止重复进入，因为出牌是常事，而翻鬼牌是一次的
    self.is_first_time_flop_flag = true

    -- 在这里记录下来，是因为有一些麻将，在小局结算的时候，服务器没有下发
    -- 而有一些，服务器却下发了，真是淡淡的忧伤啊
    self.block_cards = { {}, {}, {}, {} }
end

function GameSceneMahjong:init()
    game_scene_base.init(self)

    -- game msg
    table.merge(self.game_msg_listeners, {
        [game_msg_ids.EVENT_GAME_NOTIFY_MAKER_INFO]                  = function(data) self:on_maker_info(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_DICE_INFO]                   = function(data) self:on_dice_info(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_CARD_INFO]                   = function(data) self:on_card_info(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_OUT_CARD]                    = function(data) self:on_out_card(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_GET_CARD]                    = function(data) self:on_get_card(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_BLOCK_INFO]                  = function(data) self:on_block_info(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_BLOCK_RESULT]                = function(data) self:on_block_result(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_NOTIFY_OUT_CARD]             = function(data) self:on_notify_out_card(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_NOTIFY_NOTIFY_WAIT_BLOCK]    = function(data) self:on_notify_wait_block(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_NOTIFY_GAME_RESULT]          = function(data) self:on_game_result(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_NOTIFY_TING]                 = function(data) self:on_notify_ting(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_NOTIFY_GAME_RESULT_OVER]     = function(data) self:on_game_over(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_NOTIFY_GAME_RESULT_ONE]      = function(data) self:on_single_game_record(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_FAST_OUT_INOF]               = function(data) self:on_fast_out_info(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_KING_CARD_INFO]              = function(data) self:on_ghost_card_data(data) end,
    })

    -- game actions
    table.merge(self.game_request_actions, {
        ['play_dice'] = function(server_index)               -- 打骰子
            self.game_impl:do_play_dice({m_chair_id = server_index - 1})
        end,
        ['discard_card'] = function(server_index, card_id, cancel_callback)   -- 出牌
            if self:is_ghost_card(card_id) then
                show_msg_box_1('提示', string.format('这是%s，您确认要打出去？', self.scene_config.ghost_card_name), function()
                    self.game_impl:do_out_card({m_chair_id = server_index - 1, m_card_value = card_id })
                end, cancel_callback)
            else
                self.game_impl:do_out_card({m_chair_id = server_index - 1, m_card_value = card_id })
            end
        end,
        ['block'] = function(op_type, card_value, is_out, block_index)      -- 拦牌
            self.game_impl:do_block_opreate({
                m_chair_id = self.my_server_index - 1,
                m_opreate_type = op_type,
                m_card_value = card_value,
                m_out = is_out,
                m_block_index = block_index,
            })
        end,
        ['swap_wall_card'] = function()     -- 设置牌墙值
            self.game_impl:do_swap_wall_card({
                m_card_value = '',
            })
        end,
    })
end

function GameSceneMahjong:initViews()
    game_scene_base.initViews(self)

    local frame_bg_1 = cc.Sprite:create('mahjong/mahjong_tablecloth_frame.png')
    local size = frame_bg_1:getContentSize()

    frame_bg_1:setPosition(size.width * 0.5, display.height * 0.5)
    frame_bg_1:setScale(1.2549)
    self:addChild(frame_bg_1, 1)

    local frame_bg_2 = cc.Sprite:create('mahjong/mahjong_tablecloth_frame.png')
    frame_bg_2:setPosition(display.width - size.width * 0.5, display.height * 0.5)
    frame_bg_2:setScale(1.2549)
    frame_bg_2:setFlippedX(true)
    self:addChild(frame_bg_2, 1)
end

function GameSceneMahjong:restart()
    game_scene_base.restart(self)

    self.fake_card_ids = {}
    self.really_card_ids = {}
    self.block_cards = { {}, {}, {}, {} }

    self:requestAction('user_agree', true)
end

-- mahjong config -------------------------------------------------------------------------------------------------
function GameSceneMahjong:loadMahjongConfig()
    -- default 4 people config
    -- self.mahjong_config = clone(require 'app.platform.game.game_common.mahjong_config_4_people')
end

-- helper functions --------------------------------------------------------------------------------------------------
function GameSceneMahjong:convertStationToLocalIndex(server_index)
    -- local index coordinate, my local index is allways No.1.
    --              3
    --              |
    --              |
    --      4 ------------- 2
    --              |
    --              |
    --              1
    local count = 4 -- self.mahjong_config.count or 4
    return (server_index + count - self.my_server_index) % count + 1
end


-------------------------------------------------------------------------------------------------------------------
function GameSceneMahjong:on_game_state(data)
    game_scene_base.on_game_state(self,data)
    -- 使用不一样的背景音乐
    if data.m_base_info.m_game_status == 6 then
        play_mahjong_background_music()
    else
        play_mahjong_waiting_music()        -- game_music.lua
    end
end
function GameSceneMahjong:on_reconn_game_state(data)
    self:on_reconn_dice_num(data)           -- 先确定骰子点数
    self:on_reconn_block_info(data)         -- 
    self:on_reconn_ting_info(data)          -- 有了听牌数据，在初始化手牌的时候，就可以自动带上箭头了
    self:on_reconn_lei_card(data)           -- 先有牌墙，再到鬼牌
    self:on_reconn_card(data)               -- 
    self:on_reconn_ghost_card(data)

    -- 重连回来，没有动画，直接赋值就好
    self.roll_dice_anim_end = true
    self.init_hand_card_ended = true
    self.draw_card_anim_end = true
    self.ghost_card_anim_end = true

    -- 断线回来后，这个值服务器没有加1
    self.cur_play_count = self.cur_play_count + 1
    self:fire('play_count', self.cur_play_count, self.total_play_count)
end

function GameSceneMahjong:on_reconn_dice_num(data)
    self:fire('roll_dice_end', self.banker_server_index, data.m_dice[1], data.m_dice[2])
end

function GameSceneMahjong:on_reconn_block_info(data)
    if data.m_cur_block_level ~= 0 then
        self:on_block_info({
            m_card_value = data.m_cur_check_card,
            m_block_info = data.m_block_info,
            m_block_level = data.m_cur_block_level,
            m_block_index = data.m_block_index,
            m_checked_id = data.m_cur_check_user,
            m_out = not data.m_bdraw_stats,
        })
    end
end

function GameSceneMahjong:on_reconn_ting_info(data)
    -- 自己手牌的听牌箭头
    if data.m_notify_ting then self:on_notify_ting(data.m_notify_ting) end

    -- 处于听牌状态，这个时候显示的听牌列表
    local card_list = {}
    for index, count in ipairs(data.m_ting_count) do
        if count > 0 then
            table.insert(card_list, {
                card_id = data.m_ting_list[index],
                card_count = count,
                fan_count = 0,
            })
        end
    end
    self:fire('reset_ting_card', card_list)
end

function GameSceneMahjong:on_reconn_lei_card(data)
    self:fire('reconn_lei_card', data.m_wall_count, data.m_gang_all_count)
end

function GameSceneMahjong:on_reconn_card(data)
    for i=1, 4 do
        local location_index = self.server_index_to_local_index[i]

        local user_info = data.user_info[i]

        -- hand card
        local card_list = user_info.m_hand_card
        local card_num = user_info.m_hand_card_count - (user_info.m_draw_card > 0 and 1 or 0)
        self:fire('reconn_hand_card', location_index, card_list, card_num)

        -- 
        if user_info.m_draw_card > 0 then
            self:fire('reconn_draw_card', location_index, user_info.m_draw_card)
        end

        -- block card
        for _, v in ipairs(user_info.block_info) do
            local block_type            = mahjong_block_type_config[v.m_block_type].get_block_type(v.m_block_sub_type)
            local show_card_list        = mahjong_block_type_config[v.m_block_type].get_show_card_list(v.m_block_data)
            local src_location_index    = mahjong_block_type_config[v.m_block_type].get_src_location_index(self, v.m_block_sub_type, v.m_blocked_user)
            local dest_card_list        = mahjong_block_type_config[v.m_block_type].get_dest_card_list(v.m_block_sub_type, v.m_block_data)
            self:fire('on_reconn_block_result', block_type, show_card_list, src_location_index, { 9 }, location_index, dest_card_list)
        end

        -- out card
        self:fire('on_reconn_out_card', location_index, user_info.m_out_card)
    end
end

function GameSceneMahjong:on_reconn_ghost_card(data)
end

function GameSceneMahjong:on_notify_ting(data)
    local ting_groups = {}
    for k, v in pairs(data.ting_list or {}) do
        local out_card_id = v[1]
        ting_groups[out_card_id] = { win_card_count = data.win_card_count[k] }

        local remain_card_count = data.ting_list_count[k]

        for kk, card_id in pairs(v) do
            if kk ~= 1 and card_id ~= 0 then
                table.insert(ting_groups[out_card_id], {
                    card_id = card_id,
                    card_count = remain_card_count[kk],
                    fan_count = 0,
                })
            end
        end
    end

    self:fire('ting_card_list', data.max_win_count, ting_groups)

    play_mahjong_ting_music()   -- game_music.lua
end

function GameSceneMahjong:on_game_over(data)
    self.all_record_info = data
end

function GameSceneMahjong:on_maker_info(data)
    self.banker_server_index = data.m_chair_id + 1
    self.cur_play_count = self.cur_play_count + 1
    self.game_state = 'game_start'

    self:fire('banker_server_index', self.banker_server_index)
    self:fire('play_count', self.cur_play_count, self.total_play_count)
    self:fire('game_state', self.game_state)

    play_mahjong_background_music()
end

function GameSceneMahjong:on_dice_info(data)
    self:fire('roll_dice', self.banker_server_index, data.m_dice[1], data.m_dice[2], function()
        self.roll_dice_anim_end = true

        self:fire('roll_dice_end', self.banker_server_index, data.m_dice[1], data.m_dice[2])

        self:try_to_init_hand_card()
    end)
end

function GameSceneMahjong:on_card_info(data)
    -- 自己的手牌
    local card_list = data.m_hand_card[self.my_server_index]
    if card_list[#card_list] == 0 then  -- 移除最后面的一个 0，因为服务器发送了14张牌过来，其中有一个是 0，但这个时候这个 0 是没有用的
        table.remove(card_list, #card_list)
    end

    -- 
    self.hand_card_data = {}
    for server_index=1, 4 do
        local location_index = self:convertStationToLocalIndex(server_index)
        local card_list = (server_index == self.my_server_index and card_list or {})
        local card_num = data.m_card_count[server_index]

        self.hand_card_data[server_index] = {
            location_index = location_index,
            card_list = card_list,
            card_num = card_num,
        }
    end

    -- 
    self:try_to_init_hand_card()
end

function GameSceneMahjong:on_out_card(data)
    local location_index = self:convertStationToLocalIndex(data.m_chair_id + 1)
    self:fire('out_card', location_index, data.m_card_value)
end

function GameSceneMahjong:on_get_card(data)
    self.draw_card_data = data

    -- 摸牌
    self:try_to_draw_card()
end

function GameSceneMahjong:on_block_info(data)
    self.on_block_info_data = data

    self:try_to_block_info()
end

function GameSceneMahjong:on_block_result(data)
    -- data = {
    --     "m_block_subtype" = 0
    --     "m_card_value" = {
    --         1 = 24
    --         2 = 24
    --         3 = 24
    --         4 = 0
    --     }
    --     "m_chair_id"      = 0
    --     "m_checked_id"    = 1
    --     "m_opreate_type"  = 2
    -- }

    local block_type = mahjong_block_type_config[data.m_opreate_type].get_block_type(data.m_block_subtype)
    local show_card_list = mahjong_block_type_config[data.m_opreate_type].get_show_card_list(data.m_card_value)
    local src_location_index = mahjong_block_type_config[data.m_opreate_type].get_src_location_index(self, data.m_block_subtype, data.m_checked_id)
    local dest_location_index = self:convertStationToLocalIndex(data.m_chair_id + 1)
    local dest_card_list = mahjong_block_type_config[data.m_opreate_type].get_dest_card_list(data.m_block_subtype, data.m_card_value)
    self:fire('on_block_result', block_type, show_card_list, src_location_index, { 9 }, dest_location_index, dest_card_list)

    local server_index = data.m_chair_id + 1
    table.insert(self.block_cards[server_index], show_card_list)
end

function GameSceneMahjong:on_notify_out_card(data)
    self.on_notify_out_card_data = data

    self:try_to_out_card()
end

function GameSceneMahjong:on_notify_wait_block(data)
    -- data = {
    --     "m_block_level" = {
    --         1 = 0
    --         2 = 0
    --         3 = 0
    --         4 = 0
    --     },
    --     "m_card_value"  = 33,
    --     "m_checked_id"  = 1,
    --     "m_out"         = true,
    -- }

    if data.m_checked_id + 1 == self.my_server_index then
        self:fire('block_wait')
    end
end

function GameSceneMahjong:get_win_effect_type(data)
    return data.m_win_type == 0 and 'draw' or 'win'
end

function GameSceneMahjong:on_game_result(data)
    local win_server_index = nil
    for server_index=1, 4 do
        if data.m_win[server_index] then
            win_server_index = server_index

            break
        end
    end

    -- 
    self:fire('on_block_result', win_server_index and 'win' or 'draw', {}, nil, {}, self.server_index_to_local_index[win_server_index], {})

    -- 亮牌咯
    for server_index=1, 4 do
        local card_list = {}
        for _, card_id in ipairs(data.m_hand_card[server_index]) do
            if card_id ~= 0 then
                table.insert(card_list, card_id)
            end
        end

        local win_card = data.m_win[server_index] and data.m_win_card or nil

        local location_index = self.server_index_to_local_index[server_index]
        self:fire('liang_card', location_index, card_list, #card_list, win_card)

        --
        self:fire('update_user_score', server_index, data.m_win_score[server_index] or 0)
    end

    -- 
    if win_server_index then
        local win_effect_type = self:get_win_effect_type(data)
        self:fire('win_effect', win_effect_type, self.server_index_to_local_index[win_server_index])
    end

    -- 
    self.game_state = 'round_end'
    self:fire('game_state', self.game_state)

    -- 小局结算的时候，要重置这个值，以便下一局翻鬼牌
    self.is_first_time_flop_flag = true

    -- 
    self:schedule_once_time(1.5, function()
        self:fire('round_settle', data)
    end)
end

function GameSceneMahjong:on_fast_out_info(data)
    -- data.m_chair_id,
    -- data.m_add_fast_count,
    -- data.m_fast_all_count,

    local server_index = data.m_chair_id + 1
    self:fire('on_fast_out', server_index, data.m_fast_all_count)
end

function GameSceneMahjong:on_single_game_record(data)
    table.insert(self.game_record, 1, data)
end

-- return url, title, text
function GameSceneMahjong:getInviteInfo()
    local room_id = self:getRoomID()

    -- url
    local value = g_json.encode({
        game_id = self.game_id,
        desk_no = room_id,
        user_id = self.self_user_id,
    })

    local url_ip = clientmain:get_instance():get_config_mgr():get_share_url()
    local url = string.format("http://%s/dcmjapi/wechat.php?param=%s", tostring(url_ip), value)

    -- title text
    local title_text = self.scene_config.game_name
    title_text = string.format("%s【%s】包间(%s局)", title_text, tostring(room_id), tostring(self.game_rule.m_room_card * 4))

    -- 
    local user_count = self:getUserCount()

    -- join text
    local join_text = ''
    if user_count == 2 then
        join_text = '现在"2缺2"啦,小伙伴快来啊～\n'
    elseif user_count == 3 then
        join_text = '现在"3缺1"啦,小伙伴快来啊～\n'
    else   
        join_text = '【点击进入房间】\n'
    end

    local rule_config = self:getGameRuleConfig()
    for _, v in ipairs(rule_config.sections) do
        join_text = join_text .. v.section_desc .. '\n'
    end

    -- 
    return url, title_text, join_text
end

function GameSceneMahjong:on_ghost_card_data(data)
    self:on_ghost_card({ data.m_card }, { data.m_kingcard[1] }, data.m_king_dice[1], data.m_king_dice[2])
end

function GameSceneMahjong:on_ghost_card(fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
    self.init_ghost_card_data = {
        fake_card_ids = fake_card_ids,
        really_card_ids = really_card_ids,
        dice_num_1 = dice_num_1,
        dice_num_2 = dice_num_2,
    }

    self:try_to_flop_ghost_card()
end

function GameSceneMahjong:is_ghost_card(card_id)
    for _, id in ipairs(self.really_card_ids or {}) do
        if id == card_id then return true end
    end
end

function GameSceneMahjong:sort_card_by_id(card_id_1, card_id_2)
    local is_ghost_1 = self:is_ghost_card(card_id_1)
    local is_ghost_2 = self:is_ghost_card(card_id_2)

    if is_ghost_1 and is_ghost_2 then return card_id_1 < card_id_2 end

    if is_ghost_1 then return true end
    if is_ghost_2 then return false end

    return card_id_1 < card_id_2
end

function GameSceneMahjong:createGhostSubscript(location_index, area)
    local ghost_subscript_config = ALL_CARD_CONFIG[location_index][area].ghost_subscript

    local sprite = cc.Sprite:create(self.scene_config.ghost_subscript_file)
    sprite:setPosition(ghost_subscript_config.x, ghost_subscript_config.y)
    if ghost_subscript_config.scale then sprite:setScale(ghost_subscript_config.scale) end
    if ghost_subscript_config.rotation then sprite:setRotation(ghost_subscript_config.rotation) end

    return sprite
end

function GameSceneMahjong:createWinSubscript(location_index, area)
    local ghost_subscript_config = ALL_CARD_CONFIG[location_index][area].ghost_subscript

    local sprite = cc.Sprite:createWithSpriteFrameName('mahjong_subscript_win.png')
    sprite:setPosition(ghost_subscript_config.x, ghost_subscript_config.y)
    if ghost_subscript_config.scale then sprite:setScale(ghost_subscript_config.scale) end
    if ghost_subscript_config.rotation then sprite:setRotation(ghost_subscript_config.rotation) end

    return sprite
end

function GameSceneMahjong:getFinalSettleMoreCount(server_index, result_info) return {} end

function GameSceneMahjong:try_to_init_hand_card()
    -- 打骰子动画结束，以及手牌数据来了，就可以初始化手牌了
    if self.roll_dice_anim_end and self.hand_card_data then
        for _, v in ipairs(self.hand_card_data) do
            self:fire('init_hand_card', v.location_index, v.card_list, v.card_num, function()
                if v.location_index == self.my_local_index then    -- 自己的手牌初始化完了
                    self.hand_card_data = nil
                    self.init_hand_card_ended = true

                    self:fire('init_hand_card_ended', self.location_index)

                    -- 摸牌
                    self:try_to_draw_card()
                end
            end)
        end
    end
end

function GameSceneMahjong:try_to_draw_card()
    if self.init_hand_card_ended and self.draw_card_data then
        self.draw_card_anim_end = false

        local location_index = self.server_index_to_local_index[self.draw_card_data.m_chair_id + 1]
        self:fire('draw_card', location_index, self.draw_card_data.m_card_value, self.draw_card_data.m_bgang, function()
            self.draw_card_data = nil
            self.draw_card_anim_end = true

            if self.is_first_time_flop_flag then
                self.is_first_time_flop_flag = false
                self:try_to_flop_ghost_card()
            end
        end)
    end
end

function GameSceneMahjong:try_to_flop_ghost_card()
    if not self.draw_card_anim_end then return end

    local function __ghost_card_confirm__(fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
        self.fake_card_ids = fake_card_ids
        self.really_card_ids = really_card_ids

        self.init_ghost_card_data = nil
        self.ghost_card_anim_end = true

        self:fire('ghost_card_confirm', fake_card_ids, really_card_ids, dice_num_1, dice_num_2)

        -- 可能有 block data
        self:try_to_block_info()
        self:try_to_out_card()
    end

    -- 没有鬼牌的话，直接算翻完
    if not self.scene_config.has_ghost_card then return __ghost_card_confirm__({}, {}, 1, 1) end

    -- 鬼牌消息已经来了，就翻吧
    if self.init_ghost_card_data then
        local fake_card_ids = self.init_ghost_card_data.fake_card_ids
        local really_card_ids = self.init_ghost_card_data.really_card_ids
        local dice_num_1 = self.init_ghost_card_data.dice_num_1
        local dice_num_2 = self.init_ghost_card_data.dice_num_2

        self.fake_card_ids = fake_card_ids
        self.really_card_ids = really_card_ids

        if self.scene_config.need_flop_anim then
            self:fire('flop_ghost_card', fake_card_ids, really_card_ids, dice_num_1, dice_num_2, function()
                __ghost_card_confirm__(fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
            end)
        else
            __ghost_card_confirm__(fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
        end
    end
end

function GameSceneMahjong:try_to_out_card()
    if self.on_notify_out_card_data and self.ghost_card_anim_end then
        self.user_turn_server_index = self.on_notify_out_card_data.m_chair_id + 1
        self:fire('user_turn', self.user_turn_server_index)

        self.on_notify_out_card_data = nil
    end
end

function GameSceneMahjong:try_to_block_info()
    if self.on_block_info_data and self.ghost_card_anim_end then
        local block_info = self.on_block_info_data.m_block_info
        local block_level = self.on_block_info_data.m_block_level
        local card_id = self.on_block_info_data.m_card_value
        local is_out = self.on_block_info_data.m_out
        local block_index = self.on_block_info_data.m_block_index

        self:fire('on_block', block_info, block_level, card_id, is_out, block_index)

        self.on_block_info_data = nil
    end
end

return GameSceneMahjong
