-- ./app/platform/room/new_room_settings/20000015.lua
-- 天津麻将

local new_room_config = {
    name = '天津麻将',
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
                section_name = '规则',
                attributes = {
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '3-4人都可游戏，完三人拐末时，4张混牌，没有字牌，没有跟庄',
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
        {
            {
                section_name = '起胡',
                attributes = {
                    {
                        attr_name = 'qh',
                        ctrl_type = 'radio',
                        init_value = 1,
                        options = {
                            { text = '刮大风', value = 1, },
                            { text = '2番', value = 2, },
                            { text = '3番', value = 3, },
                        },
                    },
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '刮大风，3番起胡，素的胡牌为4番',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 26,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 10,
                        text_offset_y = -10,
                        new_line = true,
                    },
                    {
                        attr_name = 'qihu',
                        ctrl_type = 'no_ui',
                        init_value = 3,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 3,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'qh',
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
                                        name = 'qh',
                                        operator = '==',
                                        op_value = 2,
                                    },
                                },
                            },
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 3,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'qh',
                                        operator = '==',
                                        op_value = 3,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'gdf',
                        ctrl_type = 'no_ui',
                        init_value = true,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = true,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'qh',
                                        operator = '==',
                                        op_value = 1,
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
                                        name = 'qh',
                                        operator = '~=',
                                        op_value = 1,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'khsd',
                        ctrl_type = 'check_box',
                        text = '可胡素的',
                        init_value = false,
                        offset_x = 15,
                        selected_value = true,
                        unselected_value = false,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'disable',  -- 'reset_value', 'invisible', 'disable'
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'qh',
                                        operator = '~=',
                                        op_value = 3,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'khgk',
                        ctrl_type = 'check_box',
                        text = '可胡杠开',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'disable',  -- 'reset_value', 'invisible', 'disable'
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'qh',
                                        operator = '~=',
                                        op_value = 3,
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
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'lwf',
                        ctrl_type = 'check_box',
                        text = '龙伍番',
                        init_value = true,
                        offset_y = -10,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '勾选则龙按5倍底分算，捉伍按4倍底分',
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
        layout_config = {
            section_offset_x_1 = 10,
            section_offset_y = -20,
            section_interval = 60,
            section_new_line_interval = 15,
        },
    },
}

return new_room_config
