-- ./app/platform/game/game_common/component/hand_card.lua
require 'app.platform.game.game_common.game_card_config'
require 'app.platform.game.game_common.game_component_base'

local hand_card_z_order = {
    [USER_LOCATION_SELF] = {
        z_order = GAME_VIEW_Z_ORDER.HAND_CARD_SELF,
    },
    [USER_LOCATION_RIGHT] = {
        z_order = GAME_VIEW_Z_ORDER.HAND_CARD_RIGHT,
    },
    [USER_LOCATION_FACING] = {
        z_order = GAME_VIEW_Z_ORDER.HAND_CARD_FACING,
    },
    [USER_LOCATION_LEFT] = {
        z_order = GAME_VIEW_Z_ORDER.HAND_CARD_LEFT,
    },
}

local hand_card = class('hand_card_component', component_base)
function hand_card:ctor(game_scene)
    component_base.ctor(self, game_scene)
end

function hand_card:init(args)
    component_base.init(self, args)

    self.location_index = args.location_index       -- 哪个区域
    self.origin_is_back = args.is_back
    self.is_back = args.is_back                     -- front/back background
    self.area = args.area

    --
    self.hand_card_config = hand_card_z_order[self.location_index]

    -- 
    self.hand_card_node = self:create_hand_card_node()
    self.game_scene:addChild(self.hand_card_node, self.hand_card_config.z_order)

    -----------------------------------------------------------------------------------------------------------------------------------------------
    -- 游戏开始时候的发牌
    self:listenGameSignal('init_hand_card', function(location_index, card_list, card_num, callback_func) self:init_hand_card(location_index, card_list, card_num, callback_func) end)

    -- 断线重连后更新手牌
    self:listenGameSignal('reconn_hand_card', function(location_index, card_list, card_num) self:reconn_hand_card(location_index, card_list, card_num) end)

    -- 摸牌
    self:listenGameSignal('draw_card', function(location_index, card_id, is_kong, callback_func) self:draw_card(location_index, card_id, is_kong, callback_func) end)
    self:listenGameSignal('reconn_draw_card', function(location_index, card_id, is_kong) self:reconn_draw_card(location_index, card_id, is_kong) end)
    self:listenGameSignal('out_card', function(location_index, card_id) self:out_card(location_index, card_id) end)

    -- 亮牌
    self:listenGameSignal('liang_card', function(location_index, card_list, card_num, win_card) self:liang_card(location_index, card_list, card_num, win_card) end)

    self:listenGameSignal('user_ready', function(location_index, is_ready) self:on_user_ready(location_index, is_ready) end)

    -- block operation
    self:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        self:on_block_result(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
    end)

    -- 鬼牌确定后，要给手牌加上鬼牌标识，还要对手牌排个序
    self:listenGameSignal('ghost_card_confirm', function(fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
        self:update_ghost_flag()
        self:update_position()
    end)

    local zm_offset_y = { 120, 110, 120, 110 }
    self:listenGameSignal('win_effect', function(win_effect_type, location_index)
        if location_index == self.location_index and win_effect_type == 'zm' then
            local card = self.node_cards[#self.node_cards].card
            local x, y = card:getPosition()

            local anim_node = createAnimNode('mahjong/anim/win_effect/zm_light.csb', false)
            anim_node:setScale(2)
            anim_node:setPosition(x, y + zm_offset_y[location_index])
            self.game_scene:addChild(anim_node, self.hand_card_config.z_order)

            performWithDelay(anim_node, function() anim_node:removeFromParent(true) end, 1.9)
        end
    end)
end

function hand_card:on_prepare_next_round()
    self.cur_draw_card = nil

    self.hand_card_node:removeAllChildren()
    self.node_cards = {}

    self.is_back = self.origin_is_back
end

function hand_card:create_hand_card_node()
    return cc.Node:create()
end

function hand_card:create_card(card_id, area)
    local function __create_card__()
        if self.is_back then return create_card_back(self.location_index, area or CARD_AREA.HAND) end

        return create_card_front(self.location_index, area or CARD_AREA.HAND, card_id)
    end

    local card = __create_card__()

    -- 
    if self.game_scene:is_ghost_card(card_id) then
        card:addChild(self.game_scene:createGhostSubscript(self.location_index, area or CARD_AREA.HAND))
    end

    return card
end

function hand_card:get_card_position(card_num, card_index, is_liang)
    local card_location_attr = {
        [USER_LOCATION_SELF] = function()
            local card_width = ((is_liang or self.area == CARD_AREA.TAN) and 65 or 77)
            local start_x, start_y = 1060, 55
            if card_index > 0 then
                return start_x - card_width * (card_num - card_index), start_y, card_index
            else
                return start_x + card_width + 20, start_y, 0
            end
        end,
        [USER_LOCATION_RIGHT] = function()
            local card_height = ((is_liang or not self.is_back) and 38 or 30)
            local start_x, start_y = 1160, 610
            if card_index > 0 then
                return start_x, start_y - card_height * (card_num - card_index), -card_index
            else
                return start_x, start_y + card_height + 10, -100
            end
        end,
        [USER_LOCATION_FACING] = function()
            local card_width = ((is_liang or not self.is_back) and 38 or 30)
            local start_x, start_y = 450, 690
            if card_index > 0 then
                return start_x + card_width * (card_num - card_index), start_y, card_index
            else
                return start_x - card_width - 10, start_y, 0
            end
        end,
        [USER_LOCATION_LEFT] = function()
            local card_height = ((is_liang or not self.is_back) and 38 or 30)
            local start_x, start_y = 120, 180
            if card_index > 0 then
                return start_x, start_y + card_height * (card_num - card_index), card_index
            else
                return start_x, start_y - card_height - 10, 100
            end
        end,
    }

    return card_location_attr[self.location_index]()
end

-- init or reset hand card ---------------------------------------------------------------------------------------------------------------------
function hand_card:init_hand_card(location_index, card_list, card_num, callback_func)
    if location_index ~= self.location_index then return end

    -- 
    self.hand_card_node:removeAllChildren()
    self.node_cards = {}

    for i=1, card_num do
        local x, y, z_order = self:get_card_position(card_num, i)

        local card_id = card_list[i]
        local card = self:create_card(card_id, self.area)
        card:setPosition(x, y)
        card:setVisible(false)
        self.hand_card_node:addChild(card, z_order)

        self.node_cards[i] = {
            card = card,
            card_id = card_id,
        }
    end

    local delay = 0
    local count = math.floor(card_num / 4) + 1
    for i=0, count - 1 do
        self.game_scene:schedule_once_time(delay, function()
            local index = i * 4
            if self.node_cards[index+1] then self.node_cards[index+1].card:setVisible(true) end
            if self.node_cards[index+2] then self.node_cards[index+2].card:setVisible(true) end
            if self.node_cards[index+3] then self.node_cards[index+3].card:setVisible(true) end
            if self.node_cards[index+4] then self.node_cards[index+4].card:setVisible(true) end

            -- 初始化手牌的动画结束，这个是用来触发摸牌操作
            if i == count - 1 then
                self:update_position()

                if callback_func then callback_func() end
            end
        end)

        delay = delay + 0.8
    end
end

function hand_card:reconn_hand_card(location_index, card_list, card_num)
    if location_index ~= self.location_index then return end

    -- 
    self.hand_card_node:removeAllChildren()
    self.node_cards = {}

    for i=1, card_num do
        local x, y, z_order = self:get_card_position(card_num, i)

        local card_id = card_list[i]
        local card = self:create_card(card_id, self.area)
        card:setPosition(x, y)
        self.hand_card_node:addChild(card, z_order)

        self.node_cards[i] = {
            card = card,
            card_id = card_id,
        }
    end

    self:update_position()
end

function hand_card:play_draw_card_anim(card_id, callback)
    if callback then callback() end
end

function hand_card:draw_card(location_index, card_id, is_kong, callback_func)
    if location_index ~= self.location_index then return end

    -- 手牌摸牌还原点
    self:pushRestorePoint()

    -- 
    self.draw_card_anim = true      -- 这个是代表摸牌动画中的标识
    self:play_draw_card_anim(card_id, function()
        self.draw_card_anim = false

        local x, y, z_order = self:get_card_position(#self.node_cards, -1)

        -- 记录下刚摸的牌，在手牌排序的时候，忽略这张牌
        self.cur_draw_card = self:create_card(card_id, self.area)
        self.cur_draw_card:setPosition(x, y)
        self.hand_card_node:addChild(self.cur_draw_card, z_order)

        table.insert(self.node_cards, {
            card = self.cur_draw_card,
            card_id = card_id,
        })

        -- 
        if callback_func then callback_func() end
    end)
end

function hand_card:reconn_draw_card(location_index, card_id)
    if location_index ~= self.location_index then return end

    local x, y, z_order = self:get_card_position(#self.node_cards, -1)

    -- 记录下刚摸的牌，在手牌排序的时候，忽略这张牌
    self.cur_draw_card = self:create_card(card_id, self.area)
    self.cur_draw_card:setPosition(x, y)
    self.hand_card_node:addChild(self.cur_draw_card, z_order)

    table.insert(self.node_cards, {
        card = self.cur_draw_card,
        card_id = card_id,
    })
end

function hand_card:out_card(location_index, card_id)
    if location_index ~= self.location_index then return end

    -- 手牌出牌还原点
    self:pushRestorePoint()

    -- 
    if self.is_back then
        self:remove_card_by_num(1)
    else
        self:remove_card_by_ids({card_id})
    end

    -- 在出牌后，要重置
    self.cur_draw_card = nil

    self:update_position()
end

function hand_card:liang_card(location_index, card_list, card_num, win_card)
    if location_index ~= self.location_index then return end

    -- 
    self.hand_card_node:removeAllChildren()
    self.node_cards = {}

    -- 
    self.is_back = false
    for i=1, card_num do
        local x, y, z_order = self:get_card_position(card_num, i, true)

        local card_id = card_list[i]
        local card = self:create_card(card_id, CARD_AREA.TAN)
        card:setPosition(x, y)
        self.hand_card_node:addChild(card, z_order)

        self.node_cards[i] = {
            card = card,
            card_id = card_id,
        }
    end

    if win_card then
        local x, y, z_order = self:get_card_position(card_num, -1, true)

        -- 记录下刚摸的牌，在手牌排序的时候，忽略这张牌
        local card = self:create_card(win_card, CARD_AREA.TAN)
        card:setPosition(x, y)
        self.hand_card_node:addChild(card, z_order)

        table.insert(self.node_cards, {
            card = card,
            card_id = win_card,
        })
    end
end

function hand_card:on_user_ready(location_index, is_ready)
    if location_index == self.location_index and is_ready then
        self.hand_card_node:removeAllChildren()
        self.node_cards = {}
    end
end

function hand_card:on_block_result(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
    if dest_location_index ~= self.location_index then return end

    -- 手牌拦牌还原点
    self:pushRestorePoint()

    self.cur_draw_card = nil

    -- 
    self:remove_card_by_ids(dest_card_list)
end

-- remove card by ids/num
function hand_card:remove_card_by_ids(rm_card_ids)
    local function __rm_card_id__(card_id)
        if self.is_back or card_id <= 0 then
            self.node_cards[#self.node_cards].card:removeFromParent(true)
            self.node_cards[#self.node_cards] = nil

            return
        end

        for index, v in ipairs(self.node_cards) do
            if v.card_id == card_id then
                v.card:removeFromParent(true)
                table.remove(self.node_cards, index)

                return
            end
        end
    end

    for _, card_id in ipairs(rm_card_ids or {}) do
        __rm_card_id__(card_id)
    end

    -- 
    self:update_position()
end

function hand_card:remove_card_by_num(rm_card_num)
    for i=1, rm_card_num do
        self.node_cards[#self.node_cards].card:removeFromParent(true)
        self.node_cards[#self.node_cards] = nil
    end

    -- 
    self:update_position()
end

function hand_card:update_ghost_flag()
    for _, v in ipairs(self.node_cards) do
        if self.game_scene:is_ghost_card(v.card_id) then
            v.card:addChild(self.game_scene:createGhostSubscript(self.location_index, CARD_AREA.HAND))
        end
    end
end

function hand_card:update_position()
    if self.location_index == USER_LOCATION_SELF or not self.is_back then
        table.sort(self.node_cards, function(card_a, card_b)
            local card_id_1 = card_a.card_id
            local card_id_2 = card_b.card_id
            return self.game_scene:sort_card_by_id(card_id_1, card_id_2)
        end)
    end

    local card_num = #self.node_cards

    -- 忽略刚摸到的牌
    if self.cur_draw_card then card_num = card_num - 1 end

    local index = 1
    for _, v in ipairs(self.node_cards) do
        if self.cur_draw_card ~= v.card then
            local x, y, z_order = self:get_card_position(card_num, index)
            v.card:setPosition(x, y)
            v.card:setLocalZOrder(z_order)
            v.card:setVisible(true)

            index = index + 1
        end
    end
    self.hand_card_node:sortAllChildren()
end

-- 手牌的还原点
-- 记录下来当前的手牌，在还原的时候，就重新创建
function hand_card:pushRestorePoint()
    if self.game_scene.pushRestorePoint then
        local rp_data = {}
        for _, v in ipairs(self.node_cards) do
            table.insert(rp_data, v.card_id)
        end

        -- 
        self.game_scene:pushRestorePoint(rp_data, function(rp_data)
            self:reconn_hand_card(self.location_index, rp_data, #rp_data)
        end)
    end
end

return hand_card

