-- ./app/platform/game/game_common/battery_net_state.lua
require 'app.platform.game.game_common.game_component_base'

local clientmain = require 'app.platform.room.clientmain'
local basic_def = require 'app.platform.room.module.basicnotifydef'

local battery_net_state = class('battery_net_state_component', component_base)
function battery_net_state:ctor(game_scene)
    component_base.ctor(self, game_scene)

    self.csb_z_order = GAME_VIEW_Z_ORDER.BATTERY_NET_STATE
end

function battery_net_state:init(args)
    component_base.init(self)

    -- 
    self.csb_node = cc.CSLoader:createNode('game_common_res/component/battery_net_state/battery_net_state.csb')
    self.csb_node:setPosition(1177, 702)
    self.game_scene:addChild(self.csb_node, self.csb_z_order)

    -- 
    local time_label = self.csb_node:getChildByName('text_time')
    self.time_handler = self.game_scene:schedule_circle(1, function()
        local text = os.date("%H:%M", os.time())
        time_label:setString(text)
    end, true)

    -- 
    local net_state = { 'game_common_res/component/battery_net_state/net_x.png', 'game_common_res/component/battery_net_state/net_wifi.png', 'game_common_res/component/battery_net_state/net_tel.png' }
    local net_sprite = self.csb_node:getChildByName('net_state')
    local battery_process = self.csb_node:getChildByName('battery_process')
    clientmain:get_instance():get_sdk_mgr():get_event_mgr():BsAddNotifyEvent(basic_def.NOTIFY_SDK_EVENT, function(event)
        if not event or not event.args then return end
        if event.id ~= basic_def.NOTIFY_SDK_EVENT then return end
        if basic_def.NOTIFY_SDK_SYSTEM_INFO_EVENT ~= event.args.event_id then return end
        if event.args.event_data.ret ~= 0 then return end

        local state = event.args.event_data.data.state or {}
        local data = event.args.event_data.data.value or {}
        if state == 4 then  -- 电量
            battery_process:setPercent(data.data_level or 80)
        elseif state == 5 then  -- 网络信号
            net_sprite:setTexture(net_state[(data.data_type or 0) + 1])
        end
    end)

    -- 
    clientmain:get_instance():get_sdk_mgr():do_get_net_info()
    clientmain:get_instance():get_sdk_mgr():do_get_battery_info()
end

function battery_net_state:cleanup()
    if self.time_handler then
        self.game_scene:unschedule(self.time_handler)
        self.time_handler = nil
    end

    clientmain:get_instance():get_sdk_mgr():get_event_mgr():BsAddNotifyEvent(basic_def.NOTIFY_SDK_EVENT, nil)

    -- 
    component_base.cleanup(self)
end

return battery_net_state
