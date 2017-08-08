-- ./app/platform/room/new_room_settings/20000044.lua
-- 赣州麻将

local new_room_config = {
    name = '赣州麻将',
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
        -- row 1
        {
            -- col 1
            {
                section_name = '玩法',
                -- 可能有很多属性，也可以只有一个
                attributes = {
                    {
                        attr_name = 'sxf',
                        ctrl_type = 'radio',    -- 控件类型
                        init_value = 1,             -- 初始值
                        options = {
                            { text = '上下翻', value = 1, },
                            { text = '上下左右翻', value = 0, },
                        },
                        no_amend = true,
                        new_line = true,
                    },
                    {
                        attr_name = 'jpj',
                        ctrl_type = 'radio',    -- 控件类型
                        init_value = 1,             -- 初始值
                        options = {
                            { text = '精必钩', value = 1, },
                            { text = '有精点炮不能平胡', value = 0, },
                        },
                        no_amend = true,
                    },
                },
            },
            -- col 2
            {
                section_name = '霸王',
                attributes = {
                    {
                        attr_name = 'bawang',
                        ctrl_type = 'radio',
                        init_value = 1,
                        options = {
                            { text = '霸王精x2', value = 1, },
                            { text = '霸王精+10', value = 2, },
                        },
                        no_amend = true,
                    },
                },
            },
        },
        -- row 2
        {
            -- col 1
            {
                section_name = '庄家',
                attributes = {
                    {
                        attr_name = 'tongz',
                        ctrl_type = 'radio',
                        init_value = 1,
                        options = {
                            { text = '通庄', value = 1, },
                            { text = '分庄闲', value = 0, },
                        },
                        no_amend = true,
                    },
                },
            },
        },
        -- row 3
        {
            -- col 1
            {
                section_name = '底分',
                attributes = {
                    {
                        attr_name = 'basic_score',
                        ctrl_type = 'radio',
                        init_value = 1,
                        options = {
                            { text = '底分1分', value = 1, },
                            { text = '底分2分', value = 2, },
                        },
                        no_amend = true,
                    },
                },
            },
        },
        layout_config = {
            section_offset_x_2 = 400,
            section_interval = 40,
            section_offset_y = -20,
            section_attr_interval = 40,
            section_new_line_interval = 15,
        },
    },
}

return new_room_config
