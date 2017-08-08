---------------------------------------------------------
-- 日期：	20150807
-- 作者:	xxm
-- 描述:	游戏逻辑协议定义和序列化和反序列化API
---------------------------------------------------------
--定义类
local GameModule = class("GameModule")
function GameModule:ctor()
end
--------------------------------------------------------
--结构定义

--定庄消息
local t_maker_info_response_len = 1
local t_maker_info_response =
{
    m_chair_id = 0,                 --庄家位置
}

--骰子消息
local t_dice_info_response_len = 2
local t_dice_info_response =
{
    m_dice = {},                    --骰子信息
}

--发牌消息
local t_hand_card_info_response_len = 60
local t_hand_card_info_response =
{
    m_hand_card = {{},{},{},{}},   --玩家手牌
    m_card_count = {},              --玩家手牌数               
}

--玩家出牌
local t_user_out_card_result_response_len = 2
local t_user_out_card_result_response = 
{
    m_chair_id = 0,                 --玩家位置
    m_card_value = 0,               --牌值
}

--玩家摸牌
local t_user_touch_card_response_len = 3
local t_user_touch_card_response =
{
    m_chair_id = 0,                 --玩家位置
    m_card_value = 0,               --牌值
    m_bgang = false,
}

--通知玩家拦牌消息
local t_notify_block_info_response_len = 33
local t_notify_block_info_response =
{
    m_card_value = 0,               --牌值 
    m_out = false,                  --出牌/摸牌
    m_block_level = 0,              --玩家拦牌等级
    m_checked_id = 0,               --被拦牌的人  
    m_block_info = {{},{},{},{},{},},              --可执行拦牌的牌
    m_block_index = 0,              --拦牌索引
}
--通知玩家拦牌操作结果
local t_notify_block_reslut_response_len = 8
local t_notify_block_reslut_response =
{
    m_chair_id = 0,                 --玩家位置
    m_opreate_type = 0,             --操作类型 0 放弃 0x01 吃  0x02 碰 0x04 杠 0x08 听 0x10 胡
    m_card_value = {},              --牌值 0-3 选择的拦牌数据
    m_checked_id = 0,               --被拦牌的人
    m_block_subtype = 0,
}
--通知玩家出牌
local t_notify_out_card_response_len = 1
local t_notify_out_card_response =
{
    m_chair_id = 0,                 --玩家位置
}

--通知玩家等待拦牌操作消息
local t_notify_wait_block_operate_response_len = 7
local t_notify_wait_block_operate_response =
{
    m_card_value = 0,
    m_out = 0,
    m_block_level = {},
    m_checked_id = 0,               --被拦牌的人
}
--快速出牌
local t_notify_fast_out_len = 9
local t_notify_fast_out = 
{
    m_chair_id = 255,           --玩家位置
    m_add_fast_count = 0,         --添加个数
    m_fast_all_count = 0,         --总数
}

--
local t_notify_free_operate_len =11
local  t_notify_free_operate =
{ 
    m_apply_id = 0,             --申请者ID
    m_apply_chair = 0,          --申请者位置
    m_userid = 0,               --操作玩家ID
    m_chair_id = 0,             --操作玩家位置
    m_free = false,             --操作结果
     
}

local t_notify_user_free_result_len = 6
local t_notify_user_free_result  =
{
    m_owner_id = 0,                 --玩家ID
    m_owner_chair = 255,
    m_result = false,               --是否解散成功
}
local t_notify_game_config_len = 19
local t_notify_game_config = 
{ 
      m_room_card = 0,
      m_hu_qxd = false,
      m_hongaward_ma = 0,
      m_award_ma = 0,
      m_luck_mode = 0,
      m_all_ma = false, 
      m_allow_zp = false,
}
local t_notify_owner_game_info_len =  108+20
local t_notify_owner_game_info = 
{

        m_chair_id = 0,
        m_block_data = {},
        m_hand_card_count = 0,
        m_out_card_count = 0,
        m_block_count = 0,
        m_hand_card = {},
        m_out_card = {}, 
	    m_draw_card = 0,				 

}


--
local t_notify_game_result_response_len =399
local t_notify_game_result_response =
{
    m_win_type = 0,                         --牌方式 0：荒庄   1：自摸 2：放炮  3：抢杠
    m_win = {},                             --胡牌玩家
    m_hand_card = {{},},                    --玩家手牌
    m_win_card = 0,                         --胡的牌
    m_dianpao_id = 0,                       --放炮的玩家
    m_gang_score = {},                      --玩家杠分
    m_fan_score = {},                       --玩家胡牌番数
    m_luck_card = {},                       --扎码牌值 
    m_total_score = {},                     --玩家总分
    m_all_king = false,                     --是否是全码
	m_fast_count = {},      				--快速次数
	m_out_count = {},						--超时次数
	m_reward_gift = {},                     --奖励礼券
    m_user_luck_count = {},                 --玩家中码个数
    m_win_score = {},                       --玩家输赢分
    m_luck_score = {},
    m_mgang_count = {},
    m_agang_count = {},
    m_bgang_count = {},
    m_fgang_count = {},
}

local t_notify_total_record_game_info_len = 188+32+16
local t_notify_total_record_game_info = 
{
    m_play_count = 0,                       --总局数
    m_win_count = {},                       --胡牌次数
    m_qiang_win_count = {},                 --抢杠胡次数
    m_ming_gang = {},                       --明杠次数
    m_an_gang = {},                         --暗杠次数 
    m_bu_gang = {},                         --补杠次数 
    m_luck_count = {},                      --中码次数
    m_fan_score = {},                       --玩家得分
    m_gang_score = {},                      --杠分
	m_fast_count = {},      				--快速次数
	m_out_count = {},						--超时次数
	m_reward_gift = {},                     --奖励礼券
    m_finish_time = 0,                      --结束时间
    m_dian_pao_win_count={},
    m_zhua_pao_win_count={},
    m_zm_win_count = {},                    --自摸次数
} 



local t_notify_ting_response_len = 872
local t_notify_ting_response = 
{
    ting_list = {{},},              --听的牌
    ting_list_count= {{},},         --听牌个数
    win_card_count = {},            ---胡牌个数
    max_win_count = 0               --最大胡牌个数 
}
local t_user_agree_response_len = 6
local t_user_agree_response = 
{
      userid = 0,
      chair_id = 0,
      bagree = false,
}
--游戏状态基本信息
local t_game_base_info_len = 138
local t_game_base_info =
{
    m_game_status = 0,              --游戏状态
    m_user_id = {},                 --玩家id
    m_user_score = {},              --玩家分数 
    m_user_cut = {},
	m_total_play_count = 0,
	m_cur_play_count = 0,  
	m_bOpenFree = false,				--是否开启解散
	m_free_apply_id = 0,			    --申请者id
	m_free_apply_station=255,			--申请者位置 
	m_bUserChose = {},                  --玩家是否操作
	m_free_remain_time = 0,             --剩余时间 
    mj_status = 0,                      --麻将阶段
    m_banker_station = 255,             --庄家位置
    m_fast_count = {},                  --快速出牌次数
    m_out_count = {},                   --超时次数  
    m_my_station = 255,                 --自己的位置
    m_privater_station = 255,           --房主位置
    m_privater_id = 0,                  --房主ID
    m_free_time = 0,                    --解散包间时间
    m_game_config = clone(t_notify_game_config),                 --游戏配置
}

--游戏准备阶段
local t_game_status_ready_len = t_game_base_info_len+4
local t_game_status_ready =
{
    m_base_info = clone(t_game_base_info),
    m_user_ready = {},
}

--拦牌信息
local t_game_status_block_len = 8
local t_game_status_block = 
{
    m_block_type = 0,               --拦牌类型 1:吃 2 碰 4 杠
    m_block_sub_type = 0,           --拦牌子类型  1:暗杠 2 明杠 4 补杠
    m_blocked_card = 0,             --被拦的牌
    m_blocked_user = 255,           --被拦的人
    m_block_data = {},                --拦牌数据
}

-- 玩家信息
local t_game_status_user_info_len = 107+20
local t_game_status_user_info = 
{
    m_block_info = {}, 
    m_hand_card_count = 0,
    m_out_card_count = 0,
    m_block_count = 0,
    m_hand_card = {},
    m_out_card = {},   
    m_draw_card = 0,                --自己摸的牌  

}


--游戏开始阶段
local t_game_status_play_len = 670+20*4 --t_game_base_info_len + t_game_status_user_info_len*4  
local t_game_status_play =
{
    m_base_info = clone(t_game_base_info),
    m_cur_operate_station = 0,
    m_dice = {},                                   --骰子
    m_cur_operate_station =  255,                 --当前操作玩家
    m_cur_gams_stats = 0,                         --当前游戏状态
    m_cur_block_level = 0,                        --当前拦牌等级
    m_cur_check_user = 255,                       --当前被拦的人
    m_cur_check_card = 0,                         --当前被拦的牌
    m_bdraw_stats = true,                          --是否是摸牌 
    m_wall_count = 0,                              --牌墙数量
    user_info = {},                                --玩家信息
    m_gang_all_count = 0,                           --杠的总数 
    m_ting = false,
    m_ting_list= {},           				--听的牌 
    m_ting_count = {},			    --听牌的个数
    m_block_info = {{},},            --自己拦牌
    m_block_index = 0,              --拦牌索引
}

local single_game_record_len = 131+48
local single_game_record = 
{
    m_index = 0,
    m_win_type = 0,
    m_dianpaoer = 0,
    m_win_card = 0,
    m_finish_time = 0,
    m_win = {},
    m_total_score = {},
    m_gang_score = {},
    m_luck_count = {},
    m_mgang_count = {},
    m_agang_count = {},
    m_bgang_count = {},
    m_fgang_count = {}, 
	m_fast_count = {},      				--快速次数
	m_out_count = {},						--超时次数
	m_reward_gift = {},                     --奖励礼券
} 

local force_user_leave_len = 10
local force_user_leave = 
{ 
  m_dwOwnerID = 0,          --房主ID
  m_dwUserID = 0,           --被踢玩家
  m_bDeskNO = 0,             --桌子号
  m_bChairID = 0,            --被踢位置

}



------------------------------------------------------------------------------------

--庄家打骰子
local maker_play_dice_request_len = 1
GameModule.maker_play_dice_request =
{
    m_chair_id = 0,                 --庄家位置
}

--玩家出牌
local user_out_card_request_len = 2
GameModule.user_out_card_request =
{
    m_chair_id = 0,                 --玩家位置
    m_card_value = 0,               --牌值
}

--玩家拦牌操作
local user_block_operate_request_len = 11
GameModule.user_block_operate_request = 
{
    m_chair_id = 0,                 --玩家位置
    m_opreate_type = 0,             --操作类型 0 放弃 0x01 吃  0x02 碰 0x04 杠 0x08 听 0x10 胡
    m_card_value = "",               --牌值
    m_out = 0,                      --出牌/摸牌
    m_block_index = 0,              --索引
}
local swap_wall_card_request_len = 1
GameModule.swap_wall_card_request = 
{  
    m_card_value = 0,               --牌值
}

--解散游戏
local free_game_len = 8
GameModule.free_game = 
{
    m_dwUserID = 0,             --玩家id
    m_bChairID = 255,           --玩家位置
    m_free = false,             --是否解散

}
--申请更新游戏信息
local apply_game_info_len = 5
GameModule.apply_game_info  = 
{
    m_user_id = 0,             --玩家id
    m_chair_id = 255,           --玩家位置
}
local user_agree_request_len = 6
--申请游戏配置 
local apply_game_config_len = 1
GameModule.apply_game_config  = 
{ 
    m_chair_id = 255,           --玩家位置
}
GameModule.user_agree_request = 
{
     userid = 0,
     chair_id = 0,
     bagree = false,
}
local  USER_PLAY_GAME = 6

--玩家离开请求
local msg_user_left_len = 4
local msg_user_left = 
{
    m_userid = 0,               --用户ID
} 

--通知等待其他人拦牌
local  t_notify_other_block_len = 2
local  t_notify_other_block =
{ 
    m_chair_id = 0,                 --玩家位置
    m_block_level = 0,              --玩家拦牌等级
     
}
------------------------------------------------------------------------------------
--parset function

function GameModule:parse_notify_other_block(buf,len) 
   if(nil == buf or len ~= t_notify_other_block_len) then
        BASIC_LOG_ERROR("GameModule:parse_notify_other_block(nil == buf or len ~= size)")
        return nil
    end
      

     local notify_other_block_info = clone(t_notify_other_block) 
     notify_other_block_info.m_chair_id = buf:OffsetGetAsUInt8(0) 
     notify_other_block_info.m_block_level = buf:OffsetGetAsUInt8(1)  
     return notify_other_block_info
end

function GameModule:parse_user_agree_response(buf,len)
    if(nil == buf or len ~= t_user_agree_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_user_agree_response(nil == buf or len ~= size)")
        return nil
    end

    local user_agree = clone(t_user_agree_response)
    user_agree.userid = buf:OffsetGetAsUInt32(0) 
    user_agree.chair_id = buf:OffsetGetAsUInt8(4) 
    user_agree.bagree = buf:OffsetGetAsBoolean(5) 
    return user_agree
end
function GameModule:parse_notify_ting_response(buf,len)
    if(nil == buf or len ~= t_notify_ting_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_notify_ting_response(nil == buf or len ~= size)")
        return nil
    end

    local notify_ting = clone(t_notify_ting_response)
    for i = 1, 14 do    
        local temp = notify_ting.ting_list[i] 
        local temp = {} 
        for j = 1, 29 do 
            temp[j] = buf:OffsetGetAsUInt8(0+(1*(i-1)*29 + 1*(j-1))) 
        end 
        notify_ting.ting_list[i] = temp
    end   
    for i = 1, 14 do 
	    local temp = notify_ting.ting_list_count[i] 
	    local temp = {} 
	    for j = 1, 29 do 
		    temp[j] = buf:OffsetGetAsInt8(406+(1*(i-1)*29 + 1*(j-1))) 
	    end 
        notify_ting.ting_list_count[i] = temp
    end 

    for i=1, 14 do
         notify_ting.win_card_count[i]= buf:OffsetGetAsUInt32(812+(i-1)*4) 
    end
    notify_ting.max_win_count = buf:OffsetGetAsUInt32(868)  

    return notify_ting
end

function GameModule:parse_single_game_record_response(buf,len)
    if(nil == buf or len ~= single_game_record_len) then
        BASIC_LOG_ERROR("GameModule:single_game_record_len(nil == buf or len ~= size)")
        return nil
    end
    local single_game_record_info = clone(single_game_record) 

    single_game_record_info.m_index = buf:OffsetGetAsUInt32(0) 
    single_game_record_info.m_win_type = buf:OffsetGetAsInt8(4) 
    single_game_record_info.m_dianpaoer = buf:OffsetGetAsInt8(5) 
    single_game_record_info.m_win_card = buf:OffsetGetAsInt8(6) 
    single_game_record_info.m_finish_time = tostring(BasicInt64.New(buf:OffsetGetAsBasicInt64(7) )) 
    for i = 1, 4 do 
        single_game_record_info.m_win[i] = buf:OffsetGetAsBoolean(15+1*(i-1)) 
    end 
    for i = 1, 4 do 
        single_game_record_info.m_total_score[i] = buf:OffsetGetAsInt32(19+4*(i-1)) 
    end 
    for i = 1, 4 do 
        single_game_record_info.m_gang_score[i] = buf:OffsetGetAsInt32(35+4*(i-1)) 
    end 
    for i = 1, 4 do 
        single_game_record_info.m_luck_count[i] = buf:OffsetGetAsInt32(51+4*(i-1)) 
    end 
    for i = 1, 4 do 
        single_game_record_info.m_mgang_count[i] = buf:OffsetGetAsInt32(67+4*(i-1)) 
    end 
    for i = 1, 4 do 
        single_game_record_info.m_agang_count[i] = buf:OffsetGetAsInt32(83+4*(i-1)) 
    end 
    for i = 1, 4 do 
        single_game_record_info.m_bgang_count[i] = buf:OffsetGetAsInt32(99+4*(i-1)) 
    end 
    for i = 1, 4 do 
        single_game_record_info.m_fgang_count[i] = buf:OffsetGetAsInt32(115+4*(i-1)) 
    end 
    
    for i = 1, 4 do 
        single_game_record_info.m_fast_count[i] = buf:OffsetGetAsInt32(131+4*(i-1)) 
    end 
     for i = 1, 4 do 
        single_game_record_info.m_out_count[i] = buf:OffsetGetAsInt32(131+16+4*(i-1)) 
    end 
    for i = 1, 4 do 
        single_game_record_info.m_reward_gift[i] = buf:OffsetGetAsInt32(131+32+4*(i-1)) 
    end 

    return single_game_record_info
end

function GameModule:parse_notify_fast_out_info( buf,len )
    -- body
    if( nil == buf or len ~= t_notify_fast_out_len) then
        BASIC_LOG_ERROR("GameModule:t_notify_fast_out_len(nil == buf or len ~= size)")
        return nil
    end
      
    local sc_notify_fast_out = clone(t_notify_fast_out) 
    sc_notify_fast_out.m_chair_id = buf:OffsetGetAsUInt8(0) 
    sc_notify_fast_out.m_add_fast_count = buf:OffsetGetAsUInt32(1) 
    sc_notify_fast_out.m_fast_all_count = buf:OffsetGetAsUInt32(5) 

    return sc_notify_fast_out
end
function GameModule:parse_notify_user_free_operate(buf,len)

    if( nil == buf or len ~= t_notify_free_operate_len) then
        BASIC_LOG_ERROR("GameModule:t_notify_free_operate_len(nil == buf or len ~= size)")
        return nil
    end
    local user_free_operate = clone(t_notify_free_operate)   
    user_free_operate.m_apply_id = buf:OffsetGetAsUInt32(0) 
    user_free_operate.m_apply_chair = buf:OffsetGetAsUInt8(4) 
    user_free_operate.m_userid = buf:OffsetGetAsUInt32(5) 
    user_free_operate.m_chair_id = buf:OffsetGetAsUInt8(9) 
    user_free_operate.m_free = buf:OffsetGetAsBoolean(10) 

    return user_free_operate
end

function GameModule:parse_notify_user_free_result(buf,len)

    if( nil == buf or len ~= t_notify_user_free_result_len) then
        BASIC_LOG_ERROR("GameModule:t_notify_user_free_result_len(nil == buf or len ~= size)")
        return nil
    end
    local user_free_result = clone(t_notify_user_free_result) 
    user_free_result.m_owner_id = buf:OffsetGetAsUInt32(0) 
    user_free_result.m_owner_chair = buf:OffsetGetAsUInt8(4)  
    user_free_result.m_result = buf:OffsetGetAsBoolean(5) 

    return user_free_result
end

function GameModule:parse_notify_game_config(buf,len)
    
    if( nil == buf or len ~= t_notify_game_config_len) then
        BASIC_LOG_ERROR("GameModule:t_notify_game_config_len(nil == buf or len ~= size)")
        return nil
    end
    local game_config = clone(t_notify_game_config) 
    game_config.m_room_card = buf:OffsetGetAsInt32(0) 
    game_config.m_hu_qxd = buf:OffsetGetAsBoolean(4) 
    game_config.m_hongaward_ma = buf:OffsetGetAsInt32(5) 
    game_config.m_award_ma = buf:OffsetGetAsInt32(9) 
    game_config.m_luck_mode = buf:OffsetGetAsInt32(13) 
    game_config.m_all_ma = buf:OffsetGetAsBoolean(17) 
    game_config.m_allow_zp = buf:OffsetGetAsBoolean(18) 
    
    return game_config
end

function GameModule:parse_notify_owner_game_info(buf,len)
    if( nil == buf or len ~= t_notify_owner_game_info_len) then
        BASIC_LOG_ERROR("GameModule:t_notify_owner_game_info_len(nil == buf or len ~= size)")
        return nil
    end
    
    local update_user_info = clone(t_notify_owner_game_info) 

    update_user_info.m_chair_id = buf:OffsetGetAsInt8(0) 
 
    local block_item = {}
    for m=1,5  do 
        local  block_info = {} 

        block_info.m_block_type = buf:OffsetGetAsInt8(1  + (m-1)*t_game_status_block_len +0)   
        block_info.m_block_sub_type = buf:OffsetGetAsInt8(1  + (m-1)*t_game_status_block_len +1)   
        block_info.m_blocked_card = buf:OffsetGetAsInt8(1  + (m-1)*t_game_status_block_len + 2)    
        block_info.m_blocked_user = buf:OffsetGetAsInt8(1 + (m-1)*t_game_status_block_len +3)   
        local  block_data ={} 
        for j=1,4 do
            block_data[j] =  buf:OffsetGetAsInt8(1  + (m-1)*t_game_status_block_len +4 + (j-1)*1)  
        end 
        block_info.m_block_data = block_data 

        block_item[m] = block_info
    end
    update_user_info.m_block_data = block_item


    update_user_info.m_hand_card_count = buf:OffsetGetAsInt32(1 + t_game_status_block_len*5 + 0)  
    update_user_info.m_out_card_count = buf:OffsetGetAsInt32(1  + t_game_status_block_len*5 + 4)  
    update_user_info.m_block_count = buf:OffsetGetAsInt32(1 + t_game_status_block_len*5  + 8)  
    local hand_card = {}
    for j=1,14 do
            hand_card[j] = buf:OffsetGetAsInt8(1 + t_game_status_block_len*5  + 12 + (j-1)*1)  
    end
    update_user_info.m_hand_card = hand_card
        
    local out_card = {}
    for j=1,60 do
        out_card[j]= buf:OffsetGetAsInt8(1 + t_game_status_block_len*5  + 26+ (j-1)*1)  
    end 
    update_user_info.m_out_card = out_card 
         
     update_user_info.m_draw_card = buf:OffsetGetAsInt8(1 + t_game_status_block_len*5 +86 )
    return update_user_info
end
function GameModule:parse_notify_total_record_game_info(buf,len)
    if(nil == buf or len ~= t_notify_total_record_game_info_len) then
        BASIC_LOG_ERROR("GameModule:parse_notify_total_record_game_info(nil == buf or len ~= size)")
        return nil
    end
    local total_record_game_info = clone(t_notify_total_record_game_info) 
    total_record_game_info.m_play_count = buf:OffsetGetAsUInt32(0) 
    for i = 1, 4 do 
      total_record_game_info.m_win_count[i] = buf:OffsetGetAsUInt32(4+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_qiang_win_count[i] = buf:OffsetGetAsUInt32(20+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_ming_gang[i] = buf:OffsetGetAsUInt32(36+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_an_gang[i] = buf:OffsetGetAsUInt32(52+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_bu_gang[i] = buf:OffsetGetAsUInt32(68+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_luck_count[i] = buf:OffsetGetAsUInt32(84+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_fan_score[i] = buf:OffsetGetAsInt32(100+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_gang_score[i] = buf:OffsetGetAsInt32(116+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_fast_count[i] = buf:OffsetGetAsUInt32(132+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_out_count[i] = buf:OffsetGetAsUInt32(148+4*(i-1)) 
    end 
    for i = 1, 4 do 
      total_record_game_info.m_reward_gift[i] = buf:OffsetGetAsUInt32(164+4*(i-1)) 
    end 
    total_record_game_info.m_finish_time = tostring(BasicInt64.New(buf:OffsetGetAsBasicInt64(180) )) 
       for i = 1, 4 do 
      total_record_game_info.m_dian_pao_win_count[i] = buf:OffsetGetAsUInt32(188+4*(i-1)) 
    end 
     for i = 1, 4 do 
      total_record_game_info.m_zhua_pao_win_count[i] = buf:OffsetGetAsUInt32(188+16+4*(i-1)) 
    end  
    for i = 1, 4 do 
      total_record_game_info.m_zm_win_count[i] = buf:OffsetGetAsUInt32(188+32+4*(i-1)) 
    end  
    
    return total_record_game_info
end


function GameModule:parse_notify_game_result_response(buf,len)
    if(nil == buf or len ~= t_notify_game_result_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_notify_game_result_response(nil == buf or len ~= size)")
        return nil
    end
    local notify_game_result = clone(t_notify_game_result_response) 

    notify_game_result.m_win_type = buf:OffsetGetAsInt32(0) 
    for i = 1, 4 do 
      notify_game_result.m_win[i] = buf:OffsetGetAsBoolean(4+1*(i-1)) 
    end 
    for i = 1, 4 do 
	    local temp = notify_game_result.m_hand_card[i] 
	    local temp = {} 
	    for j = 1, 14 do 
		    temp[j] = buf:OffsetGetAsInt8(8+(1*(i-1)*14 + 1*(j-1))) 
	    end  
        notify_game_result.m_hand_card[i] = temp
    end 
    notify_game_result.m_win_card = buf:OffsetGetAsInt8(64) 
    notify_game_result.m_dianpao_id = buf:OffsetGetAsInt8(65) 
    for i = 1, 4 do 
      notify_game_result.m_gang_score[i] = buf:OffsetGetAsInt32(66+4*(i-1)) 
    end 
    for i = 1, 4 do 
      notify_game_result.m_fan_score[i] = buf:OffsetGetAsInt32(82+4*(i-1)) 
    end 
    for i = 1, 108 do 
      notify_game_result.m_luck_card[i] = buf:OffsetGetAsInt8(98+1*(i-1)) 
    end 
    local offset = 40

    for i = 1, 4 do 
        notify_game_result.m_total_score[i] = tostring(BasicInt64.New( buf:OffsetGetAsBasicInt64(166+offset+8*(i-1)) )) 
    end 

    notify_game_result.m_all_king = buf:OffsetGetAsBoolean(198+offset) 

    for i = 1, 4 do 
        notify_game_result.m_fast_count[i] = buf:OffsetGetAsInt32(199+offset+4*(i-1)) 
    end 
     for i = 1, 4 do 
        notify_game_result.m_out_count[i] = buf:OffsetGetAsInt32(199+offset+16+4*(i-1)) 
    end 
    for i = 1, 4 do 
        notify_game_result.m_reward_gift[i] = buf:OffsetGetAsInt32(199+offset+32+4*(i-1)) 
    end 

    for i = 1, 4 do 
        notify_game_result.m_user_luck_count[i] = buf:OffsetGetAsInt32(199+offset+48+4*(i-1)) 
    end 

    for i = 1, 4 do 
        notify_game_result.m_win_score[i] = buf:OffsetGetAsInt32(263+offset+4*(i-1)) 
    end 

    for i = 1, 4 do 
        notify_game_result.m_luck_score[i] = buf:OffsetGetAsInt32(263+offset+16+4*(i-1)) 
    end 

    for i = 1, 4 do 
        notify_game_result.m_mgang_count[i] = buf:OffsetGetAsInt32(335+4*(i-1)) 
    end 
    for i = 1, 4 do 
        notify_game_result.m_agang_count[i] = buf:OffsetGetAsInt32(351+4*(i-1)) 
    end 
    for i = 1, 4 do 
        notify_game_result.m_bgang_count[i] = buf:OffsetGetAsInt32(367+4*(i-1)) 
    end 
    for i = 1, 4 do 
        notify_game_result.m_fgang_count[i] = buf:OffsetGetAsInt32(383+4*(i-1)) 
    end 


    return notify_game_result
end


function GameModule:parse_notify_wait_block_operate_response(buf,len)
    if(nil == buf or len ~= t_notify_wait_block_operate_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_notify_wait_block_operate_response(nil == buf or len ~= size)")
        return nil
    end
    local notify_wait = clone(t_notify_wait_block_operate_response)
    notify_wait.m_card_value = buf:OffsetGetAsUInt8(0) 
    notify_wait.m_out = buf:OffsetGetAsBoolean(1) 
    for i = 1, 4 do 
      notify_wait.m_block_level[i] = buf:OffsetGetAsInt8(2+1*(i-1)) 
    end 
    notify_wait.m_checked_id = buf:OffsetGetAsUInt8(6) 
    return notify_wait
end

function GameModule:parse_notify_block_reslut(buf,len)
    if(nil == buf or len ~= t_notify_block_reslut_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_notify_block_reslut(nil == buf or len ~= size)")
        return nil
    end
    local notify_block_reslut = clone(t_notify_block_reslut_response)
    notify_block_reslut.m_chair_id = buf:OffsetGetAsUInt8(0) 
    notify_block_reslut.m_opreate_type = buf:OffsetGetAsUInt8(1) 
    for i = 1, 4 do 
      notify_block_reslut.m_card_value[i] = buf:OffsetGetAsInt8(2+1*(i-1)) 
    end 
    notify_block_reslut.m_checked_id = buf:OffsetGetAsUInt8(6) 
    notify_block_reslut.m_block_subtype = buf:OffsetGetAsUInt8(7) 
    
    return notify_block_reslut
end
function GameModule:parse_force_leave(buf,len)
  if(nil == buf or len ~= force_user_leave_len) then
        BASIC_LOG_ERROR("GameModule:parse_force_leave(nil == buf or len ~= size)")
        return nil
    end
    
    local force_info = clone(force_user_leave)
     
    force_info.m_dwOwnerID= buf:OffsetGetAsUInt32(0) 
    force_info.m_dwUserID= buf:OffsetGetAsUInt32(4) 
    force_info.m_bDeskNO= buf:OffsetGetAsUInt8(8) 
    force_info.m_bChairID= buf:OffsetGetAsUInt8(9) 


    
    return force_info
end
function GameModule:parse_game_status(buf,len)
    
    local game_bese = self:parse_game_base_info(buf,len)
    if(nil == game_bese) then
        return nil
    end

    if(game_bese.m_game_status == USER_PLAY_GAME) then
        return self:parse_game_status_play(buf,len)
    else
        return self:parse_game_status_ready(buf,len)
    end
end

function GameModule:parse_game_status_play(buf,len)
    if(nil == buf or len ~= t_game_status_play_len) then
        BASIC_LOG_ERROR("GameModule:parse_game_status_play(nil == buf or len ~= size)")
        return nil
    end

    local game_status_play = clone(t_game_status_play)

    game_status_play.m_base_info = self:parse_game_base_info(buf,len)

    local offset = t_game_base_info_len
 
    for i = 1,2  do 
         game_status_play.m_dice[i] = buf:OffsetGetAsInt8(offset+ 1*(i-1)) 
    end
    game_status_play.m_cur_operate_station = buf:OffsetGetAsInt8(offset+ 2) 
    game_status_play.m_cur_gams_stats = buf:OffsetGetAsInt8(offset+ 3) 
    game_status_play.m_cur_block_level = buf:OffsetGetAsInt8(offset+ 4) 
    game_status_play.m_cur_check_user = buf:OffsetGetAsInt8(offset+ 5) 
    game_status_play.m_cur_check_card = buf:OffsetGetAsInt8(offset+ 6) 
    game_status_play.m_bdraw_stats = buf:OffsetGetAsBoolean(offset+ 7) 
    game_status_play.m_wall_count = buf:OffsetGetAsInt32(offset+ 8)   

    local  user_len  = 0

    for i=1,4 do
        local  user_info = {}

        local block_item = {}
        for m=1,5  do 
            local  block_info = {} 

            block_info.m_block_type = buf:OffsetGetAsInt8(offset+ 12 + (i-1)*t_game_status_user_info_len + (m-1)*t_game_status_block_len +0)   
            user_len = user_len + 1
            block_info.m_block_sub_type = buf:OffsetGetAsInt8(offset+ 12 + (i-1)*t_game_status_user_info_len + (m-1)*t_game_status_block_len +1)   
            user_len = user_len + 1
            block_info.m_blocked_card = buf:OffsetGetAsInt8(offset+ 12 + (i-1)*t_game_status_user_info_len + (m-1)*t_game_status_block_len + 2)   
              user_len = user_len +1
            block_info.m_blocked_user = buf:OffsetGetAsInt8(offset+ 12 + (i-1)*t_game_status_user_info_len + (m-1)*t_game_status_block_len +3)  
              user_len = user_len +1
            local  block_data ={} 
            for j=1,4 do
                block_data[j] =  buf:OffsetGetAsInt8(offset+ 12 + (i-1)*t_game_status_user_info_len + (m-1)*t_game_status_block_len +4 + (j-1)*1) 
                user_len = user_len +1
            end 
            block_info.m_block_data = block_data 

            block_item[m] = block_info
        end
         user_info.block_info = block_item
        
       



        user_info.m_hand_card_count = buf:OffsetGetAsInt32(offset+ 12 + (i-1)*t_game_status_user_info_len + t_game_status_block_len*5 + 0) 
        user_len = user_len +4
        user_info.m_out_card_count = buf:OffsetGetAsInt32(offset+ 12 + (i-1)*t_game_status_user_info_len + t_game_status_block_len*5 + 4) 
        user_len = user_len +4
        user_info.m_block_count = buf:OffsetGetAsInt32(offset+ 12 + (i-1)*t_game_status_user_info_len + t_game_status_block_len*5  + 8) 
        user_len = user_len +4
        local hand_card = {}
        for j=1,14 do
             hand_card[j] = buf:OffsetGetAsInt8(offset+ 12 + (i-1)*t_game_status_user_info_len + t_game_status_block_len*5  + 12 + (j-1)*1) 
             user_len = user_len +1
        end
        user_info.m_hand_card = hand_card
        
        local out_card = {}
        for j=1,60 do
            out_card[j]= buf:OffsetGetAsInt8(offset+ 12 + (i-1)*t_game_status_user_info_len + t_game_status_block_len*5  + 26+ (j-1)*1) 
            user_len = user_len +1
        end 
        user_info.m_out_card = out_card 
        user_info.m_draw_card = buf:OffsetGetAsInt8(offset+ 12 + (i-1)*t_game_status_user_info_len + t_game_status_block_len*5  + 86) 
        user_len = user_len +1 
       game_status_play.user_info[i] = user_info
    end
    user_len = user_len + 12
    game_status_play.m_gang_all_count = buf:OffsetGetAsInt32(offset+ 0 + user_len) 

    game_status_play.m_ting = buf:OffsetGetAsBoolean(offset+ 4 + user_len) 
    for i = 1, 29 do 
      game_status_play.m_ting_list[i] = buf:OffsetGetAsInt8(offset+ 5 + user_len+1*(i-1)) 
    end 
    for i = 1, 29 do 
      game_status_play.m_ting_count[i] = buf:OffsetGetAsInt8(offset+ 34 + user_len +1*(i-1)) 
    end 

    for i = 1, 5 do  
        local temp = {} 
        for j = 1, 5 do 
            temp[j] = buf:OffsetGetAsInt8(offset+user_len+63+(1*(i-1)*5 + 1*(j-1))) 
        end 
        game_status_play.m_block_info[i] = temp
    end  
   
    game_status_play.m_block_index = buf:OffsetGetAsUInt32(offset+user_len+63+25)
    return game_status_play
end

function GameModule:parse_game_status_ready(buf,len)
    if(nil == buf or len ~= t_game_status_ready_len) then
        BASIC_LOG_ERROR("GameModule:parse_game_status_ready(nil == buf or len ~= size)"..tostring(len))
        return nil
    end

    local game_status_ready = clone(t_game_status_ready)
    game_status_ready.m_base_info = self:parse_game_base_info(buf,len)

    local offset = t_game_base_info_len

    for i = 1, 4 do 
        game_status_ready.m_user_ready[i] = buf:OffsetGetAsBoolean(offset+1*(i-1)) 
    end 

    return game_status_ready
end

function GameModule:parse_game_base_info(buf,len)
    if(nil == buf or len < t_game_base_info_len) then
        BASIC_LOG_ERROR("GameModule:parse_game_base_info(nil == buf or len ~= size)")
        cclog(len)
        return nil
    end
    local game_base = clone(t_game_base_info)
    game_base.m_game_status = buf:OffsetGetAsUInt8(0) 
    for i = 1, 4 do 
      game_base.m_user_id[i] = buf:OffsetGetAsInt32(1+4*(i-1)) 
    end 
    for i = 1, 4 do 
      game_base.m_user_score[i] = tostring(BasicInt64.New( buf:OffsetGetAsBasicInt64(17+8*(i-1)) )) 
    end 
    for i = 1, 4 do 
      game_base.m_user_cut[i] = buf:OffsetGetAsBoolean(49+1*(i-1)) 
    end 
    game_base.m_total_play_count = buf:OffsetGetAsUInt32(53) 
    game_base.m_cur_play_count = buf:OffsetGetAsUInt32(57) 
    
    game_base.m_bOpenFree = buf:OffsetGetAsBoolean(61) 
    game_base.m_free_apply_id = buf:OffsetGetAsUInt32(62) 
    game_base.m_free_apply_station = buf:OffsetGetAsUInt8(66) 
    for i = 1, 4 do 
      game_base.m_bUserChose[i] = buf:OffsetGetAsBoolean(67+1*(i-1)) 
    end 
    game_base.m_free_remain_time = buf:OffsetGetAsUInt32(71) 
    game_base.m_mj_status = buf:OffsetGetAsUInt8(75) 
    game_base.m_banker_station = buf:OffsetGetAsUInt8(76)  
    
    for i = 1, 4 do 
      game_base.m_fast_count[i] = buf:OffsetGetAsUInt32(77+4*(i-1)) 
    end 
    for i = 1, 4 do 
      game_base.m_out_count[i] = buf:OffsetGetAsUInt32(93+4*(i-1)) 
    end   
      
    game_base.m_my_station = buf:OffsetGetAsUInt8(109) 
    game_base.m_privater_station = buf:OffsetGetAsUInt8(110) 
    game_base.m_privater_id = buf:OffsetGetAsUInt32(111) 
    game_base.m_free_time = buf:OffsetGetAsUInt32(115)
    game_base.m_game_config = self:parse_game_config(buf,119)
    return game_base 
end

function GameModule:parse_game_config(buf,len)
 
    local game_config = clone(t_notify_game_config) 
    game_config.m_room_card = buf:OffsetGetAsInt32(len+0) 
    game_config.m_hu_qxd = buf:OffsetGetAsBoolean(len+4) 
    game_config.m_hongaward_ma = buf:OffsetGetAsInt32(len+5) 
    game_config.m_award_ma = buf:OffsetGetAsInt32(len+9) 
    game_config.m_luck_mode = buf:OffsetGetAsInt32(len+13) 
    game_config.m_all_ma = buf:OffsetGetAsBoolean(len+17) 
    game_config.m_allow_zp = buf:OffsetGetAsBoolean(len+18) 

    return game_config


end

function GameModule:parse_notify_out_card_response(buf,len)
    if(nil == buf or len ~= t_notify_out_card_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_notify_out_card_response(nil == buf or len ~= size)")
        return nil
    end

    local notify_out_card = clone(t_notify_out_card_response)
    notify_out_card.m_chair_id = buf:OffsetGetAsUInt8(0) 
    return notify_out_card
end

function GameModule:parse_notify_block_info_response(buf,len)
    if(nil == buf or len ~= t_notify_block_info_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_notify_block_info_response(nil == buf or len ~= size)")
        return nil
    end

    local notify_block_info = clone(t_notify_block_info_response) 
    notify_block_info.m_card_value = buf:OffsetGetAsUInt8(0) 
    notify_block_info.m_out = buf:OffsetGetAsBoolean(1) 
    notify_block_info.m_block_level = buf:OffsetGetAsUInt8(2) 
    notify_block_info.m_checked_id = buf:OffsetGetAsUInt8(3) 
     
    for i = 1, 5 do 
--        local temp = notify_block_info.m_block_info[i] 
--        local temp = {} 
        for j = 1, 5 do 
            notify_block_info.m_block_info[i][j] = buf:OffsetGetAsInt8(4+(1*(i-1)*5 + 1*(j-1))) 
        end 
        --notify_block_info.m_block_info[i] = temp[j] 
    end 

    notify_block_info.m_block_index = buf:OffsetGetAsInt32(29) 
    return notify_block_info
end

function GameModule:parse_user_touch_card_response(buf,len)
    if(nil == buf or len ~= t_user_touch_card_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_user_touch_card_response(nil == buf or len ~= size)")
        return nil
    end
    local user_touch_card = clone(t_user_touch_card_response)
    user_touch_card.m_chair_id = buf:OffsetGetAsUInt8(0) 
    user_touch_card.m_card_value = buf:OffsetGetAsUInt8(1) 
    user_touch_card.m_bgang = buf:OffsetGetAsBoolean(2) 

    return user_touch_card
end

function GameModule:parse_user_out_card_result_response(buf,len)
    if(nil == buf or len ~= t_user_out_card_result_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_user_out_card_result_response(nil == buf or len ~= size)")
        return nil
    end

    local user_out_card_result = clone(t_user_out_card_result_response)
    user_out_card_result.m_chair_id = buf:OffsetGetAsUInt8(0) 
    user_out_card_result.m_card_value = buf:OffsetGetAsUInt8(1) 
    return user_out_card_result
end


function GameModule:parse_maker_info_response(buf,len)
    if(nil == buf or len ~= t_maker_info_response_len) then
        BASIC_LOG_ERROR("GameModule:t_maker_info_response_len(nil == buf or len ~= size)")
        return nil
    end
    local maker_info = clone(t_maker_info_response)
    maker_info.m_chair_id = buf:OffsetGetAsUInt8(0) 

    return maker_info
end

function GameModule:parse_dice_info_response(buf,len)
    if(nil == buf or len ~= t_dice_info_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_dice_info_response(nil == buf or len ~= size)")
        return nil
    end

    local dice_info = clone(t_dice_info_response)
    for i = 1, 2 do 
        dice_info.m_dice[i] = buf:OffsetGetAsInt8(0+1*(i-1)) 
    end 
    return dice_info
end

function GameModule:parse_hand_card_info_response(buf,len)

    if(nil == buf or len ~= t_hand_card_info_response_len) then
        BASIC_LOG_ERROR("GameModule:parse_hand_card_info_response(nil == buf or len ~= size)")
        return nil
    end

    local hand_card_info = clone(t_hand_card_info_response)
    for i = 1, 4 do 
	    local temp = hand_card_info.m_hand_card[i] 
	    --local temp = {} 
	    for j = 1, 14 do 
		    temp[j] = buf:OffsetGetAsInt8(0+(1*(i-1)*14 + 1*(j-1))) 
	    end  
    end 
    for i = 1, 4 do 
      hand_card_info.m_card_count[i] = buf:OffsetGetAsInt8(56+1*(i-1)) 
    end 

    return hand_card_info
end

------------------------------------------------------------------------------------
--format function
function GameModule:format_user_agree_request(request)
     if(nil == request) then
        return nil,0
   end  
    local buf = BasicBuffer.New(6) 
    buf:OffsetSetAsUInt32(0,request.userid) 
    buf:OffsetSetAsUInt8(4,request.chair_id) 
    buf:OffsetSetAsBoolean(5,request.bagree) 
    return buf,user_agree_request_len
end
function GameModule:format_swap_wall_card_request(request)
  if(nil == request) then
        return nil,0
   end 
    local buf = BasicBuffer.New(1)  
    buf:OffsetSetAsUInt8(0,request.m_card_value) 
    return buf,swap_wall_card_request_len
end
function GameModule:format_swap_free_game_request(request)

    if(nil == request) then
        return nil,0
   end  
    local buf = BasicBuffer.New(8)  
    buf:OffsetSetAsUInt32(0,request.m_user_id) 
    buf:OffsetSetAsUInt8(4,request.m_chair_id) 
    buf:OffsetSetAsBoolean(5,request.m_free) 

    return buf,free_game_len
end
function GameModule:format_apply_update_owner_game_info(request)

  if(nil == request) then
        return nil,0
   end  
    
    local buf = BasicBuffer.New(5) 
    buf:OffsetSetAsUInt32(0,request.m_user_id) 
    buf:OffsetSetAsUInt8(4,request.m_chair_id) 
    
    return buf,apply_game_info_len
end
function GameModule:format_apply_game_config(request)

    if(nil == request) then
        return nil,0
   end   
    local buf = BasicBuffer.New(1)  
    buf:OffsetSetAsUInt8(0,request.m_chair_id)  
    return buf,apply_game_config_len

end
function GameModule:format_user_block_operate_request(request)
    if(nil == request) then
        return nil,0
    end
    local buf = BasicBuffer.New(11) 
    buf:OffsetSetAsUInt8(0,request.m_chair_id) 
    buf:OffsetSetAsUInt8(1,request.m_opreate_type) 
    for i = 1, 4 do 
        buf:OffsetSetAsInt8(2+1*(i-1),request.m_card_value[i]) 
    end 
    buf:OffsetSetAsBoolean(6,request.m_out) 
    buf:OffsetSetAsUInt32(7,request.m_block_index) 

    return buf,user_block_operate_request_len
end
function GameModule:format_user_out_card_request(request)
    if(nil == request) then
        return nil,0
    end

    local buf = BasicBuffer.New(2) 
    buf:OffsetSetAsUInt8(0,request.m_chair_id) 
    buf:OffsetSetAsUInt8(1,request.m_card_value) 

    return buf,user_out_card_request_len
end
function GameModule:format_maker_play_dice_request(request)
    if(nil == request) then
        return nil,0
    end

    local buf = BasicBuffer.New(1) 
    buf:OffsetSetAsUInt8(0,request.m_chair_id) 
    return buf,maker_play_dice_request_len
end

function GameModule:FormatBufferByUserLeftRequest(request)
    local buf = BasicBuffer.New(msg_user_left_len)
    buf:OffsetSetAsInt32(0, request.m_userid)
    return buf,msg_user_left_len
end



--返回对象
return GameModule