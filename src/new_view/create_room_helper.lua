-- ./app/platform/room/new_view/create_room_helper.lua

local default_layout_config = setmetatable({
    section_offset_x_1 = 50,
    section_offset_x_2 = 450,
    section_offset_y = 0,
    section_interval = 20,
    section_background = 'section_bg.png',
    section_background_res_type = ccui.TextureResType.plistType,
    section_attr_offset_x = 0,
    section_attr_interval = 20,
    section_new_line_interval = 5,

    bottom_section_radio_normal = 'rb_normal.png',
    bottom_section_radio_selected = 'rb_selected.png',
    bottom_section_radio_normal_disable = 'rb_normal_disable.png',
    bottom_section_radio_selected_disable = 'rb_selected_disable.png',
    bottom_section_radio_tex_res_type = ccui.TextureResType.plistType,
    bottom_section_radio_text_color_normal = cc.c3b(76, 35, 24),
    bottom_section_radio_text_color_selected = cc.c3b(189, 23, 23),

    radio_offset_x = 0,
    radio_width = 36,
    radio_height = 36,
    radio_text_height = 30,
    radio_normal = 'rb_normal.png',
    radio_selected = 'rb_selected.png',
    radio_normal_disable = 'rb_normal_disable.png',
    radio_selected_disable = 'rb_selected_disable.png',
    radio_tex_res_type = ccui.TextureResType.plistType,
    radio_text_font_name = 'font/fzzyjt.ttf',
    radio_text_font_size = 20,
    radio_link_res = 'rb_link.png',
    radio_link_res_type = ccui.TextureResType.plistType,
    radio_link_width = 120,
    radio_text_color_normal = cc.c3b(76, 35, 24),
    radio_text_color_selected = cc.c3b(189, 23, 23),

    check_box_background = 'cb_background.png',
    check_box_background_disable = 'cb_background_disable.png',
    check_box_cross = 'cb_cross.png',
    check_box_cross_disable = 'cb_cross_disable.png',
    check_box_res_type = ccui.TextureResType.plistType,
    check_box_text_font_name = 'font/fzzyjt.ttf',
    check_box_text_font_size = 20,
    check_box_text_color_normal = cc.c3b(76, 35, 24),
    check_box_text_color_selected = cc.c3b(189, 23, 23),

    combo_box_background = 'combo_box.png',
    combo_box_background_res_type = ccui.TextureResType.plistType,
    combo_box_per_column_width = 226,
    combo_box_per_row_height = 85,
    combo_box_text_color = cc.WHITE,
    combo_box_layer_color = cc.c4b(0, 0, 0, 0),
    combo_box_arrow_1 = 'combo_box_arrow_1.png',
    combo_box_arrow_2 = 'combo_box_arrow_2.png',
    combo_box_arrow_res_type = ccui.TextureResType.plistType,
    combo_box_arrow_offset_x = -8,
    combo_box_arrow_offset_y = 3,
    combo_box_text_font_name = 'font/fzzyjt.ttf',
    combo_box_text_font_size = 25,
    combo_box_scale_9_sprite = 'combo_box_background.png',
    combo_box_scale_9_res_type = ccui.TextureResType.plistType,
    combo_box_scale_9_rect = cc.rect(0, 0, 40, 40),
    combo_box_scale_9_cap_insets = cc.rect(10, 10, 20, 20),
    combo_box_rb_normal = 'combo_box_unchecked.png',
    combo_box_rb_selected = 'combo_box_checked.png',
    combo_box_rb_res_type = ccui.TextureResType.plistType,
    combo_box_rb_font_name = 'font/fzzyjt.ttf',
    combo_box_rb_font_size = 30,
    combo_box_rb_text_color = cc.BLACK,
    combo_box_rb_click_close = false,

    help_button_normal = 'hall_res/common/help_button.png',
    help_button_selected = '',
    help_button_disable = '',
    help_button_res_type = ccui.TextureResType.localType,
    help_button_layer_color = cc.c4b(0, 0, 0, 0),
    help_button_scale_9_sprite = 'help_bg.png',
    help_button_scale_9_res_type = ccui.TextureResType.plistType,
    help_button_scale_9_rect = cc.rect(0, 0, 29, 32),
    help_button_scale_9_cap_insets = cc.rect(10, 10, 10, 10),
}, {
    __newindex = function(t, k, v) error("attempt to update a read-only table!") end
})

local function check_value(operator, op_value, value)
    local all_operators = {
        ['>'] = function() return value > op_value end,
        ['<'] = function() return value < op_value end,
        ['=='] = function() return value == op_value end,
        ['>='] = function() return value >= op_value end,
        ['<='] = function() return value <= op_value end,
        ['~='] = function() return value ~= op_value end,
    }

    return all_operators[operator]()
end

local function __create_label_control__(attr_info, section_layout_config, view_self, visible_callback)
    local label_node = cc.Node:create()
    label_node:setVisible(not attr_info.init_invisible)

    local text_label = cc.Label:createWithTTF(attr_info.text, attr_info.font_name or 'font/fzzyjt.ttf', attr_info.font_size or 30)
    local text_size = text_label:getContentSize()
    text_label:setAnchorPoint(0.5, 0.5)
    if attr_info.enable_bold then text_label:enableBold() end
    text_label:setPosition(text_size.width * 0.5 + attr_info.text_offset_x, -text_size.height * 0.5 + attr_info.text_offset_y)
    text_label:setColor(attr_info.text_color or cc.WHITE)
    label_node:addChild(text_label)

    label_node:setContentSize(text_size)

    return label_node
end

local function __create_radio_attribute_control__(attr_info, section_layout_config, view_self, visible_callback)
    local rb_group = ccui.RadioButtonGroup:create()
    rb_group:setVisible(not attr_info.init_invisible)
    rb_group:setEnabled(not attr_info.init_disable)
    rb_group:setAnchorPoint(0, 0)

    local offset_x = section_layout_config.radio_offset_x
    local height = section_layout_config.radio_height + section_layout_config.radio_text_height

    local rb_text_label, value_to_rb = {}, {}
    local rb_init_selected = nil
    local rb_normal, rb_selected = section_layout_config.radio_normal, section_layout_config.radio_selected
    local rb_normal_disable, rb_selected_disable = section_layout_config.radio_normal_disable, section_layout_config.radio_selected_disable
    for index, option_info in ipairs(attr_info.options) do
        local rb = ccui.RadioButton:create(rb_normal, rb_normal, rb_selected, rb_normal_disable, rb_selected_disable, section_layout_config.radio_tex_res_type)
        rb_group:addChild(rb)
        rb_group:addRadioButton(rb)

        local text_label = cc.Label:createWithTTF(option_info.text, section_layout_config.radio_text_font_name, section_layout_config.radio_text_font_size)
        text_label:setAnchorPoint(0.5, 0.5)
        text_label:enableBold()
        rb_group:addChild(text_label)

        rb_text_label[rb] = text_label
        value_to_rb[option_info.value] = rb

        rb:addEventListener(function(rb_self, event_type)
            if event_type ~= ccui.RadioButtonEventType.selected then return end
            view_self:updateCreateAttribute(attr_info.attr_name, option_info.value)
        end)

        -- 
        local rb_width, rb_height = section_layout_config.radio_width, section_layout_config.radio_height
        if index == 1 and not attr_info.no_amend then
            local text_width = text_label:getContentSize().width
            if text_width > rb_width then rb_width = text_width end
        end

        local x = offset_x + rb_width * 0.5
        rb:setPosition(x, -rb_height * 0.5)
        text_label:setPosition(x, -(rb_height + section_layout_config.radio_text_height * 0.5))

        -- 
        if index ~= #attr_info.options then
            local link_sprite = createSpriteWithName(section_layout_config.radio_link_res, section_layout_config.radio_link_res_type)
            link_sprite:setAnchorPoint(0, 0.5)
            link_sprite:setPosition(x, -rb_height * 0.5)
            rb_group:addChild(link_sprite, -1)

            local link_width = attr_info.link_width or section_layout_config.radio_link_width
            local scale_x = link_width / 105.0      -- 105 是这张图的实际宽度
            link_sprite:setScaleX(scale_x)

            offset_x = x - section_layout_config.radio_width * 0.5 + link_width
        else
            offset_x = offset_x + rb_width
        end

        -- expression_list
        for _, v in ipairs(option_info.expression_list or {}) do
            view_self:listenExpressionAttributes(v, function(result)
                rb:setEnabled(not result)
            end, v.operation == 'reset_value' and 1 or 0)
        end

        -- 
        if option_info.value == attr_info.init_value then rb_init_selected = rb end
    end

    rb_group:addEventListener(function(rb_selected, index, event_type)
        for rb, text_label in pairs(rb_text_label) do
            text_label:setColor(rb_selected == rb and section_layout_config.radio_text_color_selected or section_layout_config.radio_text_color_normal)
        end
    end)

    -- listen expression list
    local expression_operation = {
        ['reset_value'] = function(v, result)
            if result then
                local operation_value = v.operation_value
                if v.relative_attr_name then
                    operation_value = view_self.create_attributes[v.relative_attr_name]
                    if v.operation_value then operation_value = operation_value + v.operation_value end
                end
                rb_group:setSelectedButton(value_to_rb[operation_value])
                view_self:updateCreateAttribute(attr_info.attr_name, operation_value)
            end
        end,
        ['invisible'] = function(v, result)
            rb_group:setVisible(not result)
            if visible_callback then visible_callback() end
        end,
        ['disable'] = function(v, result)
            rb_group:setEnabled(not result)
            for rb, text_label in pairs(rb_text_label) do
                rb:setEnabled(not result)
            end
        end,
    }

    -- expression_list
    for _, v in ipairs(attr_info.expression_list or {}) do
        view_self:listenExpressionAttributes(v, function(result)
            expression_operation[v.operation](v, result)
        end, v.operation == 'reset_value' and 1 or 0)
    end

    --
    rb_group:setContentSize(cc.size(offset_x, height))
    rb_group:setSelectedButton(rb_init_selected)

    return rb_group
end

local function __create_check_box_attribute_control__(attr_info, section_layout_config, view_self, visible_callback)
    local cb_node = cc.Node:create()
    cb_node:setVisible(not attr_info.init_invisible)

    local cb_background, cb_cross = section_layout_config.check_box_background, section_layout_config.check_box_cross
    local cb_background_disable, cb_cross_disable = section_layout_config.check_box_background_disable, section_layout_config.check_box_cross_disable
    local cb = ccui.CheckBox:create(cb_background, cb_background, cb_cross, cb_background_disable, cb_cross_disable, section_layout_config.check_box_res_type)
    local cb_size = cb:getContentSize()
    cb:setEnabled(not attr_info.init_disable)
    cb:setPosition(cb_size.width * 0.5, -cb_size.height * 0.5)
    cb_node:addChild(cb)

    local text_label = cc.Label:createWithTTF(attr_info.text, section_layout_config.check_box_text_font_name, section_layout_config.check_box_text_font_size)
    local text_size = text_label:getContentSize()
    text_label:setAnchorPoint(0.5, 0.5)
    text_label:enableBold()
    text_label:setPosition(cb_size.width + text_size.width * 0.5, -cb_size.height * 0.5)
    cb_node:addChild(text_label)

    -- 
    cb:addEventListener(function(_, event_type)
        if ccui.CheckBoxEventType.selected == event_type then
            view_self:updateCreateAttribute(attr_info.attr_name, attr_info.selected_value)
            text_label:setColor(section_layout_config.check_box_text_color_selected)
        else
            view_self:updateCreateAttribute(attr_info.attr_name, attr_info.unselected_value)
            text_label:setColor(section_layout_config.check_box_text_color_normal)
        end
    end)
    cb:setSelected(attr_info.init_value == attr_info.selected_value)
    text_label:setColor(attr_info.init_value == attr_info.selected_value and section_layout_config.check_box_text_color_selected or section_layout_config.check_box_text_color_normal)

    -- listen expression list
    local expression_operation = {
        ['reset_value'] = function(v, result)
            if result then
                local operation_value = v.operation_value
                if v.relative_attr_name then
                    operation_value = view_self.create_attributes[v.relative_attr_name]
                    if v.operation_value then operation_value = operation_value + v.operation_value end
                end

                cb:setSelected(attr_info.selected_value == operation_value)
                text_label:setColor(operation_value and section_layout_config.check_box_text_color_selected or section_layout_config.check_box_text_color_normal)
                view_self:updateCreateAttribute(attr_info.attr_name, operation_value)
            end
        end,
        ['invisible'] = function(v, result)
            cb_node:setVisible(not result)
            if visible_callback then visible_callback() end
        end,
        ['disable'] = function(v, result) cb:setEnabled(not result) end,
    }

    -- expression_list
    for _, v in ipairs(attr_info.expression_list or {}) do
        view_self:listenExpressionAttributes(v, function(result)
            expression_operation[v.operation](v, result)
        end, v.operation == 'reset_value' and 1 or 0)
    end

    -- 
    local width = attr_info.width or cb_size.width + text_size.width
    cb_node:setContentSize(cc.size(width, cb_size.height))

    return cb_node
end

local function __create_combo_box_attribute_control__(attr_info, section_layout_config, view_self, visible_callback)
    local node = cc.Node:create()
    node:setVisible(not attr_info.init_invisible)

    local btn_normal, btn_selected = section_layout_config.combo_box_background, section_layout_config.combo_box_background
    local btn_node = ccui.Button:create(btn_normal, btn_selected, '', section_layout_config.combo_box_background_res_type)
    local btn_size = btn_node:getContentSize()
    btn_node:setPosition(btn_size.width * 0.5, -btn_size.height * 0.5)
    btn_node:setEnabled(not attr_info.init_disable)
    node:addChild(btn_node)

    local arrow_sprite = createSpriteWithName(section_layout_config.combo_box_arrow_1, section_layout_config.combo_box_arrow_res_type)
    local arrow_size = arrow_sprite:getContentSize()
    arrow_sprite:setPosition(btn_size.width - arrow_size.width * 0.5 + section_layout_config.combo_box_arrow_offset_x, -btn_size.height * 0.5 + section_layout_config.combo_box_arrow_offset_y)
    node:addChild(arrow_sprite)

    local text_width = btn_size.width - arrow_size.width + section_layout_config.combo_box_arrow_offset_x * 2
    local font_name, font_size = section_layout_config.combo_box_text_font_name, section_layout_config.combo_box_text_font_size
    local text_label = cc.Label:createWithTTF(tostring(attr_info.init_text or attr_info.init_value), font_name, font_size, cc.size(text_width, 0), cc.TEXT_ALIGNMENT_CENTER, cc.VERTICAL_TEXT_ALIGNMENT_CENTER)
    text_label:setAnchorPoint(0.5, 0.5)
    text_label:enableBold()
    text_label:setColor(section_layout_config.combo_box_text_color)
    text_label:setPosition(text_width * 0.5, -btn_size.height * 0.5 + section_layout_config.combo_box_arrow_offset_y)
    node:addChild(text_label)

    -- 
    local combo_box_layer, combo_box_options_node = nil, nil
    local function __hide_options__()
        view_self:schedule_once(function()
            if tolua.cast(combo_box_layer, 'Node') then
                combo_box_layer:removeFromParent(true)
                combo_box_layer = nil
            end

            if tolua.cast(combo_box_options_node, 'Node') then
                combo_box_options_node:removeFromParent(true)
                combo_box_options_node = nil
            end

            if tolua.cast(arrow_sprite, 'Node') then
                setSpriteTexture(arrow_sprite, section_layout_config.combo_box_arrow_1, section_layout_config.combo_box_arrow_res_type)
            end
        end)
    end

    -- listen options
    local option_is_valid = {}
    for index, option_info in ipairs(attr_info.options) do
        if option_info.is_valid_expression then
            local init_result = view_self:listenExpressionAttributes(option_info.is_valid_expression, function(result)
                option_is_valid[index] = result
            end, 0)
            option_is_valid[index] = init_result
        else
            option_is_valid[index] = true
        end
    end
    
    btn_node:addClickEventListener(function()
        -- 如果已经显示，就隐藏
        if combo_box_layer then return __hide_options__() end

        -- 改变箭头
        setSpriteTexture(arrow_sprite, section_layout_config.combo_box_arrow_2, section_layout_config.combo_box_arrow_res_type)

        local function __get_valid_option_count__()
            local count = 0
            for _, is_valid in ipairs(option_is_valid) do
                if is_valid then count = count + 1 end
            end
            return count
        end

        -- 
        local option_count = __get_valid_option_count__()
        local col_count = (option_count >= 5 and 3 or 2)
        local row_count = math.floor(option_count / col_count)
        if row_count * col_count ~= option_count then row_count = row_count + 1 end

        local scale_9_width = col_count * section_layout_config.combo_box_per_column_width
        local scale_9_height = row_count * section_layout_config.combo_box_per_row_height

        -- 
        combo_box_layer = createBackgroundLayer(section_layout_config.combo_box_layer_color, false, nil, nil, function(touch, event) __hide_options__() end)
        cc.Director:getInstance():getRunningScene():addChild(combo_box_layer, 10000)

        combo_box_options_node = cc.Node:create()
        node:addChild(combo_box_options_node)

        -- 
        combo_box_options_node:setPosition(btn_size.width * 0.5, scale_9_height * 0.5)

        -- 
        local iv = ccui.ImageView:create(section_layout_config.combo_box_scale_9_sprite, section_layout_config.combo_box_scale_9_res_type)
        iv:setTextureRect(section_layout_config.combo_box_scale_9_rect)
        iv:setCapInsets(section_layout_config.combo_box_scale_9_cap_insets)
        iv:setScale9Enabled(true)
        iv:setTouchEnabled(true)
        iv:setContentSize(cc.size(scale_9_width, scale_9_height))
        combo_box_options_node:addChild(iv)

        local rb_normal, rb_selected = section_layout_config.combo_box_rb_normal, section_layout_config.combo_box_rb_selected
        local offset_x, offset_y = -scale_9_width * 0.5, scale_9_height * 0.5
        local cur_index = 1
        for i, option_info in ipairs(attr_info.options) do
            if option_is_valid[i] then
                local is_selected = option_info.value == view_self.create_attributes[attr_info.attr_name]

                local btn_node = ccui.Button:create(is_selected and rb_selected or rb_normal, '', '', section_layout_config.combo_box_rb_res_type)
                btn_node:setTitleColor(section_layout_config.combo_box_rb_text_color)
                btn_node:setTitleFontSize(section_layout_config.combo_box_rb_font_size)
                btn_node:setTitleFontName(section_layout_config.combo_box_rb_font_name)
                btn_node:setTitleText(tostring(option_info.text or option_info.value))
                combo_box_options_node:addChild(btn_node)

                local row = math.floor((cur_index - 1) / col_count)
                local col = math.floor((cur_index - 1) % col_count)
                local x = offset_x + (col + 0.5) * section_layout_config.combo_box_per_column_width
                local y = offset_y - (row + 0.5) * section_layout_config.combo_box_per_row_height
                btn_node:setPosition(x, y)

                btn_node:addClickEventListener(function()
                    if is_selected then return end

                    -- 
                    view_self:updateCreateAttribute(attr_info.attr_name, option_info.value)
                    text_label:setString(tostring(option_info.text or option_info.value))

                    if section_layout_config.combo_box_rb_click_close then __hide_options__() end
                end)

                cur_index = cur_index + 1
            end
        end
    end)

    local function __get_text_by_value__(value)
        for i, option_info in ipairs(attr_info.options) do
            if option_info.value == value then
                return option_info.text
            end
        end
    end

    -- listen expression list
    local expression_operation = {
        ['reset_value'] = function(v, result)
            if result then
                local operation_value = v.operation_value
                if v.relative_attr_name then
                    operation_value = view_self.create_attributes[v.relative_attr_name]
                    if v.operation_value then operation_value = operation_value + v.operation_value end
                end

                text_label:setString(tostring(__get_text_by_value__(operation_value) or operation_value))
                view_self:updateCreateAttribute(attr_info.attr_name, operation_value)
            end
        end,
        ['invisible'] = function(v, result)
            node:setVisible(not result)
            if visible_callback then visible_callback() end
        end,
        ['disable'] = function(v, result) btn_node:setEnabled(not result) end,
    }

    -- expression_list
    for _, v in ipairs(attr_info.expression_list or {}) do
        view_self:listenExpressionAttributes(v, function(result)
            expression_operation[v.operation](v, result)
        end, v.operation == 'reset_value' and 1 or 0)
    end

    -- 
    node:setContentSize(btn_size)

    return node
end

local function __create_help_button__(attr_info, section_layout_config, view_self, visible_callback)
    local btn_node = cc.Node:create()

    local btn_help = ccui.Button:create(section_layout_config.help_button_normal, section_layout_config.help_button_selected, section_layout_config.help_button_disable, section_layout_config.help_button_res_type)
    local btn_size = btn_help:getContentSize()
    btn_help:setPosition(btn_size.width * 0.5 + 20, -btn_size.height * 0.5)
    btn_node:setContentSize(cc.size(btn_size.width + 40, btn_size.height))
    btn_node:addChild(btn_help)

    local help_button_layer, help_content_node = nil, nil
    local function __hide_help_layer__()
        view_self:schedule_once(function()
            if tolua.cast(help_button_layer, 'Node') then
                help_button_layer:removeFromParent(true)
                help_button_layer = nil
            end

            if tolua.cast(help_content_node, 'Node') then
                help_content_node:removeFromParent(true)
                help_content_node = nil
            end
        end)
    end
    btn_help:addClickEventListener(function()
        if tolua.cast(help_button_layer, 'Node') then return __hide_help_layer__() end

        help_button_layer = createBackgroundLayer(section_layout_config.help_button_layer_color, false, nil, nil, function(touch, event) __hide_help_layer__() end)
        cc.Director:getInstance():getRunningScene():addChild(help_button_layer, 10000)

        -- 
        help_content_node = cc.Node:create()

        local help_label = cc.Label:createWithTTF(attr_info.text, attr_info.font_name or 'font/fzzyjt.ttf', attr_info.font_size or 24)
        local text_size = help_label:getContentSize()
        help_label:setAnchorPoint(0.5, 0.5)
        help_label:setColor(cc.WHITE)
        help_content_node:addChild(help_label)

        -- 
        local iv = ccui.ImageView:create(section_layout_config.help_button_scale_9_sprite, section_layout_config.help_button_scale_9_res_type)
        iv:setTextureRect(section_layout_config.help_button_scale_9_rect)
        iv:setCapInsets(section_layout_config.help_button_scale_9_cap_insets)
        iv:setScale9Enabled(true)
        iv:setTouchEnabled(true)
        iv:setContentSize(cc.size(text_size.width + 40, text_size.height + 20))
        help_content_node:addChild(iv, -1)

        -- 
        local x_1, y_1 = btn_node:getPosition()
        local x_2, y_2 = btn_node:getParent():getPosition()
        help_content_node:setPosition(x_1 + x_2 + 5 + (attr_info.help_offset_x or 0), y_1 + y_2 + text_size.height * 0.5 + 5 + (attr_info.help_offset_y or 0))
        btn_node:getParent():getParent():addChild(help_content_node, 1000)
    end)

    return btn_node
end

local function __create_no_ui_attribute_control__(attr_info, section_layout_config, view_self, visible_callback)
    -- listen expression list
    local expression_operation = {
        ['reset_value'] = function(v, result)
            if result then
                local operation_value = v.operation_value
                if v.relative_attr_name then
                    operation_value = view_self.create_attributes[v.relative_attr_name]
                    if v.operation_value then operation_value = operation_value + v.operation_value end
                end

                view_self:updateCreateAttribute(attr_info.attr_name, operation_value)
            end
        end,
    }

    -- expression_list
    for _, v in ipairs(attr_info.expression_list or {}) do
        view_self:listenExpressionAttributes(v, function(result)
            expression_operation[v.operation](v, result)
        end, 1)
    end
end

local default_settings = {
    name = 'default',
    bottom_section = {
        name = '局数：',
        attr_name = 'jushu',
        ctrl_type = 'radio',        -- 控件类型
        init_value = 8,             -- 初始值
        options = {
            { text_1 = '4局', text_2 = 'x1', value = 4, },
            { text_1 = '8局', text_2 = 'x2', value = 8, },
            { text_1 = '16局', text_2 = 'x4', value = 16, },
        },
    },
    top_sections = {
        {
            {
                attributes = {
                    {
                        ctrl_type = 'label',    -- 控件类型
                        text = '缺少配置',
                        font_name = 'font/fzzyjt.ttf',
                        font_size = 35,
                        enable_bold = false,
                        text_color = cc.c3b(76, 35, 24),
                        text_offset_x = 0,
                        text_offset_y = -20,
                    },
                },
            },
        },
        layout_config = {
            section_offset_y = -120,
            section_offset_x_1 = 40,
        },
    },
}

return {
    default_layout_config = default_layout_config,
    default_settings = default_settings,
    attribute_ctrls = {
        ['label']       = function(view_self, attr_info, layout_config, visible_callback) return __create_label_control__(attr_info, layout_config, view_self, visible_callback) end,
        ['radio']       = function(view_self, attr_info, layout_config, visible_callback) return __create_radio_attribute_control__(attr_info, layout_config, view_self, visible_callback) end,
        ['check_box']   = function(view_self, attr_info, layout_config, visible_callback) return __create_check_box_attribute_control__(attr_info, layout_config, view_self, visible_callback) end,
        ['combo_box']   = function(view_self, attr_info, layout_config, visible_callback) return __create_combo_box_attribute_control__(attr_info, layout_config, view_self, visible_callback) end,
        ['help_button'] = function(view_self, attr_info, layout_config, visible_callback) return __create_help_button__(attr_info, layout_config, view_self, visible_callback) end,
        ['no_ui']       = function(view_self, attr_info, layout_config, visible_callback) return __create_no_ui_attribute_control__(attr_info, layout_config, view_self, visible_callback) end,
    },
    check_value = check_value,
}
