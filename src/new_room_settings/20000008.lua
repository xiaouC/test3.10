-- ./app/platform/room/new_room_settings/20000008.lua
-- 南昌麻将

local new_room_config = {
    name = '南昌麻将',
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
                section_name = '底分',
                attributes = {
                    {
                        attr_name = 'basic_point',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        offset_x = 20,
                        options = {
                            { text = '1分', value = 1 },
                            { text = '4分', value = 4 },
                        },
                    },
                },
            },
        },
        {
            {
                section_name = '抓炮',
                attributes = {
                    {
                        attr_name = 'catch_gun',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        offset_x = 20,
                        options = {
                            { text = '一家付', value = 1 },
                            { text = '三家付', value = 3 },
                        },
                    },
                },
            },
            {
                section_name = '庄家',
                attributes = {
                    {
                        attr_name = 'chao_nt',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        offset_x = 40,
                        link_width = 150,
                        options = {
                            { text = '抄庄', value = 1 },
                            { text = '不抄庄', value = 0 },
                        },
                    },
                },
            },
        },
        {
            {
                section_name = '霸王',
                attributes = {
                    {
                        attr_name = 'bawang',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        offset_x = 20,
                        options = {
                            { text = '霸王精x2', value = 1 },
                            { text = '霸王精+10', value = 2 },
                        },
                    },
                },
            },
            {
                section_name = '精牌',
                attributes = {
                    {
                        attr_name = 'jingpai',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        offset_x = 40,
                        link_width = 150,
                        options = {
                            { text = '打出精牌算分', value = 1 },
                            { text = '打出精牌不算分', value = 0 },
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
                        attr_name = 'play_mode',
                        ctrl_type = 'radio',
                        init_value = 2,
                        no_amend = true,
                        offset_x = 20,
                        options = {
                            { text = '同一首歌', value = 1 },
                            { text = '埋地雷', value = 2 },
                            { text = '上下翻', value = 4 },
                            { text = '无下精', value = 5 },
                        },
                    },
                    {
                        attr_name = 'htyx',
                        ctrl_type = 'check_box',
                        text = '回头一笑',
                        init_value = true,
                        offset_x = 30,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        layout_config = {
            section_interval = 35,
        },
    },
}

return new_room_config
