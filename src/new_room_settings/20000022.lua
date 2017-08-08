-- ./app/platform/room/new_room_settings/20000022.lua
-- 海南麻将

local new_room_config = {
    name = '海南麻将',
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
                section_name = '抓跑',
                attributes = {
                    {
                        attr_name = 'zp_yf',
                        ctrl_type = 'radio',
                        init_value = false,
                        no_amend = true,
                        options = {
                            { text = '无番', value = false, },
                            { text = '有番', value = true, },
                        },
                    },
                    {
                        attr_name = 'take_pair',
                        ctrl_type = 'check_box',
                        text = '杠牌算有番',
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
                        attr_name = 'zx',
                        ctrl_type = 'check_box',
                        text = '庄闲',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'lz',
                        ctrl_type = 'check_box',
                        text = '连庄',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'hz',
                        ctrl_type = 'check_box',
                        text = '黄庄算分',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                        new_line = true,
                    },
                    {
                        attr_name = 'hh',
                        ctrl_type = 'check_box',
                        text = '花胡',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'fgj',
                        ctrl_type = 'check_box',
                        text = '防勾脚',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        new_line = true,
                    },
                    {
                        attr_name = 'sg_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        options = {
                            { text = '上噶', value = 0, },
                            { text = '自由上噶', value = 1, },
                        },
                    },
                },
            },
        },
        layout_config = {
            section_offset_x_1 = 50,
            section_offset_y = -60,
            section_interval = 30,
            section_new_line_interval = 30,
        },
    },
}

return new_room_config
