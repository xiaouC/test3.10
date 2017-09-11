-- ./app/platform/game/game_common/out_card_guild.lua
require 'app.platform.game.game_common.game_component_base'

local out_card_guild = class('out_card_guild', component_base)
function out_card_guild:init(args)
    component_base.init(self)

    local function __cancel__()
        self.game_scene:unschedule(self.show_guild_effect_handler)
        self.show_guild_effect_handler = nil
    end

    -- 
    self.show_flag = false
    self:listenGameSignal('user_turn', function(server_index)
        if self.show_guild_effect_handler then __cancel__() end

        if server_index ~= self.game_scene.my_server_index then return end
        if self.show_flag then return end
        self.show_flag = true

        -- 
        self.show_guild_effect_handler = self.game_scene:schedule_once_time(5, function()
            self.guild_anim_node = createAnimNode('mahjong/component/out_card_guild/out_card_guild.csb')
            self.guild_anim_node:setPosition(display.width * 0.5, 220)
            self.game_scene:addChild(self.guild_anim_node, GAME_VIEW_Z_ORDER.TING_CARD)
        end)
    end)

    self:listenGameSignal('out_card', function(location_index, card_id)
        __cancel__()

        if self.guild_anim_node then
            self.guild_anim_node:removeFromParent(true)
            self.guild_anim_node = nil
        end
    end)

    self:listenGameSignal('reconn_lei_card', function(wall_count, kong_count)
        __cancel__()

        if self.guild_anim_node then
            self.guild_anim_node:removeFromParent(true)
            self.guild_anim_node = nil
        end
    end)
end

return out_card_guild
