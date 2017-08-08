-- ./app/platform/game/game_common/game_scene_mahjong_replay.lua

require 'app.platform.game.game_common.game_msg_ids'

local cjson = require 'cjson'

local clientmain = import('...room.clientmain')
local basic_def = import('...room.module.basicnotifydef')

-- 
local game_scene_mahjong = require('app.platform.game.game_common.game_scene_mahjong')
local GameSceneMahjongReplay = class('GameSceneMahjongReplay', game_scene_mahjong)
function GameSceneMahjongReplay:ctor(game_id, self_server_index, scene_config)
    scene_config.components = table.merge({
        ['replay_ctrl']                 = { file_name = 'replay_ctrl' },

        ['hand_card_self']              = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_SELF,   is_back = false, area = CARD_AREA.TAN } },    -- 手牌
        ['hand_card_right']             = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_RIGHT,  is_back = false } },
        ['hand_card_facing']            = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_FACING, is_back = false } },
        ['hand_card_left']              = { file_name = 'hand_card',    args = { location_index = USER_LOCATION_LEFT,   is_back = false } },
        ['round_settle']                = { file_name = 'quick_settle', args = { draw_sprite_file = 'mahjong/common/game_result_draw_4.png' } },     -- 小局结算界面

        ['game_waiting_view']           = { },                                                     -- 等待玩家界面
        ['normal_chat']                 = { },
        ['voice_chat']                  = { },
        ['out_card_guild']              = { },       -- 滑动出牌引导
        ['out_card_guild_line']         = { },       -- 滑出此线出牌

        ['game_sound']                  = { },
    }, scene_config.components)

    game_scene_mahjong.ctor(self, game_id, nil, scene_config)
    self.scene_config.replay_file = scene_config.replay_file

    self.init_listen_msg_ids = {}

    -- 以谁的视角来看
    self.my_server_index = self_server_index
    self.my_local_index = self:convertStationToLocalIndex(self.my_server_index)
    print('self.my_server_index : ' .. tostring(self.my_server_index))

    -- 自己坐下后，相对位置就是固定的，这个时候就可以初始化了
    for i=1, 4 do
        local local_index = self:convertStationToLocalIndex(i)
        self.server_index_to_local_index[i] = local_index
        self.local_index_to_server_index[local_index] = i
    end

    self:fire('my_server_index', self.my_server_index)

    -- 
    self.user_id_to_server_index = {}
    self.user_info_action_callback = nil

    -- 
    self.is_pause = false
    self.is_replay = true
    self.action_interval = 1

    -- 还原点
    self.restore_points = {}

    -- 

    -- 
    self.action_type_to_preset_name = {}
    self.skip_action_preset_name = { 'notify_out_card', 'notify_user_block', 'user_block' }

    -- 预设的麻将的一些处理方法
    self.preset_action_process_func = {
        ['banker_server_index'] = function(action_data, callback)
            self.banker_server_index = action_data.data[1] + 1
            self:fire('banker_server_index', self.banker_server_index)

            self.game_state = 'game_start'
            self:fire('game_state', self.game_state)

            self:schedule_once_time(1, callback)
        end,
        ['dice_info'] = function(action_data, callback)
            self:on_dice_info({ m_dice = action_data.data, })

            self:schedule_once_time(3, callback)
        end,
        ['init_hand_card'] = function(action_data, callback)
            local hand_card_data = {
                m_hand_card = {{},{},{},{}},
                m_card_count = {},
            }

            for i=1, 4 do
                hand_card_data.m_hand_card[i] = action_data.data[i]
                hand_card_data.m_card_count[i] = (action_data.data[i] and #action_data.data[i] or 0)
            end

            -- 
            self.hand_card_data = {}
            for server_index=1, 4 do
                local location_index = self:convertStationToLocalIndex(server_index)
                local card_list = hand_card_data.m_hand_card[server_index]
                local card_num = hand_card_data.m_card_count[server_index]

                self.hand_card_data[server_index] = {
                    location_index = location_index,
                    card_list = card_list,
                    card_num = card_num,
                }
            end

            -- 
            self:try_to_init_hand_card()

            -- 
            self:schedule_once_time(2, callback)
        end,
        ['lei_card'] = function(action_data, callback)
            self:fire('show_card', action_data.data)

            self:schedule_once_time(1, callback)
        end,
        ['notify_out_card'] = function(action_data, callback)
            callback()
        end,
        ['user_draw_card'] = function(action_data, callback)
            if self.draw_card_action_flag then
                self:addRestorePoint()
            end

            -- 
            self:on_get_card({
                m_chair_id = action_data.data[1],
                m_card_value = action_data.data[2],
                m_bgang = (action_data.data[3] == 1 and true or false),
            })

            -- 摸牌后，马上通知出牌，省掉了 action_type : 0x05 那一步
            self:on_notify_out_card({
                m_chair_id = action_data.data[1],
            })

            -- 第一次摸牌后，重播才算开始
            if not self.draw_card_action_flag then
                self.draw_card_action_flag = true

                self.is_pause = true
                self:fire('replay_start', self.is_pause)
            end

            -- 
            self:schedule_once_time(1, callback)
        end,
        ['notify_user_block'] = function(action_data, callback)
            callback()
        end,
        ['user_block'] = function(action_data, callback)
            callback()
        end,
        ['block_result'] = function(action_data, callback)
            self:addRestorePoint()

            -- 
            self:on_block_result({
                m_chair_id = action_data.data[1],
                m_opreate_type = action_data.data[2],
                m_card_value = action_data.data[3],
                m_checked_id = action_data.data[4],
                m_block_subtype = action_data.data[5],
            })

            self:schedule_once_time(1, callback)
        end,
        ['out_card'] = function(action_data, callback)
            self:addRestorePoint()

            -- 
            self:on_out_card({
                m_chair_id = action_data.data[1],
                m_card_value = action_data.data[2],
            })

            self:schedule_once_time(1, callback)
        end,
        ['round_settle'] = function(action_data, callback)
            self:on_game_result({
                m_win_type = action_data.data[1],
                m_win = action_data.data[2],
                m_hand_card = action_data.data[3],
                m_win_card = action_data.data[4],
                m_dianpao_id = action_data.data[5],
                m_gang_score = action_data.data[6],
                m_fan_score = action_data.data[7],
                m_luck_card = action_data.data[8],
                m_total_score = action_data.data[9],
                m_all_king = action_data.data[10],
                m_fast_count = action_data.data[11],
                m_out_count = action_data.data[12],
                m_reward_gift = action_data.data[13],
                m_user_luck_count = action_data.data[14],
                m_win_score = action_data.data[15],
                m_luck_score = action_data.data[16],
                m_mgang_count = action_data.data[17],
                m_agang_count = action_data.data[18],
                m_bgang_count = action_data.data[19],
                m_fgang_count = action_data.data[20],
            })

            self:schedule_once_time(1, callback)
        end,
        ['user_info'] = function(action_data, callback)
            --callback()

            --
            self.user_info_action_callback = callback

            for i=1, 4 do
                local user_id = action_data.data[i]
                if user_id > 0 then
                    self.user_id_to_server_index[user_id] = i,
                    clientmain:get_instance():get_user_mgr():request_player_info(user_id)
                end
            end
            --]]
        end,
        ['bu_hua'] = function(action_data, callback)
            callback()
        end,
        ['notify_ting_card'] = function(action_data, callback)
            callback()
        end,
        ['game_rule'] = function(action_data, callback)
            self.game_rule = {  -- 这个是红中的
                m_room_card = action_data.data[1],
                m_hu_qxd = action_data.data[2],
                m_hongaward_ma = action_data.data[3],
                m_award_ma = action_data.data[4],
                m_luck_mode = action_data.data[5],
                m_all_ma = action_data.data[6], 
            }

            self:fire('update_game_rule')

            callback()
        end,
        ['ghost_card'] = function(action_data, callback)
            self:on_ghost_card({ action_data.data[1] }, action_data.data[2], 1, 1)

            self:schedule_once_time(2, callback)
        end,
        ['room_id'] = function(action_data, callback)
            self:fire('room_id', action_data.data[1])

            callback()
        end,
    }

    self:initReplayActionType()
end

function GameSceneMahjongReplay:initReplayActionType()
end

function GameSceneMahjongReplay:getActionProcessFunc(action_type)
    local preset_name = self.action_type_to_preset_name[action_type]
    return self.preset_action_process_func[preset_name]
end

function GameSceneMahjongReplay:try_to_request_game_state()
    if not self.start_flag then
        self.start_flag = true

        local file = io.open(self.scene_config.replay_file, 'r')
        if not file then return show_msg_box_2('', '录像文件已损坏，无法播放！', function() self:onExitGame() end) end

        self.replay_actions = {}
        for line in file:lines() do
            if line and #line > 4 then
                local action_data = cjson.decode(line)
                table.insert(self.replay_actions, action_data)
            end
        end

        io.close(file)

        -- 开始
        self.next_action_index = 1
        self:next_action()
    end
end

function GameSceneMahjongReplay:get_next_action_data()
    local action_data = self.replay_actions[self.next_action_index]
    self.next_action_index = self.next_action_index + 1

    -- 
    if action_data then
        local preset_name = self.action_type_to_preset_name[action_data.type]
        print('preset_name : ' .. tostring(preset_name))
        if preset_name and table.hasValue(self.skip_action_preset_name, preset_name) then
            return self:get_next_action_data()
        end
    end

    return action_data
end

function GameSceneMahjongReplay:next_action(is_forced)
    if not is_forced and self.is_pause then return end

    -- 
    local action_data = self:get_next_action_data()
    if action_data then
        dump(action_data)
        local process_func = self:getActionProcessFunc(action_data.type)
        if process_func then
            process_func(action_data, function() self:next_action() end)
        else
            print('action_data.type : ' .. tostring(action_data.type))
            print(debug.traceback())
        end
    else
        print(debug.traceback())
    end
end

function GameSceneMahjongReplay:addRestorePoint()
    self.cur_rp = {
        next_index = self.next_action_index - 1,
        rp_list = {},
    }

    table.insert(self.restore_points, self.cur_rp)
end

function GameSceneMahjongReplay:pushRestorePoint(rp_data, rp_cb)
    if not self.cur_rp then return end

    table.insert(self.cur_rp.rp_list, { rp_data = rp_data, rp_cb = rp_cb })
end

function GameSceneMahjongReplay:goBack()
    if #self.restore_points == 0 then return false end

    -- 
    local v = self.restore_points[#self.restore_points]
    self.restore_points[#self.restore_points] = nil

    -- 
    self.next_action_index = v.next_index
    for _, v in ipairs(v.rp_list) do
        v.rp_cb(v.rp_data)
    end
end

function GameSceneMahjongReplay:moveForward()
    self:next_action(true)
end

function GameSceneMahjongReplay:play()
    self.is_pause = false

    self:next_action()
end

function GameSceneMahjongReplay:pause()
    self.is_pause = true
end

---------------------------------------------------------------------------------------------------
function GameSceneMahjongReplay:onUserEvent(event)
    game_scene_mahjong.onUserEvent(event)

    -- 
    if not event or not event.args then return end
    if basic_def.NOTIFY_USER_EVENT ~= event.id then return end
    if basic_def.NOTIFY_USER_EVENT_UPDATE_PLAYER_INFO ~= event.args.event_id then return end
    if event.args.event_data.ret ~= 0 then return end

    local data = event.args.event_data.data
    if data and data ~= '' then
        local user_id = tonumber(data.uid)

        local server_index = self.user_id_to_server_index[user_id]
        self.all_user_info[server_index] = {
            m_dwUserID = user_id,
            m_bLogoID = tonumber(data.icon_id),
            m_headurl = data.headurl,
            m_nickName = data.nickname,
            is_valid = true,
        }

        self:fire('on_user_sit', server_index, user_id)
        self:fire('on_user_offline', server_index, false)

        -- 
        self.user_id_to_server_index[user_id] = nil
        if table.len(self.user_id_to_server_index) == 0 then
            self.user_info_action_callback()
        end
    end
end

-- 
return GameSceneMahjongReplay
