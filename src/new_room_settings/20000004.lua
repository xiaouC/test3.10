-- ./app/platform/room/new_room_settings/20000004.lua
-- 上海敲麻麻将

local new_room_config = {
    name = '敲麻麻将',
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
                        text = '可吃碰杠，默认可胡清一色，混一色，碰碰胡。',
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
                section_name = '底分',
                attributes = {
                    {
                        attr_name = 'basic_score',
                        ctrl_type = 'radio',
                        init_value = 2,
                        init_text = '2分',
                        options = {
                            { text = '1分', value = 1, },
                            { text = '2分', value = 2, },
                        },
                    },
                },
            },
        },
        {
            {
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'kb',
                        ctrl_type = 'check_box',
                        text = '开宝',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'hf',
                        ctrl_type = 'check_box',
                        text = '荒番',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'twohzc',
                        ctrl_type = 'check_box',
                        text = '2花抓铳',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'fcy',
                        ctrl_type = 'check_box',
                        text = '飞苍蝇',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        {
            {
                section_name = '番型',
                attributes = {
                    {
                        attr_name = 'mq',
                        ctrl_type = 'check_box',
                        text = '门清',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'ddc',
                        ctrl_type = 'check_box',
                        text = '大吊车',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        {
            {
                section_name = '封顶',
                attributes = {
                    {
                        attr_name = 'max_score',
                        ctrl_type = 'radio',
                        init_value = 0,
                        options = {
                            { text = '20分', value = 20, },
                            { text = '50分', value = 50, },
                            { text = '不封顶', value = 0, },
                        },
                    },
                },
            },
        },
        layout_config = {
            section_interval = 10,
        },
    },
}

return new_room_config
