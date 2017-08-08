---------------------------------------------------------
-- 日期：	20151010
-- 作者:	xxm
-- 描述:	游戏实例,控制层
-- 注意:    尽可能业务逻辑独立(维护成本降到最低)
-----------------------------------------------------------------------------
--创建包
local GameHandleImpl = class("GameHandleImpl")
function GameHandleImpl:ctor(args)
    self.m_desk_info = {}

    self.m_my_table_id = 0				--我的桌子号
    self.m_my_dest_station = 0			--我的位置
    self.m_game_state = 0				--游戏状态s

    self.m_is_state = false --判断是否先收到状态消息

    self.m_interface = nil

    self.msg_list = {}

    self.m_game_scene = nil
end

--------------------------------Handle-----------------------------------------
local m_gamehandlemsg = import(".gamehandlemsg")
local m_game_scene_mgr = import("..ui.gamescenemgr")

local m_gameelement = game_msg_ids

--------------------------------------------------------------------------------

--bzgameinterface.lua
function GameHandleImpl:get_game_interface()
	return self.m_interface
end

--gamehandlemsg.lua
function GameHandleImpl:get_game_handle_msg()
	if self.gamehandlemsg == nil then
		self.gamehandlemsg = m_gamehandlemsg.new()
	end
	return self.gamehandlemsg
end

function GameHandleImpl:get_game_scene_mgr()
	if self.game_scene_mgr == nil then
		self.game_scene_mgr = m_game_scene_mgr.new()
	end
	return self.game_scene_mgr
end

function GameHandleImpl:get_room_module()
    return self:get_game_interface():get_room_module()
end


function GameHandleImpl:get_user_module()
    return self:get_game_interface():get_user_module()
end

function GameHandleImpl:get_room_mgr()
    return self:get_game_interface():get_room_mgr()
end

-----------------------------------API------------------------------------------

function GameHandleImpl:init_game()
   self.msg_list = {}
   self.m_game_scene = nil
   self:get_game_handle_msg():init_handle_msg()
   self:get_game_handle_msg():BsAddNotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,handler(self,self.lua_game_handle_notify),nil)
end

function GameHandleImpl:uninit_game()
    self.m_game_scene = nil
	self.m_is_state = false
	self:get_game_handle_msg():un_init_handle_msg()
	self:get_game_scene_mgr():leave_game_scene()
end


--游戏用户行为
function GameHandleImpl:game_action(aid,hcode,buf,len,msg)
    
    BASIC_LOG_INFO("xxm: GameHandleImpl:game_action aid=%d,hcode=%d",aid,hcode)

	local switch = {}

    switch[self:get_room_module().AID_USER_SIT] = handler(self,self.on_user_sit_desk)
    switch[self:get_room_module().AID_USER_UP] = handler(self,self.on_user_up_desk)
    switch[self:get_room_module().AID_USER_COME] = handler(self,self.on_user_come)
    switch[self:get_room_module().AID_USER_NETCUT] = handler(self,self.on_user_cut)
    switch[self:get_room_module().AID_USER_SIT_ERROR] = handler(self,self.on_sit_desk_fail)
	if switch[aid] ~= nil then
		switch[aid](hcode,buf,len,msg)
	end

end

--转发消息
function GameHandleImpl:dispatch_message(mid,aid,hcode,buf,len,msg)
	if mid == self:get_room_module().MID_ROOM_ACTION then
		local switch = {}
--		switch[self:get_room_module().AID_USER_GAME_END] = handler(self,self.GameFinish)
--		switch[self:get_room_module().AID_USER_AGREE] = handler(self,self.UserAgreeGame)
--		switch[self:get_room_module().AID_USER_SCORE_CHANGE] = handler(self,self.UserChangeScore)
		if switch[aid] ~= nil then
			switch[aid](hcode,buf,len,msg)
		end
    elseif(mid == self:get_room_module().MID_DC_GR_ROOM ) then
        local switch = {}
        switch[self:get_room_module().AID_ASS_GR_GAME_READY] = handler(self,self.on_user_ready)
        if switch[aid] ~= nil then
			switch[aid](hcode,buf,len,msg)
		end
    elseif(mid == self:get_room_module().MID_GR_GAMM_FRAME ) then
        local switch = {}
        switch[self:get_room_module().AID_ASS_GR_SEND_MSG] = handler(self,self.on_game_chat_msg)
        switch[self:get_room_module().AID_ASS_GR_GPS_RESULT] = handler(self,self.on_game_gps_result)
        BASIC_LOG_ERROR('GameHandleImpl:dispatch_message(mid,aid,hcode,buf,len,msg) ========================================================')
        BASIC_LOG_ERROR('self:get_room_module().AID_ASS_GR_GPS_RESULT : ' .. tostring(self:get_room_module().AID_ASS_GR_GPS_RESULT))
        BASIC_LOG_ERROR('aid : ' .. tostring(aid))
        if switch[aid] ~= nil then
			switch[aid](hcode,buf,len,msg)
		end
--    elseif(mid == self:get_user_module().MID_LOGIN_ROOM) then
--        local switch = {}
--        switch[self:get_user_module().AID_LOGIN_RESULT] = handler(self,self.on_login_finish)
--        if switch[aid] ~= nil then
--			switch[aid](hcode,buf,len,msg)
--		end
	end
end
---------------------------------------------------------------------------------
--function GameHandleImpl:on_login_finish(hcode, buf, len, msg)
--    if(0 == hcode) then
--        local sit_user_info = msg
--        if(255 == sit_user_info.m_bDeskNO and 255 == sit_user_info.m_bDeskStation) then
--            return nil
--        end
--        BASIC_LOG_INFO("2000_2 GameHandleImpl:on_login_finish 00")
--        local my_user_info = self:get_game_interface():get_self_info()
--        if(nil == sit_user_info or nil == my_user_info ) then
--            return nil
--        end
--        if(sit_user_info.m_dwUserID == my_user_info.m_dwUserID) then
--            BASIC_LOG_INFO("2000_2 GameHandleImpl:on_login_finish 01  sit_user_info.m_dwUserID == my_user_info.m_dwUserID")
--            self.m_my_dest_station = sit_user_info.m_bDeskStation   
--            self.m_my_table_id = sit_user_info.m_bDeskIndex

--            self:get_room_mgr():request_game_station(my_user_info.m_dwUserID)
--            --self:get_room_mgr():request_user_agree(sit_user_info.m_dwUserID,sit_user_info.m_bDeskIndex,sit_user_info.m_bDeskStation,1)

--            BASIC_LOG_INFO("xxm: GameHandleImpl:on_login_finish ")
--            local scene = require("app.platform.game.20000001.ui.gamescene").new()
--	    BASIC_LOG_INFO("2000_2 GameHandleImpl:on_login_finish 02")
--            scene:SetGameImpl(self)
--            if cc.Director:getInstance():getRunningScene() then
--                BASIC_LOG_INFO("2000_2 GameHandleImpl:on_login_finish 03 replaceScene(scene)")
--                cc.Director:getInstance():replaceScene(scene)
--            else
--                BASIC_LOG_INFO("2000_2 GameHandleImpl:on_login_finish 04 runWithScene(scene)")
--                cc.Director:getInstance():runWithScene(scene)
--            end
--        end

--        if(self.m_my_table_id == sit_user_info.m_bDeskIndex) then
--            self:set_desk_info(sit_user_info,true)
--            self:get_game_scene_mgr():data_notify(m_gameelement.EVENT_GAME_NOTIFY_USER_SIT,sit_user_info)
--        end

--    end
--end 

function GameHandleImpl:set_desk_info(sit_user_info,sit)
    if(nil == sit_user_info) then
        return nil
    end

    if(self.m_my_table_id ~= sit_user_info.m_bDeskIndex) then
        return nil
    end

    if(sit) then
        self.m_desk_info[sit_user_info.m_bDeskStation] = sit_user_info.m_dwUserID
    else
        self.m_desk_info[sit_user_info.m_bDeskStation] = 0
    end
end
----------------------------------------------------------------
function GameHandleImpl:load_game_scene()

    --[[
    api_hide_loading_ext()
    if( nil == self.m_game_scene ) then
        api_show_loading_extern(5,"正在加载游戏资源。。。")
        --local scene = require("app.platform.game.20000001.ui.gamescene").new()
        local scene = require("app.platform.game.20000001.ui.loadscene").new(self)
        --scene:SetGameImpl(self)
        BASIC_LOG_INFO("2002_3 GameHandleImpl:on_user_come 03")
        if cc.Director:getInstance():getRunningScene() then
            BASIC_LOG_INFO("2002_3 GameHandleImpl:on_user_come 04 replaceScene(scene)")
            cc.Director:getInstance():replaceScene(scene)
        else
            BASIC_LOG_INFO("2002_3 GameHandleImpl:on_user_come 05 runWithScene(scene)")
            cc.Director:getInstance():runWithScene(scene)
        end
        BASIC_LOG_INFO("2002_3 GameHandleImpl:on_user_come 06")
        self.m_game_scene = scene
    end
    --]]
     
end
----------------------------------------------------------------
function GameHandleImpl:on_user_come(hcode, buf, len, msg)
    BASIC_LOG_INFO("2002_3 GameHandleImpl:on_user_come 00")
    local sit_user_info = msg
    local my_user_info = self:get_game_interface():get_self_info()
    if(nil == sit_user_info or nil == my_user_info ) then
        return nil
    end
    BASIC_LOG_INFO("2002_3 GameHandleImpl:on_user_come 01")

    if(sit_user_info.m_dwUserID == my_user_info.m_dwUserID) then
        BASIC_LOG_INFO("2002_3 GameHandleImpl:on_user_come 02 sit_user_info.m_dwUserID == my_user_info.m_dwUserID")
        
        --self:get_room_mgr():request_game_station(my_user_info.m_dwUserID)
        self:load_game_scene()

        self.m_my_dest_station = sit_user_info.m_bDeskStation
        self.m_my_table_id = sit_user_info.m_bDeskIndex
        self:set_desk_info(sit_user_info,true)
    end

    self:get_game_scene_mgr():data_notify(m_gameelement.EVENT_GAME_NOTIFY_USER_COME,sit_user_info)
end

function GameHandleImpl:on_user_sit_desk(hcode, buf, len, msg)
    BASIC_LOG_INFO("2002_2 GameHandleImpl:on_user_sit_desk 00")
    local sit_user_info = msg
    local my_user_info = self:get_game_interface():get_self_info()
    if(nil == sit_user_info or nil == my_user_info ) then
        return nil
    end
    BASIC_LOG_INFO("2002_2 GameHandleImpl:on_user_sit_desk 01")
    if(sit_user_info.m_dwUserID == my_user_info.m_dwUserID) then
        BASIC_LOG_INFO("2002_2 GameHandleImpl:on_user_sit_desk 02 sit_user_info.m_dwUserID == my_user_info.m_dwUserID")
        --self:get_room_mgr():request_game_station(10001)
        --self:GetGameSceneMgr():EnterGameScene(self)
        self.m_my_dest_station = sit_user_info.m_bDeskStation
        self.m_my_table_id = sit_user_info.m_bDeskIndex

        --self:get_room_mgr():request_game_station(my_user_info.m_dwUserID)
        if(sit_user_info.m_bUserState <= 2) then
            if G_is_close == true then
                self:get_room_mgr():request_user_agree(sit_user_info.m_dwUserID,sit_user_info.m_bDeskIndex,sit_user_info.m_bDeskStation,1)
            end
        end
 
        self:load_game_scene()
    end
    BASIC_LOG_INFO("2002_2 GameHandleImpl:on_user_sit_desk 06")
    if(self.m_my_table_id == sit_user_info.m_bDeskIndex) then
        self:set_desk_info(sit_user_info,true)
        self:get_game_scene_mgr():data_notify(m_gameelement.EVENT_GAME_NOTIFY_USER_SIT,sit_user_info)
    end
end

function GameHandleImpl:on_sit_desk_fail(hcode,buf,len,msg)
    self:get_game_scene_mgr():data_notify(m_gameelement.EVENT_GAME_NOTIFY_USER_SIT_FAIL,hcode)
end

function GameHandleImpl:on_user_up_desk(hcode,buf,len,msg)
    local sit_user_info = msg
    if(nil == sit_user_info)then
        return nil
    end
    

    local my_user_info = self:get_game_interface():get_self_info()
    if(nil == sit_user_info or nil == my_user_info ) then
        return nil
    end

    if(self.m_my_table_id == sit_user_info.m_bDeskIndex) then
        self:set_desk_info(sit_user_info,false)
        self:get_game_scene_mgr():data_notify(m_gameelement.EVENT_GAME_NOTIFY_USER_UP,sit_user_info)
    end
end

function GameHandleImpl:on_user_cut(hcode,buf,len,msg) 
    local cut_user_info = msg
    if(nil == cut_user_info)then
        return nil
    end 
    if(self.m_my_table_id == cut_user_info.m_bDeskNO) then
        self:get_game_scene_mgr():data_notify(m_gameelement.EVENT_GAME_NOTIFY_USER_CUT,cut_user_info)
    end

end
function GameHandleImpl:on_user_ready(hcode,buf,len,msg)
    if(nil == msg) then
        return nil
    end
--   self:get_game_scene_mgr():data_notify(m_gameelement.EVENT_GAME_NOTIFY_USER_READY,msg)
end

function GameHandleImpl:on_game_chat_msg(hcode,buf,len,msg)
    if(nil == msg) then
        return nil
    end
    self:get_game_scene_mgr():data_notify(m_gameelement.EVENT_GAME_NOTIFY_NOTIFY_GAME_CHAT_MSG,msg)
end

function GameHandleImpl:on_game_gps_result(hcode, buf, len, msg)
    if msg == nil then
        return nil
    end
    print('gps_data : GameHandleImpl:on_game_gps_result(hcode, buf, len, msg)')
    dump(msg)
    print('================================================================')
    self:get_game_scene_mgr():data_notify(m_gameelement.EVENT_GAME_NOTIFY_GPS_RESULT,msg)
end

--test
function GameHandleImpl:do_test(args)

    --房间列表
    --self:request_versus_desk_list()
    --创建房间
   local desk_info = clone(self:get_game_action():get_action_module().t_request_new_desk_info)
   desk_info.m_desk_name = "小小明"
   desk_info.m_password = ""
   desk_info.m_peoplecount = 2
   desk_info.m_versus_reserve = 100
   desk_info.m_versus_desclaration = "来吧兄弟们，我有的是钱"
   desk_info.m_game_config = {1,2,3,4,5,6}
   desk_info.m_play_count = 8
   self:request_new_versus_desk(desk_info)


end


--游戏逻辑通知
function GameHandleImpl:lua_game_handle_notify(event)
	if nil == event then
		return 
	end
	
	if m_gameelement.EVENT_GAME_NOTIFY ~= event.id then
		return
	end
	
	local event_param = event.args
	
	if event_param == nil then
		return
	end

    if m_gameelement.EVENT_GAME_NOTIFY_GAME_STATE == event_param.msg_code then
        self.m_is_state = true
        self:get_game_scene_mgr():data_notify(event_param.msg_code,event_param.msg_data)
        self:do_dispatch_cache_msg();
        return 
    end
    
    if self.m_is_state == false then 
        BASIC_LOG_INFO("xxm: cache msg data")
        table.insert(self.msg_list,event_param)
        return
    end

    self:get_game_scene_mgr():data_notify(event_param.msg_code,event_param.msg_data)

    --dump(event_param.msg_data)
end

function GameHandleImpl:get_timer_mgr()
    return self:get_game_interface():get_timer_mgr();
end

function GameHandleImpl:on_driver_msg(timer_id)
    self:get_timer_mgr():remove_timer(timer_id)
    self:do_dispatch_cache_msg()
end

function GameHandleImpl:do_dirver_msg()
    self:get_timer_mgr():add_timer(20000001001,2,handler(self,self.on_driver_msg),nil)
end

---------------------------------------------------------------------------------
function GameHandleImpl:do_play_dice(object)
    self:get_game_handle_msg():request_play_dice(object)
end

function GameHandleImpl:do_out_card(object)
    self:get_game_handle_msg():request_out_card(object)
end

function GameHandleImpl:do_block_opreate(object)
    --dump(object)
    self:get_game_handle_msg():request_block_opreate(object)
end
function GameHandleImpl:do_swap_wall_card(object)
    --dump(object)
    self:get_game_handle_msg():do_swap_wall_card(object)

end
function GameHandleImpl:do_user_free_game(object)

    self:get_game_handle_msg():do_user_free_game(object)
end
function GameHandleImpl:do_user_apply_game_info(object)
    self:get_game_handle_msg():do_user_apply_game_info(object)
end
function GameHandleImpl:do_get_game_config(object)
    self:get_game_handle_msg():do_get_game_config(object)
end
--小局开始
function GameHandleImpl:do_user_agree(object) 
    --dump(object)
    self:get_game_handle_msg():do_user_agree(object)
end


function GameHandleImpl:do_request_game_station(object)
    -- body
    local my_user_info = self:get_game_interface():get_self_info()
    if(my_user_info ~= nil ) then
        self:get_room_mgr():request_game_station(my_user_info.m_dwUserID)
    end
    
end

---------------------------------------------------------------------------------
function GameHandleImpl:do_get_self_info()
    return self:get_game_interface().get_self_info()
end

function GameHandleImpl:do_get_self_desk_station()
    return self.m_my_dest_station
end

function GameHandleImpl:do_get_user_info_by_id(user_id)
    return self:get_game_interface().get_room_player_info_byid(user_id)
end
--游戏开始时
function GameHandleImpl:do_request_user_agree(agree)
    local my_user_info = self:get_game_interface():get_self_info()
    if(nil == my_user_info ) then
        return nil
    end
    self:get_room_mgr():request_user_agree(my_user_info.m_dwUserID,self.m_my_table_id,self.m_my_dest_station,agree)
end
--剔除玩家 
function GameHandleImpl:do_force_user_leave(user_id,chair_id)
    local my_user_info = self:get_game_interface():get_self_info()
    if(nil == my_user_info ) then
        return nil
    end
    self:get_room_mgr():request_force_user_leave(my_user_info.m_dwUserID,self.m_my_table_id,user_id,chair_id)
end
--分发消息缓存
function GameHandleImpl:do_dispatch_cache_msg()
    for key, event_param in pairs(self.msg_list) do
        self:get_game_scene_mgr():data_notify(event_param.msg_code,event_param.msg_data)
    end
    self.msg_list = {}
end

---------------------------------------------------------------------------------
function GameHandleImpl:init_module(parent)
    self.m_interface = parent
    self:get_game_scene_mgr():init_module(self)
end

function GameHandleImpl:UserLeftRequest(userid,leaveid)
	self:get_game_handle_msg():UserLeftRequest(userid,leaveid)
end

function GameHandleImpl:send_gps_info(user_id, chair_id, longitude, latitude)
	self:get_game_handle_msg():send_gps_info(user_id, chair_id, longitude, latitude)
end

--return object
return GameHandleImpl
