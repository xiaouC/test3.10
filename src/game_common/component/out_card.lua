-- ./app/platform/game/game_common/out_card.lua
require 'app.platform.game.game_common.game_card_config'
require 'app.platform.game.game_common.game_component_base'

local out_card_config = {
    [USER_LOCATION_SELF] = {
        start_x = 410,
        start_y = 290,
        card_width = 42,
        card_height = -48,
        scale = 1,
        max_count = 24,
        offset_x_2 = 0,
        offset_y_2 = 10,
        get_row_col = function(index) return math.floor(index / 12), math.floor(index % 12) end,
        z_order_sign = 1,
        out_z_order = GAME_VIEW_Z_ORDER.OUT_CARD_SELF,
    },
    [USER_LOCATION_RIGHT] = {
        start_x = 925,
        start_y = 250,
        card_width = 46,
        card_height = 34,
        scale = 0.9,
        max_count = 27,
        offset_x_2 = 0,
        offset_y_2 = 8,
        get_row_col = function(index) return math.floor(index % 9), math.floor(index / 9) end,
        z_order_sign = -1,
        out_z_order = GAME_VIEW_Z_ORDER.OUT_CARD_RIGHT,
    },
    [USER_LOCATION_FACING] = {
        start_x = 870,
        start_y = 475,
        card_width = -42,
        card_height = 48,
        scale = 1,
        max_count = 24,
        offset_x_2 = 0,
        offset_y_2 = 10,
        get_row_col = function(index) return math.floor(index / 12), math.floor(index % 12) end,
        z_order_sign = -1,
        out_z_order = GAME_VIEW_Z_ORDER.OUT_CARD_FACING,
    },
    [USER_LOCATION_LEFT] = {
        start_x = 355,
        start_y = 520,
        card_width = -46,
        card_height = -34,
        scale = 0.9,
        max_count = 27,
        offset_x_2 = 0,
        offset_y_2 = 8,
        get_row_col = function(index) return math.floor(index % 9), math.floor(index / 9) end,
        z_order_sign = 1,
        out_z_order = GAME_VIEW_Z_ORDER.OUT_CARD_LEFT,
    },
}

local out_card = class('out_card_component', component_base)
function out_card:ctor(game_scene)
    component_base.ctor(self, game_scene)
end

function out_card:init(args)
    component_base.init(self, args)

    self.location_index = args.location_index       -- 哪个区域

    -- 
    self.out_config = out_card_config[self.location_index]

    self.out_card_node_1 = cc.Node:create()
    self.game_scene:addChild(self.out_card_node_1, self.out_config.out_z_order)

    self.out_card_node_2 = cc.Node:create()
    self.game_scene:addChild(self.out_card_node_2, self.out_config.out_z_order + 1)

    self.node_cards = {}

    --
    self:listenGameSignal('out_card', function(location_index, card_id) self:out_card(location_index, card_id) end)
    self:listenGameSignal('on_reconn_out_card', function(location_index, card_list) self:on_reconn_out_card(location_index, card_list) end)
    self:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        self:on_block_result(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
    end)
    self:listenGameSignal('fp_effect_end', function(fp_location_index)
        if fp_location_index == self.location_index then
            self:clear_last_out_card()
        end
    end)
    self:listenGameSignal('hand_selected', function(card_id) self:on_hand_selected(card_id) end)
end

function out_card:on_prepare_next_round()
    for _, v in ipairs(self.node_cards) do
        v.card:removeFromParent(true)
    end
    self.node_cards = {}
end

function out_card:get_out_position()
    local count = #self.node_cards

    local offset_x, offset_y = 0, 0
    local out_card_node = self.out_card_node_1
    if count >= self.out_config.max_count then
        count = count - self.out_config.max_count
        out_card_node = self.out_card_node_2
        offset_x, offset_y = self.out_config.offset_x_2, self.out_config.offset_y_2
    end

    local row, col = self.out_config.get_row_col(count)

    local x = self.out_config.start_x + col * self.out_config.card_width + offset_x
    local y = self.out_config.start_y + row * self.out_config.card_height + offset_y
    local z_order = count * self.out_config.z_order_sign

    return out_card_node, x, y, z_order, self.out_config.scale
end

function out_card:out_card(location_index, card_id)
    if location_index ~= self.location_index then return end

    -- 出牌还原点
    self:pushRestorePoint()

    -- 
    local out_card_node, x, y, z_order, scale = self:get_out_position()

    local card = create_card_front(self.location_index, CARD_AREA.DISCARD, card_id)
    card:setPosition(x, y)
    card:setScale(scale)
    out_card_node:addChild(card, z_order)

    table.insert(self.node_cards, {
        card = card,
        card_id = card_id,
    })

    -- 
    self.game_scene:fire('out_card_position', location_index, x, y)
end

function out_card:on_reconn_out_card(location_index, card_list)
    if location_index ~= self.location_index then return end

    -- 清理一下
    self:on_prepare_next_round()
    
    -- 
    for _, card_id in ipairs(card_list or {}) do
        if card_id <= 0 then break end

        local out_card_node, x, y, z_order, scale = self:get_out_position()

        local card = create_card_front(self.location_index, CARD_AREA.DISCARD, card_id)
        card:setPosition(x, y)
        card:setScale(scale)
        out_card_node:addChild(card, z_order)

        table.insert(self.node_cards, {
            card = card,
            card_id = card_id,
        })
    end
end

function out_card:on_block_result(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
    if src_location_index ~= self.location_index then return end

    -- 拦牌还原点
    self:pushRestorePoint()

    -- 
    if block_type == 'chow' or block_type == 'pong' or block_type == 'kong_ming' or block_type == 'kong_ming_hui' then
        self:clear_last_out_card()
    end
end

function out_card:clear_last_out_card()
    if #self.node_cards > 0 then
        self.node_cards[#self.node_cards].card:removeFromParent(true)
        self.node_cards[#self.node_cards] = nil
    end

    -- 
    self.game_scene:fire('clear_last_out_card', self.location_index)
end

function out_card:on_hand_selected(card_id)
    for _, v in ipairs(self.node_cards) do
        if v.is_selected then
            if v.card_id ~= card_id then
                v.is_selected = nil
                for _, c_node in pairs(v.card:getChildren()) do
                    c_node:setColor(cc.c3b(255, 255, 255))
                end
            end
        else
            if v.card_id == card_id then
                v.is_selected = true
                for _, c_node in pairs(v.card:getChildren()) do
                    c_node:setColor(cc.c3b(192, 255, 143))
                end
            end
        end
    end
end

-- 出牌区还原点
-- 记录下来当前的出的牌，在还原的时候，就重新创建
function out_card:pushRestorePoint()
    if self.game_scene.pushRestorePoint then
        local rp_data = {}
        for _, v in ipairs(self.node_cards) do
            table.insert(rp_data, v.card_id)
        end

        -- 
        self.game_scene:pushRestorePoint(rp_data, function(rp_data)
            self:on_reconn_out_card(self.location_index, rp_data)
        end)
    end
end

return out_card
