-- ./app/platform/room/new_room_settings/20000006.lua
-- 捉鸡麻将

local new_room_config = {
    name = '捉鸡麻将',
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
                        attr_name = 'sxj',
                        ctrl_type = 'radio',
                        init_value = false,
                        options = {
                            { text = '满堂鸡', value = false, },
                            { text = '上下鸡', value = true, },
                        },
                    },
                    {
                        attr_name = 'mtj',
                        ctrl_type = 'no_ui',
                        init_value = true,
                        new_line = true,
                    },
                    {
                        attr_name = 'ls',
                        ctrl_type = 'check_box',
                        text = '连庄',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -100,
            section_new_line_interval = 50,
        },
    },
}

return new_room_config
