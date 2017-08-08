-- ./app/platform/room/new_view/vip_month_receive_reward.lua

require 'app.platform.room.new_view.loading'
local m_clientmain = require 'app.platform.room.clientmain'

local popup_base = require 'app.platform.common.popup_base'
local VIPMonthReceiveReward = class('VIPMonthReceiveReward', popup_base)
function VIPMonthReceiveReward:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/mall/mall_reward_result_2.csb'
    self.z_order = 200

    popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function VIPMonthReceiveReward:initViews()
    popup_base.initViews(self)

    local desc = ''
    local recv_ids = {}

    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info() 
    for _, v in ipairs(user_info.m_reward) do
        if desc ~= '' then desc = desc .. '\n' end

        desc = desc .. v.desc

        table.insert(recv_ids, tonumber(v.id))
    end

    label('text_reward_desc', desc, self.csb_node)

    button('btn_receive', function()
        m_clientmain:get_instance():get_active_mgr():request_receive_roomcard(recv_ids)

        self:onClose()
    end, self.csb_node)
end

return VIPMonthReceiveReward
