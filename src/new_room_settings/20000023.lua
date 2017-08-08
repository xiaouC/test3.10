-- ./app/platform/room/new_room_settings/20000023.lua
-- 河南麻将

local new_room_config = {
    name = '河南麻将',
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
                        text = '可3-4人游戏，3人游戏必须258做将，4人游戏无须258做将。',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 26,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    },
                    {
                        attr_name = 'game_player',
                        ctrl_type = 'no_ui',
                        init_value = 4,
                    },
                },
            },
        },
        {
            {
                section_name = '字牌',
                attributes = {
                    {
                        attr_name = 'daizi',
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
                        attr_name = 'gangpao',
                        ctrl_type = 'check_box',
                        text = '杠跑',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'gao_zhuang',
                        ctrl_type = 'check_box',
                        text = '高庄',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'qiduidouble',
                        ctrl_type = 'check_box',
                        text = '七对加倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'gangkaidouble',
                        ctrl_type = 'check_box',
                        text = '杠开加倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'sihun_double',
                        ctrl_type = 'check_box',
                        text = '四混加倍',
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
                                        name = 'other_mode',
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
                                        name = 'other_mode',
                                        operator = '==',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                        new_line = true,
                    },
                    {
                        attr_name = 'mengqing',
                        ctrl_type = 'check_box',
                        text = '门清',
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
                                        name = 'other_mode',
                                        operator = '~=',
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
                                        name = 'other_mode',
                                        operator = '~=',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'quemen',
                        ctrl_type = 'check_box',
                        text = '缺门',
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
                                        name = 'other_mode',
                                        operator = '~=',
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
                                        name = 'other_mode',
                                        operator = '~=',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'dumen',
                        ctrl_type = 'check_box',
                        text = '独门',
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
                                        name = 'other_mode',
                                        operator = '~=',
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
                                        name = 'other_mode',
                                        operator = '~=',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'dianpai',
                        ctrl_type = 'check_box',
                        text = '点炮',
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
                                        name = 'other_mode',
                                        operator = '~=',
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
                                        name = 'other_mode',
                                        operator = '~=',
                                        op_value = 0,
                                    },
                                },
                            },
                        },
                    },
                    {
                        attr_name = 'yipaodx',
                        ctrl_type = 'check_box',
                        text = '一炮多响',
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
                                        name = 'dianpai',
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
                                        name = 'dianpai',
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
                section_name = '混牌',
                attributes = {
                    {
                        attr_name = 'other_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        options = {
                            { text = '无混', value = 0, },
                            { text = '原混', value = 1, },
                            { text = '上混', value = 2, },
                            { text = '下混', value = 3, },
                        },
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
