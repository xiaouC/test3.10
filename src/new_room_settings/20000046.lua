-- ./app/platform/room/new_room_settings/20000046.lua
-- 贵阳抓鸡

local new_room_config = {
    name = '贵阳抓鸡',
    max_count = 4,
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
                section_name = '规则',
                attributes = {
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '2-4人都可游戏；玩三丁、两丁时，必须缺一门才可胡牌。',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 25,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    },
                },
            },
        },
        {
            {
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'ybj',
                        ctrl_type = 'check_box',
                        text = '摇摆鸡',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        width = 120,
                    },
                    {
                        attr_name = 'wjj',
                        ctrl_type = 'check_box',
                        text = '挖掘鸡',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        width = 120,
                    },
                    {
                        attr_name = 'ylj',
                        ctrl_type = 'check_box',
                        text = '压路鸡',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        width = 120,
                        new_line = true,
                    },
                    {
                        attr_name = 'fybj',
                        ctrl_type = 'check_box',
                        text = '逢幺变鸡',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        width = 120,
                    },
                    {
                        attr_name = 'bj',
                        ctrl_type = 'check_box',
                        text = '本鸡',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        width = 120,
                    },
                    {
                        attr_name = 'lz',
                        ctrl_type = 'check_box',
                        text = '连庄',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        width = 120,
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -50,
            section_interval = 80,
            section_attr_interval = 80,
            section_new_line_interval = 50,
            check_box_text_font_size = 24,
        },
    },
}

return new_room_config
