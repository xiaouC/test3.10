-- ./app/platform/room/new_view/login_view.lua
require 'app.platform.room.new_view.loading'

local m_clientmain = require 'app.platform.room.clientmain'
local m_def = import("..module.basicnotifydef")

heart_beat_handler = heart_beat_handler or nil

local model_base = require 'app.platform.common.model_base'
local LoginView = class('LoginView', model_base)
function LoginView:ctor()
    self.csb_file = 'hall_res/login/login_scene.csb'

    model_base.ctor(self)
end

function LoginView:initViews()
    model_base.initViews(self)
end

function LoginView:clear()
    m_clientmain:get_instance():get_room_mgr():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_ROOM_EVENT, self)
    m_clientmain:get_instance():get_game_manager():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_GAME_EVENT, self)

    model_base.clear(self)
end

function LoginView:enter()
    self:tryToAutoLogin(true)
end

function LoginView:initDataFromServer()
    self:updateComplete()
end

function LoginView:updateComplete()
    -- init shaders
    require 'shaders.shaders'
    initCustomShaders()

    -- 
    require 'app.platform.common.load'
    m_clientmain:get_instance():run()

    -- 
    require 'app.platform.common.game_music'

    require 'app.platform.room.common.Define'
    UserData = require 'app.platform.room.common.UserData'
    Music = require 'app.platform.room.common.Music'
    AccountData = require 'app.platform.room.common.AccountData'

    -- 初始化文件数据
    UserData:init()
    Music:init()
    AccountData:init()

    play_hall_background_music()    -- game_music.lua

    -- 显示版本号
    local version_node = self.csb_node:getChildByName('version_background')
    version_node:setVisible(true)
    label('text_version', g_gcloud_src_version, version_node)

    -- 创建登陆按钮
    local login_csb_file = (device.platform == 'android' and 'hall_res/login/login_android.csb' or 'hall_res/login/login_ios.csb')
    local login_csb_node = cc.CSLoader:createNode(login_csb_file)
    self.csb_node:getChildByName('login_node'):addChild(login_csb_node)

    button('btn_wechat', function() self:onWechatLogin() end, login_csb_node)
    button('btn_guest', function() self:onGuestLogin() end, login_csb_node)

    G_isGuest = false --是否游客登陆 ture为游客

    m_clientmain:get_instance():get_user_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_USER_EVENT, function(event)
        new_hide_loading()      -- 无论登录成功还是失败，都应该关闭掉

        if not event or not event.args then return end
        if event.id ~= m_def.NOTIFY_USER_EVENT then return end

        local param = event.args
        if m_def.NOTIFY_USER_EVENT_LOGIN == param.event_id then
            if param.event_data.ret == 0 then
                G_firstin_hall = true       -- 打开 app 的时候，才会执行一次自动登录

                local data = param.event_data.data
                if data and data.m_username and data.m_password then
                    if G_isGuest == false then
                        G_isFirstLogin = false
                        UserData:setUserName(data.m_username)
                        if UserData:getPwdSwitch() == "on" then 
                            UserData:setUserPwd(data.m_password)
                        end
                    else
                        G_isFirstLogin = false
                        UserData:setGuestName(data.m_username)
                        UserData:setGuestPwd(data.m_password)
                        m_clientmain:get_instance():set_user_login_flag()
                    end
                end

                if not m_clientmain:get_instance():get_user_mgr():check_user_join_guild() then
                    self:enterHallScene() 
                else
                    if tonumber(data.m_room_desk_no) ~= 0 then  --断线重连
                        m_clientmain:get_instance():get_room_mgr():query_desk_info(tonumber(data.m_room_desk_no))
                    else
                        if not m_clientmain:get_instance():get_sdk_mgr():check_user_gameing() then
                            self:enterHallScene()
                        else
                            m_clientmain:get_instance():get_sdk_mgr():join_room_end()
                        end
                    end
                end
            else
                local desc = param.event_data.desc or '抱歉，登录失败，请稍后再试，或联系游戏客服人员'
                api_show_Msg_Box(desc)
            end
        elseif m_def.NOTIFY_USER_EVENT_REGISTER_ERROR == param.event_id then
            api_show_Msg_Box(param.event_data.desc)
        end
    end)
    m_clientmain:get_instance():get_room_mgr():get_event_mgr():BsAddEventListener(m_def.NOTIFY_ROOM_EVENT, self, function(event)
        new_hide_loading()      -- 无论登录成功还是失败，都应该关闭掉

        if not event or not event.args then return end
        if event.id ~= m_def.NOTIFY_ROOM_EVENT then return end

        local param = event.args
        if m_def.NOTIFY_ROOM_EVENT_QUERY_ROOM == param.event_id then
            if param.event_data.ret == 0 then
                dump(param.event_data.data)
                ----包间搜索进公会后，查询包间，进入游戏
                local data = param.event_data.data
                if data.m_desk_info and data.m_desk_info.m_roomcard_count then
                    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info()
                    if user_info and user_info.m_roomcard then
                        if tonumber(user_info.m_roomcard) < tonumber(data.m_desk_info.m_roomcard_count) then
                            api_show_Msg_Box("房卡不足，请充值")
                            return self:enterHallScene()
                        end
                    end
                end

                new_show_loading('正在登录包间。。。')
                m_clientmain:get_instance():login_wserver(data.m_room_info,data.m_desk_info.m_desk_num,0,data.m_desk_info)
            else
                api_show_Msg_Box('加入包间失败!')
                self:enterHallScene() 
            end
        elseif m_def.NOTIFY_ROOM_EVENT_QUERY_DESK == param.event_id then
            if param.event_data.ret ~= 0 then
                api_show_Msg_Box('包间不存在!')
                self:enterHallScene() 
            end
        elseif m_def.NOTIFY_ROOM_EVENT_CHECK_GAME_UPDATE == param.event_id then
            if param.event_data.ret == 0 then  
                local desk_info = param.event_data.data
                self:popupNode('app.platform.room.new_view.game_update_view', {
                    game_id = tonumber(desk_info.m_room_info.m_gameid),
                    callback = function(result)
                        if result then
                            m_clientmain:get_instance():login_wserver(desk_info.m_room_info, desk_info.m_desk_num, 0, desk_info)
                        else
                            api_show_Msg_Box('游戏更新失败!!!')
                        end
                    end,
                })
            end
        end
    end)
    m_clientmain:get_instance():get_config_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_CONFIG_EVENT, function(event) dump(event) end)       -- 感觉没啥可做的
    m_clientmain:get_instance():get_sdk_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_SDK_EVENT, function(event) dump(event) end)             -- 感觉没啥可做的
    m_clientmain:get_instance():get_game_manager():get_event_mgr():BsAddEventListener(m_def.NOTIFY_GAME_EVENT, self, function(event)
        new_hide_loading()      -- 无论登录成功还是失败，都应该关闭掉

        if not event or not event.args then return end
        if event.id ~= m_def.NOTIFY_GAME_EVENT then return end

        if m_def.NOTIFY_GAME_EVENT_SETUP_GUILD_SCENE == event.args.event_id then 
            G_is_WXcome = true
            self:enterHallScene() 
        end
    end)

    -- 心跳
    if not heart_beat_handler then
        heart_beat_handler = schedule_circle(5, function() m_clientmain:get_instance():on_frame() end)
    end

    -- auto login
    self:tryToAutoLogin(nil, true)
end

function LoginView:tryToAutoLogin(enter_flag, update_flag)
    if enter_flag then self.enter_flag = enter_flag end
    if update_flag then self.update_flag = update_flag end

    if self.enter_flag and self.update_flag then
        self.enter_flag = nil
        self.update_flag = nil

        if not G_firstin_hall then
            local open_id = UserData:get_weixin_openid()
            if open_id ~= '' and tonumber(open_id) ~= 0 then
                new_show_loading('正在登录。。。')
                m_clientmain:get_instance():get_sdk_mgr():on_weixin_repeat_login_notify_event()
            end
        end
    end
end

function LoginView:onWechatLogin()
    G_isGuest = false

    if test_auto_login then
        self:popupNode('app.platform.room.new_view.login_account_view')
    else
        new_show_loading('正在登录。。。')
        m_clientmain:get_instance():get_user_mgr():fast_login()
    end
end

function LoginView:onGuestLogin()
    G_isGuest = true
    new_show_loading('正在登录。。。')
    m_clientmain:get_instance():get_user_mgr():auto_login()
end

function LoginView:enterHallScene()
    m_clientmain:get_instance():get_room_mgr():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_ROOM_EVENT, self)
    m_clientmain:get_instance():get_game_manager():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_GAME_EVENT, self)

    G_in_Hall = true

    self:switchScene('app.platform.room.new_view.new_hall_scene')
end

function LoginView:onLogin(account, password)
    G_isGuest = false
    new_show_loading('正在登录。。。')
    m_clientmain:get_instance():login_user_to_zserver(account, password)
end

return LoginView
