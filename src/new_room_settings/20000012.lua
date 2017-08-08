-- ./app/platform/room/new_room_settings/20000012.lua
-- 柳州麻将

local new_room_config = {
    name = '柳州麻将',
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
                        text = '2至4人都可游戏',
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
        {
            {
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'mq',
                        ctrl_type = 'check_box',
                        text = '门清',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },

                },
            },
        },
        {
            {
                section_name = '钓鱼',
                attributes = {
                    {
                        attr_name = 'fish_zhuang',
                        ctrl_type = 'radio',
                        init_value = true,
                        no_amend = true,
                        offset_x = 10,
                        options = {
                            { text = '跟庄钓鱼', value = false, },
                            { text = '一五九钓鱼', value = true, },
                        },
                        new_line = true,
                    },
                    {
                        attr_name = 'fish_num',
                        ctrl_type = 'radio',
                        init_value = 4,
                        no_amend = true,
                        offset_x = 10,
                        options = {
                            { text = '2条', value = 2, },
                            { text = '4条', value = 4, },
                            { text = '6条', value = 6, },
                            { text = '8条', value = 8, },
                            { text = '10条', value = 10, },
                        },
                    },

                },
            },
        },
        layout_config = {
            section_offset_y = -10,
            section_interval = 40,
            section_new_line_interval = 30,
        },
    },
}

return new_room_config
