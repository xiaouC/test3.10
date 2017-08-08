-- ./app/platform/room/new_room_settings/20000025.lua
-- 跑得快

local new_room_config = {
    name = '跑得快',
    max_count = 5,
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
                section_name = '人数',
                attributes = {
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '2人即可开始游戏，最多3人同时游戏。',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 36,
                        enable_bold = true,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    },
                },
            },
        },
        {
            {
                section_name = '手牌',
                attributes = {
                    {
                        attr_name = 'bHandlCard',
                        ctrl_type = 'radio',
                        init_value = false,
                        options = {
                            { text = '15张', value = false, },
                            { text = '16张', value = true, },
                        },
                    },
                    {
                        attr_name = 'bShowCardCount',
                        ctrl_type = 'check_box',
                        text = '显示手牌数量',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'bHongTaoDouble',
                        ctrl_type = 'check_box',
                        text = '红桃10加倍',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        {
            {
                section_name = '玩法',
                attributes = {
                    {
                        attr_name = 'bHaveKing',
                        ctrl_type = 'radio',
                        init_value = false,
                        no_amend = true,
                        options = {
                            { text = '无赖子', value = false, },
                            { text = '有赖子', value = true, },
                        },
                    },
                    {
                        attr_name = 'bHeiTaoFirst',
                        ctrl_type = 'check_box',
                        text = '首局先出黑桃3',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'bMustOutBiggest',
                        ctrl_type = 'check_box',
                        text = '剩一张必出最大',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                        new_line = true,
                    },
                    {
                        attr_name = 'bPullBomb',
                        ctrl_type = 'check_box',
                        text = '炸弹不可拆',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'bCanThreeAndNull',
                        ctrl_type = 'check_box',
                        text = '可三不带',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'bCanThreeAndOne',
                        ctrl_type = 'check_box',
                        text = '可三带一',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '勾选可三带一，则可在游戏中\n打出三带一。不必非得是最后一\n手才打出。',
                        offset_x = -10,
                        new_line = true,
                    },
                    {
                        attr_name = 'bCanFourAndOne',
                        ctrl_type = 'check_box',
                        text = '可四带一　　',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'bCanFourAndTwo',
                        ctrl_type = 'check_box',
                        text = '可四带二',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'bCanFourAndThree',
                        ctrl_type = 'check_box',
                        text = '可四带三',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                },
            },
        },
        layout_config = {
            section_interval = 30,
            section_new_line_interval = 25,
        },
    },
}

return new_room_config
