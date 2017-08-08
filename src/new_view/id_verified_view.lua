-- ./app/platform/room/new_view/buy_card_view.lua

local popup_base = require 'app.platform.common.popup_base'
local IDVerifiedView = class('IDVerifiedView', popup_base)
function IDVerifiedView:ctor()
    self.csb_file = 'hall_res/personal/id_verified.csb'

    popup_base.ctor(self)
end

function IDVerifiedView:initViews()
    popup_base.initViews(self)

    -- button pay
    local input_name = self.csb_node:getChildByName('input_text_name')
    local input_id = self.csb_node:getChildByName('input_text_id')
    button('btn_confirm', function()
        local user_name = input_name:getString()
        if #user_name == 0 then return api_show_Msg_Tip('请输入姓名') end

        local user_id = input_id:getString()
        if #user_id == 0 then return api_show_Msg_Tip('请输入身份证号') end
        if #user_id ~= 18 and #user_id ~= 15 then return api_show_Msg_Tip('请输入正确的身份证号') end

        input_name:setString('')
        input_id:setString('')
        
        local m_clientmain = require 'app.platform.room.clientmain'
        m_clientmain:get_instance():get_user_mgr():request_user_identify(user_id, user_name)
    end, self.csb_node)
end

return IDVerifiedView
