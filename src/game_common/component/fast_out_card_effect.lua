-- ./app/platform/game/game_common/fast_out_card_effect.lua
require 'app.platform.game.game_common.game_component_base'

local fast_out_card_effect = class('fast_out_card_effect_component', component_base)
function fast_out_card_effect:init(args)
    component_base.init(self, args)

    -- 
    self.args = args

    --
    self:listenGameSignal('on_fast_out', function(server_index, count) self:on_fast_out(server_index, count) end)
end

function fast_out_card_effect:on_fast_out(server_index, count)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    local pos = self.args[location_index]

    local sprite = cc.Sprite:createWithSpriteFrameName('fast_out_card_inc_1.png')
    sprite:setPosition(pos.x, pos.y)
    self.game_scene:addChild(sprite, GAME_VIEW_Z_ORDER.USER_HEAD)

    local action_1 = cc.MoveBy:create(1.0, cc.p(0, 30))
    local action_2 = cc.FadeTo:create(1.0, 0)
    local action_4 = cc.Spawn:create(action_1, action_2)
    local action_5 = cc.CallFunc:create(function() sprite:removeFromParent(true) end)

    sprite:runAction(cc.Sequence:create(action_4, action_5))
end

return fast_out_card_effect
