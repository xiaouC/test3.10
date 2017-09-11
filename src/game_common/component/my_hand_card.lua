-- ./app/platform/game/game_common/component/my_hand_card.lua
require 'app.platform.game.game_common.game_card_config'

local hand_card = require 'app.platform.game.game_common.component.hand_card'

local my_hand_card = class('my_hand_card_component', hand_card)
function my_hand_card:ctor(game_scene)
    hand_card.ctor(self, game_scene)
end

function my_hand_card:init(args)
    hand_card.init(self, args)

    -- 
    self.cur_sel_card = {
        card = nil,
        x = nil,
        y = nil,
        double_sel = false,
    }

    self.ting_groups = {}

    registerAnimationRange('my_hand_card_zhua_pai', 'anim_hand_card_%d.png', 1, 2, 0.15/2)

    -- 听牌列表
    self:listenGameSignal('ting_card_list', function(max_win_count, ting_groups) self:update_ting_list(max_win_count, ting_groups) end)

    self.my_turn = false
    self:listenGameSignal('user_turn', function(server_index)
        self.my_turn = (server_index == self.game_scene.my_server_index)
    end)

    -- 摸牌
    registerAnimationIndices('mopai', 'draw_card_hand_%d.png', { 1, 1, 2, 2, 2, 3, 4 }, 1.0/7)
end

function my_hand_card:on_prepare_next_round()
    hand_card.on_prepare_next_round(self)

    self.cur_ting_list = nil
end

function my_hand_card:clear_ting_arrow()
    -- 清掉所有的听牌箭头
    for _, v in ipairs(self.node_cards or {}) do
        if v.card.arrow_sprite then
            v.card.arrow_sprite:removeFromParent(true)
            v.card.arrow_sprite = nil
        end
    end

    self.ting_groups = {}
    self.max_win_count = 0
end

function my_hand_card:out_card(location_index, card_id)
    -- 在这里不能调用 hand_card:out_card，因为在其他位置的手牌，在移除一张打出的牌的时候，是通过数量来移除的
    -- 而对于自己的手牌，则是使用 id 来移除，重复调用会导致移除了两张牌
    -- hand_card.out_card(self, location_index, card_id)

    -- 
    if location_index ~= self.location_index then return end

    -- 在出牌后，要重置
    self.cur_draw_card = nil

    self:update_position()

    -- 
    self.cur_ting_list = self.ting_groups[card_id]
    self.game_scene:fire('reset_ting_card', self.cur_ting_list or {})

    self:clear_ting_arrow()
    self:remove_card_by_ids({card_id})
end

function my_hand_card:create_hand_card_node()
    return createBackgroundLayer(
        cc.c4b(0, 0, 0, 0),
        false,
        function(touch, event) return self:on_touch_began(touch, event) end,
        function(touch, event) self:on_touch_moved(touch, event) end,
        function(touch, event) self:on_touch_ended(touch, event) end
    )
end

function my_hand_card:create_card(card_id, area)
    local card = hand_card.create_card(self, card_id, area)

    local ting_info = self.ting_groups[card_id]
    if ting_info then
        local arrow_file = (ting_info.win_card_count == self.max_win_count and 'ting_tips_best.png' or 'ting_tips.png')
        local offset_y = (ting_info.win_card_count == self.max_win_count and 100 or 80)
        card.arrow_sprite = cc.Sprite:createWithSpriteFrameName(arrow_file)
        card.arrow_sprite:setPosition(0, offset_y)
        card:addChild(card.arrow_sprite)
    end

    return card
end

function my_hand_card:update_ting_list(max_win_count, ting_groups)
    self:clear_ting_arrow()
    self.ting_groups = ting_groups
    self.max_win_count = max_win_count

    -- 
    for _, v in ipairs(self.node_cards or {}) do
        local ting_info = ting_groups[v.card_id]
        if ting_info then
            if v.card.arrow_sprite then v.card.arrow_sprite:removeFromParent(true) end

            local arrow_file = (ting_info.win_card_count == max_win_count and 'ting_tips_best.png' or 'ting_tips.png')
            local offset_y = (ting_info.win_card_count == max_win_count and 100 or 80)
            v.card.arrow_sprite = cc.Sprite:createWithSpriteFrameName(arrow_file)
            v.card.arrow_sprite:setPosition(0, offset_y)
            v.card:addChild(v.card.arrow_sprite)
        end
    end
end

function my_hand_card:on_touch_began(touch, event)
    if not self.my_turn then return false end

    if not self.my_turn and not self.game_scene.on_ting_flag then
        return false
    end

    -- 
    local touch_location = touch:getLocation()
    local down_sel = self:hitTest(touch_location.x, touch_location.y)
    if down_sel then
        if self.cur_sel_card.card == down_sel.card then
            self.cur_sel_card.double_sel = true

            return true
        end

        if self.cur_sel_card.card then
            self.cur_sel_card.card:setPosition(self.cur_sel_card.x, self.cur_sel_card.y)
            self.cur_sel_card.card:setScale(self.cur_sel_card.origin_scale)
            self.cur_sel_card.card:setLocalZOrder(self.cur_sel_card.z_order)
        end

        local x, y = down_sel.card:getPosition()
        self.cur_sel_card = {
            card = down_sel.card,
            card_id = down_sel.card_id,
            x = x,
            y = y,
            z_order = down_sel.card:getLocalZOrder(),
            double_sel = false,
            mv_flag = false,
            origin_scale = down_sel.card:getScale(),
        }

        self.game_scene.game_music:handselect()

        down_sel.card:setPosition(x, y + 50)
        down_sel.card:setLocalZOrder(1000)
        down_sel.card:setScale(1.1 * self.cur_sel_card.origin_scale)
        self.hand_card_node:sortAllChildren()
        self.game_scene:fire('hand_selected', down_sel.card_id)

        -- 
        local ting_list = self.ting_groups[down_sel.card_id]
        if ting_list then
            self.game_scene:fire('reset_ting_card', ting_list)
        end

        -- 
        return true
    end

    return false
end

function my_hand_card:on_touch_moved(touch, event)
    local location = touch:getLocation()

    local card_height = 120
    if self.cur_sel_card.card and location.y > card_height + 3 then
        self.cur_sel_card.mv_flag = true
    end

    if self.cur_sel_card.mv_flag then
        self.cur_sel_card.card:setPosition(location.x, location.y)

        if self.cur_sel_card.card.arrow_sprite then self.cur_sel_card.card.arrow_sprite:setVisible(false) end

        self.game_scene:fire('hand_card_mv_distance', location.x, location.y)
    end
end

function my_hand_card:on_touch_ended(touch, event)
    self.game_scene:fire('hand_card_mv_distance', 0, 0)

    --
    local location = touch:getLocation()
    local distance = 132

    -- 把牌打出去
    if self.cur_sel_card.card and location.y >= distance then
        if self:request_out_card(self.cur_sel_card.card_id) then
            self.cur_sel_card.card:setVisible(false)
            self.cur_sel_card = {}
        else
            self.cur_sel_card.card:setPosition(self.cur_sel_card.x, self.cur_sel_card.y)
            self.cur_sel_card.card:setScale(self.cur_sel_card.origin_scale)
            self.cur_sel_card.card:setLocalZOrder(self.cur_sel_card.z_order)
            self.hand_card_node:sortAllChildren()
            self.game_scene:fire('hand_selected', -1)

            if self.cur_sel_card.card.arrow_sprite then self.cur_sel_card.card.arrow_sprite:setVisible(true) end
            self.cur_sel_card = {}
        end

        return
    end

    if self.cur_sel_card.mv_flag then
        self.cur_sel_card.card:setPosition(self.cur_sel_card.x, self.cur_sel_card.y)
        self.cur_sel_card.card:setScale(self.cur_sel_card.origin_scale)
        self.cur_sel_card.card:setLocalZOrder(self.cur_sel_card.z_order)
        self.hand_card_node:sortAllChildren()
        self.game_scene:fire('hand_selected', -1)

        if self.cur_sel_card.card.arrow_sprite then self.cur_sel_card.card.arrow_sprite:setVisible(true) end
        self.cur_sel_card = {}
    end

    -- 
    local cur_sel = self:hitTest(location.x, location.y)
    if cur_sel and cur_sel.card == self.cur_sel_card.card and self.cur_sel_card.double_sel then
        if self:request_out_card(self.cur_sel_card.card_id) then
            self.cur_sel_card.card:setVisible(false)
            self.cur_sel_card = {}
        else
            self.cur_sel_card.card:setPosition(self.cur_sel_card.x, self.cur_sel_card.y)
            self.cur_sel_card.card:setScale(self.cur_sel_card.origin_scale)
            self.cur_sel_card.card:setLocalZOrder(self.cur_sel_card.z_order)
            self.hand_card_node:sortAllChildren()
            self.game_scene:fire('hand_selected', -1)

            if self.cur_sel_card.card.arrow_sprite then self.cur_sel_card.card.arrow_sprite:setVisible(true) end
            self.cur_sel_card = {}
        end
    end
end

function my_hand_card:hitTest(x, y)
    local card_width, card_height = 77, 120
    local addition_height = 60

    local function __hit_card_test__(card)
        local card_x, card_y = card:getPosition()
        local rect = cc.rect(card_x - card_width * 0.5, card_y - card_height * 0.5 - addition_height, card_width, card_height + addition_height)
        return cc.rectContainsPoint(rect, cc.p(x, y))
    end

    for _, v in ipairs(self.node_cards or {}) do
        if __hit_card_test__(v.card) then
            return v
        end
    end
end

function my_hand_card:request_out_card(card_id)
    if self.game_scene.user_turn_server_index ~= self.game_scene.my_server_index then
        return false    -- 还没到你出牌
    end

    if self.draw_card_anim then
        return false    -- 摸牌动画中，不能出牌
    end

    self.my_turn = false

    self.cur_sel_card.card:setPosition(self.cur_sel_card.x, self.cur_sel_card.y)
    self.cur_sel_card.card:setScale(self.cur_sel_card.origin_scale)
    self.cur_sel_card.card:setLocalZOrder(self.cur_sel_card.z_order)
    self.hand_card_node:sortAllChildren()
    self.game_scene:fire('hand_selected', -1)

    local request_out_card = self.cur_sel_card.card
    self.game_scene:requestAction('discard_card', self.game_scene.my_server_index, card_id, function()
        self.my_turn = true

        request_out_card:setVisible(true)
    end)

    return true
end

function my_hand_card:play_draw_card_anim(card_id, callback)
    if not self.cur_ting_list then return callback() end

    -- 关闭了摸牌时候的搓牌动画
    if UserData:getRubCardValue() ~= 'on' then return callback() end

    -- 
    local mopai_bg = cc.Sprite:create('mahjong/component/roll_dice/draw_card_background.png')
    mopai_bg:setPosition(640, 430)
    self.hand_card_node:addChild(mopai_bg, 911)

    local node = cc.Node:create()
    mopai_bg:addChild(node)

    local mopai_hand_bg = cc.Sprite:createWithSpriteFrameName('draw_card_hand_5.png')
    mopai_hand_bg:setPosition(262, 162)
    node:addChild(mopai_hand_bg, 92)

    local card = create_card_sprite(card_id)
    card:setPosition(237, 212)
    card:setScale(0.7)
    card:setRotation(-40)
    node:addChild(card, 93)

    local mopai_hand = cc.Sprite:createWithSpriteFrameName('draw_card_hand_1.png')
    mopai_hand:setPosition(262, 162)
    node:addChild(mopai_hand, 94)

    local action_1 = cc.Animate:create(cc.AnimationCache:getInstance():getAnimation('mopai'))
    local action_2 = cc.DelayTime:create(0.8)
    local action_3 = cc.CallFunc:create(function()
        mopai_bg:removeFromParent(true)
        if callback then callback() end
    end)
    mopai_hand:runAction(cc.Sequence:create(action_1, action_2, action_3))
end

-- remove card by ids/num
function my_hand_card:remove_card_by_ids(rm_card_ids)
    local function __rm_card_id__(card_id)
        if self.is_back or card_id <= 0 then
            if self.node_cards[#self.node_cards].anim_card then
                self.node_cards[#self.node_cards].anim_card:removeFromParent(true)
            end
            self.node_cards[#self.node_cards].card:removeFromParent(true)
            self.node_cards[#self.node_cards] = nil

            return
        end

        for index, v in ipairs(self.node_cards) do
            if v.card_id == card_id then
                if v.anim_card then
                    v.anim_card:removeFromParent(true)
                end
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

function my_hand_card:remove_card_by_num(rm_card_num)
    for i=1, rm_card_num do
        if #self.node_cards > 0 then
            if self.node_cards[#self.node_cards].anim_card then
                self.node_cards[#self.node_cards].anim_card:removeFromParent(true)
            end
            self.node_cards[#self.node_cards].card:removeFromParent(true)
            self.node_cards[#self.node_cards] = nil
        end
    end

    -- 
    self:update_position()
end

function my_hand_card:init_hand_card(location_index, card_list, card_num, callback_func)
    if location_index ~= self.location_index then return end

    -- 
    self:clear_all_hand_card()

    for i=1, card_num do
        local x, y, z_order = self:get_card_position(card_num, i)

        local card_id = card_list[i]
        local card = self:create_card(card_id)
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
        local handler = self.game_scene:schedule_once_time(delay, function()
            self.game_scene.game_music:faPai()

            local index = i * 4

            local function __anim_zhua_pai__(v)
                if not v then return end

                v.anim_card = cc.Sprite:createWithSpriteFrameName('anim_hand_card_1.png')
                v.anim_card:setPosition(v.card:getPosition())
                v.anim_card:setScale(v.card:getScale())
                self.hand_card_node:addChild(v.anim_card, v.card:getLocalZOrder())

                local action_1 = cc.Animate:create(cc.AnimationCache:getInstance():getAnimation('my_hand_card_zhua_pai'))
                local action_2 = cc.CallFunc:create(function()
                    v.card:setVisible(true)
                    v.anim_card:setVisible(false)

                    -- 初始化手牌的动画结束，这个是用来触发摸牌操作
                    if i == count - 1 then
                        local handler = self.game_scene:schedule_once_time(0.4, function()
                            self.game_scene.game_music:gaiPai()

                            for _, vv in ipairs(self.node_cards) do
                                vv.card:setVisible(false)

                                if vv.anim_card then
                                    vv.anim_card:setVisible(true)
                                    vv.anim_card:setSpriteFrame(cc.SpriteFrameCache:getInstance():getSpriteFrame('anim_hand_card_3.png'))
                                end
                            end

                            local handler = self.game_scene:schedule_once_time(0.1, function()
                                self:update_position()

                                for _, vv in ipairs(self.node_cards) do
                                    if vv.anim_card then
                                        vv.anim_card:removeFromParent(true)
                                        vv.anim_card = nil
                                    end

                                    vv.card:setVisible(true)
                                end

                                local handler = self.game_scene:schedule_once_time(0.1, function()
                                    if callback_func then callback_func() end
                                end)
                                table.insert(self.init_hand_card_schedule_handlers, handler)
                            end)
                            table.insert(self.init_hand_card_schedule_handlers, handler)
                        end)
                        table.insert(self.init_hand_card_schedule_handlers, handler)
                    end
                end) 
                v.anim_card:runAction(cc.Sequence:create(action_1, action_2))
            end

            __anim_zhua_pai__(self.node_cards[index+1])
            __anim_zhua_pai__(self.node_cards[index+2])
            __anim_zhua_pai__(self.node_cards[index+3])
            __anim_zhua_pai__(self.node_cards[index+4])
        end)
        table.insert(self.init_hand_card_schedule_handlers, handler)

        delay = delay + 0.8
    end
end

function my_hand_card:draw_card(location_index, card_id, is_kong, callback_func)
    if location_index ~= self.location_index then return end

    self.draw_card_anim = true      -- 这个是代表摸牌动画中的标识
    self:play_draw_card_anim(card_id, function()
        self.draw_card_anim = false

        local need_update_position = (self.cur_draw_card and true or false)

        local x, y, z_order = self:get_card_position(#self.node_cards, -1)

        -- 记录下刚摸的牌，在手牌排序的时候，忽略这张牌
        self.cur_draw_card = self:create_card(card_id)
        self.cur_draw_card:setPosition(x, y + 20)
        self.hand_card_node:addChild(self.cur_draw_card, z_order)

        table.insert(self.node_cards, {
            card = self.cur_draw_card,
            card_id = card_id,
        })

        if need_update_position then self:update_position() end

        local action_1 = cc.MoveTo:create(0.1, cc.p(x, y))
        local action_2 = cc.CallFunc:create(function() if callback_func then callback_func() end end)
        self.cur_draw_card:runAction(cc.Sequence:create(action_1, action_2))
    end)
end

return my_hand_card

