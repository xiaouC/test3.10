-- ./app/platform/game/game_common/components/game_room_info_view.lua
require 'app.platform.game.game_common.game_component_base'

local game_room_info_view = class('game_room_info_view', view_component_base)
function game_room_info_view:ctor(game_scene)
    view_component_base.ctor(self, game_scene)

    self.csb_file = 'game_common_res/component/room_info/room_info.csb'
end

function game_room_info_view:init(args)
    view_component_base.init(self,args)

    self.csb_node:setPosition(display.width - 100, display.height - 30)
    local node_panel = self.csb_node:getChildByName('node_panel')
    local root_node = node_panel:getChildByName('root_node')
    local node_bellett = root_node:getChildByName('node_bellett')

    --包间号
    self.m_lable_room_info = node_bellett:getChildByName("lable_room_info")
    self.m_lable_room_info:setString("包间号: 900000")

    local lable_time = node_bellett:getChildByName('lable_time')
    local btn_net_wifi = node_bellett:getChildByName("net_wifi")
    local btn_net_not = node_bellett:getChildByName("net_x")
    btn_net_not:setVisible(false)

    local delay = cc.DelayTime:create(5)
    local action_1 = cc.EaseBackOut:create(cc.MoveTo:create(1, cc.p(0, -40)))
    local action_2 = cc.EaseBackOut:create(cc.MoveTo:create(1, cc.p(0, 0)))
    node_bellett:runAction(cc.RepeatForever:create(cc.Sequence:create(action_1,delay,action_2,delay)))

    self.game_scene:schedule_circle(1, function()
        local times_value = os.date('%H:%M')
        lable_time:setString(times_value)
    end, true)

    self.game_scene:listenGameSignal('room_id', function(room_id) self:on_room_id(room_id) end)
end

function game_room_info_view:on_room_id(room_id)
    if( nil~=self.m_lable_room_info) then
        self.m_lable_room_info:setString("包间号:"..tostring(room_id))
    end
end

return game_room_info_view
