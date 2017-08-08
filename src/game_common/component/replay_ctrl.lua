-- ./app/platform/game/game_common/replay_ctrl.lua
require 'app.platform.game.game_common.game_component_base'

local replay_ctrl = class('voice_chat_component', view_component_base)
function replay_ctrl:ctor(game_scene)
    view_component_base.ctor(self, game_scene)

    self.csb_file = 'game_common_res/component/replay_ctrl/replay_ctrl.csb'
    self.csb_z_order = GAME_VIEW_Z_ORDER.REPLAY_CTRL
    self.need_swallow = true
end

function replay_ctrl:init(args)
    view_component_base.init(self)

    self.bg_layer:setVisible(false)

    -- 
    self.btn_prev = button('btn_prev', function() self.game_scene:goBack() end, self.csb_node)
    self.btn_play = button('btn_play', function()
        if self.game_scene.is_pause then
            self.game_scene:play()
            self.btn_play:loadTextureNormal('game_common_replay_pause.png', ccui.TextureResType.plistType)
        else
            self.game_scene:pause()
            self.btn_play:loadTextureNormal('game_common_replay_play.png', ccui.TextureResType.plistType)
        end
    end, self.csb_node)
    self.btn_play:loadTextureNormal(self.game_scene.is_pause and 'game_common_replay_play.png' or 'game_common_replay_pause.png', ccui.TextureResType.plistType)
    self.btn_next = button('btn_next', function() self.game_scene:moveForward() end, self.csb_node)
    self.btn_quit = button('btn_quit', function() self.game_scene:onExitGame() end, self.csb_node)

    -- 
    self.btn_prev:setEnabled(false)
    self.btn_play:setEnabled(false)
    self.btn_next:setEnabled(false)

    -- 
    self:listenGameSignal('replay_start', function(is_pause)
        self.btn_prev:setEnabled(true)
        self.btn_play:setEnabled(true)
        self.btn_next:setEnabled(true)

        self.btn_play:loadTextureNormal(is_pause and 'game_common_replay_play.png' or 'game_common_replay_pause.png', ccui.TextureResType.plistType)

        self.bg_layer:setVisible(true)
    end)
end

function replay_ctrl:on_round_end()
    view_component_base.on_round_end(self)

    self.bg_layer:setVisible(false)
end

function replay_ctrl:on_touch_began(touch, event)
    if self.bg_layer:isVisible() then return true end

    return false
end

function replay_ctrl:on_touch_ended(touch, event)
    self.csb_node:setVisible(not self.csb_node:isVisible())

    view_component_base.on_touch_ended(self, touch, event)
end

return replay_ctrl
