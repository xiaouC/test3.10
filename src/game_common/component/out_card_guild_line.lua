-- ./app/platform/game/game_common/out_card_guild_line.lua
require 'app.platform.game.game_common.game_component_base'

local out_card_guild_line = class('out_card_guild_line', component_base)
function out_card_guild_line:init(args)
    component_base.init(self)

    local is_show_flag = false

    -- 
    self:listenGameSignal('user_turn', function(server_index)
        if is_show_flag then return end
        if server_index ~= self.game_scene.my_server_index then return end

        is_show_flag = true

        self.out_card_line_sprite = cc.Sprite:createWithSpriteFrameName('touch_moved_out_card_line.png')
        self.out_card_line_sprite:setPosition(display.width * 0.5, 132)
        self.game_scene:addChild(self.out_card_line_sprite, GAME_VIEW_Z_ORDER.HAND_CARD_SELF)
    end)

    self:listenGameSignal('out_card', function(location_index, card_id)
        if self.out_card_line_sprite then
            self.out_card_line_sprite:removeFromParent(true)
            self.out_card_line_sprite = nil
        end
    end)

    self:listenGameSignal('reconn_lei_card', function(wall_count, kong_count)
        if self.out_card_line_sprite then
            self.out_card_line_sprite:removeFromParent(true)
            self.out_card_line_sprite = nil
        end
    end)
end

return out_card_guild_line
