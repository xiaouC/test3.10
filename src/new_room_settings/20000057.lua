-- ./app/platform/room/new_room_settings/20000057.lua
-- 兰州麻将

local new_room_config = {
    name = '兰州麻将',
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
                section_name = '听牌',
                attributes = {
                    {
                        attr_name = 'listen_card',
                        ctrl_type = 'radio',
                        init_value = 1,
                        init_text = '悄悄胡',
                        no_amend = true,
                        options = {
                            { text = '揭牌听牌', value = 0, },
                            { text = '悄悄胡', value = 1, },
                            { text = '普通胡', value = 2, },
                        },
                    },
                },
            },
        },
        {
            {
                section_name = '规则',
                attributes = {
                    {
                        attr_name = 'card_module',
                        ctrl_type = 'radio',
                        init_value = 1,
                        init_text = '中发白',
                        options = {
                            { text = '无', value = 0, },
                            { text = '中发白', value = 1, },
                            { text = '黑三风', value = 2, },
                        },
                    },
                    {
                        attr_name = 'sanyao',
                        ctrl_type = 'check_box',
                        text = '三幺',
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
                                        name = 'card_module',
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
                                        name = 'card_module',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'sanjiu',
                        ctrl_type = 'check_box',
                        text = '三九',
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
                                        name = 'card_module',
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
                                        name = 'card_module',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                        new_line = true,        -- new line
                    },
                    {
                        attr_name = 'ry_jiang',
                        ctrl_type = 'radio',
                        init_value = 1,
                        init_text = '硬258坐庄',
                        options = {
                            { text = '无', value = 0, },
                            { text = '硬258坐庄', value = 1, },
                            { text = '软258坐庄X2', value = 2, },
                        },
                    },
                    {
                        attr_name = 'wdd',
                        ctrl_type = 'check_box',
                        text = '挖到底',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'chi',
                        ctrl_type = 'check_box',
                        text = '吃',
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
                                        name = 'ry_mq',
                                        operator = '~=',
                                        op_value = 2,
                                    },
                                },
                            },
                            {
                                relational = 'and',       -- and / or
                                operation = 'disable',    -- 'reset_value', 'invisible', 'disable'
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'ry_mq',
                                        operator = '~=',
                                        op_value = 2,
                                    },
                                },
                            },
                        },
                        new_line = true,        -- new line
                    },
                    {
                        attr_name = 'ry_mq',
                        ctrl_type = 'radio',
                        init_value = 1,
                        init_text = '硬门清',
                        options = {
                            { text = '无', value = 0, },
                            { text = '硬门清', value = 1, },
                            { text = '软门清X2', value = 2, },
                        },
                        new_line = true,        -- new line
                    },
                    {
                        attr_name = 'ry_shuai',
                        ctrl_type = 'radio',
                        init_value = 1,
                        init_text = '硬甩',
                        options = {
                            { text = '无', value = 0, },
                            { text = '硬甩', value = 1, },
                            { text = '软甩', value = 2, },
                        },
                    },
                },
            },
        },
        layout_config = {
            section_attr_interval = 100,
            section_new_line_interval = 15,
        },
    },
}

return new_room_config
