-- ./app/platform/room/new_room_settings/20000053.lua
-- 北京抓五魁

local new_room_config = {
    name = '北京抓五魁',
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
                        attr_name = 'qys',
                        ctrl_type = 'check_box',
                        text = '清一色',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'qd',
                        ctrl_type = 'check_box',
                        text = '七对',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'zwk',
                        ctrl_type = 'check_box',
                        text = '捉五魁',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        {
            {
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'hdly',
                        ctrl_type = 'check_box',
                        text = '海底捞月',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'gsp',
                        ctrl_type = 'check_box',
                        text = '杠上炮',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'gskh',
                        ctrl_type = 'check_box',
                        text = '杠上开花',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        layout_config = {
            section_interval = 100,
            section_offset_y = -80,
            section_attr_interval = 50,
        },
    },
}

return new_room_config
