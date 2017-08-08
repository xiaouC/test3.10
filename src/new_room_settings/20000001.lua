-- ./app/platform/room/new_room_settings/20000001.lua
-- 红中麻将

local new_room_config = {
    name = '红中麻将',
    max_count = 4,
    is_poker = false,
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
                        attr_name = 'allow_zp',
                        ctrl_type = 'check_box',
                        text = '无红中可抓炮',
                        init_value = 1,
                        selected_value = 1,
                        unselected_value = 0,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '勾选了此玩法，则只有手中无红中\n时，才可抓炮或抢杠胡。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                    {
                        attr_name = 'hu_qxd',
                        ctrl_type = 'check_box',
                        text = '七对',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'all_award_ma',
                        ctrl_type = 'check_box',
                        text = '四红中全码',
                        init_value = 1,
                        selected_value = 1,
                        unselected_value = 0,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '手牌中有4张红中时立即胡牌，且\n牌墙中未摸起的牌都为奖码，其中\n有1、5、9的牌都为中码。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                },
            },
        },
        -- row 2
        {
            -- col 1
            {
                section_name = '扎码',
                attributes = {
                    {
                        attr_name = 'zhama',
                        ctrl_type = 'radio',
                        init_value = -2,
                        init_text = '一张定码',
                        options = {
                            { text = '2码', value = 2 },
                            { text = '4码', value = 4 },
                            { text = '6码', value = 6 },
                            { text = '一码全中', value = -1 },
                            { text = '一张定码', value = -2 },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '胡牌后，翻开牌墩中最后一张牌\n翻出牌的点数即为中码数\n风牌则中4码，鬼牌则中12码。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                    {
                        attr_name = 'card_award_ma',
                        ctrl_type = 'no_ui',
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 1,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'zhama',
                                        operator = '==',
                                        op_value = -1,
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
                                        name = 'zhama',
                                        operator = '==',
                                        op_value = -2,
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
                                        name = 'zhama',
                                        operator = '~=',
                                        op_value = -2,
                                    },
                                    {
                                        type = 'attribute',
                                        name = 'zhama',
                                        operator = '~=',
                                        op_value = -1,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'award_ma',
                        ctrl_type = 'no_ui',
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                relative_attr_name = 'zhama',
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'zhama',
                                        operator = '~=',
                                        op_value = -2,
                                    },
                                    {
                                        type = 'attribute',
                                        name = 'zhama',
                                        operator = '~=',
                                        op_value = -1,
                                    },
                                },
                            },
                            {
                                relational = 'or',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 0,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'zhama',
                                        operator = '==',
                                        op_value = -2,
                                    },
                                    {
                                        type = 'attribute',
                                        name = 'zhama',
                                        operator = '==',
                                        op_value = -1,
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
            {
                section_name = '无鬼',
                attributes = {
                    {
                        attr_name = 'hongaward_ma',
                        ctrl_type = 'radio',
                        init_value = 0,
                        init_text = '不加码',
                        options = {
                            { text = '不加码', value = 0, },
                            { text = '加1码', value = 1, },
                            { text = '加2码', value = 2, },
                        },
                    },
                },
            },
        },       
        layout_config = {
            section_offset_x_1 = 50,
            section_offset_y = -60,
            section_interval = 50,
        },
    },
}

return new_room_config
