---------------------------------------------------------
-- 日期：	20160912
-- 作者:	xxm
-- 描述:	游戏房间业务数据层接口
-- 注意:    尽可能业务逻辑独立(维护成本降到最低)
-----------------------------------------------------------------------------
local CURRENT_MODULE_NAME = ...

-- 优先 require
require 'app.platform.game.game_common.game_msg_ids'

local GameInterface = {}
-------------------------------------------------------------------------------------
local pfn_basic_game_data = nil
local m_game_manager = nil
---------------------------------------------------------------------------------------
GameInterface.EVENT_GAME_NOTIFY = "event_game_notify"
-------------------------------------------------------------------------------------
local m_game_impl = import(".logic.gamehandleimpl").new()
-------------------------------------------------------------------------------------
--事件
--[[

local event = {}
event.id = id
event.notify = notify
event.args = args

--]]
--事件通知  func为function FuncName(Event)
local event_notify_list = {}

--添加事件监听
function GameInterface.BsLuaAddNotifyEvent(id,notify,args)
	
	local event = {}
	event.id = id
	event.notify = notify 
	event.args = args
	
	event_notify_list[id] = event
end
--事件通知
local function BsLuaNotifyEvent(id,args)
	local event = event_notify_list[id]
	if nil == event then
		return
	end
	
	if args ~= nil then
		event.args = args
	end
	
	local event_notify = event.notify
	if event_notify ~= nil then
		event_notify(event)
	end
end
------------------------------------------------------------
function GameInterface.get_room_module()
    if(nil == m_game_manager) then
        return nil
    end
    return m_game_manager:get_game_room_mgr():get_room_module()
end

function GameInterface.get_user_module()
    if(nil == m_game_manager) then
        return nil
    end
    return m_game_manager:get_game_login_mgr():get_login_module()
end

function GameInterface.get_room_mgr()
    if(nil == m_game_manager) then
        return nil
    end
    return m_game_manager:get_game_room_mgr()
end

function GameInterface.get_timer_mgr()
    return m_game_manager:get_clientmain():get_timer_mgr()
end
function GameInterface.get_timer_mgr()
    return m_game_manager:get_clientmain():get_timer_mgr()
end
------------------------------------------------------------
--获取数据回调函数
function GameInterface.on_game_call_back(type_id, action_id, in_data)
	if pfn_basic_game_data ~= nil then
		return pfn_basic_game_data(type_id,action_id,in_data)
	else
		return nil
	end
end
------------------------------------------------------------
function GameInterface.get_room_player_info_byid(userID)
	local userInfo = GameInterface.on_game_call_back(0,10001,userID)
	return userInfo
end

function GameInterface.get_desk_people(deskNo)
	local deskPeople = GameInterface.on_game_call_back(0,10003,deskNo)
	return deskPeople
end

function GameInterface.get_self_info()
	local userInfo = GameInterface.on_game_call_back(0,10002,nil)

	return userInfo
end

function GameInterface.get_rooms_info()
    local rooms_info = GameInterface.on_game_call_back(0,10006,nil)

	return rooms_info
end


--退出游戏
function GameInterface.on_exit_game( )
--	local handle = nil
--	handle = cc.Director:getInstance():getScheduler():scheduleScriptFunc(
--    	function ()
--    		if handle ~= nil then
--              cc.Director:getInstance():getScheduler():unscheduleScriptEntry(handle)
--              handle = nil
--            end
--    		BzLuaNotifyEvent(EVENT_GAME_NOTIFY,EVENT_GAME_NOTIFY_UPDAATE_USER)
--    	end,1,false)
    GameInterface.on_game_call_back(1,20001,"")
	m_game_impl:uninit_game()
end
------------------------------------------------------------
--游戏初始化
function GameInterface.on_basic_game_init(parent)
    m_game_manager = parent
    m_game_impl:init_module(GameInterface)
    m_game_impl:init_game()
end

--游戏初始化
function GameInterface.on_basic_game_uinit(args)
	
end

--加载游戏
function GameInterface.on_basic_load_game(callback)
    local my_user_info = GameInterface.get_self_info()

    -- game scene node
    local game_scene = import('.ui.game_scene', CURRENT_MODULE_NAME).new(my_user_info.m_dwUserID)
    cc.Director:getInstance():replaceScene(game_scene)

    -- 把发送到 game_scene_mgr 的消息全部转发到 game_scene
    m_game_impl.game_scene_mgr.game_scene = game_scene

    game_scene.game_manager = m_game_manager
    game_scene.game_impl = m_game_impl

    --
    game_scene:init()

    -- init helper functions
    game_scene.get_self_info = function() return GameInterface.get_self_info() end
    game_scene.get_user_info_by_user_id = function(user_id) return GameInterface.on_game_call_back(0, 10001, user_id) end
    game_scene.do_force_user_leave = function(user_id, station) m_game_impl:do_force_user_leave(user_id, station) end
    game_scene.on_exit_game = function() GameInterface.on_exit_game() end

    -- 
    if callback then callback() end
end

--游戏行为
function GameInterface.on_basic_game_action(aid,hcode,buf,len,msg)
	m_game_impl:game_action(aid,hcode,buf,len,msg)
end

--转发基本消息(主)
function GameInterface.on_basic_game_diatach_message(mid,aid,hcode,buf,len,msg)
	m_game_impl:dispatch_message(mid,aid,hcode,buf,len,msg)
end

--------------------------------------------------------------------------
function GameInterface.set_callback(func_action)
	pfn_basic_game_data = func_action
end

--必须调用
function GameInterface.init_module(parent)
end

return GameInterface
