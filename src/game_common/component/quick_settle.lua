-- ./app/platform/game/game_common/quick_settle.lua

local round_settle = require 'app.platform.game.game_common.component.round_settle_view'

local quick_settle = class('quick_settle', round_settle)
function quick_settle:ctor(game_scene)
    round_settle.ctor(self, game_scene)
end

function quick_settle:getUserSettleScore(result_info)
    local user_scores = {}
    for server_index, win_score in ipairs(result_info.m_win_score) do
        local user_info = self.game_scene.all_user_info[server_index]
        if user_info then
            table.insert(user_scores, {
                server_index = server_index,
                settle_score = win_score,
            })
        end
    end
    return user_scores
end

function quick_settle:showRoundSettleDetailView(result_info)
    local user_scores = self:getUserSettleScore(result_info)
    for _, v in ipairs(user_scores or {}) do
        self.game_scene:fire('settle_score', v.server_index, v.settle_score)
    end

    -- 
    local csb_node = cc.CSLoader:createNode('mahjong/component/round_settle/quick_settle_view.csb')
    csb_node:setPosition(display.width * 0.5, 200)
    self.game_scene:addChild(csb_node, GAME_VIEW_Z_ORDER.ROUND_SETTLE)

    -- 结算详情
    local btn_settle_detail = button('btn_settle_detail', function()
        csb_node:removeFromParent(true)

        round_settle.showRoundSettleDetailView(self, result_info)
    end, csb_node)

    -- 
    local btn_settle_detail_size = btn_settle_detail:getContentSize()

    local btn_text_label = cc.Label:createWithTTF('结算详情', 'font/jxk.TTF', 50)
    btn_text_label:setColorTextureIndex(2)
    btn_text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    btn_text_label:setPosition(btn_settle_detail_size.width * 0.5, btn_settle_detail_size.height * 0.5 + 5)
    btn_text_label:enableOutline(cc.c3b(166, 24, 22), 2)
    btn_text_label:enableShadow()
    btn_settle_detail:getRendererNormal():addChild(btn_text_label)

    -- 继续游戏
    local btn_continue = button('btn_continue_game', function()
        if self.game_scene.is_replay then return self.game_scene:onExitGame() end

        -- 
        csb_node:removeFromParent(true)

        if self.game_scene.cur_play_count == self.game_scene.total_play_count then
            self.game_scene:tryToShowFinalSettle()
        else
            self.game_scene:restart()
        end
    end, csb_node)

    -- 
    local btn_continue_size = btn_continue:getContentSize()

    local text = (self.game_scene.cur_play_count == self.game_scene.total_play_count and '查看战绩' or '继续游戏')
    if self.game_scene.is_replay then text = '退出游戏' end

    local btn_text_label = cc.Label:createWithTTF(text, 'font/jxk.TTF', 50)
    btn_text_label:setColorTextureIndex(2)
    btn_text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    btn_text_label:setPosition(btn_continue_size.width * 0.5, btn_continue_size.height * 0.5 + 5)
    btn_text_label:enableOutline(cc.c3b(28, 118, 14), 2)
    btn_text_label:enableShadow()
    btn_continue:getRendererNormal():addChild(btn_text_label)
end

return quick_settle
