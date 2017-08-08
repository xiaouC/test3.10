-- ./app/platform/room/new_room_settings/20000016.lua
-- 成都麻将

local new_room_config = {
    name = '成都麻将',
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
                        attr_name = 'zmjd_zmjf',
                        ctrl_type = 'radio',
                        init_value = 0,
                        no_amend = true,
                        offset_x = 10,
                        options = {
                            { text = '自摸加底', value = 0, },
                            { text = '自摸加番', value = 1, },
                        },
                        new_line = true,
                    },
                    {
                        attr_name = 'zjmm',
                        ctrl_type = 'check_box',
                        text = '庄家买码',
                        init_value = false,
                        offset_x = 10,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'hdjf',
                        ctrl_type = 'check_box',
                        text = '海底加番',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        attr_name = 'cg_sty',
                        ctrl_type = 'check_box',
                        text = '擦挂、晒太阳',
                        init_value = true,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '海底加番：最后一张牌自摸或者最后打出一张被别人胡了都要加番。\n擦挂：放杠三家出。\n晒太阳：最后没胡牌退杠分。\n庄家买码：开局庄摸最后一张牌盖住，牌局结束翻开这张牌根据牌\n点数定中码玩家。',
                        offset_x = 0,
                        offset_y = 0,
                    },
                },
            },
        },
        {
            {
                section_name = '牌型',
                attributes = {
                    {
                        attr_name = 'jd',
                        ctrl_type = 'check_box',
                        text = '将对',
                        init_value = true,
                        offset_x = 10,
                        offset_y = -10,
                        selected_value = true,
                        unselected_value = false,
                    },
                    {
                        ctrl_type = 'help_button',
                        text = '将对：玩家手上的牌是带二、五、八的对对胡。',
                        offset_x = 0,
                        offset_y = -10,
                        help_offset_x = 320,
                        help_offset_y = -35,
                    },
                },
            },
        },
        {
            {
                section_name = '封顶',
                attributes = {
                    {
                        attr_name = 'fd',
                        ctrl_type = 'radio',
                        init_value = 5,
                        offset_x = 10,
                        options = {
                            { text = '2番', value = 2, },
                            { text = '3番', value = 3, },
                            { text = '4番', value = 4, },
                            { text = '5番', value = 5, },
                        },
                    },
                },
            },
        },
        layout_config = {
            section_offset_x_1 = 10,
            section_offset_y = -40,
            section_interval = 50,
            section_new_line_interval = 20,
        },
    },
}

return new_room_config
