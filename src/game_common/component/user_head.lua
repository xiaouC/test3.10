-- ./app/platform/game/game_common/user_head.lua
require 'app.platform.game.game_common.game_component_base'

local clientmain = require 'app.platform.room.clientmain'

local chat_side_config = {
    ['right'] = {
        offset_x = 50,
        offset_y = 20,
        background = 'game_common_chat_scale9_bg.png',
        anchor_point = { x = 0, y = 0.5 },
        background_cap_insets = { x= 16, y = 6, width = 6, height = 5 },
        text_width = 180,
        text_offset_x = 15,
        text_offset_y = -2,
        voice_offset_x = 100,
        voice_offset_y = 20,
        voice_scale_x = 1,
    },
    ['left'] = {
        offset_x = -50,
        offset_y = 20,
        background = 'game_common_chat_scale9_bg_2.png',
        anchor_point = { x = 1, y = 0.5 },
        background_cap_insets = { x= 6, y = 6, width = 6, height = 5 },
        text_width = 180,
        text_offset_x = -15,
        text_offset_y = -2,
        voice_offset_x = -100,
        voice_offset_y = 20,
        voice_scale_x = -1,
    },
}

local function __create_text_chat_node__(chat_config, text)
    local node = cc.Node:create()

    local iv = ccui.ImageView:create(chat_config.background, ccui.TextureResType.plistType)
    iv:setAnchorPoint(chat_config.anchor_point.x, chat_config.anchor_point.y)
    iv:setScale9Enabled(true)
    iv:setCapInsets(chat_config.background_cap_insets)
    node:addChild(iv)

    local text_label = cc.Label:createWithTTF(text, 'hall_res/font/jxk.TTF', 24, cc.size(chat_config.text_width, 0))
    text_label:setAnchorPoint(chat_config.anchor_point.x, chat_config.anchor_point.y)
    text_label:setPosition(chat_config.text_offset_x, chat_config.text_offset_y)
    node:addChild(text_label)

    local text_size = text_label:getContentSize()
    iv:setContentSize(cc.size(text_size.width + 22, text_size.height + 8))

    return node, iv, text_label
end

local user_head = class('user_head', component_base)
function user_head:ctor(game_scene)
    component_base.ctor(self, game_scene)

    self.csb_file = 'game_common_res/component/user_head/desk_user.csb'
    self.csb_z_order = GAME_VIEW_Z_ORDER.USER_HEAD
end

function user_head:init(args)
    component_base.init(self, args)

    --
    self.location_index = args.location_index

    self.chat_config = chat_side_config[args.chat_side]

    -- 
    self.user_head_node = cc.Node:create()
    --self.user_head_node:setVisible(false)
    self.user_head_node:setPosition(args.x, args.y)
    self.game_scene:addChild(self.user_head_node, self.csb_z_order or 0)

    self.csb_node = cc.CSLoader:createNode(self.csb_file)
    self.csb_node:setVisible(false)
    self.user_head_node:addChild(self.csb_node)

    self.user_id = 0
    self.user_head_sprite = nil

    self.node_head = self.csb_node:getChildByName('node_head')
    self.node_left_top = self.node_head:getChildByName('node_left_top')
    self.node_right_top = self.node_head:getChildByName('node_right_top')

    ---- 
    self.node_background = self.csb_node:getChildByName('node_background')
    --self.node_background:setVisible(false)

    button('btn_head_frame', function()
        local server_index = self.game_scene.local_index_to_server_index[self.location_index]
        local user_id = self.game_scene:get_user_id(server_index)
        if user_id ~= 0 then
            self.game_scene:fire('show_user_detail', user_id)
        end
    end, self.node_head)

    -- 
    self.ps_origin_x = args.x - display.width * 0.5
    self.ps_origin_y = args.y - display.height * 0.5

    self.node_ps = cc.Node:create()
    self.node_ps:setPosition(self.ps_origin_x, self.ps_origin_y)
    self.node_ps:setVisible(false)
    self.game_scene:addChild(self.node_ps, 11000)

    local sun = cc.ParticleSun:create()
    sun:setTexture(cc.Director:getInstance():getTextureCache():addImage('game_res/majiang/particle-stars.png'))
    sun:setTotalParticles(80)
    sun:setStartSize(9)
    sun:setStartSizeVar(3)
    sun:setSpeed(6)
    sun:setSpeedVar(1.5)
    self.node_ps:addChild(sun, 11)

    self.background_sprite = self.node_background:getChildByName('background')
    self.background_sprite:setVisible(false)

    -- 
    self:listenGameSignal('on_user_sit', function(server_index, user_id) self:on_user_sit(server_index, user_id) end)
    self:listenGameSignal('on_init_fast_out', function(server_index, count) self:on_fast_out(server_index, count) end)
    self:listenGameSignal('on_fast_out', function(server_index, count) self:on_fast_out(server_index, count) end)
    self:listenGameSignal('on_user_offline', function(server_index, is_offline) self:on_user_offline(server_index, is_offline) end)
    self:listenGameSignal('banker_server_index', function(server_index, is_offline) self:on_bankder_server_index(server_index) end)
    self:listenGameSignal('init_user_score', function(server_index, score) self:init_user_score(server_index, score) end)
    self:listenGameSignal('update_user_score', function(server_index, score) self:on_update_user_score(server_index, score) end)
    self:listenGameSignal('on_user_chat', function(chat_type, sub_type, server_index, user_id, msg) self:on_user_chat(chat_type, sub_type, server_index, user_id, msg) end)
    self:listenGameSignal('user_turn', function(server_index) self:on_user_turn(server_index) end)
    self:listenGameSignal('out_card', function(location_index, card_id) self:on_out_card(location_index, card_id) end)

    self.node_round_ready = self.csb_node:getChildByName('round_ready')
    self:listenGameSignal('on_user_ready', function(server_index, is_ready) self:on_user_ready(server_index, is_ready) end)
end

function user_head:on_game_state(game_state)
    view_component_base.on_game_state(self, game_state)

    self.user_head_node:setVisible((game_state ~= 'waiting') and true or false)
end

function user_head:on_game_start()
    self.node_round_ready:setVisible(false)
    self.background_sprite:setVisible(false)

    view_component_base.on_game_start(self)
end

function user_head:on_user_sit(server_index, user_id)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then return end

    -- 
    self.user_id = user_id
    if user_id == 0 then return self.csb_node:setVisible(false) end
    self.csb_node:setVisible(true)

    -- 
    local user_info = self.game_scene:get_user_info(user_id)
    self.node_head:getChildByName('text_user_name'):setString(user_info.m_nickName)

    -- 
    if self.user_head_sprite then self.user_head_sprite:removeFromParent(true) end
    self.user_head_sprite = createUserHeadSprite(user_info)
    self.node_head:getChildByName('node_head_sprite'):addChild(self.user_head_sprite)
end

function user_head:on_fast_out(server_index, count)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then return end

    self.node_head:getChildByName('node_fast_light'):getChildByName('text_fast_count'):setString(tostring(count))
end

function user_head:on_user_offline(server_index, is_offline)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then return end

    if not self.offline_sprite then
        self.offline_sprite = cc.Sprite:create('game_res/majiang/userinfo/img_cut.png')
        self.offline_sprite:setScale(1.4)
        self.offline_sprite:setVisible(false)
        self.node_head:getChildByName('node_head_sprite'):addChild(self.offline_sprite, 1)
    end

    self.offline_sprite:setVisible(is_offline)
end

function user_head:on_bankder_server_index(server_index)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then
        self.node_right_top:removeAllChildren()

        return
    end

    self.node_right_top:addChild(cc.Sprite:createWithSpriteFrameName('banker_flag.png'))
end

function user_head:init_user_score(server_index, score)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then return end

    -- 
    self.user_score = score
    self.node_head:getChildByName('text_user_id'):setString(tostring(self.user_score))
end

function user_head:on_update_user_score(server_index, score)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then return end

    self.user_score = (self.user_score or 0) + score
    self.node_head:getChildByName('text_user_id'):setString(tostring(self.user_score))
end

function user_head:on_user_chat(chat_type, sub_type, server_index, user_id, msg)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then return end
    if self.game_scene.game_state == 'waiting' then return end

    -- 
    if self.node_chat then
        self.node_chat:removeFromParent(true)
        self.node_chat = nil
    end

    -- 
    local function __show_text__(text)
        local node, iv, text_label = __create_text_chat_node__(self.chat_config, text)
        node:setPosition(self.chat_config.offset_x, self.chat_config.offset_y)
        self.csb_node:addChild(node, 100)

        self.node_chat = node

        -- 
        local action_1 = cc.DelayTime:create(4)
        local action_2 = cc.FadeTo:create(1, 0)
        local action_3 = cc.CallFunc:create(function()
            self.node_chat:removeFromParent(true)
            self.node_chat = nil
        end)  
        self.node_chat:runAction(cc.Sequence:create(action_1, action_2, action_3))
    end

    -- 
    if chat_type == 1 then
        __show_text__(msg)
    elseif chat_type == 4 then
        local index = tonumber(sub_type)

        -- 
        local sound_text = self.game_scene.scene_config.sound_text_list[index]
        __show_text__(sound_text.text)

        local user_info = self.game_scene.all_user_info[server_index]
        self.game_scene.game_music:chatVoice(sound_text.index, user_info.m_bBoy and 'boy' or 'girl')
    elseif chat_type == 3 then
        local index = tonumber(sub_type)

        local file_name = string.format('%s/anim/emoji_%d.csb', self.game_scene.scene_config.emoji_type, index)
        local anim_node = createAnimNode(file_name)
        anim_node:setPosition(self.chat_config.offset_x, self.chat_config.offset_y)
        self.csb_node:addChild(anim_node, 100)

        performWithDelay(anim_node, function() anim_node:removeFromParent(true) end, 1.2)
    else
        if user_id ~= self.game_scene.self_user_id then
            clientmain:get_instance():get_voice_mgr():play_net_record(msg)

            local anim_node = createAnimNode('game_common_res/anim_play_voice_chat.csb')
            anim_node:setPosition(self.chat_config.voice_offset_x, self.chat_config.voice_offset_y)
            anim_node:setScaleX(self.chat_config.voice_scale_x)
            self.csb_node:addChild(anim_node, 100)

            performWithDelay(anim_node, function() anim_node:removeFromParent(true) end, 4)
        end
    end
end

function user_head:on_user_turn(server_index)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then return end

    --
    self.node_ps:setVisible(true)
    --self.node_background:setVisible(true)

    -- 
    if not self.game_scene.is_replay then
        if not self.progress then
            self.progress = cc.ProgressTimer:create(cc.Sprite:createWithSpriteFrameName('desk_user_progress_bg_2.png'))
            self.progress:setType(cc.PROGRESS_TIMER_TYPE_RADIAL)
            self.node_background:addChild(self.progress, 1)
        end

        self.progress:setVisible(true)
        self.progress:setPercentage(0)
        self.progress:runAction(cc.ProgressTo:create(10, 100))

        -- 
        local action_1 = cc.DelayTime:create(10)
        local action_2 = cc.CallFunc:create(function()
            self.node_ps:setVisible(false)

            -- 只有轮到出牌的那个的头像底才闪
            if server_index == self.game_scene.my_server_index then
                self.background_sprite:runAction(cc.RepeatForever:create(cc.Blink:create(1, 1)))
            end
        end) 
        self.background_sprite:runAction(cc.Sequence:create(action_1, action_2))
    else
        self.background_sprite:runAction(cc.RepeatForever:create(cc.Blink:create(1, 1)))
    end

    -- 
    self.node_ps:stopAllActions()
    self.node_ps:setPosition(self.ps_origin_x, self.ps_origin_y + 64)
    self.node_ps:setVisible(true)
    self.background_sprite:setVisible(true)

    local time1 = 10*90/((90+128)*2)
    local time2 = 10*128/((90+128)*2)
    local move1 = cc.MoveBy:create(time1/2+0.1, cc.p(44,0)); --88 124
    local move2 = cc.MoveBy:create(time2-0.35, cc.p(0,-124));
    local move3 = cc.MoveBy:create(time1+0.4, cc.p(-88,0));
    local move4 = cc.MoveBy:create(time2-0.35, cc.p(0,124));
    local move5 = cc.MoveBy:create(time1/2+0.1, cc.p(44,0));
    local callback = cc.CallFunc:create(function()
        self.node_ps:setVisible(false)
    end)
    self.node_ps:runAction(cc.Sequence:create(move1, move2, move3, move4, move5, callback))
end

function user_head:on_out_card(location_index, card_id)
    if location_index ~= self.location_index then return end

    if self.progress then
        self.progress:setVisible(false)
        self.progress:stopAllActions()
    end
    --self.node_background:setVisible(false)
    self.background_sprite:setVisible(false)
    self.background_sprite:stopAllActions()

    self.node_ps:setVisible(false)
end

function user_head:on_user_ready(server_index, is_ready)
    local location_index = self.game_scene.server_index_to_local_index[server_index]
    if location_index ~= self.location_index then return end

    self.node_round_ready:setVisible(is_ready)
    self.background_sprite:setVisible(is_ready)
end

return user_head
