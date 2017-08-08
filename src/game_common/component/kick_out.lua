-- ./app/platform/game/game_common/kick_out.lua

local kick_out = class('kick_out_component', component_base)
function kick_out:ctor(game_scene)
    component_base.ctor(self, game_scene)
end

function kick_out:init(args)
    component_base.init(self, args)

    -- 
    self:listenGameSignal('on_kick_out', function()
        show_msg_box_2('请出包间', '您已经被房主请出包间', function()
            self.game_scene:onExitGame()
        end)
    end)
end

return kick_out
