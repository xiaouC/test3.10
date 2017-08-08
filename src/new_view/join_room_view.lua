-- ./app/platform/room/new_view/buy_card_view.lua

local m_clientmain = require 'app.platform.room.clientmain'

local popup_base = require 'app.platform.common.popup_base'
local JoinRoomView = class('JoinRoomView', popup_base)
function JoinRoomView:ctor(model_install, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/join_room.csb'

    popup_base.ctor(self, model_install, args, function(popup_self, node, cb)
        if cb then cb() end
    end, hide_anim_func)
end

function JoinRoomView:initViews()
    popup_base.initViews(self)

    --
    local num_text = ''
    local input_label = self.csb_node:getChildByName('al_input')
    local text_tips = self.csb_node:getChildByName('text_tips')

    local btn_clean = nil
    btn_clean = button('btn_clean', function()
        num_text = ''
        input_label:setString(num_text)

        text_tips:setVisible(true)
        btn_clean:setVisible(false)
    end, self.csb_node)

    -- 
    for i=0, 9 do
        button('btn_' .. i, function()
            local len = string.len(num_text)
            if len < 6 then
                num_text = num_text .. i
                input_label:setString(num_text)

                if len == 5 then
                    m_clientmain:get_instance():get_room_mgr():query_desk_info(num_text)
                end
            end
            text_tips:setVisible(false)
            btn_clean:setVisible(false)
        end, self.csb_node)
    end

    button('btn_back', function()
        num_text = string.sub(num_text, 1, -2)
        input_label:setString(num_text)

        if string.len(num_text) <= 0 then
            text_tips:setVisible(true)
        end
        btn_clean:setVisible(false)
    end, self.csb_node)
end

return JoinRoomView
