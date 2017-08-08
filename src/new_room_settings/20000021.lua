-- ./app/platform/room/new_room_settings/20000021.lua
-- 斗地主

local new_room_config = {
    name = '斗地主',
    max_count = 3,
    is_poker = true,
    bottom_section = {
        name = '局数：',
        attr_name = 'room_card',
        ctrl_type = 'radio',        -- 控件类型
        init_value = 2,             -- 初始值
        options = {
            { text_1 = '5局', text_2 = 'x1', value = 1, },
            { text_1 = '10局', text_2 = 'x2', value = 2, },
            { text_1 = '15局', text_2 = 'x3', value = 3, },
        },
    },
    top_sections = {
        {
            {
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'nt_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        options = {
                            { text = '地主明牌', value = 1, },
                            { text = '地主加倍', value = 2, },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '地主明牌：地主可明牌，选择明牌\n　　则视为加倍。\n地主加倍：地主不可明牌，在农民\n　　加倍后可选择加倍。',
                        help_offset_x = 260,
                        help_offset_y = -80,
                        new_line = true,
                    },
                    {
                        attr_name = 'take_pair',
                        ctrl_type = 'check_box',
                        text = '可三带一对',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        new_line = true,
                    },
                    {
                        attr_name = 'must_call',
                        ctrl_type = 'check_box',
                        text = '双王或4张2叫满',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '玩家手中有双王或4张2时，\n在轮到他叫分时必叫3分。',
                        help_offset_x = 220,
                        help_offset_y = -50,
                    },
                },
            },
        },
        {
            {
                section_name = '封顶',
                attributes = {
                    {
                        attr_name = 'limit_score',
                        ctrl_type = 'radio',
                        init_value = 0,
                        no_amend = true,
                        options = {
                            { text = '不限', value = 0, },
                            { text = '3炸', value = 3, },
                            { text = '4炸', value = 4, },
                            { text = '5炸', value = 5, },
                        },
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -30,
            section_interval = 120,
            section_attr_offset_x = 20,
            section_new_line_interval = 40,
        },
    },
}

return new_room_config
