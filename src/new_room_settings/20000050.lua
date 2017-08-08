-- ./app/platform/room/new_room_settings/20000050.lua
-- 安义麻将

local new_room_config = {
    name = '安义麻将',
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
                        attr_name = 'zm_double',
                        ctrl_type = 'check_box',
                        text = '自摸加倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -100,
            section_interval = 80,
            section_attr_interval = 50,
            check_box_text_font_size = 26,
        },
    },
}

return new_room_config
