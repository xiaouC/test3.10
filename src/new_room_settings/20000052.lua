-- ./app/platform/room/new_room_settings/20000052.lua
-- 憋七

local new_room_config = {
    name = '憋七',
    max_count = 4,
    is_poker = true,
    bottom_section = {
        name = '局数：',
        attr_name = 'room_card',
        ctrl_type = 'radio',        -- 控件类型
        init_value = 2,             -- 初始值
        options = {
            { text_1 = '4局', text_2 = 'x1', value = 1, },
            { text_1 = '8局', text_2 = 'x2', value = 2, },
            { text_1 = '16局', text_2 = 'x4', value = 4, },
        },
    },
    top_sections = {
        {
            {
                attributes = {
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '玩家人数为4人，使用一副牌，去掉大小王，共52张牌。玩家每人各发13张牌，\n以自己为主，不与其他玩家配合。游戏中以4个花色的7为基准接牌，无牌可\n接时则必须扣牌，玩家手中牌(不算扣下的牌)全部出完则游戏结束，游戏结算\n以扣牌点数最少或没有扣牌的玩家获胜。',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 26,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -120,
            section_offset_x_1 = 10,
        },
    },
}

return new_room_config
