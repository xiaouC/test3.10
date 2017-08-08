-- ./app/platform/game/game_common/game_more_view.lua

local m_clientmain = require 'app.platform.room.clientmain'

local function __table_merge__(dest, src)
    dest = dest or {}

    for k, v in pairs(src or {}) do
        if type(v) == 'table' then
            dest[k] = __table_merge__(dest[k], src[k])
        else
            dest[k] = v
        end
    end

    return dest
end

local function __download_rule_file__(url, callback)
    if device.platform == 'ios' then url = string.gsub(url, 'wx.qlogo.cn', '14.17.57.189') end

    local md5_name = MD5(url):toString()
    local file_name = string.format('%s%s.png', device.writablePath, md5_name)

    -- 
    if io.exists(file_name) then return callback(file_name) end

    -- 
    reg_download_notify_handler(md5_name, function(code, task_id, url, file_path, action_id)
        reg_download_notify_handler(action_id, nil)

        if 0 ~= code then return end

        callback(file_name)
    end)

    local tag = os.time()
    CBsGameManager:GetI():LuaDownloadFileTask(tag, url, file_name, md5_name)
end

-- 可以设置是否有搓牌动画，是否震屏，开启GPS，使用普通话还是方言，以及设置自定义桌布等等
local function __init_settings_node_1__(view_self, node)
    -- music
    local cb_music = node:getChildByName('cb_music')
    cb_music:setSelected(UserData:getMusic() == 'on') 
    cb_music:addEventListener(function(_, event_type)
        local is_music_on = (event_type == ccui.CheckBoxEventType.selected)
        UserData:setMusic(is_music_on and 'on' or 'off')

        if is_music_on then
            Music:playMusic()
        else
            Music:stopMusic()
        end
    end)

    local music_slider = node:getChildByName('slider_music')
    music_slider:addEventListener(function(slider, event_type)
        if event_type == ccui.SliderEventType.percentChanged then
            local value = slider:getPercent() / slider:getMaxPercent() 
            Music:setMusicValue(value)
            UserData:setMusicValue(value)
        end
    end)
    music_slider:setPercent(tonumber(UserData:getMusicValue()) * 100)

    -- sound
    local cb_sound = node:getChildByName('cb_sound')
    cb_sound:setSelected(UserData:getSound() == 'on') 
    cb_sound:addEventListener(function(_, event_type)
        local is_sound_on = (event_type == ccui.CheckBoxEventType.selected)
        UserData:setSound(is_sound_on and 'on' or 'off')
    end)

    local sound_slider = node:getChildByName('slider_sound')
    sound_slider:addEventListener(function(slider, event_type)
        if event_type == ccui.SliderEventType.percentChanged then
            local value = slider:getPercent() / slider:getMaxPercent() 
            Music:setEffectValue(value)
            UserData:setSoundValue(value)
        end
    end)
    sound_slider:setPercent(tonumber(UserData:getSoundValue()) * 100)

    -- 搓牌动画
    local cb_draw_card_anim = node:getChildByName('cb_cuopai')
    cb_draw_card_anim:setSelected(UserData:getDrawCardAnim() == 'on')
    cb_draw_card_anim:addEventListener(function(_, event_type)
        UserData:setDrawCardAnim(event_type == ccui.CheckBoxEventType.selected and 'on' or 'off')
    end)

    -- 超时出牌的震动提示
    local cb_shock = node:getChildByName('cb_zhendong')
    cb_shock:setSelected(UserData:getWarnShake() == 'on')
    cb_shock:addEventListener(function(_, event_type)
        UserData:setWarnShake(event_type == ccui.CheckBoxEventType.selected and 'on' or 'off')
    end)

    -- button gps
    button('btn_gps_1', function() m_clientmain:get_instance():get_sdk_mgr():show_app_detail() end, node)
    local btn_gps_2 = button('btn_gps_2', function() m_clientmain:get_instance():get_sdk_mgr():show_location_setting() end, node)
    btn_gps_2:setVisible(device.platform ~= 'ios')

    -- language
    local cur_language_name = '普通话'
    for _, v in ipairs(view_self.scene_instance:getLanguageConfig() or {}) do
        if v.is_selected then cur_language_name = v.name end
    end

    local arrow_sprite = node:getChildByName('sprite_arrow')
    local language_label = label('text_cur_language', cur_language_name, node)

    local language_layer = nil
    local btn_language = button('btn_language', function()
        language_layer = createBackgroundLayer(cc.c4b(0, 0, 0, 0), true, nil, nil, function(touch, event)
            language_layer:removeFromParent(true)
            arrow_sprite:setRotation(0)
        end)
        node:getChildByName('node_language'):addChild(language_layer)

        local language_csb_node = cc.CSLoader:createNode('game_common_res/game_language_choice.csb')
        language_layer:addChild(language_csb_node)

        local lv_language = language_csb_node:getChildByName('lv_content')
        lv_language:setTouchEnabled(false)
        lv_language:setScrollBarEnabled(false)

        local cur_sel_language_info = nil
        local cur_sel_sprite = nil
        for _, v in ipairs(view_self.scene_instance:getLanguageConfig() or {}) do
            local csb_widget, csb_node = createWidget('game_common_res/game_language_choice_item.csb', 270, 60)
            lv_language:addChild(csb_widget)

            label('text_language', v.name, csb_node)

            local selected_sprite = csb_node:getChildByName('iv_background')
            selected_sprite:setVisible(false)

            if v.is_selected then
                if cur_sel_sprite then
                    cur_sel_sprite:setVisible(false)
                    cur_sel_language_info.is_selected = false
                end

                cur_sel_sprite = selected_sprite
                cur_sel_sprite:setVisible(true)
                cur_sel_language_info = v
            end

            csb_widget:setTouchEnabled(true)
            csb_widget:addClickEventListener(function()
                if cur_sel_sprite then
                    cur_sel_sprite:setVisible(false)
                    cur_sel_language_info.is_selected = false
                end

                cur_sel_sprite = selected_sprite
                cur_sel_sprite:setVisible(true)
                v.is_selected = true
                cur_sel_language_info = v

                language_label:setString(v.name)
            end)
        end
        lv_language:requestDoLayout()

        -- 
        arrow_sprite:setRotation(180)
    end, node)

    -- tablecloth
    local old_hsb_value = UserData:getHSBValue()

    local btn_hsb_custom = button('btn_hsv_custom', function()
        local game_hsb_view = require('app.platform.game.game_common.game_hsb_view').new(view_self.scene_instance, {
            type = 'tablecloth',
        })
        game_hsb_view:init()
        view_self.scene_instance:addChild(game_hsb_view, 10086)

        --
        view_self:onClose()
    end, node)

    local custom_gou_sprite = nil
    

    --
    local rb_group = ccui.RadioButtonGroup:create()
    node:addChild(rb_group)

    local hsb_config = {
        {
            hsb_value = { h = 0, s = 0, b = 0, index = 1 },
            sprite_file = 'game_common_res/game_common_hsv_default.png',
            res_type = ccui.TextureResType.localType,
        },
        {
            hsb_value = { h = 0, s = 0, b = 0, index = 2 },
            sprite_file = 'game_common_res/game_common_hsv_1.png',
            res_type = ccui.TextureResType.localType,
        },
        {
            hsb_value = { h = 0, s = 0, b = 0, index = 3 },
            sprite_file = 'game_common_res/game_common_hsv_2.png',
            res_type = ccui.TextureResType.localType,
        },
        {
            hsb_value = { h = 0, s = 0, b = 0, index = 4 },
            sprite_file = 'game_common_res/game_common_hsv_3.png',
            res_type = ccui.TextureResType.localType,
        },
        {
            hsb_value = { h = 0, s = 0, b = 0, index = -1 },
            sprite_file = 'default.png',
            res_type = ccui.TextureResType.localType,
        },

    }

    local lv_hsb = node:getChildByName('lv_hsb')
    lv_hsb:setTouchEnabled(false)
    lv_hsb:setScrollBarEnabled(false)
    for i, v in ipairs(hsb_config) do
        local rb = ccui.RadioButton:create(v.sprite_file, v.sprite_file, v.sprite_file, v.sprite_file, v.sprite_file, v.res_type)
        lv_hsb:addChild(rb)
        rb_group:addRadioButton(rb)

        local gou_sprite = cc.Sprite:createWithSpriteFrameName('game_common_gou.png')
        gou_sprite:setPosition(rb:getContentSize().width - 10, 10)
        gou_sprite:setVisible(false)
        rb:addChild(gou_sprite)

        if i == old_hsb_value.index then
            rb_group:setSelectedButton(rb)
            gou_sprite:setVisible(true)
        end

        if old_hsb_value.index == -1 and i == #hsb_config then
            rb_group:setSelectedButton(rb)
        end

        rb:addEventListener(function(_, event_type)
            if event_type == ccui.RadioButtonEventType.selected then
                UserData:setHSBValue(v.hsb_value)
                view_self.scene_instance:resetTablecloth(v.hsb_value)

                gou_sprite:setVisible(true)
            else
                gou_sprite:setVisible(false)
            end

            if custom_gou_sprite then custom_gou_sprite:setVisible(false) end
        end)
    end
    lv_hsb:requestDoLayout()

    -- 
    if -1 == old_hsb_value.index then
        custom_gou_sprite = cc.Sprite:createWithSpriteFrameName('game_common_gou.png')
        custom_gou_sprite:setPosition(btn_hsb_custom:getContentSize().width - 10, 10)
        btn_hsb_custom:addChild(custom_gou_sprite)
    end
end

local function __init_rules_node__(view_self, node)
    local rule_config = view_self.scene_instance:getGameRuleConfig() or {}

    local lv_rules = node:getChildByName('lv_rules')
    lv_rules:setEnabled(false)
    lv_rules:setScrollBarEnabled(false)
    for _, v in ipairs(rule_config.sections or {}) do
        local csb_widget, csb_node = createWidget('game_common_res/game_more_rule_item.csb', 910, rule_config.section_height or 100)

        label('text_section', v.section_name, csb_node)
        label('text_desc', v.section_desc, csb_node)

        lv_rules:addChild(csb_widget)
    end
    lv_rules:requestDoLayout()

    -- 解散包间
    local btn_dismiss = button('btn_dismiss', function()
        view_self.scene_instance:onClickExitButtonEvent()
        view_self:onClose()
    end, node)
    btn_dismiss:setEnabled(view_self.scene_instance:canDismissRoom())

    -- 离开包间
    local btn_quit = button('btn_quit', function()
        view_self.scene_instance:onExitGame()
    end, node)
end

local function __init_rules_node_detail__(view_self, node)
    local rules_config = __table_merge__({
        {
            name = '基本玩法',
        },
        {
            name = '基本番型',
        },
        {
            name = '特殊规则',
        },
        {
            name = '结算规则',
        },
    }, view_self.args.rules_config or view_self.scene_instance:getRuleDetailConfig())

    -- 
    local rb_group = ccui.RadioButtonGroup:create()
    node:addChild(rb_group)

    local lv_content = node:getChildByName('lv_content')

    -- 
    local click_scroll_flag = false
    local current_checked_rb = nil
    local image_item_to_rb = {}

    -- 
    local last_scroll_to_index = 0

    local rb_normal, rb_selected = 'game_common_rule_normal.png', 'game_common_rule_selected.png'
    local rb_text_color_normal, rb_text_color_selected = cc.c3b(21, 88, 84), cc.c3b(255, 145, 6)
    for i, v in ipairs(rules_config) do
        local node_rb = node:getChildByName('node_rb_' .. i)

        local rb = ccui.RadioButton:create(rb_normal, rb_normal, rb_selected, rb_normal, rb_selected, ccui.TextureResType.plistType)
        node_rb:addChild(rb)
        rb_group:addRadioButton(rb)

        local size = rb:getContentSize()

        local text_label = cc.Label:createWithTTF(v.name, 'font/fzzyjt.ttf', 20, cc.size(20, 0))
        text_label:setAnchorPoint(0.5, 0.5)
        text_label:setPosition(size.width * 0.5 - 3, size.height * 0.5 - 6)
        text_label:setLineSpacing(-5.0)
        rb:addChild(text_label)

        if index == 1 then
            text_label:enableOutline(rb_text_color_selected, 2)
        else
            text_label:enableOutline(rb_text_color_normal, 2)
        end

        local scroll_to_index = last_scroll_to_index
        rb:addEventListener(function(_, event_type)
            if event_type == ccui.RadioButtonEventType.selected then
                click_scroll_flag = true

                lv_content:scrollToItem(scroll_to_index, cc.p(0, 1), cc.p(0,1))

                text_label:enableOutline(rb_text_color_selected, 2)
            else
                text_label:enableOutline(rb_text_color_normal, 2)
            end
        end)

        for _, img_content in ipairs(v.help_contents or {}) do
            local im = ccui.ImageView:create('default.png', ccui.TextureResType.localType)
            lv_content:addChild(im)

            __download_rule_file__(img_content, function(file_path)
                if tolua.cast(im, "Node") then
                    im:loadTexture(file_path, ccui.TextureResType.localType)
                    lv_content:requestDoLayout()
                end
            end)

            image_item_to_rb[im] = { rb, text_label }
        end

        -- 
        last_scroll_to_index = last_scroll_to_index + #v.help_contents
    end

    -- 妈的，cocos 底层里面，ListView : public ScrollView
    -- 但他们竟然都有一个成员变量，名字还一样，坑了他爹了
    ccui.ScrollView.addEventListener(lv_content, function(_, event_type)
        if event_type == ccui.ScrollviewEventType.containerMoved then
            if click_scroll_flag then return end

            local iv = lv_content:getTopmostItemInCurrentView()
            local rb, text_label = unpack(image_item_to_rb[iv])
            if current_checked_rb ~= rb then
                current_checked_rb = rb

                if rb then
                    rb_group:setSelectedButton(rb)
                    text_label:enableOutline(rb_text_color_selected, 2)
                end
            end
        end

        if event_type == ccui.ScrollviewEventType.autoscrollEnded then
            click_scroll_flag = false
        end
    end)
end

----------------------------------------------------------------------------------------------------------
local game_scene_popup_base = require 'app.platform.game.game_common.game_scene_popup_base'

local game_more_view = class('game_more_view', game_scene_popup_base)
function game_more_view:ctor(game_scene, args, show_anim_func, hide_anim_func)
    local more_configs = {
        ['SETTINGS'] = {
            csb_file = 'game_common_res/game_more_view.csb',
            init_view_func = function() end,
        },
        ['RULE_DETAIL'] = {
            csb_file = 'game_common_res/game_more_view_rule_detail.csb',
            init_view_func = function()
                local node_content = self.csb_node:getChildByName('node_rules_detail')
                __init_rules_node_detail__(self, node_content)
            end,
        },
        ['SETTING_RULE_DETAIL'] = {
            csb_file = 'game_common_res/game_more_view.csb',
            init_view_func = function() self:initViews_Three() end,
        },
    }

    self.more_config = more_configs[args.type]
    self.csb_file = self.more_config.csb_file
    self.bg_color = cc.c4b(0, 0, 0, 0)
    self.z_order = 10001

    game_scene_popup_base.ctor(self, game_scene, args, show_anim_func, hide_anim_func)
end

function game_more_view:initViews()
    game_scene_popup_base.initViews(self)

    -- init
    self.more_config.init_view_func()
end

function game_more_view:initViews_Three()
    -- title tab config
    local tab_config = {
        {
            text = '设　置',
            node_name = 'node_radio_settings',
            content_node_name = 'node_settings',
            init_func = __init_settings_node_1__,
        },
        {
            text = '玩　法',
            node_name = 'node_radio_rules',
            content_node_name = 'node_rules',
            init_func = __init_rules_node__,
        },
        {
            text = '规　则',
            node_name = 'node_radio_rules_detail',
            content_node_name = 'node_rules_detail',
            init_func = __init_rules_node_detail__,
        },
    }

    -- 
    local rb_group = ccui.RadioButtonGroup:create()
    self.csb_node:addChild(rb_group)

    local rb_content = {}
    local rb_normal, rb_selected = 'game_common_tab_normal.png', 'game_common_tab_selected.png'
    for index, v in ipairs(tab_config) do
        local rb = ccui.RadioButton:create(rb_normal, rb_normal, rb_selected, rb_normal, rb_selected, ccui.TextureResType.plistType)
        self.csb_node:getChildByName(v.node_name):addChild(rb)
        rb_group:addRadioButton(rb)

        -- 
        local init_flag = false
        local node_content = self.csb_node:getChildByName(v.content_node_name)

        -- 
        local size = rb:getContentSize()

        local text_label = cc.Label:createWithTTF(v.text, 'font/fzzyjt.ttf', 30)
        text_label:setAnchorPoint(0.5, 0.5)
        text_label:setPosition(size.width * 0.5, size.height * 0.5)
        rb:addChild(text_label)

        if index == 1 then
            text_label:setColor(cc.c3b(215, 239, 204))
            text_label:enableOutline(cc.c3b(54, 128, 94), 2)
            node_content:setVisible(true)

            init_flag = true
            v.init_func(self, node_content)

            rb_group:setSelectedButton(rb)
        else
            text_label:setColor(cc.c3b(123, 46, 19))
            text_label:disableEffect(cc.LabelEffect.OUTLINE)
            node_content:setVisible(false)
        end

        rb:addEventListener(function(_, event_type)
            if event_type == ccui.RadioButtonEventType.selected then
                text_label:setColor(cc.c3b(215, 239, 204))
                text_label:enableOutline(cc.c3b(54, 128, 94), 2)
                node_content:setVisible(true)

                -- 
                if not init_flag then
                    init_flag = true
                    v.init_func(self, node_content)
                end
            else
                text_label:setColor(cc.c3b(123, 46, 19))
                text_label:disableEffect(cc.LabelEffect.OUTLINE)
                node_content:setVisible(false)
            end
        end)
    end
end

return game_more_view
