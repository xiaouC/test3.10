-- ./app/platform/room/new_view/new_activity_daily_task.lua
require 'app.platform.room.new_view.loading'

local m_clientmain = require 'app.platform.room.clientmain'

local popup_base = require 'app.platform.common.popup_base'
local DailyActiveView = class('DailyActiveView', popup_base)
function DailyActiveView:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/activity/new_activity_daily_task.csb'

    self.daily_data = args

    popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function DailyActiveView:initViews()
    popup_base.initViews(self)

    -- 
    button('btn_share', function()
        self.scene_instance.current_active_index = 1
        m_clientmain:get_instance():get_welfare_mgr():request_gift_info()

        self:onClose()
    end, self.csb_node)

    -- 
    local lv_content = self.csb_node:getChildByName('lv_content')
    for i, v in ipairs(self.daily_data.list or {}) do
        local item_widget, item_node = createWidget('hall_res/activity/daily_item.csb', 665, 120)
        lv_content:addChild(item_widget)

        item_node:getChildByName('node_icon'):addChild(cc.Sprite:create(i == 1 and 'hall_res/activity/img_day_1.png' or 'hall_res/activity/img_day_2.png'))

        label('text_desc', v.task_desc, item_node)
        label('text_reward_count', v.m_gift_num, item_node)
        label('text_task_count', v.m_play_num, item_node)

        local btn_game = button('btn_game', function()
            -- 开包间
            if v.m_status == 0 then
                api_show_loading()

                G_in_Hall = false

                m_clientmain:get_instance():get_user_mgr():request_user_info()
                m_clientmain:get_instance():get_room_mgr():request_desk_owner()

                self:onClose()

                return
            end

            -- 领取奖励
            m_clientmain:get_instance():get_welfare_mgr():request_task_card_gift(v.m_task_type, v.m_task_id) 
        end, item_node)
        if v.m_status == 1 then btn_game:getRendererNormal():loadTextureNormal('hall_res/activity/btn_day_task_get.png') end
        if v.m_status == 2 then btn_game:setEnabled(false) end
    end
    lv_content:requestDoLayout()
end

return DailyActiveView
