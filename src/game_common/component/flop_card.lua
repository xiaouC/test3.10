-- ./app/platform/game/game_common/flop_card.lua
require 'app.platform.game.game_common.game_component_base'

local m_clientmain = require 'app.platform.room.clientmain'

local RollDiceView = class('RollDiceView', view_component_base)
function RollDiceView:ctor(game_scene)
    view_component_base.ctor(self, game_scene)

    self.csb_file = 'mahjong/component/flop_ghost_card/flop_card.csb'
    self.csb_z_order = GAME_VIEW_Z_ORDER.DICE
end

function RollDiceView:clear()
    view_component_base.clear(self)
end

function RollDiceView:init(args)
    view_component_base.init(self)

    -- 
    self.csb_node:setVisible(false)
    self.csb_node:setPosition(display.width * 0.5, display.height * 0.5)

    -- title
    local text_label = cc.Label:createWithTTF(args.flop_title, 'font/jxk.TTF', 54)
    text_label:setColorTextureIndex(2)
    text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    text_label:enableShadow()
    self.csb_node:getChildByName('node_text_title'):addChild(text_label)

    local all_temp_nodes = {}

    -- 
    self.fake_card_ids = {}
    self.really_card_ids = {}

    self:listenGameSignal('flop_ghost_card', function(fake_card_ids, really_card_ids, dice_num_1, dice_num_2, callback_func)
        self.fake_card_ids = fake_card_ids
        self.really_card_ids = really_card_ids

        -- 就是任性，先打个骰子
        self.game_scene:fire('roll_dice_custom', self.game_scene.banker_server_index, dice_num_1, dice_num_2, function()
            self.csb_node:setVisible(true)

            for _, node in ipairs(all_temp_nodes) do node:removeFromParent(true) end
            all_temp_nodes = {}

            -- 
            local anim_node = createAnimNode('mahjong/component/flop_ghost_card/anim_flop_card.csb', false)
            self.csb_node:addChild(anim_node)
            table.insert(all_temp_nodes, anim_node)

            -- 
            performWithDelay(self.csb_node, function()
                local node_ghost_card = cc.Node:create()
                self.csb_node:addChild(node_ghost_card)
                table.insert(all_temp_nodes, node_ghost_card)

                local card_width = 85
                local card_scale = 0.8
                local card_interval = 5

                -- 
                local fake_card = create_card_front(USER_LOCATION_SELF, CARD_AREA.HAND, self.fake_card_ids[1])
                fake_card:setPosition(0, 30)
                fake_card:setScale(card_scale)
                node_ghost_card:addChild(fake_card)

                -- 
                performWithDelay(self.csb_node, function()
                    local anim_boom = createAnimNode('mahjong/anim/anim_boom.csb', false)
                    anim_boom:setScale(1.3)
                    anim_boom:setPosition(0, 30)
                    self.csb_node:addChild(anim_boom)
                    table.insert(all_temp_nodes, anim_boom)

                    performWithDelay(self.csb_node, function()
                        fake_card:removeFromParent(true)

                        -- 
                        local card_count = #self.really_card_ids
                        local total_width = card_width * card_scale * card_count + (card_count - 1 ) * card_interval

                        local start_x = card_width * card_scale * 0.5 - total_width * 0.5
                        for _, card_id in ipairs(self.really_card_ids) do
                            local card = create_card_front(USER_LOCATION_SELF, CARD_AREA.HAND, card_id)
                            card:setPosition(start_x, 30)
                            card:setScale(card_scale)
                            node_ghost_card:addChild(card)

                            start_x = start_x + card_width * card_scale + card_interval
                        end
                    end, 0.3)

                    -- 
                    performWithDelay(self.csb_node, function()
                        local action_1 = cc.Spawn:create(cc.MoveBy:create(0.5, cc.p(-150, 0)), cc.ScaleTo:create(0.5, 0.75))
                        local action_2 = cc.CallFunc:create(function()
                            self.csb_node:setVisible(false)

                            if callback_func then callback_func() end
                        end)
                        node_ghost_card:runAction(cc.Sequence:create(action_1, action_2))
                    end, 1.3)
                end, 0.3)
            end, 0.5)
        end) -- end self.game_scene:fire('roll_dice_custom'
    end) -- end self:listenGameSignal('flop_ghost_card'
end

return RollDiceView
