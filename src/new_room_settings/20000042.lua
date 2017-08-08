-- ./app/platform/room/new_room_settings/20000042.lua
-- 洛阳杠次

local new_room_config = {
    name = '洛阳杠次',
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
                -- 可能有很多属性，也可以只有一个
                attributes = {
                    {
                        attr_name = 'play_mode',
                        ctrl_type = 'radio',    -- 控件类型
                        init_value = 1,             -- 初始值
                        init_invisible = false,     -- 初始不可见?
                        init_disable = false,       -- 初始不可用?
                        options = {
                            { text = '软次', value = 1, },
                            { text = '硬次', value = 2, },
                        },
                    },
                    {
                        attr_name = 'cicard_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        options = {
                            { text = '带字牌', value = 1, },
                            { text = '不带字牌', value = 2, },
                        },
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 1,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'play_mode',
                                        operator = '==',
                                        op_value = 1,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 2,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'play_mode',
                                        operator = '==',
                                        op_value = 2,
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
                section_name = '特殊',
                attributes = {
                    {
                        attr_name = 'dqsb',
                        ctrl_type = 'check_box',
                        text = '点次双倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'ypkh',
                        ctrl_type = 'check_box',
                        text = '余30张可胡',
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
                                        name = 'play_mode',
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
                                        name = 'play_mode',
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
        -- row 3
        {
            -- col 1
            {
                section_name = '杠底',
                attributes = {
                    {
                        attr_name = 'gangdi_score',
                        ctrl_type = 'radio',
                        init_value = 1,
                        options = {
                            { text = '1分', value = 1, },
                            { text = '2分', value = 2, },
                            { text = '3分', value = 3, },
                        },
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 1,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'play_mode',
                                        operator = '==',
                                        op_value = 1,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 2,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'play_mode',
                                        operator = '==',
                                        op_value = 2,
                                    },
                                },
                            },
                        },
                    },
                },
            },
            -- col 2
            {
                section_name = '自摸',
                attributes = {
                    {
                        attr_name = 'zimo_score',
                        ctrl_type = 'combo_box',
                        init_value = 3,
                        init_text = '3分',
                        options = {
                            {
                                text = '2分',
                                value = 2,
                                is_valid_expression = {
                                    relational = 'and',         -- and / or
                                    attr_list = {
                                        {
                                            type = 'attribute',
                                            name = 'gangdi_score',
                                            operator = '<=',
                                            op_value = 1,
                                        },
                                    },
                                },
                            },
                            {
                                text = '3分',
                                value = 3,
                                is_valid_expression = {
                                    relational = 'and',         -- and / or
                                    attr_list = {
                                        {
                                            type = 'attribute',
                                            name = 'gangdi_score',
                                            operator = '<=',
                                            op_value = 2,
                                        },
                                    },
                                },
                            },
                            {
                                text = '4分',
                                value = 4,
                                is_valid_expression = {
                                    relational = 'and',         -- and / or
                                    attr_list = {
                                        {
                                            type = 'attribute',
                                            name = 'gangdi_score',
                                            operator = '<=',
                                            op_value = 3,
                                        },
                                    },
                                },
                            },
                            {
                                text = '5分',
                                value = 5,
                                is_valid_expression = {
                                    relational = 'and',         -- and / or
                                    attr_list = {
                                        {
                                            type = 'attribute',
                                            name = 'gangdi_score',
                                            operator = '<=',
                                            op_value = 4,
                                        },
                                    },
                                },
                            },
                        },
                        expression_list = {
                            {
                                relational = 'and',          -- and / or
                                operation = 'invisible',    -- 'reset_value', 'invisible', 'disable'
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'play_mode',
                                        operator = '==',
                                        op_value = 2,
                                    },
                                    {
                                        type = 'expression',
                                        expression = {
                                            relational = 'and',          -- and / or
                                            attr_list = {
                                                {
                                                    type = 'attribute',
                                                    name = 'czkh',
                                                    operator = '==',
                                                    op_value = false,
                                                },
                                                {
                                                    type = 'attribute',
                                                    name = 'ypkh',
                                                    operator = '==',
                                                    op_value = false,
                                                },
                                            },
                                        },
                                    },
                                    --]]
                                },
                            },
                            {
                                relational = 'and',
                                operation = 'reset_value',
                                operation_value = 1,
                                relative_attr_name = 'gangdi_score',
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'gangdi_score',
                                        operator = '>=',
                                        op_value = 0,
                                        op_attr_name = 'zimo_score',
                                    },
                                },
                            },
                            {
                                relational = 'or',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 3,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'play_mode',
                                        operator = '==',
                                        op_value = 1,
                                    },
                                    {
                                        type = 'attribute',
                                        name = 'play_mode',
                                        operator = '==',
                                        op_value = 2,
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
                section_name = '次底',
                attributes = {
                    {
                        attr_name = 'cidi_score',
                        ctrl_type = 'combo_box',
                        init_value = 3,
                        init_text = '3分',
                        options = {
                            { text = '3分', value = 3, },
                            { text = '4分', value = 4, },
                            { text = '5分', value = 5, },
                            { text = '6分', value = 6, },
                            { text = '7分', value = 7, },
                            { text = '8分', value = 8, },
                            { text = '9分', value = 9, },
                            { text = '10分', value = 10, },
                        },
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 10,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'play_mode',
                                        operator = '==',
                                        op_value = 1,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 5,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'play_mode',
                                        operator = '==',
                                        op_value = 2,
                                    },
                                },
                            },
                        },
                    },
                },
            },
            -- col 2
            {
                section_name = '封顶',
                attributes = {
                    {
                        attr_name = 'max_score',
                        ctrl_type = 'combo_box',
                        init_value = 0,
                        init_text = '无封顶',
                        options = {
                            { text = '无封顶', value = 0 },
                            { text = '-30分', value = 30 },
                            { text = '-40分', value = 40 },
                            { text = '-50分', value = 50 },
                            { text = '-60分', value = 60 },
                            { text = '-70分', value = 70 },
                            { text = '-80分', value = 80 },
                            { text = '-90分', value = 90 },
                            { text = '-100分', value = 100 },
                        },
                    },
                },
            },
        },
        layout_config = {
            section_offset_x_2 = 450,
            section_interval = 40,
            combo_box_rb_click_close = true,
        },
    },
}

return new_room_config
