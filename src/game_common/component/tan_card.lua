-- ./app/platform/game/game_common/tan_card.lua
require 'app.platform.game.game_common.game_card_config'
require 'app.platform.game.game_common.game_component_base'

local tan_location_config = {
    [USER_LOCATION_SELF] = {
        start_x = 20,
        start_y = 55,
        x_inc_1 = 64,
        y_inc_1 = 0,
        x_inc_2 = 64,
        y_inc_2 = 0,
        x_kong_inc = 0,
        y_kong_inc = 23,
        x_block_offset = 30,
        y_block_offset = 0,
        z_order_inc = 0,
        tan_z_order = GAME_VIEW_Z_ORDER.TAN_CARD_SELF,
    },
    [USER_LOCATION_RIGHT] = {
        start_x = 1168,
        start_y = 100,
        x_inc_1 = 0,
        y_inc_1 = 35,
        x_inc_2 = 0,
        y_inc_2 = 39,
        x_kong_inc = 7,
        y_kong_inc = 0,
        x_block_offset = 0,
        y_block_offset = 10,
        z_order_inc = -1,
        tan_z_order = GAME_VIEW_Z_ORDER.TAN_CARD_RIGHT,
    },
    [USER_LOCATION_FACING] = {
        start_x = 920,
        start_y = 675,
        x_inc_1 = -37,
        y_inc_1 = 0,
        x_inc_2 = -40,
        y_inc_2 = 0,
        x_kong_inc = 0,
        y_kong_inc = 7,
        x_block_offset = -10,
        y_block_offset = 0,
        z_order_inc = 1,
        tan_z_order = GAME_VIEW_Z_ORDER.TAN_CARD_FACING,
    },
    [USER_LOCATION_LEFT] = {
        start_x = 113,
        start_y = 680,
        x_inc_1 = 0,
        y_inc_1 = -35,
        x_inc_2 = 0,
        y_inc_2 = -39,
        x_kong_inc = -7,
        y_kong_inc = 0,
        x_block_offset = 0,
        y_block_offset = -10,
        z_order_inc = 0,
        tan_z_order = GAME_VIEW_Z_ORDER.TAN_CARD_LEFT,
    },
}

local arrow_file = { 'mahjong/common/you.png', }

local arrow_config = {
    [USER_LOCATION_SELF] = {
        arrow_file = {
            [USER_LOCATION_RIGHT] = 'mahjong/common/you.png',
            [USER_LOCATION_FACING] = 'mahjong/common/shang.png',
            [USER_LOCATION_LEFT] = 'mahjong/common/zuo.png',
        },
        arrow_x = 0,
        arrow_y = 50,
        scale = 1,
    },
    [USER_LOCATION_RIGHT] = {
        arrow_file = {
            [USER_LOCATION_SELF] = 'mahjong/common/xia.png',
            [USER_LOCATION_FACING] = 'mahjong/common/shang.png',
            [USER_LOCATION_LEFT] = 'mahjong/common/zuo.png',
        },
        arrow_x = -25,
        arrow_y = 0,
        scale = 0.6,
    },
    [USER_LOCATION_FACING] = {
        arrow_file = {
            [USER_LOCATION_RIGHT] = 'mahjong/common/you.png',
            [USER_LOCATION_SELF] = 'mahjong/common/xia.png',
            [USER_LOCATION_LEFT] = 'mahjong/common/zuo.png',
        },
        arrow_x = 0,
        arrow_y = -25,
        scale = 0.6,
    },
    [USER_LOCATION_LEFT] = {
        arrow_file = {
            [USER_LOCATION_RIGHT] = 'mahjong/common/you.png',
            [USER_LOCATION_SELF] = 'mahjong/common/xia.png',
            [USER_LOCATION_FACING] = 'mahjong/common/shang.png',
        },
        arrow_x = 25,
        arrow_y = 0,
        scale = 0.6,
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
    self.need_point_to_src_location = args.need_point_to_src_location     -- 指向出牌碰杠的玩家
    self.need_arrow = args.need_arrow

    -- 
    self.tan_config = tan_location_config[self.location_index]

    self.last_x, self.last_y = self.tan_config.start_x, self.tan_config.start_y
    self.last_z_order = 0

    self.tan_card_node = cc.Node:create()
    self.game_scene:addChild(self.tan_card_node, self.tan_config.tan_z_order)

    --
    self.game_scene:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        self:on_block_result(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
    end)
    self.game_scene:listenGameSignal('on_reconn_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        self:on_block_result(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
    end)
    self.game_scene:listenGameSignal('on_reconn_clean_block_result', function(location_index)
        if location_index == self.location_index then
            self.tan_card_node:removeAllChildren()
            self.all_block_data = {}

            -- 
            self.last_x, self.last_y = self.tan_config.start_x, self.tan_config.start_y
            self.last_z_order = 0
        end
    end)
end

function tan_card:on_prepare_next_round()
    self.tan_card_node:removeAllChildren()
    self.all_block_data = {}

    -- 
    self.last_x, self.last_y = self.tan_config.start_x, self.tan_config.start_y
    self.last_z_order = 0
end

function tan_card:create_card(card_id, is_back, need_rotation, src_arrow_location_index)
    local function __real_create_card__()
        if need_rotation then
            if is_back or card_id <= 0 then return create_card_back_hor(self.location_index, CARD_AREA.TAN) end

            return create_card_front_hor(self.location_index, CARD_AREA.TAN, card_id)
        end

        -- 
        if is_back or card_id <= 0 then return create_card_back(self.location_index, CARD_AREA.TAN) end

        return create_card_front(self.location_index, CARD_AREA.TAN, card_id)
    end

    local card = __real_create_card__()
    if src_arrow_location_index then
        local arrow_sprite = cc.Sprite:create(arrow_config[self.location_index].arrow_file[src_arrow_location_index])
        arrow_sprite:setPosition(arrow_config[self.location_index].arrow_x, arrow_config[self.location_index].arrow_y)
        arrow_sprite:setScale(arrow_config[self.location_index].scale)
        card:addChild(arrow_sprite)
    end

    return card
end

function tan_card:get_position(i, block_type, src_location_index, dest_location_index)
    local position_config = {
        [1] = function()
            if self.need_point_to_src_location and is_left_user(src_location_index, dest_location_index) then
                self.last_x = self.last_x + self.tan_config.x_inc_2
                self.last_y = self.last_y + self.tan_config.y_inc_2
                self.last_z_order = self.last_z_order + self.tan_config.z_order_inc
            else
                self.last_x = self.last_x + self.tan_config.x_inc_1
                self.last_y = self.last_y + self.tan_config.y_inc_1
                self.last_z_order = self.last_z_order + self.tan_config.z_order_inc
            end
            return self.last_x, self.last_y, self.last_z_order
        end,
        [2] = function()
            if self.need_point_to_src_location and is_left_user(src_location_index, dest_location_index) then
                self.last_x = self.last_x + self.tan_config.x_inc_2
                self.last_y = self.last_y + self.tan_config.y_inc_2
                self.last_z_order = self.last_z_order + self.tan_config.z_order_inc
            else
                self.last_x = self.last_x + self.tan_config.x_inc_1
                self.last_y = self.last_y + self.tan_config.y_inc_1
                self.last_z_order = self.last_z_order + self.tan_config.z_order_inc
            end
            return self.last_x, self.last_y, self.last_z_order
        end,
        [3] = function()
            if block_type == 'kong_an' or block_type == 'kong_ming' or block_type == 'kong_bu' then
                return self.last_x + self.tan_config.x_kong_inc, self.last_y + self.tan_config.y_kong_inc, 100
            else
                if self.need_point_to_src_location and is_right_user(src_location_index, dest_location_index) then
                    self.last_x = self.last_x + self.tan_config.x_inc_2
                    self.last_y = self.last_y + self.tan_config.y_inc_2
                    self.last_z_order = self.last_z_order + self.tan_config.z_order_inc
                else
                    self.last_x = self.last_x + self.tan_config.x_inc_1
                    self.last_y = self.last_y + self.tan_config.y_inc_1
                    self.last_z_order = self.last_z_order + self.tan_config.z_order_inc
                end
                return self.last_x, self.last_y, self.last_z_order
            end
        end,
        [4] = function()
            if self.need_point_to_src_location and is_right_user(src_location_index, dest_location_index) then
                self.last_x = self.last_x + self.tan_config.x_inc_2
                self.last_y = self.last_y + self.tan_config.y_inc_2
                self.last_z_order = self.last_z_order + self.tan_config.z_order_inc
            else
                self.last_x = self.last_x + self.tan_config.x_inc_1
                self.last_y = self.last_y + self.tan_config.y_inc_1
                self.last_z_order = self.last_z_order + self.tan_config.z_order_inc
            end
            return self.last_x, self.last_y, self.last_z_order
        end,
    }

    return position_config[i]()
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

    self:pushRestorePoint()

    -- 补杠
    if block_type == 'kong_bu' then
        local card_id = show_card_list[1]
        local x, y, z_order, block_data = self:get_bu_kong_position(card_id)

        local card = self:create_card(card_id, false, false)
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
        src_location_index = src_location_index,
        src_card_list = src_card_list,
        dest_location_index = dest_location_index,
        dest_card_list = dest_card_list,
        node_cards = {},
    }

    local arrow_card_id = nil
    for i, card_id in ipairs(show_card_list or {}) do
        local x, y, z_order = self:get_position(i, block_type, src_location_index, dest_location_index)

        local need_rotation = false
        if self.need_point_to_src_location then
            if i == 1 and is_left_user(src_location_index, dest_location_index) then need_rotation = true end
            if i == 4 and is_right_user(src_location_index, dest_location_index) then need_rotation = true end
            if i == 3 and block_type ~= 'kong_an' and block_type ~= 'kong_ming' and block_type ~= 'kong_bu' and is_right_user(src_location_index, dest_location_index) then need_rotation = true end
        end

        local src_arrow_location_index = nil
        if self.need_arrow and not arrow_card_id and card_id == src_card_list[1] then
            arrow_card_id = card_id
            src_arrow_location_index = src_location_index
        end

        local card = self:create_card(card_id, false, need_rotation, src_arrow_location_index)
        card:setPosition(x, y)
        self.tan_card_node:addChild(card, z_order)

        block_data.node_cards[i] = card
    end

    table.insert(self.all_block_data, block_data)

    self.last_x = self.last_x + self.tan_config.x_block_offset
    self.last_y = self.last_y + self.tan_config.y_block_offset
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
                src_location_index = v.src_location_index,
                src_card_list = v.src_card_list,
                dest_location_index = v.dest_location_index,
                dest_card_list = v.dest_card_list,
            })
        end

        -- 
        self.game_scene:pushRestorePoint(rp_data, function(rp_data)
            self.tan_card_node:removeAllChildren()
            self.all_block_data = {}

            -- 
            self.last_x, self.last_y = self.tan_config.start_x, self.tan_config.start_y
            self.last_z_order = 0

            -- 
            for _, v in ipairs(rp_data) do
                local block_data = {
                    block_type = v.block_type,
                    card_list = v.card_list,
                    src_location_index = v.src_location_index,
                    src_card_list = v.src_card_list,
                    dest_location_index = v.dest_location_index,
                    dest_card_list = v.dest_card_list,
                    node_cards = {},
                }

                local arrow_card_id = nil
                for i, card_id in ipairs(v.card_list or {}) do
                    local x, y, z_order = self:get_position(i, v.block_type, v.src_location_index, v.dest_location_index)

                    local need_rotation = false
                    if self.need_point_to_src_location then
                        if i == 1 and is_left_user(v.src_location_index, v.dest_location_index) then need_rotation = true end
                        if i == 4 and is_right_user(v.src_location_index, v.dest_location_index) then need_rotation = true end
                        if i == 3 and v.block_type ~= 'kong_an' and v.block_type ~= 'kong_ming' and v.block_type ~= 'kong_bu' and is_right_user(v.src_location_index, v.dest_location_index) then need_rotation = true end
                    end

                    local src_arrow_location_index = nil
                    if self.need_arrow and not arrow_card_id and card_id == v.src_card_list[1] then
                        arrow_card_id = card_id
                        src_arrow_location_index = v.src_location_index
                    end

                    local card = self:create_card(card_id, false, need_rotation, src_arrow_location_index)
                    card:setPosition(x, y)
                    self.tan_card_node:addChild(card, z_order)

                    block_data.node_cards[i] = card
                end

                table.insert(self.all_block_data, block_data)

                -- 
                self.last_x = self.last_x + self.tan_config.x_block_offset
                self.last_y = self.last_y + self.tan_config.y_block_offset
            end
        end)
    end
end

return tan_card
