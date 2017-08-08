-- ./app/platform/game/game_common/next_round_ready.lua
require 'app.platform.game.game_common.game_component_base'

local next_round_ready = class('next_round_ready_component', component_base)
function next_round_ready:init(args)
    component_base.init(self, args)

    -- 
    self.args = args

    -- 
    self.node = cc.Node:create()
    self.node:setVisible(false)
    self.game_scene:addChild(self.node, GAME_VIEW_Z_ORDER.BLOCK)

    -- 
    self.all_ready_sprites = {}

    self:listenGameSignal('on_user_ready', function(server_index, is_ready) self:on_user_ready(server_index, is_ready) end)
end

function next_round_ready:on_round_end()
    for _, sprite in pairs(self.all_ready_sprites) do
        sprite:setVisible(false)
    end
    self.node:setVisible(true)
end

function next_round_ready:on_game_start()
    self.node:setVisible(false)
end

function next_round_ready:on_user_ready(server_index, is_ready)
    local location_index = self.game_scene.server_index_to_local_index[server_index]

    if not self.all_ready_sprites[location_index] then
        self.all_ready_sprites[location_index] = cc.Sprite:createWithSpriteFrameName('next_round_ready.png')
        self.node:addChild(self.all_ready_sprites[location_index])

        local pos = self.args[location_index]
        if pos then
            self.all_ready_sprites[location_index]:setPosition(pos.x, pos.y)
        end
    end

    self.all_ready_sprites[location_index]:setVisible(is_ready)
end

return next_round_ready
