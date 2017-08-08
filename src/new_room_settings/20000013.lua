-- ./app/platform/room/new_room_settings/20000013.lua
-- 两房麻将

local new_room_config = {
    name = '两房麻将',
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
                section_name = '手牌',
                attributes = {
                    {
                        attr_name = 'handcard_num',
                        ctrl_type = 'radio',
                        init_value = 13,
                        options = {
                            { text = '13张', value = 13, },
                            { text = '10张', value = 10, },
                            { text = '7张', value = 7, },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '选13张，可3或4人游戏。\n选10张或7张仅可4人游戏。',
                        help_offset_x = 220,
                        help_offset_y = -50,
                    },
                },
            },
        },
        {
            {
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'zmjd_zmjf',
                        ctrl_type = 'radio',
                        init_value = 0,
                        no_amend = true,
                        offset_x = 10,
                        options = {
                            { text = '自摸加底', value = 0, },
                            { text = '自摸加番', value = 1, },
                        },
                    },
                    {
                        attr_name = 'dgh',
                        ctrl_type = 'radio',
                        init_value = 0,
                        no_amend = true,
                        offset_x = 80,
                        link_width = 150,
                        options = {
                            { text = '点杠花(引杠给)', value = 0, },
                            { text = '点杠花(大家给)', value = 1, },
                        },
                    },
                    {
                        attr_name = 'last_hu',
                        ctrl_type = 'radio',
                        init_value = 0,
                        offset_x = 60,
                        link_width = 150,
                        options = {
                            { text = '最后一圈必胡', value = 0, },
                            { text = '放小胡大', value = 1, },
                        },
                    },
                },
            },
        },
        {
            {
                section_name = '牌型',
                attributes = {
                    {
                        attr_name = 'baijiao',
                        text = '摆叫',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'baojiao',
                        text = '爆叫',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                        new_line = true,
                    },
                    {
                        attr_name = 'mq_zz_jxw',
                        text = '门清、中张、夹心五',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'yj_jd',
                        text = '幺九、将对',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'ddd',
                        text = '大单吊',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'tdh',
                        text = '天地胡',
                        init_value = true,
                        ctrl_type = 'check_box',
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
                        attr_name = 'fd',
                        ctrl_type = 'radio',
                        init_value = 2,
                        options = {
                            { text = '2番', value = 2, },
                            { text = '3番', value = 3, },
                            { text = '4番', value = 4, },
                            { text = '5番', value = 5, },
                            { text = '6番', value = 6, },
                        },
                    },
                    {
                        attr_name = 'fdjd',
                        text = '封顶加底',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -20,
            section_interval = 30,
        },
    },
}

return new_room_config
