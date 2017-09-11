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
    btn_settle_detail:loadTextureNormal('game_res/majiang/result/btn_detail.png', ccui.TextureResType.localType)

    -- 继续游戏
    local btn_continue = button('btn_continue_game', function()
        if self.game_scene.is_replay then return self.game_scene:onExitGame() end

        -- 
        csb_node:removeFromParent(true)

        if self:isGameEnd(result_info) then
            self.game_scene:tryToShowFinalSettle()
        else
            self.game_scene:restart()
        end
    end, csb_node)

    -- btn_last: 查看战绩，btn_continue: 继续游戏
    local text = (self:isGameEnd(result_info) and 'game_res/majiang/result/btn_last.png' or 'game_res/majiang/result/btn_continue.png')
    if self.game_scene.is_replay then text = 'game_res/majiang/result/btn_return.png' end
    btn_continue:loadTextureNormal(text, ccui.TextureResType.localType)

    -- 流局
    local win_index = nil
    for server_index=1, 4 do
        if result_info.m_win[server_index] then
            win_index = server_index
        end
    end

    if not win_index then
        csb_node:getChildByName('node_draw'):setVisible(true)
        csb_node:getChildByName('node_draw'):addChild(cc.Sprite:create(self.game_result_draw_sprite_file))
    end
end

return quick_settle
