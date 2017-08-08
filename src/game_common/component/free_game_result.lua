-- ./app/platform/game/game_common/free_game_result.lua
require 'app.platform.game.game_common.game_component_base'

local free_game_result = class('free_game_result_component', component_base)
function free_game_result:init(args)
    component_base.init(self)

    -- 
    self:listenGameSignal('user_free_result', function(server_index, user_id, result)
        local content = result and '您所在包间已经解散！' or string.format('玩家“%s”不同意解散包间', self.game_scene:get_user_info(user_id).m_nickName)
        show_msg_box_2('解散包间', content, function()
            if result then
                self.game_scene:tryToShowFinalSettle()
            end
        end)
    end)
end

return free_game_result
