-- ./app/platform/room/new_room_settings/20000017.lua
-- 白板变

local new_room_config = {
    name = '白板变',
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
                        attr_name = 'hu_qxd',
                        ctrl_type = 'check_box',
                        text = '七对',
                        init_value = 1,
                        offset_y = -10,
                        selected_value = 1,
                        unselected_value = 0,
                    },
                    {
                        attr_name = 'all_award_ma',
                        ctrl_type = 'check_box',
                        text = '四白板全码',
                        init_value = 1,
                        offset_y = -10,
                        selected_value = 1,
                        unselected_value = 0,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '手牌中有4张白板时，立即胡牌，且牌\n墙中未摸起的牌都为奖码，其中有1、\n5、9的牌都为中码(白板算1)。',
                        offset_x = 0,
                        offset_y = -10,
                        help_offset_x = 280,
                        help_offset_y = -60,
                    },
                },
            },
        },
        {
            {
                section_name = '奖码',
                attributes = {
                    {
                        attr_name = 'jiang_ma',
                        ctrl_type = 'radio',
                        init_value = -2,
                        offset_x = 10,
                        options = {
                            { text = '2码', value = 2, },
                            { text = '4码', value = 4, },
                            { text = '6码', value = 6, },
                            { text = '一码全中', value = -1, },
                            { text = '一张定码', value = -2, },
                        },
                    },
                    {
                        attr_name = 'award_ma',
                        ctrl_type = 'no_ui',
                        init_value = 0,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                relative_attr_name = 'jiang_ma',
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'jiang_ma',
                                        operator = '~=',
                                        op_value = -1,
                                    },
                                    {
                                        type = 'attribute',
                                        name = 'jiang_ma',
                                        operator = '~=',
                                        op_value = -2,
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
                                        name = 'jiang_ma',
                                        operator = '==',
                                        op_value = -1,
                                    },
                                    {
                                        type = 'attribute',
                                        name = 'jiang_ma',
                                        operator = '==',
                                        op_value = -2,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'card_award_ma',
                        ctrl_type = 'no_ui',
                        init_value = 1,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 2,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'jiang_ma',
                                        operator = '==',
                                        op_value = -1,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 1,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'jiang_ma',
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
                                        name = 'jiang_ma',
                                        operator = '~=',
                                        op_value = -2,
                                    },
                                    {
                                        type = 'attribute',
                                        name = 'jiang_ma',
                                        operator = '~=',
                                        op_value = -1,
                                    },
                                },
                            },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '胡牌后翻开牌墙中最后一张牌，根据翻出牌的点数确定中码数，\n例如翻到9万，则计为中9码。\n【一码全中】：结算分：2+中码数，白板计为10码。\n【一张定吗】结算分：2+2*中码数，白板计为12码。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                },
            },
        },
        {
            {
                section_name = '无鬼',
                attributes = {
                    {
                        attr_name = 'hongaward_ma',
                        ctrl_type = 'radio',
                        init_value = 0,
                        options = {
                            { text = '不加码', value = 0, },
                            { text = '加1码', value = 1, },
                            { text = '加2码', value = 2, },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '游戏中，白板是万能牌，如果胡牌时\n手牌中没有白板，在奖码环节可选\n择是否额外奖码张数。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                },
            },
        },
        layout_config = {
            section_offset_x_1 = 10,
            section_offset_y = -50,
            section_interval = 50,
            section_new_line_interval = 20,
        },
    },
}

return new_room_config
