-- ./app/platform/room/new_room_settings/20000055.lua
-- 河源七仔

local new_room_config = {
    name = '河源七仔',
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
                        text = '河源七仔是一种广为流传的客家牌类游戏，使用一\n副牌，四人参加，打发类似升级，具有很强的对抗\n性。',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 35,
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
            section_offset_x_1 = 40,
        },
    },
}

return new_room_config
