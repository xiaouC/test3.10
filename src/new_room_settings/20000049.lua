-- ./app/platform/room/new_room_settings/20000049.lua
-- 十三水

local new_room_config = {
    name = '十三水',
    max_count = 7,
    is_poker = true,
    bottom_section = {
        name = '局数：',
        attr_name = 'room_card',
        ctrl_type = 'radio',        -- 控件类型
        init_value = 2,             -- 初始值
        options = {
            { text_1 = '6局', text_2 = 'x1', value = 1, },
            { text_1 = '12局', text_2 = 'x2', value = 2, },
            { text_1 = '18局', text_2 = 'x3', value = 3, },
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
                        text = '可2-7人游戏',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 35,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    }
                },
            },
        },
        -- row 2
        {
            -- col 1
            {
                section_name = '比牌',
                attributes = {
                    {
                        attr_name = 'play_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        options = {
                            { text = '通比模式', value = 1, },
                            { text = '庄家模式', value = 2, },
                        },
                    },
                },
            },
        },
        -- row 3
        {
            -- col 1
            {
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'dys',
                        ctrl_type = 'check_box',
                        text = '多一色',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'wbb',
                        ctrl_type = 'check_box',
                        text = '王百变',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        -- row 4
        {
            -- col 1
            {
                section_name = '报道',
                attributes = {
                    {
                        attr_name = 'wtbd',
                        ctrl_type = 'check_box',
                        text = '炸弹五条可报道',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'thbd',
                        ctrl_type = 'check_box',
                        text = '同花顺可报道',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        layout_config = {
            section_interval = 40,
        },
    },
}

return new_room_config
