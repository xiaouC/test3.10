-- ./app/platform/game/game_common/final_settle_view.lua

local final_settle = require 'app.platform.game.game_common.component.final_settle_view'
----------------------------------------------------------------------------------------------------------
local FinalSettleView = class('FinalSettleView', final_settle)
function FinalSettleView:getUserScore(result_info, server_index)
    return result_info.m_fan_score[server_index] + result_info.m_gang_score[server_index]
end

function FinalSettleView:getFinalSettleMoreCount(result_info, server_index)
    -- 
    local ret_data = {}

    -- 自摸糊次数
    if result_info.m_zm_win_count[server_index] > 0 then
        table.insert(ret_data, { '自摸胡次数', result_info.m_zm_win_count[server_index] })
    end

    -- 抢杠胡次数
    if result_info.m_qiang_win_count[server_index] > 0 then
        table.insert(ret_data, { '抢杠胡次数', result_info.m_qiang_win_count[server_index] })
    end

    -- 抓炮次数
    if result_info.m_zhua_pao_win_count[server_index] > 0 then
        table.insert(ret_data, { '抓跑次数', result_info.m_zhua_pao_win_count[server_index] })
    end

    -- 明杠次数
    if result_info.m_ming_gang[server_index] > 0 then
        table.insert(ret_data, { '明杠次数', result_info.m_ming_gang[server_index] })
    end

    -- 暗杠次数
    if result_info.m_an_gang[server_index] > 0 then
        table.insert(ret_data, { '暗杠次数', result_info.m_an_gang[server_index] })
    end

    -- 中马次数
    if result_info.m_luck_count[server_index] > 0 then
        table.insert(ret_data, { '中马次数', result_info.m_luck_count[server_index] })
    end

    -- 
    return ret_data
end

return FinalSettleView
