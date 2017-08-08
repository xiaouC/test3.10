-- ./app/platform/room/new_room_settings/20000009.lua
-- 红中宝

local new_room_config = {
    name = '红中宝',
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
                section_name = '规则',
                attributes = {
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '2人即可开始游戏，最多4人同时游戏。2人游戏时无万字牌。',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 26,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    },
                },
            },
        },
        -- row 2
        {
            -- col 1
            {
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'can_zhuac',
                        ctrl_type = 'check_box',
                        text = '接炮胡',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'can_multi_zhuac',
                        ctrl_type = 'check_box',
                        text = '一炮多响　',
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
                                        name = 'can_zhuac',
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
                                        name = 'can_zhuac',
                                        operator = '==',
                                        op_value = false,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'can_qgh',
                        ctrl_type = 'check_box',
                        text = '抢杠胡',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '如果你已经听牌，其他人补杠你胡的牌\n你和其他人可以同时抢杠胡',
                        offset_x = 0,
                        offset_y = 0,
                        new_line = true,        -- new line
                    },
                    {
                        attr_name = 'hu_qxd',
                        ctrl_type = 'check_box',
                        text = '七　对',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'all_award_ma',
                        ctrl_type = 'check_box',
                        text = '四红中全码',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '手牌中有4张红中时立即胡牌，\n且牌墙中未摸起的牌都为奖码，\n其中有1、5、9的牌都为中码。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                },
            },
        },
        -- row 3
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
                            { text = '2码', value = 2, },
                            { text = '4码', value = 4, },
                            { text = '6码', value = 6, },
                            { text = '8码', value = 8, },
                            { text = '10码', value = 10, },
                            { text = '一张定码', value = 11, },
                            { text = '一码全中', value = 12, },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '【奖码玩法】胡牌后从牌墙最后翻起约定\n张数的牌作为奖码，每张带有1、5、9及\n红中都为中码，每中一码胡牌分+2。\n【一张定码】胡牌后翻开牌墙中的最后一\n张牌，该牌的点数即为中码数，如翻到红\n中则中12码。\n【一码全中】牌局结束，有人胡牌，从牌\n墙尾墩摸一张牌，翻开是序数牌则算胡牌\n玩家中该序数牌的码，若翻开是红中则算\n玩家中10码。一个码算1分。',
                        offset_x = -300,
                        offset_y = -150,
                    },
                },
            },
        },
        -- row 4
        {
            -- col 1
            {
                section_name = '无鬼',
                attributes = {
                    {
                        attr_name = 'hongaward_ma',
                        ctrl_type = 'radio',
                        init_value = 0,
                        init_text = '不加码',
                        options = {
                            { text = '不加码', value = 0 },
                            {
                                text = '加 1 码',
                                value = 1,
                                expression_list = {
                                    {
                                        relational = 'or',       -- and / or
                                        operation = 'disable',    -- 'reset_value', 'invisible', 'disable'
                                        attr_list = {
                                            {
                                                type = 'attribute',
                                                name = 'award_ma',
                                                operator = '==',
                                                op_value = 11,
                                            },
                                            {
                                                type = 'attribute',
                                                name = 'award_ma',
                                                operator = '==',
                                                op_value = 12,
                                            },
                                        },
                                    },
                                },
                            },
                            {
                                text = '加 2 码',
                                value = 2,
                                expression_list = {
                                    {
                                        relational = 'or',       -- and / or
                                        operation = 'disable',    -- 'reset_value', 'invisible', 'disable'
                                        attr_list = {
                                            {
                                                type = 'attribute',
                                                name = 'award_ma',
                                                operator = '==',
                                                op_value = 11,
                                            },
                                            {
                                                type = 'attribute',
                                                name = 'award_ma',
                                                operator = '==',
                                                op_value = 12,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        expression_list = {
                            {
                                relational = 'or',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 0,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'award_ma',
                                        operator = '==',
                                        op_value = 11,
                                    },
                                    {
                                        type = 'attribute',
                                        name = 'award_ma',
                                        operator = '==',
                                        op_value = 12,
                                    },
                                },
                            },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '游戏中红中是万能牌，如果胡\n牌时手牌中没有红中，在奖码\n环节可选择是否额外奖励奖码\n张数。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                },
            },
        },
        layout_config = {
            section_interval = 30,
        },
    },
}

return new_room_config
