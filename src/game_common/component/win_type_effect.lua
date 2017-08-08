-- ./app/platform/game/game_common/win_type_effect.lua
require 'app.platform.game.game_common.game_component_base'

local win_type_effect = class('win_type_effect_component', component_base)
function win_type_effect:init(args)
    component_base.init(self)

    -- 
    self.win_effect_position = {}
    self:init_win_effect_position()

    -- 
    self:listenGameSignal('win_effect', function(win_effect_type, location_index)
        local function __get_effect_file_path__()
            local file_path = string.format('game_res/%d/anim/win_effect/%s.csb', self.game_scene.game_id, win_effect_type)
            local file_path = cc.FileUtils:getInstance():fullPathForFilename(file_path)
            if cc.FileUtils:getInstance():isFileExist(file_path) then
                return file_path
            end

            local file_path = string.format('mahjong/anim/win_effect/%s.csb', win_effect_type)
            local file_path = cc.FileUtils:getInstance():fullPathForFilename(file_path)
            if cc.FileUtils:getInstance():isFileExist(file_path) then
                return file_path
            end
        end

        local file_path = __get_effect_file_path__()
        if file_path then
            local pos = self.win_effect_position[location_index] or { x = 0, y = 0 }

            local anim_node = createAnimNode(file_path, false)
            anim_node:setScale(2)
            anim_node:setPosition(pos.x, pos.y)
            self.game_scene:addChild(anim_node, GAME_VIEW_Z_ORDER.BLOCK)

            performWithDelay(anim_node, function() anim_node:removeFromParent(true) end, 1.9)
        end
    end)
end

function win_type_effect:init_win_effect_position()
    self.win_effect_position[USER_LOCATION_SELF] = { x = 640, y = 270 }
    self.win_effect_position[USER_LOCATION_RIGHT] = { x = 820, y = 380 }
    self.win_effect_position[USER_LOCATION_FACING] = { x = 640, y = 550 }
    self.win_effect_position[USER_LOCATION_LEFT] = { x = 460, y = 380 }
end

return win_type_effect
