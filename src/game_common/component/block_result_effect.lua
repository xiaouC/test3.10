-- ./app/platform/game/game_common/block_result_effect.lua
require 'app.platform.game.game_common.game_component_base'

local block_result_effect = class('block_result_effect_component', component_base)
function block_result_effect:init(args)
    component_base.init(self)

    -- 
    self.all_block_effects = {}
    self:init_block_effect_list()

    self.all_block_location_position = {}
    self:init_block_location_position()

    -- 
    self:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        local csb_effect = self.all_block_effects[block_type]
        if csb_effect then
            local pos = self.all_block_location_position[dest_location_index] or { x = 0, y = 0 }

            local anim_node = cc.CSLoader:createNode(csb_effect)
            anim_node:setPosition(pos.x, pos.y)
            self.game_scene:addChild(anim_node, GAME_VIEW_Z_ORDER.BLOCK)

            local anim_timeline = cc.CSLoader:createTimeline(csb_effect)
            anim_timeline:gotoFrameAndPlay(0, false)
            anim_node:runAction(anim_timeline)

            performWithDelay(anim_node, function()
                anim_node:removeFromParent(true)
            end, 1.5)
        end
    end)
end

function block_result_effect:init_block_effect_list()
    --self.all_block_effects['pass'] = 'mahjong/anim/anim_block_pass.csb'
    self.all_block_effects['chow'] = 'mahjong/anim/anim_block_chow.csb'
    self.all_block_effects['pong'] = 'mahjong/anim/anim_block_pong.csb'
    self.all_block_effects['kong_an'] = 'mahjong/anim/anim_block_kong.csb'
    self.all_block_effects['kong_ming'] = 'mahjong/anim/anim_block_kong.csb'
    self.all_block_effects['kong_bu'] = 'mahjong/anim/anim_block_kong.csb'
    self.all_block_effects['ting'] = 'mahjong/anim/anim_block_ting.csb'
    --self.all_block_effects['win'] = 'mahjong/anim/anim_block_win.csb'
end

function block_result_effect:init_block_location_position()
    self.all_block_location_position[USER_LOCATION_SELF] = { x = 640, y = 270 }
    self.all_block_location_position[USER_LOCATION_RIGHT] = { x = 820, y = 380 }
    self.all_block_location_position[USER_LOCATION_FACING] = { x = 640, y = 550 }
    self.all_block_location_position[USER_LOCATION_LEFT] = { x = 460, y = 380 }
end

return block_result_effect
