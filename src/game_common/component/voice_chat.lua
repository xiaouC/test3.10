-- ./app/platform/game/game_common/voice_chat.lua
require 'app.platform.game.game_common.game_component_base'

local clientmain = require 'app.platform.room.clientmain'
local basic_def = require 'app.platform.room.module.basicnotifydef'

local voice_chat = class('voice_chat_component', view_component_base)
function voice_chat:ctor(game_scene)
    view_component_base.ctor(self, game_scene)

    self.csb_z_order = GAME_VIEW_Z_ORDER.VOICE_CHAT
    self.need_swallow = false
end

function voice_chat:init(args)
    view_component_base.init(self)

    -- 
    self.voice_chat_sprite = cc.Sprite:create('game_common_res/component/voice_chat/voice_chat_button_1.png')
    self.voice_chat_sprite:setPosition(args.x, args.y)
    self.bg_layer:addChild(self.voice_chat_sprite)

    local size = self.voice_chat_sprite:getContentSize()
    self.rc_voice = { x = 0, y = 0, width = size.width, height = size.height }

    -- 
    self.send_voice_flag = false
    clientmain:get_instance():get_voice_mgr():get_event_mgr():BsAddNotifyEvent(basic_def.NOTIFY_VOICE_EVENT, function(event)
        if not event or not event.args then return end
        if event.id ~= basic_def.NOTIFY_VOICE_EVENT then return end
        if m_def.NOTIFY_VOICE_EVENT_UPLOAD_FILE ~= event.args.event_id then return end

        if not self.send_voice_flag then return end
        self.send_voice_flag = false

        local data = event.args.event_data.data
        local ret = event.args.event_data.ret
        if tonumber(ret) == 11 then
            m_clientmain:get_instance():get_voice_mgr():start_play(data.file_path)
            m_clientmain:get_instance():get_game_manager():get_game_room_mgr():send_game_chat_msg(self.game_scene.self_user_id, 2, 1, data.file_id)
        end
    end)

    -- 大局结算的时候，隐藏
    self:listenGameSignal('final_settle', function(result_info, user_count)
        self.bg_layer:setVisible(false)
    end)
end

function voice_chat:on_touch_began(touch, event)
    local pos = self.voice_chat_sprite:convertToNodeSpace(touch:getLocation())
    if not self.cd_sprite and cc.rectContainsPoint(self.rc_voice, pos) and not self.csb_node_voice then
        self.csb_node_voice = cc.CSLoader:createNode('game_common_res/component/voice_chat/voice_chat_anim.csb')
        self.csb_node_voice:setPosition(display.width * 0.5, display.height * 0.5)
        self.bg_layer:addChild(self.csb_node_voice)

        self.anim_node = createAnimNode('game_common_res/component/voice_chat/anim_voicing.csb', true)
        self.csb_node_voice:getChildByName('node_anim'):addChild(self.anim_node)

        -- 
        self.csb_node_voice:getChildByName('text_tips'):setString('手指上滑，取消发送')

        self.voicing_flag = true
    end

    --return view_component_base.on_touch_began(self, touch, event)
    return self.voicing_flag and true or false
end

function voice_chat:on_touch_moved(touch, event)
    if not self.cd_sprite and self.csb_node_voice then
        local pos = touch:getLocation()
        if pos.y <= 360 then
            if not self.voicing_flag then
                self.voicing_flag = true

                self.anim_node:setVisible(true)
                self.csb_node_voice:getChildByName('node_cancel'):setVisible(false)
                self.csb_node_voice:getChildByName('text_tips'):setString('手指上滑，取消发送')
            end
        else
            if self.voicing_flag then
                self.voicing_flag = false

                self.anim_node:setVisible(false)
                self.csb_node_voice:getChildByName('node_cancel'):setVisible(true)
                self.csb_node_voice:getChildByName('text_tips'):setString('松开手指，取消发送')
            end
        end
    end

    view_component_base.on_touch_moved(self, touch, event)
end

function voice_chat:on_touch_ended(touch, event)
    if not self.cd_sprite and self.voicing_flag ~= nil then
        if self.voicing_flag then
            self.send_voice_flag = true

            clientmain:get_instance():get_voice_mgr():stop_record_voice()
            clientmain:get_instance():get_voice_mgr():upload_record()
        else
            self.send_voice_flag = false

            clientmain:get_instance():get_voice_mgr():stop_record_voice()
            clientmain:get_instance():get_voice_mgr():upload_record()
        end

        self.voicing_flag = nil

        self.csb_node_voice:removeFromParent(true)
        self.csb_node_voice = nil

        -- 
        if self.cd_handler then self.game_scene:unschedule(self.cd_handler) end
        if self.cd_sprite then self.cd_sprite:removeFromParent(true) end

        self.cd_sprite = cc.Sprite:createWithSpriteFrameName('voice_chat_time_3.png')
        self.cd_sprite:setPosition(1230, 345)
        self.bg_layer:addChild(self.cd_sprite)

        self.voice_chat_sprite:setTexture('game_common_res/component/voice_chat/voice_chat_button_2.png')

        local cd_count = 3
        self.cd_handler = self.game_scene:schedule_circle(1, function()
            cd_count = cd_count - 1
            if cd_count <= 0 then
                self.game_scene:unschedule(self.cd_handler)
                self.cd_handler = nil

                self.cd_sprite:removeFromParent(true)
                self.cd_sprite = nil

                self.voice_chat_sprite:setTexture('game_common_res/component/voice_chat/voice_chat_button_1.png')
            else
                self.cd_sprite:setSpriteFrame(string.format('voice_chat_time_%d.png', cd_count))
            end
        end)
    end

    view_component_base.on_touch_ended(self, touch, event)
end

return voice_chat
