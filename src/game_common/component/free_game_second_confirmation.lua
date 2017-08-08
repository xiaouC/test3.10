-- ./app/platform/game/game_common/free_game_second_confirmation.lua
require 'app.platform.game.game_common.game_component_base'

local free_game_second_confirmation = class('free_game_second_confirmation_component', component_base)
function free_game_second_confirmation:init(args)
    component_base.init(self)

    self.second_confirmation_flag = false

    -- 
    self:listenGameSignal('second_confirmation_free_game', function(callback_func)
        if self.second_confirmation_flag then return end
        self.second_confirmation_flag = true

        -- 
        show_msg_box_1('申请解散包间', '您确认要解散包间吗？', function()
            self.second_confirmation_flag = false
            callback_func(true)
        end, function()
            self.second_confirmation_flag = false
            callback_func(false)
        end)
    end)
end

return free_game_second_confirmation
