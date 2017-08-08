-- ./app/platform/room/new_room_settings/20000002.lua
-- 五人牛牛

local new_room_config = {
    name = '五人牛牛',
    max_count = 5,
    is_poker = true,
    bottom_section = {
        name = '局数：',
        attr_name = 'room_card',
        ctrl_type = 'radio',        -- 控件类型
        init_value = 2,             -- 初始值
        options = {
            { text_1 = '10局', text_2 = 'x1', value = 1, },
            { text_1 = '20局', text_2 = 'x2', value = 2, },
            { text_1 = '30局', text_2 = 'x3', value = 3, },
        },
    },
    top_sections = {
        {
            {
                section_name = '人数',
                attributes = {
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '2人即可开始游戏，最多5人同时游戏。',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 26,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    },
                    {
                        ctrl_type = 'no_ui',
                        attr_name = 'game_player',
                        init_value = 5,
                    },
                    {
                        ctrl_type = 'no_ui',
                        attr_name = 'begin_nt',
                        init_value = 255,
                    },
                },
            },
        },
        {
            {
                section_name = '换庄',
                attributes = {
                    {
                        attr_name = 'change_nt',
                        ctrl_type = 'radio',
                        init_value = 1,
                        init_text = '牛九换庄',
                        options = {
                            { text = '牛九换庄', value = 1, },
                            { text = '牛牛换庄', value = 2, },
                            { text = '轮庄', value = 3, },
                        },
                    },
                },
            },
        },
        {
            {
                section_name = '可选',
                attributes = {
                    {
                        attr_name = 'wuhuaniu',
                        ctrl_type = 'check_box',
                        text = '五花牛(5倍)',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'sizha',
                        ctrl_type = 'check_box',
                        text = '四炸(8倍)',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'wuxiaoniu',
                        ctrl_type = 'check_box',
                        text = '五小牛(10倍)',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        {
            {
                section_name = '王牌',
                attributes = {
                    {
                        attr_name = 'king_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        init_text = '无王牌',
                        options = {
                            { text = '无王牌', value = 1, },
                            { text = '王当十', value = 2, },
                            { text = '王当百', value = 3, },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '大小王可以百变为任何牌来组成牌型，当同\n样牌型比牌时，有王组成的牌型更大。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                },
            },
        },
        -- row 4
        {
            -- col 1
            {
                section_name = '闲家',
                attributes = {
                    {
                        attr_name = 'other_mode',
                        ctrl_type = 'radio',
                        init_value = 2,
                        init_text = '可买两手牌',
                        options = {
                            { text = '只买一手牌', value = 1 },
                            { text = '可买两手牌', value = 2 },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '闲家可以选择买一手或两手牌。\n选择两手牌时，会分别和庄家比\n较大小。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                    {
                        attr_name = 'upscore',
                        ctrl_type = 'check_box',
                        text = '升分',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'threescore',
                        ctrl_type = 'check_box',
                        text = '3分模式',
                        init_value = false,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        layout_config = {
            section_interval = 10,
        },
    },
}

return new_room_config
