-- ./app/platform/game/game_common/round_settle_big_score.lua
require 'app.platform.game.game_common.game_component_base'

local round_settle_big_score = class('normal_chat_component', component_base)
function round_settle_big_score:init(args)
    component_base.init(self)

    -- 大局结算的时候，隐藏
    self:listenGameSignal('settle_score', function(server_index, settle_score)
        local location_index = self.game_scene.server_index_to_local_index[server_index]
        if location_index ~= args.location_index then return end

        -- 
        if self.score_node then
            self.score_node:removeFromParent(true)
            self.score_node = nil
        end

        -- 
        self.score_node = cc.CSLoader:createNode(string.format('game_common_res/component/round_settle_score/%s_score.csb', settle_score >= 0 and 'inc' or 'dec'))
        self.score_node:setPosition(args.x, args.y)
        self.game_scene:addChild(self.score_node, GAME_VIEW_Z_ORDER.ROUND_SETTLE)

        -- 
        self.score_node:getChildByName('label_score'):setString('/' .. math.abs(settle_score))
    end)

    self:listenGameSignal('final_settle', function()
        if self.score_node then
            self.score_node:removeFromParent(true)
            self.score_node = nil
        end
    end)
end

function round_settle_big_score:on_prepare_next_round()
    component_base.on_prepare_next_round(self)

    -- 
    if self.score_node then
        self.score_node:removeFromParent(true)
        self.score_node = nil
    end
end

return round_settle_big_score
