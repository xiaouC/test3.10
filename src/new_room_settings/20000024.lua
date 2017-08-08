-- ./app/platform/room/new_room_settings/20000024.lua
-- 韶关麻将

local new_room_config = {
    name = '韶关麻将',
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
                        attr_name = 'gk_all',
                        ctrl_type = 'check_box',
                        text = '杠爆全包',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'qgh',
                        ctrl_type = 'check_box',
                        text = '可抢杠胡',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = true,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'qg_all',
                                        operator = '==',
                                        op_value = true,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'qg_all',
                        ctrl_type = 'check_box',
                        text = '抢杠全包',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = false,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'qgh',
                                        operator = '==',
                                        op_value = false,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'qg_all_awardma',
                        ctrl_type = 'radio',
                        init_value = 0,
                        no_amend = true,
                        options = {
                            { text = '不奖码', value = 0, },
                            { text = '奖码', value = 1, },
                            { text = '加倍奖码', value = 2, },
                        },
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 0,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'qg_all',
                                        operator = '==',
                                        op_value = false,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'disable',  -- 'reset_value', 'invisible', 'disable'
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'qg_all',
                                        operator = '==',
                                        op_value = false,
                                    },
                                },
                            },
                        },
                        new_line = true,
                    },
                    {
                        attr_name = 'win_yjw',
                        ctrl_type = 'check_box',
                        text = '有一九万',
                        init_value = true,
                        offset_y = 30,
                        selected_value = true,
                        unselected_value = false,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = false,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'king_mode',
                                        operator = '==',
                                        op_value = 2,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'win_bhg',
                        ctrl_type = 'check_box',
                        text = '荒庄不荒杠',
                        init_value = true,
                        offset_y = 30,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        {
            offset_y = 30,
            {
                section_name = '番型',
                attributes = {
                    {
                        attr_name = 'win_ddh',
                        ctrl_type = 'check_box',
                        text = '对对胡4倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_hys',
                        ctrl_type = 'check_box',
                        text = '混一色4倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_hdd',
                        ctrl_type = 'check_box',
                        text = '混对8倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_qys',
                        ctrl_type = 'check_box',
                        text = '清一色8倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_qdd',
                        ctrl_type = 'check_box',
                        text = '清对16倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        new_line = true,
                    },
                    {
                        attr_name = 'win_yj',
                        ctrl_type = 'check_box',
                        text = '幺九16倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_qyj',
                        ctrl_type = 'check_box',
                        text = '清幺九32倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_qf',
                        ctrl_type = 'check_box',
                        text = '全番32倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_13',
                        ctrl_type = 'check_box',
                        text = '十三幺32倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = false,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'king_mode',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'disable',  -- 'reset_value', 'invisible', 'disable'
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'king_mode',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'win_jpqb',
                        ctrl_type = 'check_box',
                        text = '歼牌全包',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        {
            {
                section_name = '鬼牌',
                attributes = {
                    {
                        attr_name = 'king_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        options = {
                            { text = '无鬼', value = 0, },
                            { text = '翻鬼', value = 1, },
                            { text = '双鬼', value = 2, },
                        },
                    },
                    {
                        attr_name = 'no_king_double',
                        ctrl_type = 'check_box',
                        text = '无鬼加倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = false,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'king_mode',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'disable',  -- 'reset_value', 'invisible', 'disable'
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'king_mode',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'four_king_win',
                        ctrl_type = 'check_box',
                        text = '4鬼胡牌',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = false,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'king_mode',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'disable',  -- 'reset_value', 'invisible', 'disable'
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'king_mode',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'four_king_times',
                        ctrl_type = 'radio',
                        init_value = 2,
                        no_amend = true,
                        options = {
                            { text = '2倍', value = 2, },
                            { text = '3倍', value = 3, },
                        },
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'disable',  -- 'reset_value', 'invisible', 'disable'
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'king_mode',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        {
            {
                section_name = '奖码',
                attributes = {
                    {
                        attr_name = 'award_ma',
                        ctrl_type = 'radio',
                        init_value = 4,
                        no_amend = true,
                        options = {
                            { text = '2码', value = 2, },
                            { text = '4码', value = 4, },
                            { text = '6码', value = 6, },
                            { text = '8码', value = 8, },
                            { text = '10码', value = 10, },
                            { text = '一张定码', value = 0, },
                        },
                    },
                    {
                        attr_name = 'card_award_ma_num',
                        ctrl_type = 'no_ui',
                        init_value = 1,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 1,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'award_ma',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 0,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'award_ma',
                                        operator = '~=',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '胡牌后，翻开牌墩中最后一张牌，\n翻出牌的点数即为中码数，\n风牌则中4码，鬼牌则中12码。',
                        offset_x = -10,
                    },
                    {
                        attr_name = 'win_mgg',
                        ctrl_type = 'check_box',
                        text = '码跟杠',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        offset_x = -25,
                    },
                },
            },
        },
        layout_config = {
            section_interval = 30,
            section_offset_y = -20,
        },
    },
}

return new_room_config
