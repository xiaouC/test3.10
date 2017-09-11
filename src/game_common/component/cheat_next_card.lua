-- ./app/platform/game/game_common/component/cheat_next_card.lua
require 'app.platform.game.game_common.game_component_base'

local clientmain = require 'app.platform.room.clientmain'
local basic_def = require 'app.platform.room.module.basicnotifydef'

local cheat_next_card = class('cheat_next_card_component', component_base)
function cheat_next_card:ctor(game_scene)
    component_base.ctor(self, game_scene)

    self.csb_z_order = GAME_VIEW_Z_ORDER.VOICE_CHAT
end

function cheat_next_card:init(args)
    component_base.init(self)

    if not GAME_TEST then return end

    --
    local btn_cheat = ccui.Button:create('game_common_btn_yellow.png', '', '', ccui.TextureResType.plistType)
    btn_cheat:setScale(0.5)
    btn_cheat:setTitleFontSize(40)
    btn_cheat:setTitleText('Click Me!')
    btn_cheat:setPosition(70, 100)
    self.game_scene:addChild(btn_cheat, self.csb_z_order)

    self.cheat_layer = nil
    btn_cheat:addClickEventListener(function()
        if not self.cheat_layer then
            local card_width, card_height = 85, 123
            local card_scale = 1

            local all_card_nodes = {}

            local down_card_node = nil
            local function on_touch_began(touch, event)
                for index, v in ipairs(all_card_nodes) do
                    local x, y = v.card_node:getPosition()
                    local rc = cc.rect(x - card_width * card_scale * 0.5, y - card_height * card_scale * 0.5, card_width * card_scale, card_height * card_scale)
                    if cc.rectContainsPoint(rc, touch:getLocation()) then
                        down_card_node = v.card_node

                        down_card_node:stopAllActions()
                        down_card_node:runAction(cc.ScaleTo:create(0.05, 0.9))

                        return true
                    end
                end

                return self.cheat_layer:isVisible()
            end
            local function on_touch_ended(touch, event)
                for index, v in ipairs(all_card_nodes) do
                    local x, y = v.card_node:getPosition()
                    local rc = cc.rect(x - card_width * card_scale * 0.5, y - card_height * card_scale * 0.5, card_width * card_scale, card_height * card_scale)
                    if cc.rectContainsPoint(rc, touch:getLocation()) then
                        if down_card_node == v.card_node then
                            self.game_scene:requestAction('swap_wall_card', v.card_id)
                        end

                        break
                    end
                end

                if down_card_node then
                    down_card_node:stopAllActions()
                    down_card_node:runAction(cc.ScaleTo:create(0.05, 1.0))

                    down_card_node = nil
                end
            end

            -- 
            self.cheat_layer = createBackgroundLayer(nil, true, on_touch_began, nil, on_touch_ended)
            self.game_scene:addChild(self.cheat_layer, self.csb_z_order)

            -- 
            local card_list = {
                { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, },
                { 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, },
                { 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, },
                { 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, },
            }

            local card_interval_x, card_interval_y = 30, 20

            local y = 580
            for _, v in ipairs(card_list) do
                local x = 180
                for index, card_id in ipairs(v) do
                    local card_node = create_card_front(USER_LOCATION_SELF, CARD_AREA.HAND, card_id)
                    card_node:setPosition(x, y)
                    card_node:setScale(card_scale)
                    self.cheat_layer:addChild(card_node)

                    table.insert(all_card_nodes, {
                        card_node = card_node,
                        card_id = card_id,
                    })

                    -- 
                    x = x + card_width + card_interval_x
                end

                y = y - (card_height + card_interval_y)
            end

            -- close button
            local btn_close = ccui.Button:create('game_common_btn_yellow.png', '', '', ccui.TextureResType.plistType)
            btn_close:setScale(0.8)
            btn_close:setTitleFontSize(40)
            btn_close:setTitleText('Close')
            btn_close:setPosition(1100, 120)
            self.cheat_layer:addChild(btn_close)

            btn_close:addClickEventListener(function()
                self.cheat_layer:removeFromParent(true)
                self.cheat_layer = nil
            end)
        end
    end)
end

return cheat_next_card
