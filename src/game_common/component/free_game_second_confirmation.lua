-- ./app/platform/game/game_common/free_game_second_confirmation.lua
require 'app.platform.game.game_common.game_component_base'

local free_game_second_confirmation = class('free_game_second_confirmation_component', component_base)
function free_game_second_confirmation:init(args)
    component_base.init(self)

    self.second_confirmation_flag = false
    self.node_msg_box = nil

    -- 
    self:listenGameSignal('second_confirmation_free_game', function(callback_func)
        if self.second_confirmation_flag then return end
        self.second_confirmation_flag = true

        -- 
        self.node_msg_box = show_msg_box_1('申请解散包间', '您确认要解散包间吗？', function()
            self.second_confirmation_flag = false
            self.node_msg_box = nil
            callback_func(true)
        end, function()
            self.second_confirmation_flag = false
            self.node_msg_box = nil
            callback_func(false)
        end)
    end)

    -- 
    self:listenGameSignal('key_back_pressed', function(callback_func)
        if not tolua.cast(self.node_msg_box, 'Node') then
            self.second_confirmation_flag = true

            self.node_msg_box = show_msg_box_1('申请解散包间', '您确认要解散包间吗？', function()
                self.second_confirmation_flag = false
                self.node_msg_box = nil
                callback_func(true)
            end, function()
                self.second_confirmation_flag = false
                self.node_msg_box = nil
                callback_func(false)
            end)
        else
            self.node_msg_box:removeFromParent(true)
            self.second_confirmation_flag = false
            self.node_msg_box = nil
        end
    end)
end

return free_game_second_confirmation
