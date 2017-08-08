-- ./app/platform/game/game_common/game_waiting_view.lua
require 'app.platform.game.game_common.game_component_base'

local m_clientmain = require 'app.platform.room.clientmain'

local GameWaitingView = class('GameWaitingView', view_component_base)
function GameWaitingView:ctor(game_scene)
    view_component_base.ctor(self, game_scene)

    self.csb_file = 'game_common_res/component/waiting/waiting.csb'
    self.csb_z_order = 300
end

function GameWaitingView:cleanup()
    view_component_base.cleanup(self)
end

function GameWaitingView:init(args)
    view_component_base.init(self)

    -- 
    self.csb_node:setVisible(false)
    self.min_count = args.min_count     -- 至少几人可以开始游戏

    -- button start game or invite friends
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


    -- button cancel
    self.btn_cancel = button('btn_cancel', function()
        -- 如果是房主的话，那就是开始游戏，这个出现在少于4人时候
        -- 其他情况下，都是房主看不见的
        if self.game_scene.my_server_index == self.game_scene.homeowner_server_index then
            self.game_scene:requestAction('user_agree', true)
        else
            self.game_scene:requestAction('user_agree', false)
        end
    end, self.csb_node)
    -- 
    self.all_user_nodes = {}
    for server_index=1, 4 do
        local node_user = self.csb_node:getChildByName('node_' .. server_index)

        self.all_user_nodes[server_index] = {
            node_user = node_user,
            sprite_user_head = nil,
            node_warning_bg = node_user:getChildByName('warning_bg'),
            node_ready_flag = node_user:getChildByName('ready_flag'),
            node_homeowner_flag = node_user:getChildByName('homeowner_flag'),
            node_waiting = node_user:getChildByName('node_waiting'),
            node_user_head = node_user:getChildByName('node_user_head'),
            text_user_name = node_user:getChildByName('text_user_name'),
            text_user_id = node_user:getChildByName('text_user_id'),
            al_zan = node_user:getChildByName('al_zan'),
            al_paipin = node_user:getChildByName('al_paipin'),
            btn_leave = button('btn_leave_or_invite', function()
                local user_id = self.game_scene:get_user_id(server_index)
                self.game_scene:requestAction('kick_out', user_id, server_index)
            end, node_user),
        }

        button('btn_user_detail', function()
            local user_id = self.game_scene:get_user_id(server_index)
            if user_id ~= 0 then
                self.game_scene:fire('show_user_detail', user_id)
            end
        end, node_user)
    end

    -- 
    self:listenGameSignal('room_id', function(room_id) self.csb_node:getChildByName('al_room_id'):setString(tostring(room_id)) end)
    self:listenGameSignal('play_count', function(cur_play_count, total_play_count)
        self.csb_node:getChildByName('al_ju'):setString(tostring(total_play_count))
    end)

    self:listenGameSignal('on_user_sit', function(server_index, user_id) self:onUserSit(server_index, user_id) end)
    self:listenGameSignal('on_user_offline', function(server_index, is_offline) self:onUserOffline(server_index, is_offline) end)
    self:listenGameSignal('on_user_ready', function(server_index, is_ready) self:onUserReady(server_index, is_ready) end)
    self:listenGameSignal('homeowner_server_index', function(server_index) self:onHomeower(server_index) end)

    -- game rule
    self:listenGameSignal('update_game_rule', function()
        local rule_config = self.game_scene:getGameRuleConfig()
        for i=1, 4 do
            local node_section = self.csb_node:getChildByName('node_section_' .. i)

            -- 
            local section_info = rule_config.sections[i]
            node_section:setVisible(section_info and true or false)

            if section_info then
                label('text_section', section_info.section_name, node_section)
                label('text_rule_text', section_info.section_desc, node_section)
            end
        end
    end)
    self:listenGameSignal('on_user_chat', function(chat_type, sub_type, server_index, user_id, msg) self:on_user_chat(chat_type, sub_type, server_index, user_id, msg) end)
    self:listenGameSignal('update_gps_data', function() self:update_gps_data() end)

    self:update_gps_data()
end

function GameWaitingView:on_game_state(game_state)
    view_component_base.on_game_state(self, game_state)

    self.csb_node:setVisible(game_state == 'waiting' and true or false)
end

function GameWaitingView:onUserSit(server_index, user_id)
    local v = self.all_user_nodes[server_index]

    local user_info = self.game_scene:get_user_info(user_id)

    -- 
    v.text_user_name:setString(user_info.m_nickName)

    local text_user_id = 'ID:'
    if user_info.m_dwUserID == 0 or user_info.m_dwUserID == '' then
        text_user_id = ''
    else
        text_user_id = text_user_id .. user_info.m_dwUserID
    end
    v.text_user_id:setString(text_user_id)

    -- 
    v.node_user_head:removeAllChildren()
    if user_id ~= 0 then
        v.node_user_head:addChild(createUserHeadSprite(user_info))
    end

    -- 
    if user_info.m_cardqualityvalue then
        if user_info.m_cardqualityvalue < 0 then
            v.al_paipin:setString('/' .. tostring(math.abs(user_info.m_cardqualityvalue)))
        else
            v.al_paipin:setString(tostring(user_info.m_cardqualityvalue))
        end
    else
        v.al_paipin:setString('//')
    end

    if user_id ~= 0 then
        local zan_num = (user_info.m_praisevalue or 0)
        local cha_num = (user_info.m_tramplevalue or 0)
        local hao_ping_num = 100
        if zan_num ~= 0 and cha_num ~= 0 then
            hao_ping_num = math.floor(zan_num / (zan_num + cha_num) * 100)
        end
        v.al_zan:setString(hao_ping_num .. '-')
    else
        v.al_zan:setString('//')
    end

    -- 
    v.node_waiting:setVisible(user_id == 0)

    --
    local is_homeowner = (server_index == self.game_scene.homeowner_server_index)
    local homeowner_is_me = (self.game_scene.homeowner_server_index == self.game_scene.my_server_index)
    v.btn_leave:setVisible(not is_homeowner and homeowner_is_me and user_id ~= 0)

    self:updateReadyButton()
end

function GameWaitingView:onUserOffline(server_index, is_offline)
    if self.all_user_nodes[server_index].sprite_user_head then
        self.all_user_nodes[server_index].sprite_user_head:setColor(is_offline and cc.c3b(125, 125, 125) or cc.WHITE)
    end

    self:updateReadyButton()
end

function GameWaitingView:onUserReady(server_index, is_ready)
    if server_index == self.game_scene.homeowner_server_index then
        self.all_user_nodes[server_index].node_ready_flag:setVisible(true)
    else
        self.all_user_nodes[server_index].node_ready_flag:setVisible(is_ready)
    end

    self:updateReadyButton()
end

function GameWaitingView:onHomeower(server_index)
    for i, v in ipairs(self.all_user_nodes) do
        v.node_homeowner_flag:setVisible(i == server_index)

        -- 
        local is_homeowner = (i == server_index)
        local homeowner_is_me = (self.game_scene.homeowner_server_index == self.game_scene.my_server_index)
        local user_id = self.game_scene:get_user_id(i)
        v.btn_leave:setVisible(not is_homeowner and homeowner_is_me and user_id ~= 0)
    end
end

function GameWaitingView:isAllReady()
    for i=1, 4 do
        -- 除了房主之外，其他的都准备好了，就都准备好了
        if i ~= self.game_scene.homeowner_server_index and not self.game_scene.is_user_ready[i] then
            return false
        end
    end
    return true
end

function GameWaitingView:getReadyCount()
    local count = 1
    for i=1, 4 do
        if i ~= self.game_scene.homeowner_server_index and self.game_scene.is_user_ready[i] then
            count = count + 1
        end
    end
    return count
end

function GameWaitingView:isAllUserReady()
    local total_count = 1
    local count = 1
    for i=1, 4 do
        if i ~= self.game_scene.homeowner_server_index then
            if self.game_scene.all_user_info[i] then
                total_count = total_count + 1

                if self.game_scene.is_user_ready[i] then
                    count = count + 1
                end
            end
        end
    end
    return count, total_count
end

function GameWaitingView:updateReadyButton()
    local btn_state = nil

    local user_count = self.game_scene:getUserCount()
    if self.game_scene.my_server_index == self.game_scene.homeowner_server_index then
        -- 房主的话，如果满桌了，而且其他三人都准备好了，就显示开始游戏按钮，否则显示邀请好友按钮
        if self:isAllReady() then
            btn_state = 'start'
        else
            btn_state = 'invite'
        end

        -- 旁边的开始游戏小按钮
        local count, total_count = self:isAllUserReady()
        if count == total_count and count >= self.min_count and count < 4 then
            self.btn_cancel:setVisible(true)
            self.btn_cancel:loadTextureNormal('game_waiting_start_small.png', ccui.TextureResType.plistType)
        else
            self.btn_cancel:setVisible(false)
        end
    else
        -- 非房主的话，在准备后，显示邀请好友按钮和取消准备按钮
        -- 没有准备好的时候，显示准备按钮，隐藏取消按钮
        if self.game_scene.is_user_ready[self.game_scene.my_server_index] then
            btn_state = 'invite'
        else
            btn_state = 'ready'
        end

        self.btn_cancel:setVisible(self.game_scene.is_user_ready[self.game_scene.my_server_index])
    end

    if btn_state ~= self.btn_state then
        self.btn_state = btn_state

        if btn_state == 'ready' then
            self.btn_text_label:setString('准    备')
            self.btn_text_label:enableOutline(cc.c3b(166, 24, 22), 2)
            self.btn_start_or_invite:loadTextureNormal('btn_advance_2.png', ccui.TextureResType.plistType)
        elseif btn_state == 'start' then
            self.btn_text_label:setString('开始游戏')
            self.btn_text_label:enableOutline(cc.c3b(166, 24, 22), 2)
            self.btn_start_or_invite:loadTextureNormal('btn_advance_2.png', ccui.TextureResType.plistType)
        elseif btn_state == 'invite' then
            self.btn_text_label:setString('邀请好友')
            self.btn_text_label:enableOutline(cc.c3b(28, 118, 14), 2)
            self.btn_start_or_invite:loadTextureNormal('btn_advance_1.png', ccui.TextureResType.plistType)
        end
    end
end

function GameWaitingView:inviteFriends()
    local url, title_text, join_text = self.game_scene:getInviteInfo()
    m_clientmain:get_instance():get_sdk_mgr():share_web(url, title_text, join_text, 0)
end

function GameWaitingView:on_user_chat(chat_type, sub_type, server_index, user_id, msg)
    if self.game_scene.game_state ~= 'waiting' then return end

    -- 
    local v = self.all_user_nodes[server_index]
    if v.node_chat then
        if tolua.cast(v.node_chat, 'Node') then v.node_chat:removeFromParent(true) end
        v.node_chat = nil
    end

    local x, y = v.node_user:getPosition()

    -- 
    local function __show_text__(text)
        local node, iv, text_label = create_text_chat_node(text)
        node:setPosition(x + 40, y + 80)
        self.csb_node:addChild(node, 100)

        v.node_chat = node

        -- 
        local action_1 = cc.DelayTime:create(4)
        local action_2 = cc.FadeTo:create(1, 0)
        local action_3 = cc.CallFunc:create(function()
            v.node_chat:removeFromParent(true)
            v.node_chat = nil
        end)  
        v.node_chat:runAction(cc.Sequence:create(action_1, action_2, action_3))
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
        play_chat_effect(user_info.m_bBoy and 'boy' or 'girl', sound_text.index)
    elseif chat_type == 3 then
        local index = tonumber(sub_type)

        local file_name = string.format('%s/anim/emoji_%d.csb', self.game_scene.scene_config.emoji_type, index)
        local anim_node = createAnimNode(file_name)
        anim_node:setPosition(x, y + 70)
        self.csb_node:addChild(anim_node, 100)

        performWithDelay(anim_node, function() anim_node:removeFromParent(true) end, 1.2)
    else
        if user_id ~= self.game_scene.self_user_id then
            clientmain:get_instance():get_voice_mgr():play_net_record(msg)    

            local anim_node = createAnimNode('game_common_res/anim_play_voice_chat.csb')
            anim_node:setPosition(x + 90, y + 80)
            self.csb_node:addChild(anim_node, 100)

            performWithDelay(anim_node, function() anim_node:removeFromParent(true) end, 4)
        end
    end
end

function GameWaitingView:update_gps_data()
    if not self.game_scene.gps_data then return end
    dump(self.game_scene.gps_data)

    -- gps information
    --[[
    local gps_info = { true, false, false, true }
    local gps_distance = { {0.1, 0.1, 0.1, 0.1}, {0.1, 0.1, 0.1, 0.1}, {0.1, 0.1, 0.1, 0.1}, {0.1, 0.1, 0.1, 0.1} }
    local gps_city = { '北京', '上海', '广州', '深圳' }
    --]]
    local gps_info = self.game_scene.gps_data.get_gps_info or {}
    local gps_distance = self.game_scene.gps_data.distance or {}
    local gps_city = self.game_scene.gps_data.city or {}
    --]]

    for server_index=1, 4 do
        self.all_user_nodes[server_index].node_warning_bg:setVisible(false)
    end

    local all_user_info = self.game_scene.all_user_info

    -- 
    for server_index=1, 4 do
        if gps_info[server_index] then
            for i=1, 4 do
                if server_index ~= i and gps_info[i] and all_user_info[i] and gps_distance[server_index][i] <= 0.1 then
                    self.all_user_nodes[i].node_warning_bg:setVisible(true)
                end
            end
        end
    end
end

return GameWaitingView
