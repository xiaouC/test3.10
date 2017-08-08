-- ./app/platform/game/game_common/out_card_tips.lua
require 'app.platform.game.game_common.game_component_base'

local out_card_tips = class('out_card_tips_component', component_base)
function out_card_tips:init(args)
    component_base.init(self)

    -- 
    self.icon_tips = cc.Sprite:createWithSpriteFrameName('out_card_tips.png')
    self.icon_tips:setVisible(false)
    self.game_scene:addChild(self.icon_tips, GAME_VIEW_Z_ORDER.OUT_CARD_TIPS)

    local mv_1 = cc.MoveBy:create(0.5, cc.p(0,15))
    local mv_2 = cc.MoveBy:create(0.5, cc.p(0,-15))
    self.icon_tips:runAction(CCRepeatForever:create(cc.Sequence:create(mv_1, mv_2)))

    self.last_out_card_x = 0
    self.last_out_card_y = 0

    local tips_offset_y = { 50, 35, 40, 35 }
    self:listenGameSignal('out_card_position', function(location_index, x, y)
        self.last_out_card_x = x
        self.last_out_card_y = y

        self.icon_tips:setPosition(x, y + tips_offset_y[location_index])
        self.icon_tips:setVisible(true)
    end)
    self:listenGameSignal('clear_last_out_card', function(location_index)
        self.icon_tips:setVisible(false)
    end)

    local fp_offset_y = { 70, 55, 60, 55 }
    self:listenGameSignal('win_effect', function(win_effect_type, location_index)
        if win_effect_type == 'fp' then
            local anim_node = createAnimNode('mahjong/anim/win_effect/fp_zhua.csb', false)
            anim_node:setScale(2)
            anim_node:setPosition(self.last_out_card_x, self.last_out_card_y + fp_offset_y[location_index])
            self.game_scene:addChild(anim_node, GAME_VIEW_Z_ORDER.OUT_CARD_TIPS)

            performWithDelay(anim_node, function() anim_node:removeFromParent(true) end, 1.9)
        end
    end)
end

function out_card_tips:on_prepare_next_round()
    self.icon_tips:setVisible(false)
end

return out_card_tips
