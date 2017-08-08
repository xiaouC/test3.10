-- app/platform/game/game_common/game_card_config.lua

-- 玩家的位置
USER_LOCATION_SELF     = 1      -- 本家
USER_LOCATION_RIGHT    = 2      -- 下家
USER_LOCATION_FACING   = 3      -- 对家
USER_LOCATION_LEFT     = 4      -- 上家

-- 牌区域
CARD_AREA = {
    LEI         = 1,        -- 垒牌区
    HAND        = 2,        -- 手牌区
    DISCARD     = 3,        -- 出牌区
    TAN         = 4,        -- 碰杠摊牌区
}

-- 
CARD_FRONT = 1      -- 正面背景
CARD_BACK = 2       -- 背面背景

ALL_CARD_CONFIG = {
    [USER_LOCATION_SELF] = {    -- 本家
        [CARD_AREA.LEI] = {         -- 垒牌区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_1_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_1_back.png', },
            },
            x = 0, y = 3,
            scale = 0.35,
        },
        [CARD_AREA.HAND] = {        -- 手牌区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_11_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_11_front.png' },
            },
            x = 0, y = -10,
            scale = 1,
            node_scale = 0.9,
            ghost_subscript = { x = -12, y = 27, scale = 0.8 },
        },
        [CARD_AREA.DISCARD] = {     -- 出牌区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_2_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_2_back.png' },
            },
            x = 0, y = 5,
            scale = 0.45,
        },
        [CARD_AREA.TAN] = {         -- 碰杠区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_9_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_9_back.png' },
            },
            x = 0, y = 10,
            scale = 0.65,
            ghost_subscript = { x = -12, y = 27, scale = 0.8 },
        },
    },
    [USER_LOCATION_RIGHT] = {   -- 下家的
        [CARD_AREA.LEI] = {         -- 垒牌区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_4_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_4_back.png' },
            },
            x = 3, y = 1,
            scale = 0.35,
            rotation = -90,
        },
        [CARD_AREA.HAND] = {        -- 手牌区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_8_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_5_back.png' },
            },
            x = 3, y = 0,
            scale = 0.45,
            rotation = -90,
            ghost_subscript = { x = -5, y = -8, scale = 0.4, rotation = -90 },
        },
        [CARD_AREA.DISCARD] = {     -- 出牌区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_6_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_6_back.png' },
            },
            x = 0, y = 4,
            scale = 0.45,
            rotation = -90,
        },
        [CARD_AREA.TAN] = {         -- 碰杠区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_8_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_8_back.png' },
            },
            x = 4, y = 0,
            scale = 0.35,
            rotation = -90,
            ghost_subscript = { x = -5, y = -8, scale = 0.4, rotation = -90 },
        },
    },
    [USER_LOCATION_FACING] = {  -- 对家的
        [CARD_AREA.LEI] = {
            card_bg = {             -- 垒牌去
                [CARD_FRONT] = { frame_name = 'card_bg_1_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_1_back.png' },
            },
            x = 0, y = 3,
            scale = 0.35,
        },
        [CARD_AREA.HAND] = {        -- 手牌区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_8_front.png', rotation = -90, },
                [CARD_BACK] = { frame_name = 'card_bg_3_back.png' },
            },
            x = 0, y = 5,
            scale = 0.4,
            --rotation = -180,
            ghost_subscript = { x = -8, y = 15, scale = 0.4 },
        },
        [CARD_AREA.DISCARD] = {     -- 出牌区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_2_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_2_back.png' },
            },
            x = 0, y = 5,
            scale = 0.45,
            --rotation = -180,
        },
        [CARD_AREA.TAN] = {         -- 碰杠区
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_8_front.png', rotation = -90, },
                [CARD_BACK] = { frame_name = 'card_bg_8_back.png', rotation = -90, },
            },
            x = 0, y = 5,
            scale = 0.35,
            --rotation = -180,
            ghost_subscript = { x = -8, y = 15, scale = 0.4 },
        },
    },
    [USER_LOCATION_LEFT] = {
        [CARD_AREA.LEI] = {
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_4_front.png', flip_x = true },
                [CARD_BACK] = { frame_name = 'card_bg_4_back.png', flip_x = true },
            },
            x = -3, y = 1,
            scale = 0.35,
            rotation = 90,
        },
        [CARD_AREA.HAND] = {
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_8_front.png', flip_x = true },
                [CARD_BACK] = { frame_name = 'card_bg_5_back.png', flip_x = true },
            },
            x = -3, y = 0,
            scale = 0.4,
            rotation = 90,
            ghost_subscript = { x = 5, y = 7, scale = 0.4, rotation = 90 },
        },
        [CARD_AREA.DISCARD] = {
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_6_front.png', },
                [CARD_BACK] = { frame_name = 'card_bg_6_back.png', flip_x = true },
            },
            x = 0, y = 4,
            scale = 0.45,
            rotation = 90,
        },
        [CARD_AREA.TAN] = {
            card_bg = {
                [CARD_FRONT] = { frame_name = 'card_bg_8_front.png', flip_x = true, },
                [CARD_BACK] = { frame_name = 'card_bg_8_back.png', flip_x = true },
            },
            x = -4, y = 0,
            scale = 0.35,
            rotation = 90,
            ghost_subscript = { x = 5, y = 7, scale = 0.4, rotation = 90 },
        },
    },
}

-- 
function create_card_back(location, area)
    local card_config = ALL_CARD_CONFIG[location][area]

    local card_node = cc.Node:create()
    if card_config.node_scale then card_node:setScale(card_config.node_scale) end

    local card_back = cc.Sprite:createWithSpriteFrameName(card_config.card_bg[CARD_BACK].frame_name)
    card_node:addChild(card_back)

    if card_config.card_bg[CARD_BACK].flip_x then card_back:setFlippedX(true) end
    if card_config.card_bg[CARD_BACK].flip_y then card_back:setFlippedY(true) end
    if card_config.card_bg[CARD_BACK].rotation then card_back:setRotation(card_config.card_bg[CARD_BACK].rotation) end

    return card_node
end

-- 
CARD_KIND_CONFIG = { 'w', 'tiao', 'tong', 'zi' }
CARD_PATTERN = 'card_%s_%d.png'
local function get_card_number(card_id) return card_id % 16 end
local function get_card_kind(card_id) return math.floor(card_id / 16) + 1 end
local function get_card_sprite_frame_name(card_id)
    local kind = get_card_kind(card_id)
    local num = get_card_number(card_id)
    return string.format(CARD_PATTERN, CARD_KIND_CONFIG[kind], num)
end

function create_card_front(location, area, card_id)
    local card_config = ALL_CARD_CONFIG[location][area]

    local card_node = cc.Node:create()
    if card_config.node_scale then card_node:setScale(card_config.node_scale) end

    local card_front = cc.Sprite:createWithSpriteFrameName(card_config.card_bg[CARD_FRONT].frame_name)
    card_node:addChild(card_front)

    if card_config.card_bg[CARD_FRONT].flip_x then card_front:setFlippedX(true) end
    if card_config.card_bg[CARD_FRONT].flip_y then card_front:setFlippedY(true) end
    if card_config.card_bg[CARD_FRONT].rotation then card_front:setRotation(card_config.card_bg[CARD_FRONT].rotation) end

    -- 
    if card_id and card_id ~= 0 then
        local card_frame_name = get_card_sprite_frame_name(card_id)
        local card_sprite = cc.Sprite:createWithSpriteFrameName(card_frame_name)

        card_sprite:setPosition(card_config.x, card_config.y)
        card_sprite:setScale(card_config.scale)
        if card_config.skew_x then card_sprite:setSkewX(card_config.skew_x) end
        if card_config.skew_y then card_sprite:setSkewY(card_config.skew_y) end
        if card_config.rotation then card_sprite:setRotation(card_config.rotation) end

        card_node:addChild(card_sprite)
    end

    -- 
    return card_node
end

function create_card_sprite(card_id)
    local card_frame_name = get_card_sprite_frame_name(card_id)
    return cc.Sprite:createWithSpriteFrameName(card_frame_name)
end
