
local check_is_win_normal = class('check_is_win_normal')
function check_is_win_normal:ctor()
    self.all_kind_groups = {
        { start_index =  1, end_index =  9, },          -- 1 - 9 万
        { start_index = 10, end_index = 18, },          -- 1 - 9 条
        { start_index = 19, end_index = 27, },          -- 1 - 9 筒
        { start_index = 28, end_index = 28, },          -- 东
        { start_index = 29, end_index = 29, },          -- 南
        { start_index = 30, end_index = 30, },          -- 西
        { start_index = 31, end_index = 31, },          -- 北
        { start_index = 32, end_index = 32, },          -- 中
        { start_index = 33, end_index = 33, },          -- 发
        { start_index = 34, end_index = 34, },          -- 白
    }
end

function check_is_win_normal:check_is_win_no_eyes(card_num, total_count, kind_group, kind_index, kind_offset)
    if total_count == 0 then return true end
    
    local card_index = kind_group.start_index + kind_offset
    if card_index > kind_group.end_index then
        local next_kind_group = self.all_kind_groups[kind_index+1]
        if not next_kind_group then return false end

        return self:check_is_win_no_eyes(card_num, total_count, next_kind_group, kind_index + 1, 0)
    end

    local num = card_num[card_index]
    if num == 0 then
        return self:check_is_win_no_eyes(card_num, total_count, kind_group, kind_index, kind_offset + 1)
    end

    if num == 1 or num == 2 then
        if card_index + 2 > kind_group.end_index or card_index + 1 > kind_group.end_index or card_num[card_index+1] == 0 or card_num[card_index+2] == 0 then
            return false
        end

        card_num[card_index] = card_num[card_index] - 1
        card_num[card_index+1] = card_num[card_index+1] - 1
        card_num[card_index+2] = card_num[card_index+2] - 1
        total_count = total_count - 3

        if self:check_is_win_no_eyes(card_num, total_count, kind_group, kind_index, kind_offset) then
            return true
        end

        card_num[card_index] = card_num[card_index] + 1
        card_num[card_index+1] = card_num[card_index+1] + 1
        card_num[card_index+2] = card_num[card_index+2] + 1
        total_count = total_count + 3

        return false
    end

    if num == 3 then
        card_num[card_index] = card_num[card_index] - 3
        total_count = total_count - 3

        if self:check_is_win_no_eyes(card_num, total_count, kind_group, kind_index, kind_offset + 1) then
            return true
        end

        card_num[card_index] = card_num[card_index] + 3
        total_count = total_count + 3

        -- 
        if card_index + 2 > kind_group.end_index or card_index + 1 > kind_group.end_index or card_num[card_index+1] == 0 or card_num[card_index+2] == 0 then
            return false
        end

        card_num[card_index] = card_num[card_index] - 1
        card_num[card_index+1] = card_num[card_index+1] - 1
        card_num[card_index+2] = card_num[card_index+2] - 1
        total_count = total_count - 3

        if self:check_is_win_no_eyes(card_num, total_count, kind_group, kind_index, kind_offset) then
            return true
        end

        card_num[card_index] = card_num[card_index] + 1
        card_num[card_index+1] = card_num[card_index+1] + 1
        card_num[card_index+2] = card_num[card_index+2] + 1
        total_count = total_count + 3

        return false
    end

    -- num == 4
    if card_index + 2 > kind_group.end_index or card_index + 1 > kind_group.end_index or card_num[card_index+1] == 0 or card_num[card_index+2] == 0 then
        return false
    end

    card_num[card_index] = card_num[card_index] - 1
    card_num[card_index+1] = card_num[card_index+1] - 1
    card_num[card_index+2] = card_num[card_index+2] - 1
    total_count = total_count - 3

    if self:check_is_win_no_eyes(card_num, total_count, kind_group, kind_index, kind_offset) then
        return true
    end

    card_num[card_index] = card_num[card_index] + 1
    card_num[card_index+1] = card_num[card_index+1] + 1
    card_num[card_index+2] = card_num[card_index+2] + 1
    total_count = total_count + 3

    return false
end

function check_is_win_normal:check_is_win_no_ghost(card_num, total_count)
    for _, v in ipairs(self.all_kind_groups) do
        for index=v.start_index, v.end_index do
            if card_num[index] >= 2 then
                card_num[index] = card_num[index] - 2
                total_count = total_count - 2

                if self:check_is_win_no_eyes(card_num, total_count, self.all_kind_groups[1], 1, 0) then
                    return true
                end

                card_num[index] = card_num[index] + 2
                total_count = total_count + 2
            end
        end
    end

    return false
end

function check_is_win_normal:check_is_win_with_ghost(ghost_count, card_num, total_count)
    if ghost_count == 0 then
        return self:check_is_win_no_ghost(card_num, total_count)
    end

    for _, v in ipairs(self.all_kind_groups) do
        for index=v.start_index, v.end_index do
            card_num[index] = card_num[index] + 1
            if self:check_is_win_with_ghost(ghost_count - 1, card_num, total_count + 1) then
                return true
            end
        end
    end

    return false
end

function check_is_win_normal:check_is_win(ghost_card_id_1, ghost_card_id_2, hand_cards, new_card_id)
    local card_num = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }

    local total_count = 0
    for _, card_id in ipairs(hand_cards) do
        card_num[card_id] = card_num[card_id] + 1
        total_count = total_count + 1
    end

    if new_card_id then
        card_num[new_card_id] = card_num[new_card_id] + 1
        total_count = total_count + 1
    end

    local ghost_count = 0
    if ghost_card_id_1 then
        ghost_count = card_num[ghost_card_id_1]
        card_num[ghost_card_id_1] = 0
    end
    if ghost_card_id_2 then
        ghost_count = ghost_count + card_num[ghost_card_id_2]
        card_num[ghost_card_id_2] = 0
    end

    return self:check_is_win_with_ghost(ghost_count, card_num, total_count - ghost_count)
end

return check_is_win_normal
