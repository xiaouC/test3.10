-- ./app/platform/room/new_room_settings/20000007.lua
-- 血战麻将

local new_room_config = {
    name = '血战麻将',
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
                        attr_name = 'zmjd_zmjf',
                        ctrl_type = 'radio',
                        init_value = 0,
                        no_amend = true,
                        offset_x = 10,
                        link_width = 150,
                        options = {
                            { text = '自摸加底', value = 0, },
                            { text = '自摸加番', value = 1, },
                        },
                    },
                    {
                        attr_name = 'hsz',
                        text = '换三张',
                        init_value = true,
                        ctrl_type = 'check_box',
                        offset_x = 100,
                        selected_value = true,
                        unselected_value = false,
                    },
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
                        attr_name = 'dgh',
                        ctrl_type = 'radio',
                        init_value = 0,
                        no_amend = true,
                        offset_x = 10,
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
                        offset_x = 50,
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
                        attr_name = 'mq_zz_jxw',
                        text = '门清、中张、夹心五',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'yj_jd',
                        text = '幺九、将对　　　　',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'dz',
                        text = '独张　　　　　　　',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                        new_line = true,
                    },
                    {
                        attr_name = 'ddd',
                        text = '大单吊　　　　　　　',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'tdh',
                        text = '天地胡　　　　　　',
                        init_value = true,
                        ctrl_type = 'check_box',
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '中张：所有牌没有一和九。胡牌加1番。\n门清：没有碰和明杠。胡牌加1番。\n夹心五：胡的为，4和6中间夹的5，加1番。\n将对：带二、五、八的对对胡。\n独张：可胡的牌全部出现，只剩最后一张，胡到\n了则算独张，加1番。\n大单吊：只剩下一张牌，单吊将。\n天胡：庄家发完牌，换三张后就胡牌，叫天胡。\n地胡：闲家在发完牌后就已经听牌，庄打第一张\n牌刚好胡庄打的这张，叫地胡。',
                        offset_x = 0,
                        offset_y = 0,
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
            section_interval = 50,
        },
    },
}

return new_room_config
