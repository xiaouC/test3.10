require 'app.platform.game.game_common.game_component_base'

local m_clientmain = require 'app.platform.room.clientmain'

local game_ready_view = class('game_ready_view', view_component_base)
function game_ready_view:ctor(game_scene)
    view_component_base.ctor(self, game_scene)

    self.csb_file = 'game_common_res/component/ready/ready_view.csb'
end

function game_ready_view:init(args)
    view_component_base.init(self,args)

   
    self.btn_state = nil
    self.btn_start_or_invite = button('btn_start_or_invite', function()
        if self.btn_state == 'ready' then
            self.game_scene:requestAction('user_agree', true)
        elseif self.btn_state == 'start' then
            self.game_scene:requestAction('user_agree', true)
        elseif self.btn_state == 'invite' then
            self:inviteFriends()
        end
    end, self.csb_node)
    

    local btn_size = self.btn_start_or_invite:getContentSize()
    self.btn_text_label = cc.Label:createWithTTF('开始游戏', 'font/fzzyjt.ttf', 40)
    self.btn_text_label:setColorTextureIndex(2)
    self.btn_text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    self.btn_text_label:setPosition(btn_size.width * 0.5, btn_size.height * 0.5 + 5)
    self.btn_text_label:enableOutline(cc.c3b(166, 24, 22), 2)
    self.btn_text_label:enableShadow()
    self.btn_start_or_invite:getRendererNormal():addChild(self.btn_text_label)
    self.btn_start_or_invite:setVisible(false)

    self:listenGameSignal('on_user_ready', function(server_index, is_ready) self:onUserReady(server_index, is_ready) end)
    self:listenGameSignal('on_user_sit', function(server_index, user_id) self:on_user_sit(server_index, user_id) end)

    button('btn_start_or_invite', function()
        self:on_start_or_invite()
    end, self.csb_node)

    self.btn_cancel = button('btn_cancel',function() 
        self:on_cancel_button()
    end, self.csb_node)
end


function game_ready_view:onUserReady(server_index, is_ready)
    dump(is_ready)
    --if server_index ~= self.game_scene.m_chair_id then return end
    
    if(self.game_scene.homeowner_server_index == server_index) then
        if(is_ready) then
            self:update_button_state('start')
        else
            self:update_button_state('invite',true)
        end
    else
        if(is_ready) then
            self:update_button_state('start')
        else
            self:update_button_state('ready')
        end
        self.btn_start_or_invite:setVisible(true)
    end
end


function game_ready_view:on_user_sit(server_index, user_id)
--    if server_index ~= self.game_scene.m_chair_id then return end

--    if(self.game_scene.homeowner_server_index == server_index) then
--        self.btn_text_label:setString("开始游戏")
--    else
--        self.btn_text_label:setString("准备游戏")
--        self.btn_start_or_invite:setVisible(true)
--    end
    
end


function game_ready_view:on_start_or_invite()
    --my is home over
--    if(self.game_scene.homeowner_server_index == self.game_scene.m_chair_id) then
--        self.btn_start_or_invite:setVisible(true)
--    else
--        self.btn_start_or_invite:setVisible(false)
--    end
    if(self.btn_state == 'ready') then
        --start game
        self:update_button_state('start')
    end
end

function game_ready_view:on_cancel_button()
    if(self.btn_state == 'start') then
        self:update_button_state('ready')
    end
end

function game_ready_view:update_button_state(state,is_homeowner)
    if (state == 'ready') then
        self.btn_state = 'ready'
        self.btn_text_label:setString("开始游戏")
        self.btn_start_or_invite:setVisible(true)
        self.btn_cancel:setVisible(false)
        self.btn_text_label:enableOutline(cc.c3b(166, 24, 22), 2)
        self.btn_start_or_invite:loadTextureNormal('btn_advance_2.png', ccui.TextureResType.plistType)
        self.game_scene:requestAction('user_agree', false)
    elseif(state == 'start') then
        self.btn_state = 'start'
        self.btn_text_label:setString("邀请好友")
        self.btn_start_or_invite:setVisible(true)
        self.btn_cancel:setVisible(true)
        self.btn_text_label:enableOutline(cc.c3b(166, 24, 22), 2)
        self.btn_start_or_invite:loadTextureNormal('btn_advance_1.png', ccui.TextureResType.plistType)
        self.game_scene:requestAction('user_agree', true)
    elseif(state == 'invite') then
        self.btn_state = 'invite'
        self.btn_text_label:setString("邀请好友")
        self.btn_start_or_invite:setVisible(true)
        self.btn_cancel:setVisible(not is_homeowner)
        self.btn_text_label:enableOutline(cc.c3b(28, 118, 14), 2)
        self.btn_start_or_invite:loadTextureNormal('btn_advance_1.png', ccui.TextureResType.plistType)
    end
end

return game_ready_view