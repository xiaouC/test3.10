-- ./app/platform/room/new_room_settings/20000011.lua
-- 天水麻将

local new_room_config = {
    name = '天水麻将',
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
                        attr_name = 'qxd',
                        ctrl_type = 'check_box',
                        text = '可胡七对',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -130,
            section_offset_x_1 = 80,
        },
    },
}

return new_room_config
