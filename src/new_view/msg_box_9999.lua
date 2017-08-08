-- ./app/platform/room/new_view/msg_box_9999.lua

local popup_base = require 'app.platform.common.popup_base'
local MsgBox9999 = class('MsgBox9999', popup_base)
function MsgBox9999:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/common/msg_box_9999.csb'

    popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function MsgBox9999:initViews()
    popup_base.initViews(self)

    -- 
    label('text_title', self.args.title, self.csb_node)

    local function __create_label_widget__(text)
        local text_label = cc.Label:createWithSystemFont(text, '黑体', 16, cc.size(800, 0))
        local text_size = text_label:getContentSize()
        text_label:setPosition(text_size.width * 0.5 + 5, text_size.height * 0.5)

        local widget = ccui.Widget:create()
        widget:setContentSize(text_size)
        widget:addChild(text_label)

        return widget
    end

    local lv_content = self.csb_node:getChildByName('lv_content')
    lv_content:setScrollBarEnabled(false)
    lv_content:addChild(__create_label_widget__(self.args.text))
    lv_content:requestDoLayout()
end

return MsgBox9999
