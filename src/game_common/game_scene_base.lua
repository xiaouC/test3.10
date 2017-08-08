-- ./app/platform/game/game_common/game_scene_base.lua
local CURRENT_MODULE_NAME = ...

require 'app.platform.common.common'
require 'app.platform.common.signal'

local clientmain = import('...room.clientmain')
local basic_def = import('...room.module.basicnotifydef')

-- The scene's config looks like this:
-- self.scene_config = {
--      max_player_count = 4,
--     background = 'mahjong/mahjong_scene_bg.jpg',             -- 背景
--     game_name = '',
--     preload_plist = {                                        -- 需要预加载的 plist
--     },
--     listen_msg_ids = {},                                     -- 当这些 msg 回来后，才初始化与游戏相关的界面
--     components = {},                                         -- 组件
--     sound_text_list = {},
--     emoji_type = 'mahjong',
--     game_type = 'mahjong',
-- }

local model_base = require 'app.platform.common.model_base'

local GameSceneBase = class('GameSceneBase', model_base)
function GameSceneBase:ctor(game_id, self_user_id, scene_config)
    self.game_id = game_id
    self.self_user_id = self_user_id

    -- 
    self.all_user_info = {}
    self.local_index_to_server_index = {}
    self.server_index_to_local_index = {}

    self.my_server_index = nil                   -- 自己的 station
    self.my_local_index =  nil
    self.banker_server_index = nil               -- 庄家的 station

    -- scene resource config
    self.scene_config = scene_config
    self.scene_config.max_player_count = scene_config.max_player_count or 4
    table.merge_append(self.scene_config.preload_plist, { 'game_common_res/game_common.plist' })
    self.scene_config.components = table.merge({
        ['net_work_reconn']             = { file_name = 'net_work_reconn', },       -- 网络重连
        ['game_waiting_view']           = { file_name = 'game_waiting_view', args = { min_count = 4 } },                                                     -- 等待玩家界面
        ['kick_out']                    = { file_name = 'kick_out', },                                                              -- 被踢的提示界面
        ['normal_chat']                 = { file_name = 'normal_chat', args = { x = 1230, y = 335, }, },
        ['voice_chat']                  = { file_name = 'voice_chat', args = { x = 1230, y = 235 }, },            -- 语音聊天
        ['user_detail']                 = { file_name = 'user_detail', },
        ['ip_warning']                  = { file_name = 'ip_warning', },
        ['battery_net_state']           = { file_name = 'battery_net_state', },
    }, self.scene_config.components)

    -- 初始化与游戏相关的界面需要监听的 msg
    self.init_listen_msg_ids = {
        [game_msg_ids.EVENT_GAME_NOTIFY_USER_SIT] = { cur_count = 0, total_count = 1, }         -- 用户坐下
    }
    for id, count in ipairs(self.scene_config.listen_msg_ids or {}) do
        self.init_listen_msg_ids[id] = {
            cur_count = 0,            -- 已经返回的计数
            total_count = count,      -- 需要返回的总数
        }
    end

    -- clear callback: 有时候，不能简单的通过 self:clear 来执行清理的话，可以通过注册一个回调来执行清理
    -- clear callback 将被优先执行，最后才执行 self:clear
    -- 在多个 clear callback 里面，先添加进来的，会先执行
    self.cleanup_callback = {}

    -- listen user event
    self.user_event_listeners = {}

    -- helper functions
    self.get_user_info_by_user_id = nil

    -- game record
    self.game_record = {}

    -----------------------------------------------------------------------------------------------------------
    -- listen game attributes
    -- 这个只有在对应的属性发生变化的时候才会 fire
    self.game_attributes = {}
    self.game_attribute_listeners = {}

    -- 这个有没有改变都会 fire
    self.game_signal_listeners = {}

    -- init listen game msg
    self.game_msg_listeners = {}

    -- init request action
    self.game_request_actions = {}

    -- game error actions
    self.listen_game_error_actions = {}

    -- 组件
    self.all_components = {}

    -- 
    model_base.ctor(self)
end

function GameSceneBase:init()
    self:initViews()

    --[[
    --clientmain:get_instance():get_im_mgr():get_event_mgr():BsAddNotifyEvent(basic_def.NOTIFY_IM_EVENT,handler(self,self.onImEvent))
    clientmain:get_instance():get_voice_mgr():get_event_mgr():BsAddNotifyEvent(basic_def.NOTIFY_VOICE_EVENT, function(event)
    end)
    clientmain:get_instance():get_push_mgr():get_listener_mgr():BsAddEventListener(basic_def.NOTIFY_PUSH_EVENT,self, function(event)
    end)
    --]]

    -- 
    clientmain:get_instance():get_user_mgr():get_event_mgr():BsAddNotifyEvent(basic_def.NOTIFY_USER_EVENT, function(event) self:onUserEvent(event) end)

    -- 注册需要监听的错误
    if self.game_impl then
        self.listen_game_error_actions[self.game_impl:get_room_module().AID_USER_SIT_ERROR] = function(hcode, msg)
            new_hide_loading()

            -- 
            local error_config = {
                [4006] = function() self:fire('on_kick_out') end,    -- 被踢
                [4007] = function() self:fire('user_free_result', nil, nil, true) end,    -- 解散
                [4009] = function() self:fire('user_free_result', nil, nil, true) end,    -- 解散
            }

            local err_func = error_config[hcode]
            if err_func then return err_func() end

            -- 其他错误暂时先直接返回大厅
            self:onExitGame() 
        end

        -- 错误处理函数
        self.super_game_action = self.game_impl.game_action
        self.game_impl.game_action = function(game_impl_self, aid, hcode, buf, len, msg)
            if self.listen_game_error_actions then
                local error_action_func = self.listen_game_error_actions[aid]
                if error_action_func then return error_action_func(hcode, msg) end
            end

            if self.super_game_action then self.super_game_action(game_impl_self, aid, hcode, buf, len, msg) end
        end
    end

    -- game msg
    table.merge(self.game_msg_listeners, {
        [game_msg_ids.EVENT_GAME_NOTIFY_GAME_STATE]                  = function(data) self:on_game_state(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_FORCE_LEAVE]                 = function(data) self:on_force_leave(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_USER_SIT]                    = function(data) self:on_user_sit_desk(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_USER_UP]                     = function(data) self:on_user_up_desk(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_USER_CUT]                    = function(data) self:on_user_cut(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_USER_READY]                  = function(data) self:on_user_ready(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_NOTIFY_GAME_CHAT_MSG]        = function(data) self:on_game_chat_msg(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_USER_FREE_OPERATE]           = function(data) self:on_user_free_operate(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_USER_FREE_RESULT]            = function(data) self:on_user_free_result(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_USER_COME]                   = function(data) self:on_user_sit_desk(data) end,
        [game_msg_ids.EVENT_GAME_NOTIFY_GPS_RESULT]                  = function(data) self:on_gps_result(data) end,
    })

    -- 
    table.merge(self.game_request_actions, {
        ['myself_info'] = function() self.game_impl:do_get_self_info() end,                         -- 请求自己的信息
        ['user_info'] = function(user_id)
            return self.get_user_info_by_user_id(user_id)
            --self.game_impl:do_get_user_info_by_id(user_id)
        end,       -- 请求玩家的信息
        ['myself_station'] = function() self.game_impl:do_get_self_desk_station() end,              -- 请求自己的位置
        ['user_agree'] = function(agree)
            if self.game_state == 'waiting' then
                self.game_impl:do_request_user_agree(agree)
            else
                self.game_impl:do_user_agree({
                    userid = self.self_user_id,
                    chair_id = self.my_server_index - 1,
                    bagree = agree,
                })
            end
        end,
        ['game_state'] = function() self.game_manager:get_game_room_mgr():request_game_station_ext() end,
        ['kick_out'] = function(user_id, server_index) self.game_impl:do_force_user_leave(user_id, server_index - 1) end,
        ['ip_addr'] = function(user_id)         -- 请求 ip
            clientmain:get_instance():get_user_mgr():request_user_ip(user_id)
        end,
        ['gps_data'] = function()
            clientmain:get_instance():get_sdk_mgr():do_lbs_action(function(longitude, latitude, province, city)
                if self.my_server_index then
                    local user_id = clientmain:get_instance():get_user_mgr():get_user_info().m_uid
                    clientmain:get_instance():get_game_manager():get_game_room_mgr():send_gps_info(user_id, self.my_server_index - 1, longitude, latitude, province, city)
                end
            end)
            --clientmain:get_instance():get_game_manager():get_game_room_mgr():send_gps_info(self.self_user_id, 1, 113.95185, 22.541185, 'guangdong', 'shenzhen')
        end,
        ['apply_game_info'] = function()
            self.game_impl:do_user_apply_game_info({
                m_user_id = '',
                m_chair_id = '',
            })
        end,
        ['apply_game_config'] = function()
            self.game_impl:do_get_game_config({
                m_chair_id = '',
            })
        end,
        ['free_game'] = function(is_argee)                  -- 请求解散包间，是否同意解散包间，都是用这个
            self.game_impl:do_user_free_game({
                m_chair_id = self.my_server_index - 1,
                m_free = is_argee,
                m_user_id = self.self_user_id,
            })
        end,
    })
end

-------------------------------------------------------------------------------------------------------------------

function GameSceneBase:reset_user_ready(data)
    local is_all_ready = true
    for i=1, 4 do
        self.is_user_ready[i] = data.m_user_ready[i]
        if not data.m_user_ready[i] then
            is_all_ready = false
        end
    end

    -- 不是游戏中掉线连上来，而且局数不是0，那么就代表小局结算的时候掉线了
    -- 这个时候，就需要有个地方让玩家继续游戏
    if data.m_base_info.m_cur_play_count > 0 then
        if not data.m_user_ready[data.m_base_info.m_my_station+1] then
            self:fire('reconn_no_ready')
        end
    end
    return is_all_ready
end

function GameSceneBase:init_user_ready(data)
    -- 
    self.is_user_ready = {}

    local is_all_ready = true

    -- 在断线重连的时候，m_user_ready = nil
    if data.m_base_info.m_game_status ~= 6 then
        is_all_ready = self:reset_user_ready(data)
    end

    -- 如果大家都准备好了，那就证明游戏正在进行中
    self.game_state = ''
    if is_all_ready then
        self.game_state = 'playing'
    else
        -- 如果有人没有准备好，并且一局都没有打过的话，那就代表处于等待玩家
        -- 如果已经打过了，那就处于小局结算，这个时候就要等待大家准备好，然后开始下一局
        if data.m_base_info.m_cur_play_count == 0 then
            self.game_state = 'waiting'
        else
            self.game_state = 'round_end'
        end
    end

   
end

function GameSceneBase:on_game_state(data)
    new_hide_loading()

    -- 
    self.game_rule = data.m_base_info.m_game_config

    
    --self.m_total_play_count = data.m_base_info.m_total_play_count
    local max_player_count = self.scene_config.max_player_count
    -- 先赋值，后 fire
    -- 先缓存 user info，才 fire
    for server_index=1, max_player_count do
        local user_id = data.m_base_info.m_user_id[server_index]
        if user_id ~= 0 then
            self.all_user_info[server_index] = self.get_user_info_by_user_id(user_id)
            self.all_user_info[server_index].is_valid = true
        end
    end
    self.homeowner_id = data.m_base_info.m_privater_id
    self.homeowner_server_index = data.m_base_info.m_private_station + 1
    self.banker_server_index = data.m_base_info.m_banker_station + 1

    self.cur_play_count = data.m_base_info.m_cur_play_count
    self.total_play_count = data.m_base_info.m_total_play_count
    self.free_game_duration = data.m_base_info.m_free_time

    --
    self:init_user_ready(data)
    --
    self:fire('game_state', self.game_state)
    self:fire('update_game_rule')

    self:fire('homeowner_id', self.homeowner_id)
    self:fire('homeowner_server_index', self.homeowner_server_index)
    self:fire('banker_server_index', self.banker_server_index)

    -- 
    local desk_info = clientmain:get_instance():get_room_mgr():get_desk_info()
    self.room_id = desk_info.m_desk_room_no or 0
    self:fire('room_id', self.room_id)
    self:fire('play_count', data.m_base_info.m_cur_play_count, data.m_base_info.m_total_play_count)

    for server_index=1, max_player_count do
        local user_id = data.m_base_info.m_user_id[server_index]
        if user_id ~= 0 then
            self:fire('on_user_sit', server_index, user_id)

            -- 主动请求一下 ip
            self:requestAction('ip_addr', user_id)
        end
        self:requestAction('gps_data', user_id)

        self:fire('init_user_score', server_index, data.m_base_info.m_user_score[server_index])
        self:fire('on_user_offline', server_index, data.m_base_info.m_user_cut[server_index])

        if data.m_base_info.m_game_status ~= 6 then
            self:fire('on_user_ready', server_index, data.m_user_ready[server_index])
        end

        self:fire('on_init_fast_out', server_index, data.m_base_info.m_fast_count[server_index])
    end

    if data.m_base_info.m_bOpenFree then
        self:fire('user_free_result', nil, nil, true)
    end

    -- 断线重连
    if data.m_base_info.m_game_status == 6 then
        self:on_reconn_game_state(data)
    end
end

function GameSceneBase:on_reconn_game_state(data)
end

function GameSceneBase:on_force_leave(data)
    self:fire('on_kick_out')
end

function GameSceneBase:on_user_sit_desk(data)
    local server_index = data.m_bDeskStation + 1
    local user_id = data.m_dwUserID

    print('myself user id : ' .. tostring(self.self_user_id))
    if not self.my_server_index and user_id == self.self_user_id then
        self.my_server_index = server_index
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
        self:try_to_request_game_state()
    end

    -- cache user info
    -- self.all_user_info[server_index] = self:requestAction('user_info', user_id)
    self.all_user_info[server_index] = self.get_user_info_by_user_id(user_id)
    self.all_user_info[server_index].is_valid = true

    self:fire('on_user_sit', server_index, user_id)
    self:fire('on_user_offline', server_index, false)

    -- 主动请求一下 ip
    self:requestAction('ip_addr', user_id)
    self:requestAction('gps_data', user_id)
end

function GameSceneBase:on_user_up_desk(data)
    local server_index = data.m_bDeskStation + 1

    -- 当游戏还没开局的时候，才清理掉玩家的数据
    if self.cur_play_count == 0 then
        self.all_user_info[server_index] = nil
    end

    self:fire('on_user_sit', server_index, 0)
end

function GameSceneBase:on_user_cut(data)
    local server_index = data.m_bDeskStation + 1
    self:fire('on_user_offline', server_index, true)
end

function GameSceneBase:on_user_ready(data)
    local server_index = data.chair_id + 1
    self.is_user_ready[server_index] = data.bagree
    self:fire('on_user_ready', server_index, data.bagree)
end

function GameSceneBase:on_game_chat_msg(data)
    local server_index = self:get_server_index_by_user_id(data.m_dwUserID)
    self:fire('on_user_chat', data.m_dwTalkType, data.m_dwSubType, server_index, data.m_dwUserID, data.m_dwSysMsg)
end

function GameSceneBase:on_user_free_operate(data)
    -- local data = {
    --     m_apply_chair = 0,
    --     m_apply_id    = 6109491,
    --     m_chair_id    = 0,
    --     m_free        = true,
    --     m_userid      = 6109491,
    -- }

    local apply_server_index = self.server_index_to_local_index[data.m_apply_chair + 1]
    local apply_user_id = data.m_apply_id
    local op_user_server_index = self.server_index_to_local_index[data.m_chair_id + 1]
    local op_user_id = data.m_userid
    local is_agree = data.m_free
    self:fire('user_free_operate', apply_server_index, apply_user_id, op_user_server_index, op_user_id, is_agree)
end

function GameSceneBase:on_user_free_result(data)
    --local data = {
    --    m_owner_chair = 0,
    --    m_owner_id = 6109549,
    --    m_result = true,
    --}

    -- 只有一个人的话，就直接退出吧
    if data.m_result and self:getUserCount() == 1 then
        return self:onExitGame()
    end

    -- 
    local server_index = data.m_owner_chair + 1
    local user_id = data.m_owner_id
    self:fire('user_free_result', server_index, user_id, data.m_result)
end

function GameSceneBase:on_gps_result(event)
    if not event or not event.args then return end

    local data = event.args.event_data
    self.gps_data = data or {}
    dump(self.gps_data)
    self:fire('update_gps_data')
    --]]

    --[[
    self.gps_data = {
        chair_id = 0,
        city = {
            [1] = '广东深圳1',
            [2] = '广东深圳2',
            [3] = '广东深圳3',
            [4] = '广东深圳4',
        },
        distance = {
            [1] = {
                [1] = 0,
                [2] = 670.795,
                [3] = 670.795,
                [4] = 0,
            },
            [2] = {
                [1] = 670.795,
                [2] = 0,
                [3] = 0,
                [4] = 0,
            },
            [3] = {
                [1] = 670.795,
                [2] = 0,
                [3] = 0,
                [4] = 0,
            },
            [4] = "0",
        },
        dwUserID = 0,
        get_gps_info = {
            [1] = true,
            [2] = true,
            [3] = true,
            [4] = false,
        },
        province = {
            [1] = "",
            [2] = "",
            [3] = "",
            [4] = "",
        },
    }
    self:fire('update_gps_data')
    --]]
end

function GameSceneBase:onUserEvent(event)
    if not event or not event.args then return end
    if basic_def.NOTIFY_USER_EVENT ~= event.id then return end

    local param = event.args
    if basic_def.NOTIFY_USER_EVENT_USERADDRESS == param.event_id then
        if event.args.event_data.ret ~= 0 then return end
        local data = param.event_data.data 
        if data then self:fire('user_ip_addr', data.uid, data.login_ip) end
    elseif basic_def.NOTIFY_USER_EVENT_UPDATE_PLAYER_INFO == param.event_id  then
        if event.args.event_data.ret ~= 0 then return end
        local data = param.event_data.data 
    elseif basic_def.NOTIFY_USER_EVENT_AREAWARD_INFO == param.event_id then
        if event.args.event_data.ret == 0 then
            show_msg_box_2('提示', '土豪，您已完成打赏，小伙伴对您的豪爽振奋不已！', nil, '知道了')
        end
    elseif basic_def.NOTIFY_USER_EVENT_GETAWARD_INFO == param.event_id then
        local label_string = ''
        for i=1, 7 do
            if data[i] then
                local data_string = string.format('恭喜收到土豪"%s",打赏的%d张房卡,快继续游戏吧。\n', tostring(data[i].nickname), tonumber(data[i].roomcard))
                label_string = string.format('%s%s', label_string, data_string)
            end
        end
        show_msg_box_2('提示', label_string)
    end
end

function GameSceneBase:loadComponent(file_name)
    if not file_name then return end

    -- 
    local file_path = string.format('app/platform/game/%d/component/%s.lua', self.game_id, file_name)
    local file_path = cc.FileUtils:getInstance():fullPathForFilename(file_path)
    if cc.FileUtils:getInstance():isFileExist(file_path) then
        return require(string.format('app.platform.game.%d.component.%s', self.game_id, file_name)).new(self)
    end

    local file_path = string.format('app/platform/game/game_common/component/%s.lua', file_name)
    if cc.FileUtils:getInstance():isFileExist(file_path) then
        return require(string.format('app.platform.game.game_common.component.%s', file_name)).new(self)
    end

    return nil
end

function GameSceneBase:initComponents()
    for component_name, v in pairs(self.scene_config.components or {}) do
        local component_obj = self:loadComponent(v.file_name)
        if component_obj then
            component_obj:init(v.args)

            self.all_components[component_name] = component_obj
        end
    end
end

function GameSceneBase:registerComponent(component_name, file_name, args)
    -- 
    self:unregisterComponent(component_name)

    --
    local component_obj = self:loadComponent(file_name)
    if component_obj then
        component_obj:init(args)

        self.all_components[component_name] = component_obj
    end
end

function GameSceneBase:unregisterComponent(component_name)
    local component_obj = self.all_components[component_name]
    if component_obj then
        component_obj:cleanup()

        self.all_components[component_name] = nil
    end
end

function GameSceneBase:initViews()
    model_base.initViews(self)

    -- background color
    local bg_layer = createBackgroundLayer(
                            cc.c4b(0, 0, 0, 0),
                            true,
                            function(touch, event) return self:on_touch_began(touch, event) end,
                            function(touch, event) self:on_touch_moved(touch, event) end,
                            function(touch, event) self:on_touch_ended(touch, event) end
                        )
    self:addChild(bg_layer)

    -- 桌布
    local hsb_value = UserData:getHSBValue() or { h = 0, s = 0, b = 0, index = 1 }
    self:resetTablecloth(hsb_value)

    -- 右上角的更多按钮，这个按钮应该一开始就存在，要不然想出去都还得看时机
    local game_more_entry = cc.CSLoader:createNode('game_common_res/game_more_entry.csb')
    game_more_entry:setPosition(70, 680)
    self:addChild(game_more_entry, 450)

    button('btn_more', function() self:popupNode('app.platform.game.game_common.game_more_view', { type = 'SETTING_RULE_DETAIL', }) end, game_more_entry)

    -- preload resource
    self:preloadResourceAndListenMsg()
end

function GameSceneBase:resetTablecloth(hsb_value)
    local index = math.abs(hsb_value.index)
    if self.background_index ~= index then
        -- 首先，需要确认的就是，这张桌布是否存在
        local file_path = string.format('%s/tablecloth_%d.jpg', self.scene_config.game_type, index)
        file_path = cc.FileUtils:getInstance():fullPathForFilename(file_path)
        if not cc.FileUtils:getInstance():isFileExist(file_path) then
            index = 1
        end

        -- 这次才是真的切换
        if self.background_index ~= index then
            self.background_index = index

            if self.background_sprite then
                self.background_sprite:removeFromParent(true)
                self.background_sprite = nil
            end

            -- 
            self.background_sprite = cc.Sprite:create(file_path)
            self.background_sprite:setPosition(display.width * 0.5, display.height * 0.5)
            self.background_sprite:setScale(1.2549)
            self:addChild(self.background_sprite)

            self.background_sprite:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('tablecloth'))
        end
    end

    self.background_sprite:setUniformCustom(hsb_value.h, hsb_value.s / 100.0, hsb_value.b / 100.0, 0)
end

function GameSceneBase:addCleanupCallback(callback)
    table.insert(self.cleanup_callback, callback)
end

function GameSceneBase:clear()
    if self.super_game_action and self.game_impl then
        self.game_impl.game_action = self.super_game_action
        self.super_game_action = nil
    end

    for _, fn in ipairs(self.cleanup_callback) do fn() end
    self.cleanup_callback = {}

    self:unlistenAllGameAttribute()
    self:unlistenAllGameSignal()

    for component_name, component_obj in ipairs(self.all_components) do
        component_obj:clear()
    end

    model_base.clear(self)
end

function GameSceneBase:on_touch_began(touch, event)
    return true
end

function GameSceneBase:on_touch_moved(touch, event)
end

function GameSceneBase:on_touch_ended(touch, event)
end

function GameSceneBase:listenUserEvent(event_id, callback)
    if not self.user_event_listeners[event_id] then self.user_event_listeners[event_id] = {} end
    table.insert(self.user_event_listeners[event_id], callback)
end

function GameSceneBase:unlistenUserEvent(event_id, callback)
    for i, cb in ipairs(self.user_event_listeners[event_id] or {}) do
        if cb == callback then
            table.remove(self.user_event_listeners[event_id], i)

            return
        end
    end
end

function GameSceneBase:listen_label(name, attr_name, init_text, convert_func, parent_node)
    convert_func = convert_func or tostring

    local label_node = parent_node:getChildByName(name)
    local unlisten_cb = self:listenGameAttribute(attr_name, function(v)
        print('attr_name : ' .. tostring(attr_name))
        print('v : ' .. tostring(v))
        label_node:setString(convert_func(v))
    end)

    label_node:setString(tostring(init_text or ''))

    return unlisten_cb
end

-- preload ------------------------------------------------------------------------------------------------------
function GameSceneBase:showLoadingAnimation()
    if not self.loading_frame then
        self.loading_frame = cc.Sprite:create('game_common_res/loading_frame.png');
        self.loading_frame:setPosition(display.width * 0.5, display.height * 0.5)
        self:addChild(self.loading_frame, 10001)
    end

    self.loading_frame:runAction(cc.RepeatForever:create(cc.RotateBy:create(2.0, 360)))
end

function GameSceneBase:hideLoadingAnimation()
    self.loading_frame:removeFromParent(true)
    self.loading_frame = nil
end

function GameSceneBase:preloadResourceAndListenMsg()
    -- show loading animation
    self:showLoadingAnimation()

    local function __check_listen_msg__()
        for _, v in pairs(self.init_listen_msg_ids or {}) do
            if v.cur_count < v.total_count then return false end
        end
        return true
    end

    -- 
    local index = 1
    self:scheduleUpdateWithPriorityLua(function()
        -- plist 加载完了，需要等待的 msg 也回来了，就可以正常的初始化游戏界面了
        if index > #self.scene_config.preload_plist and __check_listen_msg__() then
            self:unscheduleUpdate()

            -- 
            self:initComponents()

            -- request game state
            self.preload_flag = true
            self:try_to_request_game_state()

            -- hide loading animation
            return self:hideLoadingAnimation()
        end

        -- load plist
        if index <= #self.scene_config.preload_plist then
            cc.SpriteFrameCache:getInstance():addSpriteFrames(self.scene_config.preload_plist[index]);
            index = index + 1
        end
    end, 0.03)  
end

function GameSceneBase:try_to_request_game_state()
    if self.preload_flag and self.my_server_index then
        self:requestAction('game_state')
    end
end

-- listen msg ids -----------------------------------------------------------------------------------------------
function GameSceneBase:data_notify(id, data)
    if not id then print(debug.traceback()) end
    if self.init_listen_msg_ids[id] then
        self.init_listen_msg_ids[id].cur_count = self.init_listen_msg_ids[id].cur_count + 1
    end

    print('GameSceneBase:data_notify id : ' .. tostring(id))
    dump(data)
    local fn = self.game_msg_listeners[id]
    if fn then fn(data) end
end

-- helper functions ------------------------------------------------------------------------------------------------
function GameSceneBase:getRoomID()
    local desk_info = clientmain:get_instance():get_room_mgr():get_desk_info()
    if desk_info then return desk_info.m_desk_room_no or 0 end
    return 0 
end

-- listen game attributes -----------------------------------------------------------------------------------------
function GameSceneBase:listenGameAttribute(attr_name, callback)
    if not self.game_attribute_listeners[attr_name] then self.game_attribute_listeners[attr_name] = {} end
    self.game_attribute_listeners[attr_name][callback] = 1

    signal.listen(attr_name, callback, 0)

    return callback
end

function GameSceneBase:listenGameAttributeList(attr_list, callback)
    for _, name in ipairs(attr_list or {}) do
        self:listenGameAttribute(name, callback)
    end
end

function GameSceneBase:unlistenGameAttribute(attr_name, callback)
    if self.game_attribute_listeners[attr_name] then
        self.game_attribute_listeners[attr_name][callback] = nil
    end

    signal.unlisten(attr_name, callback)
end

function GameSceneBase:unlistenAllGameAttribute()
    for name, v in pairs(self.game_attribute_listeners) do
        for cb, _ in pairs(v) do
            signal.unlisten(name, cb)
        end
    end
    self.game_attribute_listeners = {}
end

function GameSceneBase:updateGameAttribute(attr_name, value)
    if self.game_attributes[attr_name] ~= value then
        self.game_attributes[attr_name] = value
        signal.fire(attr_name, value)
    end
end

function GameSceneBase:updateGameAttributes(attr_list)
    local fire_attrs = {}

    for name, value in pairs(attr_list or {}) do
        if self.game_attributes[name] ~= value then
            self.game_attributes[name] = value
            table.insert(fire_attrs, name)
        end
    end

    for _, name in ipairs(fire_attrs) do
        signal.fire(name, attr_list[name])
    end
end

function GameSceneBase:listenGameSignal(name, callback)
    if not self.game_signal_listeners[name] then self.game_signal_listeners[name] = {} end
    self.game_signal_listeners[name][callback] = 1

    signal.listen(name, callback, 0)

    return callback
end

function GameSceneBase:listenGameSignalList(name_list, callback)
    for _, name in ipairs(name_list or {}) do
        self:listenGameSignal(name, callback)
    end
end

function GameSceneBase:unlistenGameSignal(name, callback)
    if self.game_signal_listeners[name] then
        self.game_signal_listeners[name][callback] = nil
    end

    signal.unlisten(name, callback)
end

function GameSceneBase:unlistenAllGameSignal()
    for name, v in pairs(self.game_signal_listeners) do
        for cb, _ in pairs(v) do
            signal.unlisten(name, cb)
        end
    end

    self.game_signal_listeners = {}
end

function GameSceneBase:fire(name, ...)
    signal.fire(name, ...)
end

------------------------------------------------------------------------------------------------------------------
function GameSceneBase:requestAction(action, ...)
    local action_func = self.game_request_actions[action]
    if action_func then action_func(...) end
end

function GameSceneBase:onClickExitButtonEvent()
    --if self.my_server_index ~= self.homeowner_server_index and self.game_state == 'waiting' then
    --    self:onExitGame()
    --else
        self:fire('second_confirmation_free_game', function(is_confirm)
            if is_confirm then
                self:requestAction('free_game', true)
            end
        end)
    --end
end

function GameSceneBase:canDismissRoom()
    if self.my_server_index == self.homeowner_server_index then return true end

    return self.game_state ~= 'waiting'
end

-- 这个一般每个游戏都需要继承重写的方法
function GameSceneBase:getGameRuleConfig()
    -- like this
    -- return {
    --     game_name = '抓五魁',
    --     sections = {
    --         {
    --             section_name = '玩法',
    --             section_desc = '可以 海底捞月、杠上炮，不可以 杠上开花',
    --         },
    --         {
    --             section_name = '牌型',
    --             section_desc = '可胡 清一色、七对，不可胡 捉五魁',
    --         },
    --     },
    -- }
end

-- 这个 game scene 可以缓存，每个游戏都应该需要重写的方法
function GameSceneBase:getRuleDetailConfig()
    -- like this
    -- return {
    --     {
    --         name = '基本玩法',
    --         help_contents = { string.format('http://192.168.1.160:50080/20000053/rule_1.png') },
    --     },
    --     {
    --         name = '基本翻型',
    --         help_contents = { string.format('http://192.168.1.160:50080/20000053/rule_2.png') },
    --     },
    --     {
    --         name = '特殊规则',
    --         help_contents = { string.format('http://192.168.1.160:50080/20000053/rule_3.png') },
    --     },
    --     {
    --         name = '结算规则',
    --         help_contents = { string.format('http://192.168.1.160:50080/20000053/rule_4.png') },
    --     },
    -- }

    return {
        {
            name = '基本玩法',
            help_contents = { string.format('%s/%d/rule_1.png', g_game_rules_url, self.game_id) },
        },
        {
            name = '基本番型',
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

-- 这个需要 game scene 存起来，因为在音效播放的时候用到
function GameSceneBase:getLanguageConfig()
    if not self.language_config then
        self.language_config = {
            { name = '普通话', is_selected = true, },
        }
    end

    return self.language_config

    -- like this
    -- return {
    --     { name = '普通话', is_selected = true, },
    --     { name = '方言', is_selected = false, },
    --     { name = '韶关话', is_selected = false, },
    -- }
end

function GameSceneBase:onExitGame()
    if self.game_impl then self.game_impl:UserLeftRequest(self.user_ID, 1) end

    unload_game_module(self.game_id)

    if self.is_replay then G_Hall_State = 1 end

    self:switchScene('app.platform.room.new_view.new_hall_scene')
end

function GameSceneBase:restart()
    self:fire('game_state', 'prepare_next_round')
end

-- 尝试打开大结算界面
-- 1，包间解散后，玩家确认后调用过来
-- 2，游戏局数打完后，玩家在看完小结算界面后调用过来
function GameSceneBase:tryToShowFinalSettle()
    -- 包间解散后，如果有大结算的数据，就把大结算界面打开
    if not self.all_record_info then return self:onExitGame() end

    local user_count = self:getUserCount()
    self:fire('final_settle', self.all_record_info, user_count)
end

function GameSceneBase:get_user_info(user_id)
    for _, v in pairs(self.all_user_info) do
        if v.m_dwUserID == user_id then
            return v
        end
    end

    return {
        m_nickName = '',
        m_bLogoID = 0,
        m_headurl = '',
        m_dwUserID = '',
    }
end

function GameSceneBase:get_user_info_by_server_index(server_index)
    return self.all_user_info[server_index] or {
        m_nickName = '',
        m_bLogoID = 0,
        m_headurl = '',
        m_dwUserID = '',
    }
end

function GameSceneBase:get_user_id(server_index)
    local user_info = self.all_user_info[server_index]
    return user_info and user_info.m_dwUserID or 0
end

function GameSceneBase:get_server_index_by_user_id(user_id)
    for server_index=1, 4 do
        if self.all_user_info[server_index] and self.all_user_info[server_index].m_dwUserID == user_id then
            return server_index
        end
    end

    return -1
end

function GameSceneBase:getUserCount()
    local count = 0
    for i=1, 4 do
        if self.all_user_info[i] then
            count = count + 1
        end
    end
    return count
end

return GameSceneBase
