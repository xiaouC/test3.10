-- ./app/platform/room/new_room_settings/20000003.lua
-- 推倒胡

local new_room_config = {
    name = '推倒胡',
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
                section_name = '风牌',
                attributes = {
                    {
                        attr_name = 'feng',
                        ctrl_type = 'radio',
                        init_value = true,
                        init_text = '带风',
                        options = {
                            { text = '带风', value = true, },
                            { text = '不带风', value = false, },
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
                        attr_name = 'qgh',
                        ctrl_type = 'check_box',
                        text = '可抢杠胡',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'mg_qgh',
                        ctrl_type = 'no_ui',
                        init_value = false,
                    },
                    {
                        attr_name = 'qg_all',
                        ctrl_type = 'check_box',
                        text = '抢杠全包',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'gk_all',
                        ctrl_type = 'check_box',
                        text = '杠爆全包',
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
                        new_line = true,
                    },
                    {
                        attr_name = 'win_qd',
                        ctrl_type = 'check_box',
                        text = '可胡七对',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'qd_double',
                        ctrl_type = 'check_box',
                        text = '七对加倍',
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
                                        name = 'win_qd',
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
                                        name = 'win_qd',
                                        operator = '==',
                                        op_value = false,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'win_qys',
                        ctrl_type = 'check_box',
                        text = '清一色4倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'win_13',
                        ctrl_type = 'check_box',
                        text = '十三幺13倍',
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
                                        name = 'feng',
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
                                        name = 'feng',
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
        {
            {
                section_name = '鬼牌',
                attributes = {
                    {
                        attr_name = 'king_mode',
                        ctrl_type = 'radio',
                        init_value = 3,
                        init_text = '无鬼',
                        options = {
                            { text = '无鬼', value = 1, },
                            { text = '白板做鬼', value = 2, },
                            { text = '翻鬼', value = 3, },
                            { text = '双鬼', value = 4, },
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
                                        op_value = 1,
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
                                        op_value = 1,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'no_king_double',
                        ctrl_type = 'check_box',
                        text = '无鬼加倍',
                        init_value = false,
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
                                        op_value = 1,
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
                                        op_value = 1,
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
                section_name = '买码',
                attributes = {
                    {
                        attr_name = 'award_mode',
                        ctrl_type = 'radio',
                        init_value = 4,
                        init_text = '4码',
                        options = {
                            { text = '2码', value = 2 },
                            { text = '4码', value = 4 },
                            { text = '6码', value = 6 },
                            { text = '8码', value = 8 },
                            { text = '10码', value = 10 },
                            { text = '一张定码', value = 1 },
                        },
                    },
                    {
                        attr_name = 'my_mgdf',
                        ctrl_type = 'check_box',
                        text = '码跟底分',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
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
