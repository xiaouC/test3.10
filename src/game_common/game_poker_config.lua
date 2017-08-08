-- app/platform/game/game_common/game_poker_config.lua

-- 玩家的位置
POKER_USER_LOCATION_SELF     = 1      -- 本家
POKER_USER_LOCATION_ONE      = 2      -- 逆时针第1家
POKER_USER_LOCATION_TWO      = 3      -- 逆时针第2家
POKER_USER_LOCATION_THREE    = 4      -- 逆时针第3家
POKER_USER_LOCATION_FOUR     = 5      -- 逆时针第4家

-- 
POKER_CARD_TYPE_DIAMONDS    = 1       -- 方块
POKER_CARD_TYPE_CLUBS       = 2       -- 梅花
POKER_CARD_TYPE_HEARTS      = 3       -- 红桃
POKER_CARD_TYPE_SPADES      = 4       -- 黑桃

-- 
local poker_card_width, poker_card_height = 163, 221        -- 扑克牌原型的高宽
function create_poker_card_front(card_id, anchor_point)
    anchor_point = anchor_point or cc.p(0, 0)

    --
    local card_type = math.floor(card_id / 16) + 1
    local card_real_id = math.floor(card_id % 16)

    -- 
    local card_node = cc.Node:create()
    local bg_sprite = cc.Sprite:createWithSpriteFrameName('poker_card_front.png')
    bg_sprite:setAnchorPoint(anchor_point)
    card_node:addChild(bg_sprite)

    -- 
    local lt_sprite = cc.Sprite:createWithSpriteFrameName(string.format('poker_card_%02d.png', card_real_id))
    lt_sprite:setAnchorPoint(0, 1)
    lt_sprite:setPosition(20 - poker_card_width * anchor_point.x, poker_card_height * (1 - anchor_point.y) - 20)
    if card_real_id ~= 14 and card_real_id ~= 15 then
        lt_sprite:setColor((card_type == POKER_CARD_TYPE_DIAMONDS or card_type == POKER_CARD_TYPE_HEARTS) and cc.c3b(160, 0, 0) or cc.c3b(0, 0, 0))
    end
    card_node:addChild(lt_sprite)

    -- 不是大小王
    if card_real_id ~= 14 and card_real_id ~= 15 then
        local lt_sprite_1 = cc.Sprite:createWithSpriteFrameName(string.format('poker_card_type_%02d_s.png', card_type))
        lt_sprite_1:setAnchorPoint(0, 1)
        lt_sprite_1:setPosition(20 - poker_card_width * anchor_point.x, poker_card_height * (1 - anchor_point.y) - 80)
        card_node:addChild(lt_sprite_1)
    end

    -- 右下方
    local rb_file = ''
    if card_real_id <= 10 then
        rb_file = string.format('poker_card_type_%02d_b.png', card_type)
    elseif card_real_id == 14 then
        rb_file = string.format('poker_card_type_14.png')       -- 小王
    elseif card_real_id == 15 then
        rb_file = string.format('poker_card_type_15.png')       -- 大王
    else
        rb_file = string.format('poker_card_type_%02d%s.png', card_real_id, (card_type == POKER_CARD_TYPE_DIAMONDS or card_type == POKER_CARD_TYPE_HEARTS) and '_r' or '_b')
    end

    local rb_sprite = cc.Sprite:createWithSpriteFrameName(rb_file)
    rb_sprite:setAnchorPoint(1, 0)
    rb_sprite:setPosition(poker_card_width * (1 - anchor_point.x) - 20, 20 - poker_card_height * anchor_point.y)
    card_node:addChild(rb_sprite)

    -- 
    return card_node
end

function create_poker_card_back()
    local card_node = cc.Node:create()
    local bg_sprite = cc.Sprite:createWithSpriteFrameName('poker_card_back.png')
    bg_sprite:setAnchorPoint(0, 0)
    card_node:addChild(bg_sprite)

    -- 
    return card_node
end

-- 扇形展开的扑克牌，当前只有3和5张牌，当有其他数量出现的时候，再增加吧
local sector_group_other_config = {
    [3] = {
        { x = -82, y = -2, rotation = -16, ap = { x = 0.5, y = 0 } },
        { x = -38, y = 0, rotation = 0, ap = { x = 0.5, y = 0 } },
        { x = 2, y = -7, rotation = 15, ap = { x = 0.5, y = 0 } },
    },
    [5] = {
        { x = -112, y = -11, rotation = -26, ap = { x = 0.5, y = 0 } },
        { x = -80, y = -3, rotation = -10, ap = { x = 0.5, y = 0 } },
        { x = -38, y = 0, rotation = 0, ap = { x = 0.5, y = 0 } },
        { x = 1, y = -6, rotation = 8, ap = { x = 0.5, y = 0 } },
        { x = 32, y = -20, rotation = 25, ap = { x = 0.5, y = 0 } }
    },
}
local sector_group_self_config = {
    [3] = {
        { x = -115, y = -6, rotation = -15, ap = { x = 0.5, y = 0 } },
        { x = -59, y = 2, rotation = 0, ap = { x = 0.5, y = 0 } },
        { x = 2, y = -7, rotation = 15, ap = { x = 0.5, y = 0 } },
    },
    [5] = {
        { x = -202, y = -45, rotation = -25, ap = { x = 0.5, y = 0 } },
        { x = -137, y = -20, rotation = -10, ap = { x = 0.5, y = 0 } },
        { x = -59, y = -15, rotation = 0, ap = { x = 0.5, y = 0 } },
        { x = 15, y = -27, rotation = 10, ap = { x = 0.5, y = 0 } },
        { x = 78, y = -49, rotation = 25, ap = { x = 0.5, y = 0 } }
    },
}
function create_poker_sector_group(is_self, card_list)
    local sg_config = is_self and sector_group_self_config[#card_list] or sector_group_other_config[#card_list]
    if not sg_config then return end

    local node = cc.Node:create()
    local all_card_nodes = {}

    for index, card_id in ipairs(card_list) do
        local card = create_poker_card_front(card_id, sg_config[index].ap)
        card:setPosition(sg_config[index].x, sg_config[index].y)
        card:setRotation(sg_config[index].rotation)
        node:addChild(card)
        table.insert(all_card_nodes, card)
    end

    return node, all_card_nodes
end

-- subscript_type: [ 'dizhu', ]
function create_poker_card_front_subscript(card_id, subscript_type, anchor_point)
    if not subscript_type then return create_poker_card_front(card_id, anchor_point) end

    -- 
    anchor_point = anchor_point or cc.p(0, 0)

    local card_node = create_poker_card_front(card_id, anchor_point)

    local subscript_sprite = cc.Sprite:createWithSpriteFrameName(string.format('poker_%s.png', subscript_type))
    subscript_sprite:setAnchorPoint(1, 1)
    subscript_sprite:setPosition(poker_card_width * (1 - anchor_point.x), poker_card_height * (1 - anchor_point.y))
    card_node:addChild(subscript_sprite)

    return card_node
end
