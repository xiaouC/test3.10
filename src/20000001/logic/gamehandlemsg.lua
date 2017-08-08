---------------------------------------------------------
-- 日期：	20151010
-- 作者:	xxm
-- 描述:	游戏消息
-- 注意:    尽可能业务逻辑独立(维护成本降到最低)
-----------------------------------------------------------------------------
--定义类
local GameHandleMsg = class("GameHandleMsg")

function GameHandleMsg:ctor()
end

-----------------------------------------------------------------------------

local m_game_module = import(".module.gamemodule").new()

local m_gameelement = game_msg_ids

local msg_stoc_state = nil					--游戏状态
local msg_create_cow = nil					--生成牛消息
local msg_catch_result = nil				--捕牛结果消息

----------------------------------Instance-------------------------------------------

--获取事件
function GameHandleMsg:GetBasicEvent()
    if(self.basicevent == nil ) then
        self.basicevent = g_basicevent.new()
    end
	return self.basicevent
end


local event_param =
{
   msg_code = 0,
   msg_data = nil,
}
 
function GameHandleMsg:BsAddNotifyEvent(id,notify,args)
	self:GetBasicEvent():BsAddNotifyEvent(id,notify,args)
end

function GameHandleMsg:NotifyEvent(id,args)
	self:GetBasicEvent():BsNotifyEvent(id,args)
end
-----------------------------------------------------------------------------
function GameHandleMsg:get_module()
    return m_game_module
end
-----------------------------------------------------------------------------

function GameHandleMsg:handle_game_message(aid,buf,len)
    print("xxm ====================    handle_game_message")

cclog("******************************")
cclog("******* subid:"..tostring(aid).."****************")
cclog("******************************")

	switch = {}
	switch[1] = handler(self,self.on_game_state)
	switch[5] = handler(self,self.on_focre_leave)
    switch[1000] = handler(self,self.on_maker_info)
    switch[1001] = handler(self,self.on_dice_info)
    switch[1002] = handler(self,self.on_card_info)
    switch[1003] = handler(self,self.on_out_card)
    switch[1004] = handler(self,self.on_get_card)
    switch[1005] = handler(self,self.on_block_info)
    switch[1006] = handler(self,self.on_block_result)
    switch[1007] = handler(self,self.on_notify_out_card)
    switch[1008] = handler(self,self.on_notify_wait_block)
    switch[1009] = handler(self,self.on_game_result)
    switch[1010] = handler(self,self.on_notify_ting)
    switch[1011] = handler(self,self.on_user_agree)
    switch[1012] = handler(self,self.on_single_game_record)
    switch[1013] = handler(self,self.on_game_over)
    switch[1014] = handler(self,self.on_fast_out)
    switch[1015] = handler(self,self.on_user_free_operate)
    switch[1016] = handler(self,self.on_user_free_result)
    switch[1017] = handler(self,self.on_game_config)
    switch[1101] = handler(self,self.on_update_my_gameinfo)
    switch[1022] = handler(self,self.on_notify_other_block)
	local func = switch[aid]
	if func ~= nil then
		func(buf,len)
	end
end

--初始化
function GameHandleMsg:init_handle_msg()
	reg_game_msg_handler(handler(self,self.handle_game_message))
end
--反初始化
function GameHandleMsg:un_init_handle_msg()
	reg_game_msg_handler(nil)
end

----------------------------------------------------------------------------
--request
--打骰
function GameHandleMsg:request_play_dice(data_object)
    if(nil == data_object) then
        return nil
    end

    local buf,len = self:get_module():format_maker_play_dice_request(data_object)
    api_basic_send_message(2005,2000,0,buf,len,true,false)
end
--出牌
function GameHandleMsg:request_out_card(data_object)
    if(nil == data_object) then
        return nil
    end
    local buf,len = self:get_module():format_user_out_card_request(data_object)
    api_basic_send_message(2005,2001,0,buf,len,true,false)
end
--拦牌操作
function GameHandleMsg:request_block_opreate(data_object)

    if(nil == data_object) then
        return nil
    end    

    local buf,len = self:get_module():format_user_block_operate_request(data_object)
    api_basic_send_message(2005,2002,0,buf,len,true,false)
end
--设置牌墙值
function GameHandleMsg:do_swap_wall_card(data_object)

    if(nil == data_object) then
        return nil
    end    

    local buf,len = self:get_module():format_swap_wall_card_request(data_object)
    api_basic_send_message(2005,2003,0,buf,len,true,false)
end


function GameHandleMsg:do_user_agree(data_object)
     if(nil == data_object) then
        return nil
    end    

    local buf,len = self:get_module():format_user_agree_request(data_object)
    api_basic_send_message(2005,2004,0,buf,len,true,false)
end

function GameHandleMsg:do_user_free_game(data_object)
    if(nil == data_object) then
        return nil
    end     
    local buf,len = self:get_module():format_swap_free_game_request(data_object)
    api_basic_send_message(2005,2005,0,buf,len,true,false)  
end

function GameHandleMsg:do_user_apply_game_info(data_object)

    if(nil == data_object) then
        return nil
    end     
    local buf,len = self:get_module():format_apply_update_owner_game_info(data_object)
    api_basic_send_message(2005,1202,0,buf,len,true,false)  
end
function GameHandleMsg:do_get_game_config(data_object)
    
    if(nil == data_object) then
        return nil
    end 
    local buf,len = self:get_module():format_apply_game_config(data_object)
    api_basic_send_message(2005,1201,0,buf,len,true,false)  

end
-----------------------------------------------------------------------------
--response
--游戏状态信息
function GameHandleMsg:on_game_state(buf,len)
	local game_state = self:get_module():parse_game_status(buf,len)

	local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_GAME_STATE
	param.msg_data = game_state
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--玩家被强制离开
function GameHandleMsg:on_focre_leave(buf,len)

	local force_leave = self:get_module():parse_force_leave(buf,len)

	local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_FORCE_LEAVE
	param.msg_data = force_leave
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)

end
--定庄消息
function GameHandleMsg:on_maker_info(buf,len)
    local make_info = self:get_module():parse_maker_info_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_MAKER_INFO
	param.msg_data = make_info
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--打骰子
function GameHandleMsg:on_dice_info(buf,len)
    local dice_info = self:get_module():parse_dice_info_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_DICE_INFO
	param.msg_data = dice_info
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end

--发牌消息
function GameHandleMsg:on_card_info(buf,len)
    local card_info = self:get_module():parse_hand_card_info_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_CARD_INFO
	param.msg_data = card_info
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--玩家出牌
function GameHandleMsg:on_out_card(buf,len)
    local out_card = self:get_module():parse_user_out_card_result_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_OUT_CARD
	param.msg_data = out_card
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--玩家摸牌
function GameHandleMsg:on_get_card(buf,len)
    local get_card = self:get_module():parse_user_touch_card_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_GET_CARD
	param.msg_data = get_card
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--通知拦牌消息
function GameHandleMsg:on_block_info(buf,len)
    local block_info = self:get_module():parse_notify_block_info_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_BLOCK_INFO
	param.msg_data = block_info
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--拦牌结果消息
function GameHandleMsg:on_block_result(buf,len)
    local block_result = self:get_module():parse_notify_block_reslut(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_BLOCK_RESULT
	param.msg_data = block_result
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--通知玩家出牌
function GameHandleMsg:on_notify_out_card(buf,len)
    local notify_out_card = self:get_module():parse_notify_out_card_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_NOTIFY_OUT_CARD
	param.msg_data = notify_out_card
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--等待拦牌操作消息
function GameHandleMsg:on_notify_wait_block(buf,len)
    local notify_wait_block = self:get_module():parse_notify_wait_block_operate_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_NOTIFY_NOTIFY_WAIT_BLOCK
	param.msg_data = notify_wait_block
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--游戏一把结束
function GameHandleMsg:on_game_result(buf,len)
    local game_result = self:get_module():parse_notify_game_result_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_NOTIFY_GAME_RESULT
	param.msg_data = game_result
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--游戏总局数结束
function GameHandleMsg:on_game_over(buf,len)
    local game_over = self:get_module():parse_notify_total_record_game_info(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_NOTIFY_GAME_RESULT_OVER
	param.msg_data = game_over
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--快速出牌
function GameHandleMsg:on_fast_out(buf,len)
    -- body
    local fast_cout = self:get_module():parse_notify_fast_out_info(buf,len)
    local param = event_param
    param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_FAST_OUT_INOF
    param.msg_data = fast_cout
    self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--玩家申请解散游戏操作
function GameHandleMsg:on_user_free_operate(buf,len)

    local free_operate = self:get_module():parse_notify_user_free_operate(buf,len)
    local param = event_param
    param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_USER_FREE_OPERATE
    param.msg_data = free_operate
    self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end
--解散游戏结果
function GameHandleMsg:on_user_free_result(buf,len)

    local free_reslut = self:get_module():parse_notify_user_free_result(buf,len)
    local param = event_param
    param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_USER_FREE_RESULT
    param.msg_data = free_reslut
    self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end 
--游戏配置文件
function  GameHandleMsg:on_game_config(buf,len) 
    local game_config = self:get_module():parse_notify_game_config(buf,len)
    local param = event_param
    param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_GAME_CONFIG
    param.msg_data = game_config
    self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
    
end
--更新自己游戏信息
function GameHandleMsg:on_update_my_gameinfo(buf,len) 

    local game_info = self:get_module():parse_notify_owner_game_info(buf,len)
    local param = event_param
    param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_OWNER_GAME_INFO
    param.msg_data = game_info
    self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)

end
--听牌消息
function GameHandleMsg:on_notify_ting(buf,len)

    local notify_ting = self:get_module():parse_notify_ting_response(buf,len)
    local param = event_param
	param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_NOTIFY_TING
	param.msg_data = notify_ting
	self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)

end
--玩家准备消息
function GameHandleMsg:on_user_agree(buf,len)

    local user_agree = self:get_module():parse_user_agree_response(buf,len)
    local param = event_param
    param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_USER_READY
    param.msg_data = user_agree
    self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)
end

--单局记录
function GameHandleMsg:on_single_game_record(buf,len)

    local single_game = self:get_module():parse_single_game_record_response(buf,len)
    local param = event_param
    param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_NOTIFY_GAME_RESULT_ONE
    param.msg_data = single_game
    self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)

end

--通知等待其他玩家拦牌
function GameHandleMsg:on_notify_other_block(buf,len)
    
    local other_block = self:get_module():parse_notify_other_block(buf,len)
    local param = event_param
    param.msg_code = m_gameelement.EVENT_GAME_NOTIFY_WAIT_OTHER_BLOCK
    param.msg_data = other_block
    self:NotifyEvent(m_gameelement.EVENT_GAME_NOTIFY,param)

end

function GameHandleMsg:UserLeftRequest(userid,leaveid)
	local request = {}
	request.m_userid = userid
	
	local buf,len = self:get_module():FormatBufferByUserLeftRequest(request)
	
	api_basic_send_message(2002,leaveid,0,buf,len,1,true)
end
-----------------------------------------------------------------------------
function GameHandleMsg:init_module(parent)
end

--return object
return GameHandleMsg
