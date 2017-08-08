-- ./app/platform/room/new_view/notice_view.lua
require 'app.platform.room.new_view.loading'

local m_clientmain = require 'app.platform.room.clientmain'
local m_def = require 'app.platform.room.module.basicnotifydef'

local popup_base = require 'app.platform.common.popup_base'
local NoticeView = class('NoticeView', popup_base)
function NoticeView:ctor()
    self.csb_file = 'hall_res/common/new_notice_view.csb'
    self.recv_notice_list = {}

    popup_base.ctor(self)
end

function NoticeView:initViews()
    popup_base.initViews(self)

    -- 
    local lv_radio = self.csb_node:getChildByName('lv_radio')
    lv_radio:setScrollBarEnabled(false)
    lv_radio:setItemsMargin(10)

    local lv_content = self.csb_node:getChildByName('lv_content')
    lv_content:setItemsMargin(2)

    local lv_content_size = lv_content:getContentSize()
    local function __update_content__(v)
        if not v then return end

        lv_content:removeAllChildren()

        local function __create_label_widget__(text, offset_x, font_name, font_size, text_color, is_system_font)
            local function __create_label__()
                if is_system_font then
                    return cc.Label:createWithSystemFont(text, font_name, font_size, cc.size(lv_content_size.width - 40, 0), cc.TEXT_ALIGNMENT_LEFT, cc.VERTICAL_TEXT_ALIGNMENT_CENTER)
                else
                    return cc.Label:createWithTTF(text, font_name, font_size, cc.size(lv_content_size.width - 40, 0), cc.TEXT_ALIGNMENT_LEFT, cc.VERTICAL_TEXT_ALIGNMENT_CENTER)
                end
            end
            local label_1 = __create_label__()
            local size_1 = label_1:getContentSize()

            local widget_1 = ccui.Widget:create()
            widget_1:setContentSize(cc.size(lv_content_size.width, size_1.height))
            widget_1:addChild(label_1)

            label_1:setColor(text_color)
            label_1:setAnchorPoint(0, 0.5)
            label_1:setPosition(10 + offset_x, size_1.height * 0.5)

            lv_content:addChild(widget_1)
        end

        -- title
        --__create_label_widget__(v.m_name, 0, 'res/font/fzzyjt.ttf', 34, cc.c3b(91, 6, 6), false)
        label('text_1', v.m_name, self.csb_node)

        -- date time
        local dt = os.date("*t", tonumber(v.m_create_time));
        local text = string.format("%d/%02d/%02d %02d:%02d", dt.year, dt.month, dt.day, dt.hour, dt.min)
        --__create_label_widget__(text, 5, 'res/font/jxk.TTF', 22, cc.c3b(91, 6, 6), false)
        label('text_2', text, self.csb_node)

        -- content
        __create_label_widget__(v.m_context, 10, 'res/font/fzzyjt.ttf', 24, cc.c3b(255, 255, 255), false)

        lv_content:jumpToTop()
        lv_content:requestDoLayout()
    end

    local rb_group = ccui.RadioButtonGroup:create()
    self.anim_node:addChild(rb_group)

    local last_sel_index = 1
    self:appendView('update_notice', function()
        if not tolua.cast(self.csb_node, 'Node') then return end

        -- 
        rb_group:removeAllRadioButtons()
        lv_radio:removeAllChildren()
        for i, v in ipairs(self.recv_notice_list or {}) do
            local rb_widget, rb, text_label = createRadioWidget{
                img_normal = 'hall_notice_button_1.png',
                img_selected = 'hall_notice_button_2.png',
                tex_res_type = ccui.TextureResType.plistType,
                text = v.m_title,
                text_color = cc.c3b(255, 255, 255),
                font_name = 'font/fzzyjt.ttf',
                font_size = 26,
                onchanged = function(rb, event_type) end,
                enable_outline = true,
                outline_size = 2,
                outline_color = (i == 1 and cc.c3b(199, 105, 59) or cc.c3b(89, 99, 154)),
            }

            rb:addEventListener(function(_, event_type)
                text_label:enableOutline(event_type == ccui.RadioButtonEventType.selected and cc.c3b(199, 105, 59) or cc.c3b(89, 99, 154), 2)

                if event_type == ccui.RadioButtonEventType.selected then __update_content__(v) end
            end)

            lv_radio:addChild(rb_widget)
            rb_group:addRadioButton(rb)
        end
        lv_radio:requestDoLayout()

        __update_content__(self.recv_notice_list[last_sel_index] or self.recv_notice_list[1])
    end)
end

function NoticeView:initDataFromServer()
    m_clientmain:get_instance():get_notice_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_NOTICE_EVENT, function(event)
        if not event or not event.args then return end
        if event.args.event_data.ret ~= 0 then return end
        if m_def.NOTIFY_NOTICE_EVENT_NOTICE ~= event.args.event_id then return end
        if not tolua.cast(self.csb_node, 'Node') then return end

        for _, v in ipairs(event.args.event_data.data.list or {}) do
            table.insert(self.recv_notice_list, v)
        end

        self:updateViews()
    end)

    m_clientmain:get_instance():get_notice_mgr():request_system_notice()
    m_clientmain:get_instance():get_notice_mgr():request_guild_notice()
end

return NoticeView
