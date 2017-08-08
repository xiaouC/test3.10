-- ./app/platform/room/new_room_settings/20000020.lua
-- 天地牛牛

local new_room_config = {
    name = '天地牛牛',
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
            { text_1 = '30局', text_2 = 'x4', value = 3, },
        },
    },
    top_sections = {
        {
            {
                section_name = '规则',
                attributes = {
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '2人即可开始游戏，最多五人同时游戏。无百变真牌型 > 有百变假牌型，\n同样假牌型比点数，黑桃K最大，小王最小。',
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
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'play_mode',
                        ctrl_type = 'radio',
                        init_value = 1,
                        no_amend = true,
                        options = {
                            { text = '普通', value = 1, },
                            { text = '特殊', value = 2, },
                        },
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '可组特殊牌型：\n五花牛 - 5倍、炸弹 - 8倍、\n五小牛 - 10倍、地炸 - 12倍、天炸 - 16倍\n地炸是A - 10的炸弹+王或A-10的三条+\n双王组成的牌型\n天炸是JQK的炸弹+王或JQK的三条+双\n王组成的牌型。',
                        help_offset_x = 220,
                        help_offset_y = -50,
                    },
                    {
                        attr_name = 'begin_nt',
                        ctrl_type = 'no_ui',
                        init_value = 255,
                    },
                    {
                        attr_name = 'change_nt',
                        ctrl_type = 'no_ui',
                        init_value = 1,
                    },
                    {
                        attr_name = 'giveup_nt',
                        ctrl_type = 'no_ui',
                        init_value = true,
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -50,
            section_interval = 70,
            section_new_line_interval = 40,
        },
    },
}

return new_room_config
