-- ./app/platform/game/game_common/ting_card.lua
require 'app.platform.game.game_common.game_card_config'
require 'app.platform.game.game_common.game_component_base'

local ting_card = class('ting_card_component', component_base)
function ting_card:ctor(game_scene)
    component_base.ctor(self, game_scene)
end

function ting_card:init(args)
    component_base.init(self, args)

    -- 带不带番
    self.has_fan_count = args.has_fan_count
    self.item_width = 60
    self.item_height = self.has_fan_count and 100 or 70

    self.origin_x, self.origin_y = 240, 200

    -- 
    self.cb_ting = ccui.Button:create('mahjong/component/ting_list/ting_checked.png', 'mahjong/component/ting_list/ting_unchecked.png')
    self.cb_ting:setVisible(false)
    self.cb_ting:setPosition(args.x, args.y)
    self.game_scene:addChild(self.cb_ting, GAME_VIEW_Z_ORDER.TING_CARD)

    -- 
    self.csb_node = cc.CSLoader:createNode('mahjong/component/ting_list/ting_node.csb')
    self.csb_node:setVisible(false)
    self.csb_node:setPosition(self.origin_x, self.origin_y)
    self.game_scene:addChild(self.csb_node, GAME_VIEW_Z_ORDER.TING_CARD)

    -- 
    self.card_list_valid = false
    self.cb_ting_checked = true

    self.cb_ting:addClickEventListener(function()
        self.cb_ting_checked = not self.cb_ting_checked
        self.cb_ting:loadTextureNormal(self.cb_ting_checked and 'mahjong/component/ting_list/ting_checked.png' or 'mahjong/component/ting_list/ting_unchecked.png')
        self.csb_node:setVisible(self.card_list_valid and self.cb_ting_checked)
    end)

    -- 
    self.all_ting_cards = {}
    self.node_card = self.csb_node:getChildByName(self.has_fan_count and 'node_card' or 'node_card_simple')

    self.origin_width, self.origin_height = 40, 30
    self.bg_scale9 = self.csb_node:getChildByName('background_scale9')

    self:listenGameSignal('reset_ting_card', function(card_list) self:resetTingCard(card_list) end)
    self:listenGameSignal('update_ting_card', function(update_card_list) self:updateTingCard(update_card_list) end)
    self:listenGameSignal('dec_ting_card', function(card_id, count) self:decTingCard(card_id, count) end)
    self:listenGameSignal('ting_card_list', function(max_win_count, ting_groups) self.csb_node:setVisible(false) end)
    self:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        if block_type == 'win' or block_type == 'draw' then
            self.node_card:removeAllChildren()
            self.all_ting_cards = {}
            self.csb_node:setVisible(false)
        end

        local server_index = self.game_scene.local_index_to_server_index[dest_location_index]
        if server_index ~= self.game_scene.my_server_index then
            if block_type == 'chow' then
                self:decTingCard(show_card_list[1], 1)
                self:decTingCard(show_card_list[2], 1)
            end

            if block_type == 'pong' then
                self:decTingCard(show_card_list[1], 2)
            end

            if block_type == 'kong_bu' then
                self:decTingCard(show_card_list[1], 1)
            end

            if block_type == 'kong_ming' then
                self:decTingCard(show_card_list[1], 3)
            end

            if block_type == 'kong_an' then
                self:decTingCard(show_card_list[1], 4)
            end
        end
    end)

    -- 自己摸牌，剩余牌减 1
    self:listenGameSignal('draw_card', function(location_index, card_id, is_kong, callback_func)
        local server_index = self.game_scene.local_index_to_server_index[location_index]
        if server_index == self.game_scene.my_server_index then
            self:decTingCard(card_id, 1)
        end
    end)
    -- 其他玩家出牌，剩余牌减 1
    self:listenGameSignal('out_card', function(location_index, card_id)
        local server_index = self.game_scene.local_index_to_server_index[location_index]
        if server_index ~= self.game_scene.my_server_index then
            self:decTingCard(card_id, 1)
        end
    end)
end

function ting_card:on_prepare_next_round()
    self.node_card:removeAllChildren()

    self.all_ting_cards = {}

    self.card_list_valid = false
    self.cb_ting_checked = true

    self.csb_node:setVisible(false)

    self.cb_ting:setVisible(false)
    self.cb_ting:loadTextureNormal('mahjong/component/ting_list/ting_checked.png')
end

function ting_card:resetTingCard(card_list)
    self.all_ting_cards = {}

    -- 
    self.node_card:removeAllChildren()

    if self:is_any_card_win(card_list) then
        self.card_list_valid = true
        self.cb_ting:setVisible(self.card_list_valid)
        self.csb_node:setVisible(self.card_list_valid and self.cb_ting_checked)

        self.csb_node:getChildByName('ting_title'):setVisible(false)
        self.bg_scale9:setContentSize(cc.size(self.origin_width + self.item_width + 40, self.origin_height + self.item_height + 30))
        self.csb_node:setPosition(self.origin_x, self.origin_y)

        local anim_any_card = createAnimNode('mahjong/anim/anim_any_card.csb')
        anim_any_card:setPosition(10, -5)
        self.node_card:addChild(anim_any_card)

        local any_card_line_node = createAnimNode('mahjong/anim/anim_any_card_line.csb')
        any_card_line_node:setScale(1.32)
        any_card_line_node:setPosition(390, -190)
        self.node_card:addChild(any_card_line_node)

        return
    end

    ----------------------------------------------------------------------------------------------------------------
    -- resize content size
    local card_count = #card_list

    self.card_list_valid = card_count > 0
    self.cb_ting:setVisible(self.card_list_valid)
    self.csb_node:setVisible(self.card_list_valid and self.cb_ting_checked)
    self.csb_node:getChildByName('ting_title'):setVisible(true)

    -- 高宽
    local row_count = math.floor((card_count - 1) / 12) + 1
    local col_count = (card_count >= 12 and 12 or card_count)
    self.bg_scale9:setContentSize(cc.size(self.origin_width + col_count * self.item_width, self.origin_height + row_count * self.item_height))
    self.csb_node:setPosition(self.origin_x, self.origin_y + (row_count - 1) * self.item_height)

    -- 
    for index, v in ipairs(card_list) do
        local row = math.floor((index - 1) / 12)
        local col = math.floor((index - 1) % 12)

        local node = cc.CSLoader:createNode(self.has_fan_count and 'mahjong/component/ting_list/ting_node_card.csb' or 'mahjong/component/ting_list/ting_node_card_simple.csb')
        node:setPosition(col * self.item_width, -row * self.item_height)
        self.node_card:addChild(node)

        node:getChildByName('node_card'):addChild(create_card_sprite(v.card_id))

        local text_num_bg = node:getChildByName('ting_num_bg')
        text_num_bg:setSpriteFrame(v.card_count > 0 and 'ting_num_bg_1.png' or 'ting_num_bg_2.png')

        local text_card_count = node:getChildByName('ting_num')
        text_card_count:setSpriteFrame(string.format('ting_num_%d.png', v.card_count))

        local text_fan_count = nil
        if self.has_fan_count then
            text_fan_count = node:getChildByName('text_fan_count')
            text_fan_count:setString(v.fan_count .. '番')
            text_fan_count:setColor(v.card_count > 0 and cc.c3b(174, 37, 5) or cc.c3b(110, 110, 110))
        end

        table.insert(self.all_ting_cards, {
            node = node,
            text_num_bg = text_num_bg,
            text_card_count = text_card_count,
            text_fan_count = text_fan_count,
            card_id = v.card_id,
            card_count = v.card_count,
            fan_count = v.fan_count,
        })
    end
end

function ting_card:updateTingCard(update_card_list)
    for _, v in ipairs(update_card_list or {}) do
        for _, vv in ipairs(self.all_ting_cards or {}) do
            if v.card_id == vv.card_id then
                if vv.card_count ~= v.card_count then
                    vv.card_count = v.card_count

                    vv.text_num_bg:setSpriteFrame(v.card_count > 0 and 'ting_num_bg_1.png' or 'ting_num_bg_2.png')
                    vv.text_card_count:setSpriteFrame(string.format('ting_num_%d.png', v.card_count))

                    if self.has_fan_count then
                        vv.text_fan_count:setColor(v.card_count > 0 and cc.c3b(174, 37, 5) or cc.c3b(110, 110, 110))
                    end
                end

                if self.has_fan_count and vv.fan_count ~= v.fan_count then
                    vv.fan_count = v.fan_count
                    if vv.text_fan_count then
                        vv.text_fan_count:setString(v.fan_count .. '番')
                    end
                end

                break
            end
        end
    end
end

function ting_card:decTingCard(card_id, count)
    for _, v in ipairs(self.all_ting_cards or {}) do
        if v.card_id == card_id then
            v.card_count = v.card_count - count

            v.text_num_bg:setSpriteFrame(v.card_count > 0 and 'ting_num_bg_1.png' or 'ting_num_bg_2.png')
            v.text_card_count:setSpriteFrame(string.format('ting_num_%d.png', v.card_count))

            if self.has_fan_count then
                v.text_fan_count:setColor(v.card_count > 0 and cc.c3b(174, 37, 5) or cc.c3b(110, 110, 110))
            end

            return
        end
    end
end

function ting_card:is_any_card_win(card_list)
    return #card_list >= 27
end

return ting_card
