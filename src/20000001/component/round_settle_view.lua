-- ./app/platform/game/20000001/component/round_settle_view.lua

----------------------------------------------------------------------------------------------------------
local round_settle_base = require 'app.platform.game.game_common.component.quick_settle'
local RoundSettleView = class('RoundSettleView', round_settle_base)
function RoundSettleView:get_special_status(server_index, result_info)
    if result_info.m_win_type == 1 and result_info.m_win[server_index] then
        return '胡'
    end

    if result_info.m_win_type == 2 and result_info.m_dianpao_id + 1 == server_index then
        return '点炮'
    end

    return ''
end

function RoundSettleView:get_line_simple_1(server_index, result_info)
    local score = tonumber(result_info.m_gang_score[server_index])
    return string.format('杠　分: %s%d', score >= 0 and '+' or '', score)
end

function RoundSettleView:get_line_simple_2(server_index, result_info)
    local score = tonumber(result_info.m_fan_score[server_index])
    return string.format('胡牌分: %s%d', score >= 0 and '+' or '', score)
end

function RoundSettleView:get_line_simple_3(server_index, result_info)
    local score = result_info.m_luck_score[server_index]
    return string.format('中马分: %s%d', score >= 0 and '+' or '', score)
end

function RoundSettleView:get_card_data(server_index, result_info)
    local card_data = round_settle_base.get_card_data(self, server_index, result_info)

    -- 胡的，显示中码信息
    if result_info.m_win[server_index] then
        card_data.additional_reward = {
            text_2 = '马',
            cards = {},
            num = (result_info.m_user_luck_count[server_index] or 0),
        }

        if result_info.m_all_king then
            card_data.additional_reward.text_1 = '四红中全马：'
        else
            local reward_types = { '中马：', '一张定马：', '一马全中：', }
            card_data.additional_reward.text_1 = reward_types[self.game_scene.game_rule.m_luck_mode+1]
        end

        -- 一张定码/一码全中
        if self.game_scene.game_rule.m_luck_mode == 1 or self.game_scene.game_rule.m_luck_mode == 2 then
            card_data.additional_reward.cards = result_info.m_luck_card
        else
            for _, card_id in ipairs(result_info.m_luck_card) do
                local is_valid = ((card_id % 16 == 1) or (card_id % 16 == 5) or (card_id % 16 == 9))
                if is_valid then
                    table.insert(card_data.additional_reward.cards, card_id)
                end
            end
        end
    end

    return card_data
end

function RoundSettleView:get_line_detail_1(server_index, result_info)
    if result_info.m_win_type == 0 then return {} end

    -- 
    local pre_score = (result_info.m_win[server_index] and '+' or '')

    local line_info = {
        {
            text_1 = '胡牌分：',
            text_2 = pre_score .. result_info.m_fan_score[server_index],
        },
    }

    -- 0: 荒庄， 1: 自摸， 2: 抓跑， 3: 抢杠， 4: 杠上开花
    if result_info.m_win_type > 0 then
        if result_info.m_win[server_index] then
            local score = 0
            if result_info.m_win_type == 1 or result_info.m_win_type == 2 then score = 2 end

            local win_desc = { '自摸', '抓跑', '抢杠胡', '杠上开花', }
            table.insert(line_info, {
                text_1 = win_desc[result_info.m_win_type],
                text_2 = (score > 0 and ('+' .. score) or ''),
            })

            -- 
            if result_info.m_win_type == 1 or result_info.m_win_type == 2 then
                local user_count = self.game_scene:getUserCount()
                local desc = { '收一份', '收两份', '收三份' }
                table.insert(line_info, {
                    text_1 = (result_info.m_win_type == 1 and desc[user_count-1] or '收一份'),
                })
            end
        else
            local text = nil
            if result_info.m_win_type == 1 then
                text = '被自摸'
            elseif result_info.m_win_type == 2 and result_info.m_dianpao_id + 1 == server_index then
                text = '点炮'
            elseif result_info.m_win_type == 3 and result_info.m_dianpao_id + 1 == server_index then
                text = '被抢杠胡'
            elseif result_info.m_win_type == 4 then
                text = '被杠上开花'
            end

            if text then
                table.insert(line_info, {
                    text_1 = text,
                })
            end
        end
    end

    return line_info
end

function RoundSettleView:get_line_detail_2(server_index, result_info)
    if result_info.m_win_type == 0 then return {} end

    -- 
    local pre_score = (result_info.m_win[server_index] and '+' or '')

    local line_info = {
        {
            text_1 = '中马分：',
            text_2 = pre_score .. result_info.m_luck_score[server_index],
        },
    }

    -- 不是抢杠胡
    if self.game_scene.game_rule.m_luck_mode ~= 2 and result_info.m_win_type ~= 3 then
        table.insert(line_info, {
            text_1 = '胡牌分：',
            text_2 = pre_score .. result_info.m_fan_score[server_index],
        })
    end

    -- 没有胡，胡牌类型为 点炮/抢杠胡，不是放炮的，那么就不显示中码数，所以在这个条件前面加一个NOT，就是需要显示中码数的了
    if not ((not result_info.m_win[server_index]) and (result_info.m_win_type == 2 or result_info.m_win_type == 3) and (result_info.m_dianpao_id + 1 ~= server_index)) then
        local count = 0
        if result_info.m_win[server_index] then
            count = result_info.m_user_luck_count[server_index]
        else
            for i=1, 4 do
                if result_info.m_win[i] and result_info.m_user_luck_count[i] > 0 then
                    count = count + result_info.m_user_luck_count[i]
                end
            end
        end

        table.insert(line_info, {
            text_1 = '中马数：',
            text_2 = math.abs(count),
        })
    end

    return line_info
end

function RoundSettleView:get_line_detail_3(server_index, result_info)
    if result_info.m_win_type == 0 then return {} end

    -- 
    local line_info = {
        {
            text_1 = '杠　分：',
            text_2 = (result_info.m_gang_score[server_index] >= 0 and '+' or '') .. result_info.m_gang_score[server_index],
        },
    }

    -- 明杠次数
    if result_info.m_mgang_count[server_index] > 0 then
        table.insert(line_info, {
            text_1 = '明杠',
            text_2 = 'x' .. result_info.m_mgang_count[server_index],
        })
    end

    -- 暗杠次数
    if result_info.m_agang_count[server_index] > 0 then
        table.insert(line_info, {
            text_1 = '暗杠',
            text_2 = 'x' .. (result_info.m_agang_count[server_index]),
        })
    end

    -- 补杠次数
    if result_info.m_bgang_count[server_index] > 0 then
        table.insert(line_info, {
            text_1 = '补杠',
            text_2 = 'x' .. result_info.m_bgang_count[server_index],
        })
    end

    -- 放杠次数
    if result_info.m_fgang_count[server_index] > 0 then
        table.insert(line_info, {
            text_1 = '放杠',
            text_2 = 'x' .. result_info.m_fgang_count[server_index],
        })
    end

    return line_info
end

return RoundSettleView
