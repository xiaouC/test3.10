-- ./app/platform/room/new_view/rule_detail_view.lua
-- 

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

--
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

local RuleDetailView = class('RuleDetailView', cc.Node)
function RuleDetailView:ctor(config)
    self.rule_config = __table_merge__({
        {
            x = 75, y = 520,
            img_selected = 'rule_radio_selected.png',
            img_normal = 'rule_radio_normal.png',
        },
        {
            x = 75, y = 375,
            img_selected = 'rule_radio_selected.png',
            img_normal = 'rule_radio_normal.png',
        },
        {
            x = 75, y = 230,
            img_selected = 'rule_radio_selected.png',
            img_normal = 'rule_radio_normal.png',
        },
        {
            x = 75, y = 85,
            img_selected = 'rule_radio_selected.png',
            img_normal = 'rule_radio_normal.png',
        },
    }, config)

    -- 
    self:init()
end

function RuleDetailView:init()
    local listener = cc.EventListenerTouchOneByOne:create()
    listener:setSwallowTouches(true)
    listener:registerScriptHandler(function(touch, event) return true end, cc.Handler.EVENT_TOUCH_BEGAN)
    listener:registerScriptHandler(function(touch, event) end, cc.Handler.EVENT_TOUCH_MOVED)
    listener:registerScriptHandler(function(touch, event) end, cc.Handler.EVENT_TOUCH_ENDED )
    self:getEventDispatcher():addEventListenerWithSceneGraphPriority(listener, self)

    self:initViews()
end

function RuleDetailView:initViews()
    self:setPosition(display.width * 0.5, display.height * 0.5)

    local layer_color = cc.LayerColor:create(cc.c4b(0, 0, 0, 120))
    layer_color:setPosition(-display.width * 0.5, -display.height * 0.5)
    self:addChild(layer_color)

    -- 
    self.anim_node = cc.Node:create()
    self:addChild(self.anim_node)

    -- 
    self.csb_node = cc.CSLoader:createNode('game_common_res/rule_detail_view.csb')
    self.anim_node:addChild(self.csb_node)

    button('btn_close', function() self:removeFromParent(true) end, self.csb_node)

    -- 
    local rb_group = ccui.RadioButtonGroup:create()
    rb_group:setPosition(118 - display.width * 0.5, 52 - display.height * 0.5)
    self.csb_node:addChild(rb_group)

    local lv_content = self.csb_node:getChildByName('lv_content')

    -- 
    local click_scroll_flag = false
    local current_checked_rb = nil
    local image_item_to_rb = {}

    -- 
    local last_scroll_to_index = 0
    for i, v in ipairs(self.rule_config) do
        local rb = ccui.RadioButton:create(v.img_normal, v.img_normal, v.img_selected, v.img_normal, v.img_selected, ccui.TextureResType.plistType)
        rb:setPosition(v.x, v.y)
        rb_group:addChild(rb)
        rb_group:addRadioButton(rb)

        local size = rb:getContentSize()

        local text_label = cc.Label:createWithTTF(v.name, 'res/font/jxk.TTF', 20, cc.size(20, 0))
        text_label:setAnchorPoint(0.5, 0.5)
        text_label:setPosition(size.width * 0.5 - 2, size.height * 0.5 - 10)
        text_label:setColor(i == 1 and cc.c3b(101, 40, 25) or cc.c3b(255, 232, 134))
        rb:addChild(text_label)

        local scroll_to_index = last_scroll_to_index
        rb:addEventListener(function(_, event_type)
            if event_type == ccui.RadioButtonEventType.selected then
                click_scroll_flag = true

                lv_content:scrollToItem(scroll_to_index, cc.p(0, 1), cc.p(0,1))
            end
            text_label:setColor(event_type == ccui.RadioButtonEventType.selected and cc.c3b(101, 40, 25) or cc.c3b(255, 232, 134))
        end)

        for _, img_content in ipairs(v.help_contents) do
            local im = ccui.ImageView:create('default.png', ccui.TextureResType.localType)
            lv_content:addChild(im)

            __download_rule_file__(img_content, function(file_path)
                im:loadTexture(file_path, ccui.TextureResType.localType)
                lv_content:requestDoLayout()
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
                    text_label:setColor(cc.c3b(101, 40, 25))
                end
            end
        end

        if event_type == ccui.ScrollviewEventType.autoscrollEnded then
            click_scroll_flag = false
        end
    end)
end

return RuleDetailView
