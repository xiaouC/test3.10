-- ./app/platform/room/new_room_settings/20000056.lua
-- 二人庄河

local new_room_config = {
    name = '二人庄河',
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
                section_name = '牌型',
                attributes = {
                    {
                        attr_name = 'cq',
                        ctrl_type = 'check_box',
                        text = '纯清再X2',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '不勾选，纯清一色也可胡，但只计2倍；勾选，\n纯清一色胡牌4倍。',
                        offset_x = 50,
                        offset_y = -110,
                        new_line = true,
                    },
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '小鸡满天飞        冲宝        杠上开花        七巧对\n\n飘胡              清一色      纯清一色        闭门胡',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 25,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    },
                    {
                        attr_name = 'play_mode',
                        ctrl_type = 'no_ui',
                        init_value = 1,
                    },
                    {
                        attr_name = 'qd',
                        ctrl_type = 'no_ui',
                        init_value = true,
                    },
                },
            },
        },
        {
            {
                section_name = '封顶',
                attributes = {
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '64倍',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 30,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    },
                    {
                        attr_name = 'max_mode',
                        ctrl_type = 'no_ui',
                        init_value = 64,
                    },

                },
            },
        },
        layout_config = {
            section_offset_y = -50,
            section_interval = 100,
            section_new_line_interval = 25,
            section_attr_interval = 50,
        },
    },
}

return new_room_config
