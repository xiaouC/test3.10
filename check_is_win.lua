
local check_is_win_obj = require('test.check_is_win.check_is_win_normal').new()

function test_check_is_win()
    print('lua:' .. collectgarbage('count'))

    --local ghost_card_id_1 = 32
    --local ghost_card_id_2 = nil
    --local hand_cards = { 32, 32, 13, 13, 14, 15, 16, 19, 20, 21, 23, 25, 26 }
    --local new_card_id = 26

    local ghost_card_id_1 = nil
    local ghost_card_id_2 = nil
    local hand_cards = { 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9 }
    local new_card_id = nil

    if new_card_id then table.insert(hand_cards, new_card_id) end

    -- 
    local is_win = nil

    local st = os.clock()
    for i=1, 100000 do
        for card_id=1, 34 do
            is_win = check_is_win_obj:check_is_win(ghost_card_id_1, ghost_card_id_2, hand_cards, card_id)
        end
    end
    local win_cards = {}
    for card_id=1, 34 do
        local is_win = check_is_win_obj:check_is_win(ghost_card_id_1, ghost_card_id_2, hand_cards, card_id)
        if is_win then table.insert(win_cards, card_id) end
    end
    local et = os.clock()

    -- 
    print('is_win : ' .. tostring(is_win))
    dump(win_cards, 'win_cards')
    print(string.format('elapsed time : %.5f', et - st));

    collectgarbage('setpause', 100)
    collectgarbage('setstepmul', 5000)

    collectgarbage('collect')
    print('lua:'..collectgarbage('count'))
end
