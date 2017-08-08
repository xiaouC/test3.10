-- ./app/platform/room/new_room_settings/20000005.lua
-- 英超麻将

local new_room_config = {
    name = '英超麻将',
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
        -- row 1
        {
            -- col 1
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
                            {
                                relational = 'and',       -- and / or
                                operation = 'disable',    -- 'reset_value', 'invisible', 'disable'
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
                        init_text = '不奖码',
                        options = {
                            { text = '不奖码', value = 0, },
                            { text = '奖码', value = 1, },
                            { text = '加倍奖码', value = 2, },
                        },
                        expression_list = {
                            {
                                relational = 'and',       -- and / or
                                operation = 'disable',    -- 'reset_value', 'invisible', 'disable'
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
                },
            },
        },
        -- row 2
        {
            -- col 1
            {
                section_name = '番型',
                attributes = {
                    {
                        attr_name = 'win_ddh',
                        ctrl_type = 'check_box',
                        text = '对对胡两倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_qys',
                        ctrl_type = 'check_box',
                        text = '清一色三倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_qdd',
                        ctrl_type = 'check_box',
                        text = '清对四倍　',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_yj',
                        ctrl_type = 'check_box',
                        text = '幺九五倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        new_line = true,
                    },
                    {
                        attr_name = 'win_qf',
                        ctrl_type = 'check_box',
                        text = '全番六倍　',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_13',
                        ctrl_type = 'check_box',
                        text = '十三幺七倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_12',
                        ctrl_type = 'check_box',
                        text = '十二张全包',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        -- row 3
        {
            -- col 1
            {
                section_name = '鬼牌',
                attributes = {
                    {
                        attr_name = 'king_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        init_text = '翻鬼',
                        options = {
                            { text = '无鬼', value = 0, },
                            { text = '翻鬼', value = 1, },
                            { text = '双鬼', value = 2, },
                        },
                    },
                    {
                        attr_name = 'no_king_double',
                        ctrl_type = 'check_box',
                        text = '无鬼加番',
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
                                relational = 'and',       -- and / or
                                operation = 'disable',    -- 'reset_value', 'invisible', 'disable'
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
                        text = '四鬼胡牌',
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
                                relational = 'and',       -- and / or
                                operation = 'disable',    -- 'reset_value', 'invisible', 'disable'
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
                        init_text = '2倍',
                        options = {
                            { text = '2倍', value = 2, },
                            { text = '3倍', value = 3, },
                        },
                        expression_list = {
                            {
                                relational = 'and',       -- and / or
                                operation = 'disable',    -- 'reset_value', 'invisible', 'disable'
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
        -- row 4
        {
            -- col 1
            {
                section_name = '奖码',
                attributes = {
                    {
                        attr_name = 'award_ma',
                        ctrl_type = 'radio',
                        init_value = 2,
                        init_text = '2码',
                        options = {
                            { text = '2码', value = 2 },
                            { text = '4码', value = 4 },
                            { text = '6码', value = 6 },
                            { text = '8码', value = 8 },
                            { text = '10码', value = 10 },
                            { text = '一张定码', value = 0 },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '胡牌后，翻开牌墩中最后一张牌\n翻出牌的点数即为中码数\n风牌则中4码，鬼牌则中12码。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                    {
                        attr_name = 'card_award_ma_num',
                        ctrl_type = 'no_ui',
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = true,
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
                                operation_value = false,
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
                },
            },
        },
        layout_config = {
            section_offset_x_1 = 10,
            section_offset_y = -20,
            section_interval = 30,
        },
    },
}

return new_room_config
