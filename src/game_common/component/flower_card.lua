-- ./app/platform/game/game_common/flower_card.lua
require 'app.platform.game.game_common.game_card_config'
require 'app.platform.game.game_common.game_component_base'

local flower_location_config = {
    [USER_LOCATION_SELF] = {
        start_x = 870,
        start_y = 135,
        x_inc = -39,
        y_inc = 0,
        scale = 0.6,
        z_order_inc = 0,
        flower_z_order = GAME_VIEW_Z_ORDER.LEI_CARD_SELF - 1,
    },
    [USER_LOCATION_RIGHT] = {
        start_x = 1118,
        start_y = 570,
        x_inc = 0,
        y_inc = -33,
        scale = 0.9,
        z_order_inc = -1,
        flower_z_order = GAME_VIEW_Z_ORDER.LEI_CARD_RIGHT - 1,
    },
    [USER_LOCATION_FACING] = {
        start_x = 420,
        start_y = 630,
        x_inc = 33,
        y_inc = 0,
        scale = 0.9,
        z_order_inc = 1,
        flower_z_order = GAME_VIEW_Z_ORDER.LEI_CARD_FACING - 1,
    },
    [USER_LOCATION_LEFT] = {
        start_x = 163,
        start_y = 205,
        x_inc = 0,
        y_inc = 33,
        scale = 0.9,
        z_order_inc = 0,
        flower_z_order = GAME_VIEW_Z_ORDER.LEI_CARD_LEFT - 1,
    },
}

local flower_card = class('flower_card_component', component_base)
function flower_card:ctor(game_scene)
    component_base.ctor(self, game_scene)

    self.all_flower_cards = {}
end

function flower_card:init(args)
    component_base.init(self, args)

    self.location_index = args.location_index       -- 哪个区域

    -- 
    self.flower_config = flower_location_config[self.location_index]

    self.next_x, self.next_y = self.flower_config.start_x, self.flower_config.start_y
    self.next_z_order = 0

    self.flower_card_node = cc.Node:create()
    self.game_scene:addChild(self.flower_card_node, self.flower_config.flower_z_order)

    --
    self:listenGameSignal('on_flower', function(location_index, card_id) self:on_flower(location_index, card_id) end)
    self:listenGameSignal('on_reconn_flower', function(location_index, card_list, card_num) self:on_reconn_flower(location_index, card_list, card_num) end)
end

function flower_card:on_prepare_next_round()
    self.flower_card_node:removeAllChildren()
    self.all_flower_cards = {}

    -- 
    self.next_x, self.next_y = self.flower_config.start_x, self.flower_config.start_y
    self.next_z_order = 0
end

function flower_card:create_card(card_id)
    return create_card_front(self.location_index, CARD_AREA.TAN, card_id)
end

function flower_card:get_next_position()
    local x, y, z_order = self.next_x, self.next_y, self.next_z_order

    self.next_x = self.next_x + self.flower_config.x_inc
    self.next_y = self.next_y + self.flower_config.y_inc
    self.next_z_order = self.next_z_order + self.flower_config.z_order_inc

    return x, y, z_order, self.flower_config.scale
end

function flower_card:on_flower(location_index, card_id)
    if self.location_index ~= location_index then return end

    -- 
    self:pushRestorePoint()

    -- 
    local x, y, z_order, scale = self:get_next_position()

    local card = self:create_card(card_id)
    card:setPosition(x, y)
    card:setScale(scale)
    self.flower_card_node:addChild(card, z_order)

    table.insert(self.all_flower_cards, {
        card = card,
        card_id = card_id,
    })
end

function flower_card:on_reconn_flower(location_index, card_list, card_num)
    if location_index ~= self.location_index then return end

    -- 
    self:on_prepare_next_round()

    for i=1, card_num do
        local card_id = card_list[i]
        local x, y, z_order, scale = self:get_next_position()

        local card = self:create_card(card_id)
        card:setPosition(x, y)
        card:setScale(scale)
        self.flower_card_node:addChild(card, z_order)

        table.insert(self.all_flower_cards, {
            card = card,
            card_id = card_id,
        })
    end
end

-- 花牌的还原点，记录下当前的花牌，在还原的时候，就重新显示
function flower_card:pushRestorePoint()
    if self.game_scene.pushRestorePoint then
        local rp_data = {}
        for _, v in ipairs(self.all_flower_cards) do
            table.insert(rp_data, v.card_id)
        end

        -- 
        self.game_scene:pushRestorePoint(rp_data, function(rp_data)
            self:on_reconn_flower(self.location_index, rp_data)
        end)
    end
end

return flower_card
