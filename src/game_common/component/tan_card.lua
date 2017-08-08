-- ./app/platform/game/game_common/tan_card.lua
require 'app.platform.game.game_common.game_card_config'
require 'app.platform.game.game_common.game_component_base'

local tan_location_config = {
    [USER_LOCATION_SELF] = {
        start_x = 80,
        start_y = 55,
        x_inc = 64,
        y_inc = 0,
        x_kong_inc = 0,
        y_kong_inc = 23,
        x_block_offset = 40,
        y_block_offset = 0,
        z_order_inc = 0,
        tan_z_order = GAME_VIEW_Z_ORDER.TAN_CARD_SELF,
    },
    [USER_LOCATION_RIGHT] = {
        start_x = 1190,
        start_y = 140,
        x_inc = 0,
        y_inc = 35,
        x_kong_inc = 7,
        y_kong_inc = 0,
        x_block_offset = 0,
        y_block_offset = 10,
        z_order_inc = -1,
        tan_z_order = GAME_VIEW_Z_ORDER.TAN_CARD_RIGHT,
    },
    [USER_LOCATION_FACING] = {
        start_x = 1000,
        start_y = 680,
        x_inc = -37,
        y_inc = 0,
        x_kong_inc = 0,
        y_kong_inc = 7,
        x_block_offset = -20,
        y_block_offset = 0,
        z_order_inc = 1,
        tan_z_order = GAME_VIEW_Z_ORDER.TAN_CARD_FACING,
    },
    [USER_LOCATION_LEFT] = {
        start_x = 100,
        start_y = 630,
        x_inc = 0,
        y_inc = -35,
        x_kong_inc = -7,
        y_kong_inc = 0,
        x_block_offset = 0,
        y_block_offset = -10,
        z_order_inc = 0,
        tan_z_order = GAME_VIEW_Z_ORDER.TAN_CARD_LEFT,
    },
}

local tan_card = class('tan_card_component', component_base)
function tan_card:ctor(game_scene)
    component_base.ctor(self, game_scene)

    self.all_block_data = {}
end

function tan_card:init(args)
    component_base.init(self, args)

    self.location_index = args.location_index       -- 哪个区域

    -- 
    self.tan_config = tan_location_config[self.location_index]

    self.next_x, self.next_y = self.tan_config.start_x, self.tan_config.start_y
    self.next_z_order = 0

    self.tan_card_node = cc.Node:create()
    self.game_scene:addChild(self.tan_card_node, self.tan_config.tan_z_order)

    --
    self.game_scene:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        self:on_block_result(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
    end)
    self.game_scene:listenGameSignal('on_reconn_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        self:on_block_result(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
    end)
end

function tan_card:on_prepare_next_round()
    self.tan_card_node:removeAllChildren()
    self.all_block_data = {}

    -- 
    self.next_x, self.next_y = self.tan_config.start_x, self.tan_config.start_y
    self.next_z_order = 0
end

function tan_card:create_card(card_id, is_back)
    if is_back or card_id <= 0 then return create_card_back(self.location_index, CARD_AREA.TAN) end

    return create_card_front(self.location_index, CARD_AREA.TAN, card_id)
end

function tan_card:get_next_position(i, block_type)
    local x, y, z_order = self.next_x, self.next_y, self.next_z_order

    if (block_type == 'kong_an' or block_type == 'kong_ming' or block_type == 'kong_bu') and i == 3 then
        x = x - self.tan_config.x_inc + self.tan_config.x_kong_inc
        y = y - self.tan_config.y_inc + self.tan_config.y_kong_inc
        z_order = 100
    else
        self.next_x = self.next_x + self.tan_config.x_inc
        self.next_y = self.next_y + self.tan_config.y_inc
        self.next_z_order = self.next_z_order + self.tan_config.z_order_inc
    end

    return x, y, z_order
end

function tan_card:get_bu_kong_position(card_id)
    for _, v in ipairs(self.all_block_data) do
        if v.block_type == 'pong' then
            for _, id in ipairs(v.card_list) do
                if id == card_id then
                    local x, y = v.node_cards[2]:getPosition()

                    return x + self.tan_config.x_kong_inc, y + self.tan_config.y_kong_inc, 100, v
                end
            end
        end
    end
end

function tan_card:on_block_result(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
    if self.location_index ~= dest_location_index then return end

    if #show_card_list == 0 then return end

    -- 补杠
    if block_type == 'kong_bu' then
        local card_id = show_card_list[1]
        local x, y, z_order, block_data = self:get_bu_kong_position(card_id)

        local card = self:create_card(card_id, false)
        card:setPosition(x, y)
        self.tan_card_node:addChild(card, z_order)

        block_data.block_type = 'kong_ming'
        table.insert(block_data.card_list, card_id)
        table.insert(block_data.node_cards, card)

        return
    end

    -- 
    local block_data = {
        block_type = block_type,
        card_list = show_card_list,
        node_cards = {},
    }

    for i, card_id in ipairs(show_card_list or {}) do
        local x, y, z_order = self:get_next_position(i, block_type)

        local card = self:create_card(card_id, false)
        card:setPosition(x, y)
        self.tan_card_node:addChild(card, z_order)

        block_data.node_cards[i] = card
    end

    table.insert(self.all_block_data, block_data)

    -- 
    self.next_x = self.next_x + self.tan_config.x_block_offset
    self.next_y = self.next_y + self.tan_config.y_block_offset
end

-- 碰杠区的牌的还原点
-- 记录下当前碰杠的牌，在还原的时候，就重新显示
function tan_card:pushRestorePoint()
    if self.game_scene.pushRestorePoint then
        local rp_data = {}
        for _, v in ipairs(self.all_block_data) do
            table.insert(rp_data, {
                block_type = v.block_type,
                card_list = clone(v.card_list),
            })
        end

        -- 
        self.game_scene:pushRestorePoint(rp_data, function(rp_data)
            self.tan_card_node:removeAllChildren()
            self.all_block_data = {}

            -- 
            self.next_x, self.next_y = self.tan_config.start_x, self.tan_config.start_y
            self.next_z_order = 0

            -- 
            for _, v in ipairs(rp_data) do
                local block_data = {
                    block_type = v.block_type,
                    card_list = v.card_list,
                    node_cards = {},
                }

                for i, card_id in ipairs(v.card_list or {}) do
                    local x, y, z_order = self:get_next_position(i, v.block_type)

                    local card = self:create_card(card_id, false)
                    card:setPosition(x, y)
                    self.tan_card_node:addChild(card, z_order)

                    block_data.node_cards[i] = card
                end

                table.insert(self.all_block_data, block_data)

                -- 
                self.next_x = self.next_x + self.tan_config.x_block_offset
                self.next_y = self.next_y + self.tan_config.y_block_offset
            end
        end)
    end
end

return tan_card
