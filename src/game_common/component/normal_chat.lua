-- ./app/platform/game/game_common/normal_chat.lua
require 'app.platform.game.game_common.game_component_base'

local clientmain = require 'app.platform.room.clientmain'
local basic_def = require 'app.platform.room.module.basicnotifydef'

local normal_chat = class('normal_chat_component', component_base)
function normal_chat:ctor(game_scene)
    component_base.ctor(self, game_scene)

    self.csb_z_order = GAME_VIEW_Z_ORDER.VOICE_CHAT
end

function normal_chat:init(args)
    component_base.init(self)

    -- 
    self.normal_chat_node = cc.CSLoader:createNode('game_common_res/component/normal_chat/normal_chat_button.csb')
    self.normal_chat_node:setPosition(args.x, args.y)
    self.game_scene:addChild(self.normal_chat_node, self.csb_z_order)

    self.chat_view = nil
    self.btn_chat = button('btn_chat', function()
        if not self.chat_view then
            self.chat_view = self.game_scene:popupNode('app.platform.game.game_common.chat_view', {
                user_id = self.game_scene.self_user_id,
                sound_text_list = self.game_scene.scene_config.sound_text_list,
                emoji_type = self.game_scene.scene_config.emoji_type,
                on_close_cb = function()
                    self.chat_view = nil

                    --self.btn_chat:loadTextureNormal('game_common_res/chat/btn_chat_1.png')
                end,
            })

            --self.btn_chat:loadTextureNormal('game_common_res/chat/btn_chat_2.png')
        else
            self.chat_view:onClose()
            self.chat_view = nil

            --local file_name = self.chat_view and 'game_common_res/chat/btn_chat_2.png' or 'game_common_res/chat/btn_chat_1.png'
            --self.btn_chat:loadTextureNormal(file_name)
        end
    end, self.normal_chat_node)

    -- 大局结算的时候，隐藏
    self:listenGameSignal('final_settle', function(result_info, user_count)
        self.normal_chat_node:setVisible(false)
    end)
end

return normal_chat
