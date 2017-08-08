-- ./app/platform/room/new_view/new_activity_win_task.lua
require 'app.platform.room.new_view.loading'

local m_clientmain = require 'app.platform.room.clientmain'

local popup_base = require 'app.platform.common.popup_base'
local WinActiveView = class('WinActiveView', popup_base)
function WinActiveView:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/activity/new_activity_win_task.csb'

    self.win_data = args

    popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function WinActiveView:initViews()
    popup_base.initViews(self)

    -- 
    button('btn_share', function()
        self.scene_instance.current_active_index = 1
        m_clientmain:get_instance():get_welfare_mgr():request_gift_info()

        self:onClose()
    end, self.csb_node)

    -- 
    local btn_receive = button('btn_receive', function() m_clientmain:get_instance():get_welfare_mgr():request_task_card_gift(tostring(self.win_data.uid), 0) end, self.csb_node)
    btn_receive:setTitleText(self.win_data.task_record == 1 and '领  取' or '已领取')
    btn_receive:setEnabled(self.win_data.state == 1)

    if self.win_data.state == 0 then
        label('text_task_state', string.format('当前任务状态：第 %d 名', self.win_data.ranking), self.csb_node)
    elseif self.win_data.state == 1 then
        label('text_task_state', '当前任务状态：已完成', self.csb_node)
    else
        label('text_task_state', '当前任务状态：已领取', self.csb_node)
    end
end

return WinActiveView
