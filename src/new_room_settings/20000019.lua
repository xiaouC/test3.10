-- ./app/platform/room/new_room_settings/20000019.lua
-- 广西麻将

local new_room_config = {
    name = '广西麻将',
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
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'mq',
                        ctrl_type = 'check_box',
                        text = '门清',
                        init_value = false,
                        offset_y = -10,
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
            section_offset_y = -50,
            section_interval = 70,
            section_new_line_interval = 40,
        },
    },
}

return new_room_config
