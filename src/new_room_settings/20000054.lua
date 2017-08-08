-- ./app/platform/room/new_room_settings/20000054.lua
-- 沧州麻将

local new_room_config = {
    name = '沧州麻将',
    max_count = 4,
    bottom_section = {
        name = '圈数：',
        attr_name = 'room_card',
        ctrl_type = 'radio',        -- 控件类型
        init_value = 2,             -- 初始值
        options = {
            { text_1 = '1圈', text_2 = 'x1', value = 1, },
            { text_1 = '2圈', text_2 = 'x2', value = 2, },
            { text_1 = '4圈', text_2 = 'x4', value = 4, },
        },
    },
    top_sections = {
        {
            {
                section_name = '规则',
                attributes = {
                    {
                        attr_name = 'rule_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        init_text = '发胡',
                        options = {
                            { text = '点炮单付', value = 0, },
                            { text = '发胡', value = 1, },
                        },
                    },
                },
            },
        },
        {
            {
                section_name = '风牌',
                attributes = {
                    {
                        attr_name = 'wind_mode',
                        ctrl_type = 'check_box',
                        text = '不带风',
                        init_value = 1,
                        selected_value = 0,
                        unselected_value = 1,
                    },
                    {
                        attr_name = 'rule_ssbk',
                        ctrl_type = 'check_box',
                        text = '十三不靠',
                        init_value = 1,
                        selected_value = 1,
                        unselected_value = 0,
                        expression_list = {
                            {
                                relational = 'and',         -- and / or
                                operation = 'reset_value',  -- 'reset_value', 'invisible', 'disable'
                                operation_value = 0,
                                attr_list = {
                                    {
                                        type = 'attribute',
                                        name = 'wind_mode',
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
                                        name = 'wind_mode',
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
        layout_config = {
            section_interval = 100,
            section_offset_y = -80,
        },
    },
}

return new_room_config
