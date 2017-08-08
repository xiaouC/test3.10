-- ./app/platform/room/new_room_settings/20000018.lua
-- 玉贵麻将

local new_room_config = {
    name = '玉贵麻将',
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
                section_name = '字牌',
                attributes = {
                    {
                        attr_name = 'feng',
                        ctrl_type = 'radio',
                        init_value = true,
                        no_amend = true,
                        options = {
                            { text = '带字', value = true, },
                            { text = '不带字', value = false, },
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
                        attr_name = 'qd',
                        ctrl_type = 'check_box',
                        text = '七对',
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
                                        name = 'lqd',
                                        operator = '==',
                                        op_value = true,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = true,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'dlqd',
                                        operator = '==',
                                        op_value = true,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = true,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'slqd',
                                        operator = '==',
                                        op_value = true,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'lqd',
                        ctrl_type = 'check_box',
                        text = '龙七对',
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
                                        name = 'qd',
                                        operator = '==',
                                        op_value = false,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = true,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'dlqd',
                                        operator = '==',
                                        op_value = true,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = true,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'slqd',
                                        operator = '==',
                                        op_value = true,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'dlqd',
                        ctrl_type = 'check_box',
                        text = '双龙七对',
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
                                        name = 'qd',
                                        operator = '==',
                                        op_value = false,
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
                                        name = 'lqd',
                                        operator = '==',
                                        op_value = false,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = true,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'slqd',
                                        operator = '==',
                                        op_value = true,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'slqd',
                        ctrl_type = 'check_box',
                        text = '三龙七对',
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
                                        name = 'qd',
                                        operator = '==',
                                        op_value = false,
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
                                        name = 'lqd',
                                        operator = '==',
                                        op_value = false,
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
                                        name = 'dlqd',
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
                section_name = '摸码',
                attributes = {
                    {
                        attr_name = 'award_ma',
                        ctrl_type = 'radio',
                        init_value = 4,
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
                        attr_name = 'card_award_ma',
                        ctrl_type = 'no_ui',
                        init_value = 0,
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
                },
            },
        },
        layout_config = {
            section_offset_y = -30,
            section_interval = 50,
        },
    },
}

return new_room_config
