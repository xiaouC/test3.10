---------------------------------------------------------
--桌子内头像
---------------------------------------------------------
local user_head = require("app.platform.game.game_common.component.user_head")
local user_head_view = class('user_head_view', user_head)
function user_head_view:ctor(game_scene)
    user_head.ctor(self, game_scene)

    self.csb_file = 'game_common_res/component/user_head/desk_user_view.csb'
    self.csb_z_order = GAME_VIEW_Z_ORDER.USER_HEAD
end

function user_head_view:init(args)
    user_head.init(self,args)

    self.btn_out_room = button('btn_out_room', function()
        
    end, self.csb_node)

    self.csb_node:setVisible(false)
    self:listenGameSignal('homeowner_server_index', function(server_index) self:onHomeower(server_index) end)

end

function user_head_view:on_user_sit(server_index, user_id)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then return end

    self.csb_node:setVisible(user_id ~= 0)
    user_head.on_user_sit(self,server_index, user_id)
    --dump(user_id)
    self:onHomeower(server_index)
end

function user_head_view:onHomeower()
    local local_index = self.game_scene.server_index_to_local_index[self.game_scene.homeowner_server_index]
    local is_homeowner = (self.location_index == local_index)
    local homeowner_is_me = self.game_scene.homeowner_server_index == self.game_scene.my_server_index
    
    self.btn_out_room:setVisible(not is_homeowner and homeowner_is_me)
end

function user_head:on_game_state(game_state)
    view_component_base.on_game_state(self, game_state)

    self.user_head_node:setVisible(true and true or false)
end

return user_head_view