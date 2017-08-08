-- ./app/platform/game/game_common/game_signal.lua
-- 当前使用的 signal 的说明，不一定完整，发现有遗漏的，请反馈给 xiaou

----------------------------------------------------------------------------------------------------------------------------------
-- signal:    game_state
-- 游戏状态: [ 'waiting', 'game_start', 'playing', 'round_end', 'prepare_next_round', 'game_end', 'game_quit' ]
----------------------------------------------------------------------------------------------------------------------------------
local game_state = 'waiting'
game_scene:fire('game_state', game_state)
game_scene:listenGameSignal('game_state', function(game_state)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: update_game_rule
-- 游戏的规则设置
----------------------------------------------------------------------------------------------------------------------------------
local game_rule = {}
game_scene:fire('update_game_rule', game_rule)
game_scene:listenGameSignal('update_game_rule', function(game_rule)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: homeowner_id
-- 房主的 user_id
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('homeowner_id', homeowner_id)   -- 房主的 user_id
game_scene:listenGameSignal('homeowner_id', function(homeowner_id) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: homeowner_server_index
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('homeowner_server_index', server_index)
game_scene:listenGameSignal('homeowner_server_index', function(server_index) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: banker_server_index
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('banker_server_index', server_index)
game_scene:listenGameSignal('banker_server_index', function(server_index) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: my_server_index
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('my_server_index', server_index)
game_scene:listenGameSignal('my_server_index', function(server_index) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: room_id
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('room_id', room_id)
game_scene:listenGameSignal('room_id', function(room_id) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: play_count
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('play_count', cur_play_count, total_play_count)
game_scene:listenGameSignal('play_count', function(cur_play_count, total_play_count) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_user_sit
-- 有玩家坐下
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('on_user_sit', server_index, user_id)
game_scene:listenGameSignal('on_user_sit', function(server_index, user_id) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: init_user_score
-- 玩家的初始分数
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('init_user_score', server_index, score)
game_scene:listenGameSignal('init_user_score', function(server_index, score) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: update_user_score
-- 更新玩家的分数，这基本上是在一个小局结束后触发，score 是这个小局的得分
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('update_user_score', server_index, score)
game_scene:listenGameSignal('update_user_score', function(server_index, score) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_user_offline
-- 玩家是否掉线
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('on_user_offline', server_index, is_offline)
game_scene:listenGameSignal('on_user_offline', function(server_index, is_offline) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_user_ready
-- 玩家是否准备好
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('on_user_ready', server_index, is_ready)
game_scene:listenGameSignal('on_user_ready', function(server_index, is_ready) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_init_fast_out
-- 初始化玩家闪电出牌次数
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('on_init_fast_out', server_index, fast_count)
game_scene:listenGameSignal('on_init_fast_out', function(server_index, fast_count) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_fast_out
-- 更新玩家闪电出牌的次数，fast_count 是当前的数量
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('on_fast_out', server_index, fast_count)
game_scene:listenGameSignal('on_fast_out', function(server_index, fast_count) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: roll_dice
-- 打骰子，这里的最后一个参数是一个回调，当动画结束后，需要回调
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('roll_dice', banker_server_index, dice_num_1, dice_num_2, function()
end)
game_scene:listenGameSignal('roll_dice', function(banker_server_index, dice_num_1, dice_num_2, callback_func) end)


----------------------------------------------------------------------------------------------------------------------------------
-- signal: roll_dice_end
-- 骰子动画结束，点数确认
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('roll_dice_end', banker_server_index, dice_num_1, dice_num_2)
game_scene:listenGameSignal('roll_dice_end', function(banker_server_index, dice_num_1, dice_num_2) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: reset_ting_card
-- 重置听牌列表，这个听牌列表时屏幕上显示出来的听牌列表
----------------------------------------------------------------------------------------------------------------------------------
local card_list = {
    { card_id = 1, card_count = 1, fan_count = 1, }
    { card_id = 1, card_count = 1, fan_count = 1, }
}
game_scene:fire('reset_ting_card', card_list)
game_scene:listenGameSignal('reset_ting_card', function(card_list) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: reconn_lei_card
-- 断线重连回来，重新初始化牌墙
----------------------------------------------------------------------------------------------------------------------------------
local wall_count = 1        -- 从前往后，已经拿了多少张牌
local kong_count = 1        -- 从后往前，已经杠了多少张牌
game_scene:fire('reconn_lei_card', wall_count, kong_count)
game_scene:listenGameSignal('reconn_lei_card', function(wall_count, kong_count) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: reconn_hand_card
-- 断线重连回来，重新初始化手牌
----------------------------------------------------------------------------------------------------------------------------------
local location_index = USER_LOCATION_SELF
local card_list = { 1, 2, 3, 4 }
local card_num = 13
game_scene:fire('reconn_hand_card', location_index, card_list, card_num)
game_scene:listenGameSignal('reconn_hand_card', function(location_index, card_list, card_num) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: reconn_draw_card
-- 断线重连回来，重新初始化摸到的牌
----------------------------------------------------------------------------------------------------------------------------------
local location_index = USER_LOCATION_SELF
local card_id = 1
game_scene:fire('reconn_draw_card', location_index, card_id)
game_scene:listenGameSignal('reconn_draw_card', function(location_index, card_id) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_reconn_block_result
-- 断线重连回来，重新初始化碰和杠的牌
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('on_reconn_block_result', block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
game_scene:listenGameSignal('on_reconn_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_reconn_out_card
-- 断线重连回来，重新初始化出牌区的牌
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('on_reconn_out_card', location_index, card_list)
game_scene:listenGameSignal('on_reconn_out_card', function(location_index, card_list) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: ting_card_list
-- 断线重连回来，重新初始化听牌的数据
----------------------------------------------------------------------------------------------------------------------------------
local max_win_count = 1     -- 最大赢牌的数量
local ting_groups = {
    [out_card_id] = {   -- 打出这张牌
        { card_id = 1, card_count = 1, fan_count = 1, } -- 胡这张牌的数据，id, 剩余数量，番数
        { card_id = 1, card_count = 1, fan_count = 1, } -- 胡这张牌的数据，id, 剩余数量，番数
    },
}      
game_scene:fire('ting_card_list', max_win_count, ting_groups)
game_scene:listenGameSignal('ting_card_list', function(max_win_count, ting_groups) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal:    init_hand_card    --------------------------------------------------------------------------------------------------
-- 初始化手牌，游戏开始时候触发 --------------------------------------------------------------------------------------------------
-- 当手牌初始化的动画结束后，需要回调传递过去的函数，
----------------------------------------------------------------------------------------------------------------------------------
local location_index = USER_LOCATION_SELF   -- [USER_LOCATION_SELF, USER_LOCATION_RIGHT, USER_LOCATION_FACING, USER_LOCATION_LEFT]
local card_list = { 1, 1, 1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9 }
game_scene:fire('init_hand_card', location_index, card_list, #card_list, function()
end)
game_scene:listenGameSignal('init_hand_card', function(location_index, card_list, card_num, callback_func)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: init_hand_card_ended
-- 在初始化手牌的动画结束后触发
----------------------------------------------------------------------------------------------------------------------------------
local location_index = USER_LOCATION_SELF
game_scene:fire('init_hand_card_ended', location_index)
game_scene:listenGameSignal('init_hand_card_ended', function(location_index)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: draw_card
-- 摸牌 
----------------------------------------------------------------------------------------------------------------------------------
local location_index = USER_LOCATION_SELF   -- 谁摸牌
local card_id = 8                           -- 摸是什么牌
local is_kong = false                       -- 是杠码？(这里就是说明是从前摸还是从后摸)
game_scene:fire('draw_card', location_index, card_id, is_kong, function()   -- 最后摸牌也许会有动画，在动画结束后回调
end)
game_scene:listenGameSignal('draw_card', function(location_index, card_id, is_kong, callback_func)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: user_turn
-- 轮到玩家出牌
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('user_turn', server_index)
game_scene:listenGameSignal('user_turn', function(server_index) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: out_card
-- 玩家出牌
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('out_card', location_index, card_id)
game_scene:listenGameSignal('out_card', function(location_index, card_id) end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: liang_card
-- 亮牌 
----------------------------------------------------------------------------------------------------------------------------------
local location_index = USER_LOCATION_SELF
local card_list = { 1, 1, 1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9 }
game_scene:fire('liang_card', location_index, card_list, #card_list)
game_scene:listenGameSignal('liang_card', function(location_index, card_list, card_num)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_block
-- 显示拦牌界面 
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('on_block', block_info, block_level, card_id, is_out, block_index)
game_scene:listenGameSignal('on_block', function(block_info, block_level, card_id, is_out, block_index)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_block_result
-- 拦牌结果 - [ 'pong' / 'kong_ming' / 'kong_an' / 'kong_bu' / 'chow' / 'win' ]
----------------------------------------------------------------------------------------------------------------------------------
local block_type = 'pong'               -- 碰 / 明杠 / 暗杠 / 补杠 / 吃
local show_card_list = { 2, 2, 2 }      -- 碰杠区域显示的牌
local src_location_index = USER_LOCATION_SELF   -- 如果是玩家打出的牌，那个这个指向出牌的玩家
local src_card_list = { 2 }                     -- 玩家出的牌，在这里，我给的是一个列表，不过一般情况都应该只有一个
local dest_location_index = USER_LOCATION_SELF      -- 碰杠的玩家
local dest_card_list = { 2, 2 }                     -- 从碰杠玩家手牌中拿走的牌
game_scene:fire('on_block_result', block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
game_scene:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: user_free_operate
-- 解散包间的时候，玩家同意/拒绝
----------------------------------------------------------------------------------------------------------------------------------
local apply_server_index = 1    -- 请求解散的玩家的服务器索引
local apply_user_id = 1         -- 请求解散的玩家的 id
local op_user_server_index = 1  -- 当前操作的玩家的服务器索引
local op_user_id = 1            -- 当前操作的玩家的 id
local is_agree = true           -- 当前操作的玩家同意还是拒绝解散包间
game_scene:fire('user_free_operate', apply_server_index, apply_user_id, op_user_server_index, op_user_id, is_agree)
game_scene:listenGameSignal('user_free_operate', function(apply_server_index, apply_user_id, op_user_server_index, op_user_id, is_agree)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: second_confirmation_free_game
-- 请求解散包间的二次确认(这里是请求的二次确认)
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('second_confirmation_free_game', function(is_confirm)   -- 这里传递的参数是一个回调函数，要求在回调的时候传递确认结果
end)

game_scene:listenGameSignal('second_confirmation_free_game', function(callback_func)
    callback_func(is_confirm)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: user_free_result
-- 解散包间的结果
----------------------------------------------------------------------------------------------------------------------------------
local server_index = 1  -- 解散包间失败的话，这个是拒绝解散包间的玩家(如果断线回来收到的话，那server_index和user_id都为nil)
local user_id = 0       -- 解散包间失败的话，这个是拒绝解散包间的玩家
local result = true     -- 解散包间是否成功
game_scene:fire('user_free_result', server_index, user_id, result)
game_scene:listenGameSignal('user_free_result', function(server_index, user_id, result)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: on_kick_out
-- 被踢出包间
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('on_kick_out')
game_scene:listenGameSignal('on_kick_out', function()
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: round_settle
-- 小局结算
----------------------------------------------------------------------------------------------------------------------------------
local data = {}      -- 服务器返回的数据
game_scene:fire('round_settle', data)
game_scene:listenGameSignal('round_settle', function(data)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: final_settle
-- 大结算
----------------------------------------------------------------------------------------------------------------------------------
local all_record_info = {}      -- 服务器返回的数据
local user_count = 4            -- 进行游戏的玩家的个数
game_scene:fire('final_settle', all_record_info, user_count)
game_scene:listenGameSignal('final_settle', function(all_record_info, user_count)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: reconn_no_ready
-- 小局结算的时候掉线了，重新进入游戏，会收到这个 signal
-- 这个时候，更多的作用，是让玩家可以继续游戏，比如来一个按钮等等
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('reconn_no_ready')
game_scene:listenGameSignal('reconn_no_ready', function()
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: flop_ghost_card
-- 在收到鬼牌信息后，会触发翻鬼牌的动画
----------------------------------------------------------------------------------------------------------------------------------
game_scene:fire('flop_ghost_card', fake_card_ids, really_card_ids, dice_num_1, dice_num_2, function()
end)
game_scene:listenGameSignal('flop_ghost_card', function(fake_card_ids, really_card_ids, dice_num_1, dice_num_2, callback_func)
end)

----------------------------------------------------------------------------------------------------------------------------------
-- signal: ghost_card_confirm
-- 鬼牌确认
----------------------------------------------------------------------------------------------------------------------------------
local fake_card_ids = { 1 }         -- 翻出来的牌
local really_card_ids = { 2, 3 }    -- 真正的鬼牌
local dice_num_1 = 1                -- 骰子点数
local dice_num_2 = 1
game_scene:fire('ghost_card_confirm', fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
game_scene:listenGameSignal('ghost_card_confirm', function(fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
end)



