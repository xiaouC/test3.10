-- ./app/platform/room/new_room_settings/20000010.lua
-- 滑水麻将

local new_room_config = {
    name = '滑水麻将',
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
                section_name = '风牌',
                attributes = {
                    {
                        attr_name = 'feng',
                        ctrl_type = 'radio',
                        init_value = true,
                        offset_x = 20,
                        options = {
                            { text = '带风', value = true },
                            { text = '不带风', value = false },
                        },
                    },
                },
            },
        },
        {
            {
                section_name = '下鱼',
                attributes = {
                    {
                        attr_name = 'fish_num',
                        ctrl_type = 'radio',
                        init_value = 2,
                        offset_x = 20,
                        options = {
                            { text = '无鱼', value = 0 },
                            { text = '2条', value = 2 },
                            { text = '5条', value = 5 },
                            { text = '8条', value = 8 },
                            { text = '12条', value = 12 },
                        },
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -100,
            section_interval = 50,
        },
    },
}

return new_room_config
