-- ./app/platform/room/new_view/notice_view_2.lua

local popup_base = require 'app.platform.common.popup_base'
local NoticeView = class('NoticeView', popup_base)
function NoticeView:ctor(model_install, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/common/notice_view_2.csb'

    popup_base.ctor(self, model_install, args, show_anim_func, hide_anim_func)
end

function NoticeView:initViews()
    popup_base.initViews(self)

    -- 
    label('text_title', self.args.title, self.csb_node)
    label('text_name', self.args.name, self.csb_node)

    local sv_content = self.csb_node:getChildByName('sv_content')
    local sv_size = sv_content:getContentSize()

    local text_label = cc.LabelTTF:create(self.args.context, "黑体", 24, cc.size(sv_size.width - 20, 0), cc.TEXT_ALIGNMENT_LEFT)
    text_label:setColor(cc.c3b(62, 19, 20))
    sv_content:addChild(text_label)

    local text_size = text_label:getContentSize()
    if sv_size.height >= text_size.height then
        text_label:setPosition(sv_size.width * 0.5 + 2, sv_size.height - text_size.height * 0.5)
        sv_content:setInnerContainerSize(cc.size(sv_size.width, sv_size.height + 5))
    else
        text_label:setPosition(sv_size.width * 0.5 + 2, text_size.height * 0.5)
        sv_content:setInnerContainerSize(cc.size(sv_size.width, text_size.height + 5))
    end

    local btn_ok = button('btn_ok', function() self:onClose() end, self.csb_node)
    btn_ok:setEnabled(false)

    local time = 3
    self.cd_handler = self:schedule_circle(1, function()
        time = time - 1

        if time > 0 then
            btn_ok:setTitleText(string.format('知道了(%d)', time))
        else
            btn_ok:setTitleText('知道了')
        end

        if time < 0 then
            self:unschedule(self.cd_handler)

            btn_ok:setEnabled(true)
        end
    end)
end

return NoticeView
