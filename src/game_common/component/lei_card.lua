-- ./app/platform/game/game_common/lei_card.lua
require 'app.platform.game.game_common.game_card_config'
require 'app.platform.game.game_common.game_component_base'

local lei_card_config = {
    [USER_LOCATION_SELF] = {
        lei_z_order = GAME_VIEW_Z_ORDER.LEI_CARD_SELF,
    },
    [USER_LOCATION_RIGHT] = {
        lei_z_order = GAME_VIEW_Z_ORDER.LEI_CARD_RIGHT,
    },
    [USER_LOCATION_FACING] = {
        lei_z_order = GAME_VIEW_Z_ORDER.LEI_CARD_FACING,
    },
    [USER_LOCATION_LEFT] = {
        lei_z_order = GAME_VIEW_Z_ORDER.LEI_CARD_LEFT,
    },
}

local lei_card = class('lei_card_component', component_base)
function lei_card:ctor(game_scene)
    component_base.ctor(self, game_scene)
end

function lei_card:init(args)
    component_base.init(self, args)

    self.is_back = args.is_back                     -- front/back background

    self.init_lei_card_flag = false
    self.lei_stack_num = { 17, 17, 17, 17 }      -- location index : 墩数

    --local lei_card_info = {
    --    card = card,
    --    shadow_card = card,
    --    is_valid = false,
    --    pre_card_info = card,
    --    next_card_info = card,
    --}
    self.all_lei_cards = {}
    self.location_lei_card = {}
    for i=USER_LOCATION_SELF, USER_LOCATION_LEFT do
        local node = cc.Node:create()
        node:setVisible(false)
        self.game_scene:addChild(node, lei_card_config[i].lei_z_order)

        self.location_lei_card[i] = { node = node, all_card_info = {} }
    end

    -- 
    self.pickup_location_index = USER_LOCATION_SELF
    self.pickup_stack_index = 1

    -- 剩余牌数
    self.last_card_count = 0
    self.label_card_count = cc.LabelAtlas:_create('0', 'mahjong/common/last_card_num.png', 32, 38, string.byte('0'))
    self.label_card_count:setAnchorPoint(0.5, 0.5)
    self.label_card_count:setScale(0.7)
    self.label_card_count:setPosition(641, 380)
    self.label_card_count:setVisible(false)
    self.game_scene:addChild(self.label_card_count, GAME_VIEW_Z_ORDER.LEI_CARD_SELF)

    -- 
    self:listenGameSignal('banker_server_index', function(banker_server_index) self:on_banker_server_index(banker_server_index) end)

    -- 一般都需要重载这个方法，以决定从那里开始摸牌
    self:listenGameSignal('roll_dice_end', function(banker_server_index, dice_num_1, dice_num_2) self:on_roll_dice_end(banker_server_index, dice_num_1, dice_num_2) end)

    -- 因为这个 signal 会触发四次[4个玩家]，所以在这里只选取了自己的来处理
    self:listenGameSignal('init_hand_card', function(location_index, card_list, card_num) self:on_init_hand_card(location_index, card_list, card_num) end)
    self:listenGameSignal('reconn_lei_card', function(wall_count, kong_count, dice_num_1, dice_num_2) self:on_reconn_lei_card(wall_count, kong_count, dice_num_1, dice_num_2) end)

    -- 鬼牌确认后，要在牌墙上翻出来
    self:listenGameSignal('ghost_card_confirm', function(fake_card_ids, really_card_ids, dice_num_1, dice_num_2) self:on_ghost_card_confirm(fake_card_ids, really_card_ids, dice_num_1, dice_num_2) end)

    self:listenGameSignal('draw_card', function(location_index, card_id, is_kong, callback_func) self:on_draw_card(location_index, card_id, is_kong, callback_func) end)
    self:listenGameSignal('on_flower', function(location_index, card_id) self:on_flower(location_index, card_id) end)

    self:listenGameSignal('show_card', function(card_list) self:on_show_card(card_list) end)
end

function lei_card:resetLeiCard()
    self.all_lei_cards = {}
    for _, v in ipairs(self.location_lei_card) do
        v.node:removeAllChildren()
        v.all_card_info = {}
    end

    self.init_lei_card_flag = false
end

function lei_card:on_game_waiting()
    self.location_lei_card[USER_LOCATION_SELF].node:setVisible(false)
    self.location_lei_card[USER_LOCATION_RIGHT].node:setVisible(false)
    self.location_lei_card[USER_LOCATION_FACING].node:setVisible(false)
    self.location_lei_card[USER_LOCATION_LEFT].node:setVisible(false)
    self.label_card_count:setVisible(false)
end

function lei_card:on_game_start()
    self.location_lei_card[USER_LOCATION_SELF].node:setVisible(true)
    self.location_lei_card[USER_LOCATION_RIGHT].node:setVisible(true)
    self.location_lei_card[USER_LOCATION_FACING].node:setVisible(true)
    self.location_lei_card[USER_LOCATION_LEFT].node:setVisible(true)
    self.label_card_count:setVisible(true)
end

function lei_card:on_prepare_next_round()
    self.location_lei_card[USER_LOCATION_SELF].node:setVisible(true)
    self.location_lei_card[USER_LOCATION_RIGHT].node:setVisible(true)
    self.location_lei_card[USER_LOCATION_FACING].node:setVisible(true)
    self.location_lei_card[USER_LOCATION_LEFT].node:setVisible(true)
    self.label_card_count:setVisible(false)

    for _, card_info in ipairs(self.all_lei_cards) do
        if card_info.shadow_card then
            card_info.shadow_card:removeFromParent(true)
            card_info.shadow_card = nil
        end
        card_info.is_valid = true
        card_info.card:setVisible(true)
    end
end

-- 这个方法，一般也需要重载，牌墙的墩数，可能与庄家的位置有关系
function lei_card:get_lei_col_num(banker_server_index)
    return { 17, 17, 17, 17 }, 17 * 4 * 2
end

function lei_card:on_banker_server_index(banker_server_index)
    self.lei_stack_num, self.max_card_count = self:get_lei_col_num(banker_server_index)

    self:init_lei_cards()
end

-- 一般都需要重载这个方法，以决定从那里开始摸牌
-- 默认的是洛阳杠次的拿牌规则：
--   两骰子点数相加：1,5,9 自己，依次类推
--   骰子点数小的决定墩数
function lei_card:on_roll_dice_end(banker_server_index, dice_num_1, dice_num_2)
    local location_index = self.game_scene.server_index_to_local_index[banker_server_index]
    self.pickup_location_index = (location_index + dice_num_1 + dice_num_2 - 2) % 4 + 1
    self.pickup_stack_index = math.min(dice_num_1, dice_num_2) + 1
end

function lei_card:create_card(location_index, is_back, card_id)
    if is_back then return create_card_back(location_index, CARD_AREA.LEI) end

    return create_card_front(location_index, CARD_AREA.LEI, card_id)
end

function lei_card:get_card_position(location_index, stack_index, is_top_card)
    local card_location_settings = {
        [USER_LOCATION_SELF] = function()
            local card_width = 31
            local start_x, start_y = 940, 185
            return start_x - card_width * stack_index, start_y + (is_top_card and 10 or 0), (is_top_card and 1 or 0)
        end,
        [USER_LOCATION_RIGHT] = function()
            local card_height = 28
            local start_x, start_y = 1068, 635
            return start_x + (is_top_card and 6 or 0), start_y - card_height * stack_index + (is_top_card and 2 or 0), (is_top_card and 1 or 0)
        end,
        [USER_LOCATION_FACING] = function()
            local card_width = 31
            local start_x, start_y = 350, 575
            return start_x + card_width * stack_index, start_y + (is_top_card and 10 or 0), (is_top_card and 1 or 0)
        end,
        [USER_LOCATION_LEFT] = function()
            local card_height = 28
            local start_x, start_y = 213, 135
            return start_x + (is_top_card and -6 or 0), start_y + card_height * stack_index + (is_top_card and 2 or 0), (is_top_card and 1 or 0)
        end,
    }

    return card_location_settings[location_index]()
end

function lei_card:init_lei_cards()
    if not self.init_lei_card_flag then
        self.init_lei_card_flag = true

        local function __create_card_info__(pre_card_info, location_index, stack_index, is_top_card)
            local x, y, z_order = self:get_card_position(location_index, stack_index, is_top_card)
            local card = self:create_card(location_index, self.is_back, 0)
            card:setPosition(x, y)
            self.location_lei_card[location_index].node:addChild(card, z_order)

            local card_info = {
                card = card,
                shadow_card = nil,
                is_valid = true,
                location_index = location_index,
                pre_card_info = pre_card_info,
                next_card_info = nil,
            }

            -- next 由后来者赋值
            if pre_card_info then pre_card_info.next_card_info = card_info end

            return card_info
        end

        local first_card_info, pre_card_info = nil, nil
        for location_index=USER_LOCATION_LEFT, USER_LOCATION_SELF, -1 do
            local stack_num = self.lei_stack_num[location_index]
            for index=1, stack_num do
                --
                local card_info = __create_card_info__(pre_card_info, location_index, index, true)
                table.insert(self.all_lei_cards, card_info)
                table.insert(self.location_lei_card[location_index].all_card_info, card_info)
                pre_card_info = card_info

                if not first_card_info then first_card_info = card_info end                    -- 因为第一个创建的时候，没有 pre_card_info，所以要在记录下来，等都创建完后，再补回来

                -- 
                local card_info = __create_card_info__(pre_card_info, location_index, index, false)
                table.insert(self.all_lei_cards, card_info)
                table.insert(self.location_lei_card[location_index].all_card_info, card_info)
                pre_card_info = card_info
            end
        end

        -- 
        first_card_info.pre_card_info = pre_card_info
        pre_card_info.next_card_info = first_card_info
    end
end

function lei_card:get_card_info(location_index, stack_index, is_top)
    local card_index = stack_index * 2 - (is_top and 1 or 0)
    return self.location_lei_card[location_index].all_card_info[card_index]
end

function lei_card:pickup_card_info(card_info, is_reconn)
    if not card_info.is_valid then
        return self:pickup_card_info(card_info.next_card_info, is_reconn)
    end

    if is_reconn then
        if card_info.shadow_card then card_info.shadow_card:setVisible(false) end
        card_info.card:setVisible(false)
        card_info.is_valid = false

        return card_info.next_card_info
    else
        local mv_action_1 = cc.MoveBy:create(0.1, cc.p(0, 15))
        local hide_action = cc.CallFunc:create(function()
            if card_info.shadow_card then card_info.shadow_card:setVisible(false) end
            card_info.card:setVisible(false)
        end)
        local mv_action_2 = cc.MoveBy:create(0.1, cc.p(0, -15))
        card_info.card:runAction(cc.Sequence:create(mv_action_1, hide_action, mv_action_2))
        card_info.is_valid = false

        -- 剩余牌数量减 1
        self.last_card_count = self.last_card_count - 1
        self.label_card_count:setString(tostring(self.last_card_count))

        -- 
        return card_info.next_card_info
    end
end

function lei_card:pickup_next_card(pickup_num, is_reconn)
    pickup_num = pickup_num or 1

    for i=1, pickup_num do
        self.next_card_info = self:pickup_card_info(self.next_card_info, is_reconn)
    end
end

function lei_card:pickup_last_card(is_reconn)
    -- 取走最后一墩上面的牌
    if self.last_stack_card_info.is_valid then
        self:pickup_card_info(self.last_stack_card_info, is_reconn)
    else
        -- 取走最后一墩下面的牌
        if self.last_stack_card_info.next_card_info.is_valid then
            self:pickup_card_info(self.last_stack_card_info.next_card_info, is_reconn)

            -- 往前移一墩
            self.last_stack_card_info = self.last_stack_card_info.pre_card_info.pre_card_info
        else
            -- 如果这最后的一墩牌都是无效的话，嗯，往前一墩试试吧
            self.last_stack_card_info = self.last_stack_card_info.pre_card_info.pre_card_info
            self:pickup_last_card(is_reconn)     -- 其实，这里是不是不应该递归呢，如果到这里，是不是自己写错逻辑了呢，暂时先这么写吧
        end
    end
end

-- 因为这个 signal 会触发四次[4个玩家]，所以在这里只选取了自己的来处理
function lei_card:on_init_hand_card(location_index, card_list, card_num)
    if location_index ~= USER_LOCATION_SELF then return end

    --
    self.next_card_info = self:get_card_info(self.pickup_location_index, self.pickup_stack_index, true)
    self.last_stack_card_info = self.next_card_info.pre_card_info.pre_card_info     -- 指向最后一墩上面的那张牌

    self.last_card_count = self.max_card_count

    -- 
    local index = 1
    -- local total_counter = 13        -- 4 * 4 * 3 + 1 * 4
    local total_counter = {}
    local user_count = self.game_scene:getUserCount()
    for i=1, user_count do
        total_counter[(i-1)*3+1] = 4
        total_counter[(i-1)*3+2] = 4
        total_counter[(i-1)*3+3] = 4
    end
    total_counter[user_count*3+1] = user_count
    self.handler = self.game_scene:schedule_circle(0.05, function()
        self:pickup_next_card(total_counter[index])

        index = index + 1
        if index > #total_counter then
            self.game_scene:unschedule(self.handler)
            self.handler = nil
        end
    end)
end

function lei_card:on_reconn_lei_card(wall_count, kong_count, dice_num_1, dice_num_2)
    -- 重新还原牌墙的牌
    self:on_prepare_next_round()

    --
    self.next_card_info = self:get_card_info(self.pickup_location_index, self.pickup_stack_index, true)
    self.last_stack_card_info = self.next_card_info.pre_card_info.pre_card_info     -- 指向最后一墩上面的那张牌

    -- 先给鬼牌留个位置
    if self.game_scene.scene_config.has_ghost_card then
        self:update_ghost_card_position(dice_num_1, dice_num_2)
        self.ghost_card_info.is_valid = false
    end

    -- 
    local pickup_count = self.max_card_count - wall_count - kong_count - 1
    self:pickup_next_card(pickup_count, true)

    --
    for i=1, kong_count do
        self:pickup_last_card(true)
    end

    -- 重连后更新剩余牌数
    self.last_card_count = wall_count
    self.label_card_count:setString(tostring(self.last_card_count))
    self.label_card_count:setVisible(true)
    self.reconn_last_card_count = true
end

-- 翻出来的鬼牌所在的牌墙位置
function lei_card:update_ghost_card_position(dice_num_1, dice_num_2)
    self.ghost_card_info = self.last_stack_card_info

    local count = dice_num_1 + dice_num_2 - 2
    for i=1, count do
        self.ghost_card_info = self.ghost_card_info.pre_card_info.pre_card_info
    end
end

function lei_card:on_ghost_card_confirm(fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
    self:update_ghost_card_position(dice_num_1, dice_num_2)

    local card = self:create_card(self.ghost_card_info.location_index, false, fake_card_ids[1])
    card:setPosition(self.ghost_card_info.card:getPosition())
    self.ghost_card_info.card:getParent():addChild(card, self.ghost_card_info.card:getLocalZOrder())
    self.ghost_card_info.is_valid = false
    self.ghost_card_info.card:setVisible(false)

    self.ghost_card_info.shadow_card = card

    -- 鬼牌不能被摸走，剩余牌数量减 1
    if not self.reconn_last_card_count then
        self.reconn_last_card_count = nil

        self.last_card_count = self.last_card_count - 1
        self.label_card_count:setString(tostring(self.last_card_count))
    end
end

function lei_card:on_draw_card(location_index, card_id, is_kong, callback_func)
    -- 牌墙的还原点
    self:pushRestorePoint(is_kong)

    -- 
    if is_kong then
        self:pickup_last_card()
    else
        self:pickup_next_card()
    end
end

function lei_card:on_flower(location_index, card_id)
    -- 牌墙的还原点
    self:pushRestorePoint(false)

    self:pickup_next_card()
end

function lei_card:on_show_card(card_list)
    local next_card_info = self.next_card_info
    for _, card_id in ipairs(card_list) do
        local card = self:create_card(next_card_info.location_index, false, card_id)
        card:setPosition(next_card_info.card:getPosition())
        next_card_info.card:getParent():addChild(card, next_card_info.card:getLocalZOrder())
        next_card_info.card:setVisible(false)

        next_card_info.shadow_card = card

        next_card_info = next_card_info.next_card_info
    end
end

-- 牌墙的还原点
-- 记录下当前要拿走的牌，在还原的时候，就重新显示
function lei_card:pushRestorePoint(is_kong)
    if self.game_scene.pushRestorePoint then
        local rp_data = {
            is_kong = is_kong,      -- 是不是杠牌，这个决定是从牌墙的那一头拿走的牌
            stack_top_is_valid = false,
            stack_card_info = nil,
            card_info = nil,
        }

        if is_kong then
            rp_data.stack_card_info = self.last_stack_card_info

            -- 这个是保存到底是上面的那张牌还是下面的那张牌
            if self.last_stack_card_info.is_valid then
                rp_data.stack_top_is_valid = true
                rp_data.card_info = self.last_stack_card_info
            else
                rp_data.card_info = self.last_stack_card_info.next_card_info
            end
        else
            rp_data.card_info = self.next_card_info
        end

        -- 
        self.game_scene:pushRestorePoint(rp_data, function(rp_data)
            if rp_data.card_info.shadow_card then
                rp_data.card_info.shadow_card:setVisible(true)
            else
                rp_data.card_info.card:setVisible(true)
            end
            rp_data.card_info.is_valid = true

            -- 
            if rp_data.is_kong then
                self.last_stack_card_info = rp_data.stack_card_info
                self.last_stack_card_info.is_valid = rp_data.stack_top_is_valid
            else
                self.next_card_info = rp_data.card_info
            end
        end)
    end
end

return lei_card
