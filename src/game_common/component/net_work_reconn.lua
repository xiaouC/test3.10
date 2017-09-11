-- ./app/platform/game/game_common/net_work_reconn.lua
require 'app.platform.game.game_common.game_component_base'
require 'app.platform.game.game_common.loading'

local clientmain = require 'app.platform.room.clientmain'
local basic_def = require 'app.platform.room.module.basicnotifydef'

local net_work_reconn = class('net_work_reconn_component', component_base)
function net_work_reconn:init(args)
    component_base.init(self)

    self.is_reconnecting = false

    -- 
    clientmain:get_instance():get_keepalive_mgr():get_event_mgr():BsAddNotifyEvent(basic_def.NOTIFY_KEEPALIVE_EVENT, function(event)
        if not event or not event.args then return end

        local param = event.args

        if event.id == basic_def.NOTIFY_KEEPALIVE_EVENT then
            if basic_def.NOTIFY_SOCKET_RE_CONNECT == param.event_id then
                if param.event_data.ret ~= 0 then
                    self.is_reconnecting = true
                    new_show_loading('断线重连中，请稍候。。。')
                end
            elseif basic_def.NOTIFY_KEEPALIVE_EVENT_MAIN == param.event_id then
                if param.event_data.ret ~= 0 then
                    self:showReconnectMsgBox()
                end
            end
        end
    end)

    self:listenGameSignal('game_state', function()
        if self.is_reconnecting then
            self.is_reconnecting = false

            new_hide_loading()
        end
    end)
end

function net_work_reconn:showReconnectMsgBox()
    show_msg_box_2('', '您的当前网络环境较差，请检查您的网络后重试!', function()
        local ret = clientmain:get_instance():get_game_manager():re_start_game(2)
        if 0 ~= ret then self:showReconnectMsgBox() end
    end)
end

return net_work_reconn
