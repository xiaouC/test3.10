-- ./app/platform/room/new_view/new_hall_scene.lua

local m_clientmain = require 'app.platform.room.clientmain'
local m_def = require 'app.platform.room.module.basicnotifydef'

local default_marquee_msg = '友间麻将旨在为玩家提供一流的线上家乡游戏，让玩家体验最纯粹的地方游戏，请玩家勿做它用。'

local model_base = require 'app.platform.common.model_base'
local new_hall_scene = class('new_hall_scene', model_base)
function new_hall_scene:ctor(init_content_tpye)
    self.csb_file = 'hall_res/hall/new_hall_scene.csb'

    -- 
    self.next_static_marquee_index = 1
    self.static_marquee_list = { default_marquee_msg, }          -- 比如一些常驻的系统公告，不能删除，会循环播放，但优先级较低
    self.dynamic_marquee_list = {}      -- 比如玩家聊天，世界事件的触发等，滚屏后就会被移除，优先级较高

    self.current_active_index = 1

    -- 公会胜局榜数据
    self.recv_guild_rank_data = {
        my_rank = -1,
        my_count = 4656,
        rank_list = {},
    }

    -- 手气榜数据
    self.recv_lucky_data = {
        is_valid = false,
        comment_list = {},
    }

    -- 
    model_base.ctor(self)
end

function new_hall_scene:clear()
    if m_clientmain:get_instance():get_push_mgr():get_listener_mgr() then
        m_clientmain:get_instance():get_push_mgr():get_listener_mgr():BsRemoveEventListener(m_def.NOTIFY_PUSH_EVENT, self) 
    end

    if m_clientmain:get_instance():get_game_manager():get_event_mgr() then
        m_clientmain:get_instance():get_game_manager():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_GAME_EVENT, self) 
    end

    if m_clientmain:get_instance():get_room_mgr():get_event_mgr() then
        m_clientmain:get_instance():get_room_mgr():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_ROOM_EVENT, self) 
    end

    -- db.CCFactory:getInstance():clear(true)

    -- 
    model_base.clear(self)
end

function new_hall_scene:enter()
    model_base.enter(self)

    -- 
    if G_is_WXcome == true then
        G_is_WXcome = false
        api_show_Msg_Box('您选择的包间中的好友已开始游戏，邀请你的好友，开始新的游戏吧!')
    end

    -- 在录像界面
    if G_Hall_State == 1 then
        G_Hall_State = 0
        self:popupNode('app.platform.room.new_view.new_game_record')
    end

    -- 
    if GAME_TEST ~= true then
        if G_is_close == false then
            self:onShowAnnouncement()
        end
    end

    self:onCheckInviteUser()

    self:checkDailyReward()
end

function new_hall_scene:onShowAnnouncement()
    self.user_reg_time = 0

    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info() 
    if user_info and user_info.m_reg_time then
        local record_time = g_json.decode(UserData:get_userinfo_regtime()) or {}
        self.user_reg_time = record_time[tostring(user_info.m_uid)] or 0

        local function __save_user_reg_time__()
            local record_time = g_json.decode(UserData:get_userinfo_regtime()) or {}
            record_time[tostring(user_info.m_uid)] = self.user_reg_time
            dump(record_time)
            UserData:set_userinfo_regtime(g_json.encode(record_time))
        end

        if self.user_reg_time == 0 then
            self.user_reg_time = tonumber(user_info.m_reg_time)
            __save_user_reg_time__()

            self:popupNode('app.platform.room.new_view.notice_view')
        else
            local old_time = os.date("*t", tonumber(self.user_reg_time))
            local new_time = os.date("*t", tonumber(user_info.m_reg_time))

            if new_time.year - old_time.year == 1 or new_time.month - old_time.month == 1 or new_time.day - old_time.day == 1 then
                self.user_reg_time = tonumber(user_info.m_reg_time)
                __save_user_reg_time__()

                self:popupNode('app.platform.room.new_view.notice_view')
            end
        end
    end
end

-- 没加入公会，检测是否点击链接进来
function new_hall_scene:onCheckInviteUser()
    -- 已加入公会不用检测
    local join_flag = m_clientmain:get_instance():get_user_mgr():check_user_join_guild() 
    if join_flag == true then return end

    -- 没有桌号，表示不是点链接进来
    local user_desk_no = m_clientmain:get_instance():get_sdk_mgr():get_user_desk_no() 
    if user_desk_no == nil then return end

    -- 国内外苹果，游客登录都不能点链接进来
    if G_isGuest == true then return m_clientmain:get_instance():get_sdk_mgr():set_user_desk_no(nil) end

    -- 
    if self.Halljoin_layer ~= nil then self.Halljoin_layer:onClose() end
    self.Halljoin_layer = require("app.platform.room.new_view.halljoinguildscene").new(self, 2)
    self:addChild(self.Halljoin_layer, 14)
end

function new_hall_scene:checkDailyReward()
    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info() 
    dump(user_info)
    if user_info and user_info.m_reward and #user_info.m_reward > 0 then
        self:popupNode('app.platform.room.new_view.vip_month_receive_reward')
    end
end

function new_hall_scene:initViews()
    model_base.initViews(self)

    -- background color
    local bg_layer = createBackgroundLayer(
            cc.c4b(0, 0, 0, 0),
            true,
            function(touch, event) return self:on_touch_began(touch, event) end,
            function(touch, event) self:on_touch_moved(touch, event) end,
            function(touch, event) self:on_touch_ended(touch, event) end
        )
    self:addChild(bg_layer, -1)

    -- 
    G_in_Hall = true
    local node_text = self.csb_node:getChildByName('node_text')

    -- 
    self.down_alpha_button_index = nil
    self.down_alpha_sprite = nil

    -- 这个顺序很重要，这是如果有重叠区域的时候，优先点击的是谁
    self.alpha_button_config = {
        [1] = {
            name = 'join_room',
            center_pos = { x = 1020, y = 235 },
            radius = 130,
            onclick = function(v)
                if v.is_back_room then
                    G_in_Hall = false
                    --api_show_loading_ext(0.5)
                    --m_clientmain:get_instance():get_user_mgr():request_user_info()
                    local userinfo = m_clientmain:get_instance():get_user_mgr():get_user_info()
                    if userinfo.m_desk_info ~= nil then
                        if userinfo.m_desk_info.m_desk_room_no ~= nil then
                            m_clientmain:get_instance():get_room_mgr():query_desk_info(tonumber(userinfo.m_desk_info.m_desk_room_no))
                        end
                    end
                else
                    if self:UserCanPlay() then
                        -- api_show_loading_ext(0.5)
                        -- m_clientmain:get_instance():get_user_mgr():request_user_info()
                        self:popupNode('app.platform.room.new_view.join_room_view')
                    else
                        -- 加入公会再说
                        if self.Halljoin_layer then self.Halljoin_layer:onClose() end
                        self.Halljoin_layer = require("app.platform.room.new_view.halljoinguildscene").new(self, 2)
                        self:addChild(self.Halljoin_layer, 14)
                    end
                end
            end,
            sprite = self.csb_node:getChildByName('sprite_join_room'),
            is_enable = true,
            is_back_room = false,
        },
        [2] = {
            name = 'match_room',
            center_pos = { x = 1020, y = 505 },
            radius = 130,
            onclick = function(v) api_show_Msg_Tip('努力开发中，敬请期待') end,
            sprite = self.csb_node:getChildByName('sprite_match_room'),
            is_enable = true,
        },
        [3] = {
            name = 'guild_room',
            center_pos = { x = 1210, y = 375 },
            radius = 130,
            onclick = function(v) api_show_Msg_Tip('努力开发中，敬请期待') end,
            sprite = self.csb_node:getChildByName('sprite_guild_room'),
            is_enable = true,
        },
        [4] = {
            name = 'create_room',
            center_pos = { x = 820, y = 375 },
            radius = 140,
            onclick = function(v)
                G_in_Hall = false
                if self:UserCanPlay() then
                    --api_show_loading()
                    m_clientmain:get_instance():get_user_mgr():request_user_info()
                    m_clientmain:get_instance():get_room_mgr():request_game_list()
                    m_clientmain:get_instance():get_room_mgr():request_desk_owner()
                else
                    -- 加入公会再说
                    if self.Halljoin_layer then self.Halljoin_layer:onClose() end
                    self.Halljoin_layer = require("app.platform.room.new_view.halljoinguildscene").new(self, 1)
                    self:addChild(self.Halljoin_layer, 14)
                end
            end,
            sprite = self.csb_node:getChildByName('sprite_create_room'),
            is_enable = true,
        },
    }

    --[[
    -- test
    for _, v in ipairs(self.alpha_button_config) do
        local layer_color = cc.LayerColor:create(cc.c4b(255, 0, 0, 125), v.radius * 2, v.radius * 2)
        layer_color:setPosition(v.center_pos.x - v.radius, v.center_pos.y - v.radius)
        self:addChild(layer_color)
    end
    --]]

    --------------------------------------------------------------------------------------------------------------------------------------
    -- 排行榜
    self.node_rank_lucky_hide_pos = { x = -345, y = 325 }
    self.node_rank_lucky_show_pos = { x = 350, y = 325 }
    self.node_rank_lucky = cc.CSLoader:createNode('hall_res/hall/hall_rank_lucky.csb')
    self.node_rank_lucky:setPosition(self.node_rank_lucky_hide_pos.x, self.node_rank_lucky_hide_pos.y)
    self:addChild(self.node_rank_lucky)

    self.is_rank_list_hide = true
    self.is_down_blank_area = false
    self.rank_lucky_background = self.node_rank_lucky:getChildByName('background')

    button('btn_rank_list', function() self:changeRankListVisible() end, self.node_rank_lucky)

    -- radio button group: [公会胜局榜, 昨日手气最佳]
    local rb_group = ccui.RadioButtonGroup:create()
    self.node_rank_lucky:getChildByName('node_radio_group'):addChild(rb_group)

    local function __create_radio_button__(img_normal, img_selected, offset_x, onchanged)
        local rb = ccui.RadioButton:create(img_normal, img_normal, img_selected, img_normal, img_selected, ccui.TextureResType.plistType)
        rb:setPosition(offset_x, 0)
        rb_group:addChild(rb)
        rb_group:addRadioButton(rb)

        -- 
        rb:addEventListener(function(_, event_type)
            if event_type ~= ccui.RadioButtonEventType.selected then return end
            if onchanged then onchanged() end
        end)

        return rb
    end

    local rb_left = __create_radio_button__('hall_button_guild_rank_2.png', 'hall_button_guild_rank_1.png', -125, function() m_clientmain:get_instance():get_rank_mgr():requst_win_rank(1) end)     -- 公会胜局榜
    local rb_right = __create_radio_button__('hall_button_best_lucky_2.png', 'hall_button_best_lucky_1.png', 125, function() m_clientmain:get_instance():get_rank_mgr():request_luck() end)         -- 昨日手气最佳

    -- 
    local node_rank = self.node_rank_lucky:getChildByName('node_rank')
    local node_lucky = self.node_rank_lucky:getChildByName('node_lucky')
    rb_group:addEventListener(function(rb_selected, index, event_type) node_rank:setVisible(rb_selected == rb_left) node_lucky:setVisible(rb_selected == rb_right) end)
    rb_group:setSelectedButton(rb_left)

    -- 更新公会胜局榜
    self:appendView('update_guild_rank', function()
        if not tolua.cast(node_rank, 'Node') then return end

        -- 在最上方，自己的排名，以及对战局数
        local node_no_rank = node_rank:getChildByName('node_no_rank')
        node_no_rank:removeAllChildren()

        local al_rank_myself = node_rank:getChildByName('al_rank_myself')

        if self.recv_guild_rank_data.my_rank == -1 or self.recv_guild_rank_data.my_rank > 100 then
            local rank_text = (self.recv_guild_rank_data.my_rank == -1 and '未上榜' or '100+')

            local rank_label = cc.Label:createWithTTF(rank_text, 'font/jxk.TTF', 32)
            rank_label:setColorTextureIndex(4)
            rank_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
            rank_label:setAnchorPoint(0, 0.5)
            rank_label:enableShadow()

            node_no_rank:addChild(rank_label)

            node_no_rank:setVisible(true)
            al_rank_myself:setVisible(false)
        else
            al_rank_myself:setString(tostring(self.recv_guild_rank_data.my_rank))

            node_no_rank:setVisible(false)
            al_rank_myself:setVisible(true)
        end

        node_rank:getChildByName('al_play_count'):setString(tostring(self.recv_guild_rank_data.my_count))

        -- 排名列表
        local lv_rank_content = node_rank:getChildByName('lv_rank')
        lv_rank_content:setScrollBarEnabled(false)
        lv_rank_content:removeAllChildren()
        for i, v in ipairs(self.recv_guild_rank_data.rank_list or {}) do
            local item_csb_file = (i == self.recv_guild_rank_data.my_rank and 'hall_res/hall/hall_rank_item_myself.csb' or 'hall_res/hall/hall_rank_item_others.csb')
            --local item_csb_file = (i == 1 and 'hall_res/hall/hall_rank_item_myself.csb' or 'hall_res/hall/hall_rank_item_others.csb')

            local item_widget, item_node = createWidget(item_csb_file, 632, 102)
            lv_rank_content:addChild(item_widget)

            -- 排名
            item_node:getChildByName('al_rank'):setString(tostring(i))

            -- 头像
            local head_sprite = createUserHeadSprite({m_bLogoID = v.head_id, m_headurl = v.head_url}, 0.7)
            item_node:getChildByName('node_head'):addChild(head_sprite)

            -- 用户名和ID
            label('text_user_name', v.user_name, item_node)
            label('text_user_id', 'ID：' .. v.user_id, item_node)

            -- 局数
            item_node:getChildByName('al_play_count'):setString(tostring(v.count))
        end
        -- lv_rank_content:requestDoLayout()
        lv_rank_content:forceDoLayout()
        lv_rank_content:jumpToTop()
    end)

    --------------------------------------------------------------------------------------------------------------------
    local node_content = node_lucky:getChildByName('node_content')
    self.text_zan_count = node_content:getChildByName('text_zan_count')
    self.btn_zan = button('btn_zan', function()
        m_clientmain:get_instance():get_rank_mgr():request_like()

        self.btn_zan:setEnabled(false)
        self.text_zan_count:setVisible(true)
        self.text_zan_count:setString(tostring(self.recv_lucky_data.zan_count + 1))
    end, node_content)
    self.btn_zan:setEnabled(false)
    self.text_zan_count:setVisible(true)
    local btn_play = button('btn_play', function() api_show_Msg_Tip("努力开发中，敬请期待") end, node_content)

    local input_text = node_content:getChildByName('input_text')
    button('btn_send', function()
        local leave_msg = input_text:getString()
        if #leave_msg == 0 then return api_show_Msg_Tip('请输入文字') end
        if not CheckSensitiveWords(leave_msg) then return api_show_Msg_Box('您的帐号输入了不合法词汇！') end

        m_clientmain:get_instance():get_rank_mgr():request_comments(leave_msg)

        input_text:setString('')
    end, node_content)

    -- 更新手气榜
    self:appendView('update_lucky', function()
        if not tolua.cast(node_lucky, 'Node') then return end

        local node_content = node_lucky:getChildByName('node_content')
        local node_tips = node_lucky:getChildByName('node_tips')
        if not self.recv_lucky_data.is_valid then
            node_content:setVisible(false)
            node_tips:setVisible(true)

            node_tips:removeAllChildren()

            -- 
            local text_label = cc.Label:createWithTTF('数据正在统计，明日开启。', 'font/jxk.TTF', 30)
            text_label:setColorTextureIndex(5)
            text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
            text_label:setAnchorPoint(0.5, 0.5)
            text_label:enableOutline(cc.c3b(186, 54, 52), 2)

            node_tips:addChild(text_label)

            return
        end

        --
        node_content:setVisible(true)
        node_tips:setVisible(false)

        -- 
        self.btn_zan:setEnabled(self.recv_lucky_data.can_zan)
        self.text_zan_count:setVisible(not self.recv_lucky_data.can_zan)
        if not self.recv_lucky_data.can_zan then
            self.text_zan_count:setString(tostring(self.recv_lucky_data.zan_count))
        end

        -- name, id, win style
        label('text_name', self.recv_lucky_data.user_name, node_content)
        label('text_id', 'ID: ' .. tostring(self.recv_lucky_data.user_id), node_content)
        label('text_win_style', self.recv_lucky_data.win_style, node_content)

        -- head
        node_content:getChildByName('node_head'):removeAllChildren()
        local head_sprite = createUserHeadSprite({m_bLogoID = self.recv_lucky_data.head_id, m_headurl = self.recv_lucky_data.head_url}, 1)
        node_content:getChildByName('node_head'):addChild(head_sprite)

        -- 战绩
        node_content:getChildByName('al_zhanji'):setString(tostring(self.recv_lucky_data.score))

        -- 
        local node_card_list = node_content:getChildByName('node_card_list')
        local game_type_config = {
            [1] = {
                sprite_file = 'hall_res/hall/btn_lookvideo.png',
                process_func = function() self:showMahjongCardList(node_card_list) end,
            },
            [2] = {
                sprite_file = 'hall_res/hall/btn_lookvideo_nn.png',
                process_func = function() self:showNiuNiuCardList(node_card_list) end,
            },
            [3] = {
                sprite_file = 'hall_res/hall/btn_lookvideo_ddz.png',
                process_func = function() self:showDouDiZhuCardList(node_card_list) end,
            },
            [4] = {
                sprite_file = 'hall_res/hall/btn_lookvideo_zp.png',
                process_func = function() end,
            },
        }

        local v = game_type_config[self.recv_lucky_data.game_type]
        if v then
            btn_play:loadTextureNormal(v.sprite_file)
            v.process_func()
        end
    end)

    -- 更新手气榜的评论列表
    self:appendView('update_lucky_comment_list', function()
        if not tolua.cast(node_lucky, 'Node') then return end

        local node_content = node_lucky:getChildByName('node_content')
        local lv_chat_content = node_content:getChildByName('lv_chat')
        lv_chat_content:setScrollBarEnabled(false)
        lv_chat_content:removeAllChildren()
        for _, v in ipairs(self.recv_lucky_data.comment_list or {}) do
            local item_widget, item_node = createWidget('hall_res/hall/hall_chat_item.csb', 650, 65)
            lv_chat_content:addChild(item_widget)

            local head_sprite = cc.Sprite:create('hall_res/head/head_7.png')
            item_node:getChildByName('node_head'):addChild(head_sprite)

            label('text_name', v.user_name, item_node)
            label('text_id', 'ID: ' .. v.user_id, item_node)

            local iv = ccui.ImageView:create('hall_comment_background.png', ccui.TextureResType.plistType)
            iv:setAnchorPoint(0, 0.5)
            iv:setScale9Enabled(true)
            iv:setCapInsets(cc.rect(16, 6, 6, 5))
            item_node:getChildByName('node_chat'):addChild(iv)

            local text_label = cc.Label:createWithTTF(v.comment_text .. v.comment_text, 'font/jxk.TTF', 20, cc.size(420, 0))
            text_label:setAnchorPoint(0, 0.5)
            text_label:setPosition(15, -2)
            item_node:getChildByName('node_chat'):addChild(text_label)

            local text_size = text_label:getContentSize()
            iv:setContentSize(cc.size(text_size.width + 22, text_size.height + 8))
        end
        lv_chat_content:requestDoLayout()
    end)

    ----------------------------------------------------------------------------------------------------------------------------------
    local function __hall_button__(name, onclick, parent_node)
        return button(name, function()
            if not self.is_rank_list_hide then self:changeRankListVisible() end
            if onclick then onclick() end
        end, parent_node)
    end
    ----------------------------------------------------------------------------------------------------------------------------------
    -- 购买按钮
    __hall_button__('btn_buy', function() self:bugRoomCard() end, self.csb_node)  
    -- 免费领取房卡按钮
    __hall_button__('btn_free_room_card', function() m_clientmain:get_instance():get_welfare_mgr():request_gift_info() end, self.csb_node)   
    -- 录像
    __hall_button__('btn_record', function() self:popupNode('app.platform.room.new_view.new_game_record') end, self.csb_node)  
    -- 公告
    __hall_button__('btn_notice', function() self:popupNode('app.platform.room.new_view.notice_view') end, self.csb_node)  
    -- 设置
    __hall_button__('btn_settings', function() self:popupNode('app.platform.room.new_view.settings_view') end, self.csb_node)  
    -- 头像
    __hall_button__('btn_head_frame', function() self:popupNode('app.platform.room.new_view.new_hall_personal') end, self.csb_node)  
    -- 胜局任务
    __hall_button__('btn_task', function()
        self.current_active_index = 3
        m_clientmain:get_instance():get_welfare_mgr():request_task_list()
    end, self.csb_node)  
    -- 呼朋唤友
    __hall_button__('btn_invite', function()
        self.current_active_index = 1
        m_clientmain:get_instance():get_welfare_mgr():request_gift_info()
    end, self.csb_node)  
    -- 每日活跃
    __hall_button__('btn_daily', function()
        self.current_active_index = 2
        m_clientmain:get_instance():get_welfare_mgr():request_task_list()
    end, self.csb_node)
    -- 实名认证
    self.btn_real_name = __hall_button__('btn_real_name', function()
        if not tolua.cast(self.id_verified_view, 'Node') then
            self.id_verified_view = self:popupNode('app.platform.room.new_view.id_verified_view')
        end
    end, self.csb_node)

    -- 
    self.label_game_name = label('text_game_name', '', self.node_rank_lucky)

    -----------------------------------------------------------------------------------------------------------------------------------------------------
    -- user info
    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info() or {}

    -- user head, vip
    local head_sprite = createUserHeadSprite(user_info, 1)
    self.csb_node:getChildByName('node_head'):addChild(head_sprite)
    self.csb_node:getChildByName('btn_head_frame'):getChildByName('hall_vip_icon_1'):setVisible(tonumber(user_info.m_vip_level) > 0)

    -- 
    label('text_user_name', user_info.m_nickname or '', node_text)
    label('text_user_id', string.format("ID: %d", tonumber(user_info.m_uid or 0)), node_text)
    label('text_room_card', tostring(user_info.m_roomcard or 0), node_text)
    label('text_ticket', tostring(user_info.m_voucher or 0), node_text)
    self.label_title = label('text_guild_name', '', node_text)
    self.label_guild_id = label('text_guild_id', '', node_text)

    self:updateGuildNameAndID(user_info)

    -- 跑马灯
    self:startMarquee()

    -- 
    require 'dragonbones'
    local factory = db.CCFactory:getInstance()

    if not G_girl_dragon_bone_data then
        G_girl_dragon_bone_data = factory:loadDragonBonesData('hall_res/hall/Girl_ske.json')
    end

    if G_girl_dragon_bone_data then
        factory:loadTextureAtlasData('hall_res/hall/Girl_tex.json')

        local armatureNames = G_girl_dragon_bone_data:getArmatureNames()
        local armatureDisplay = factory:buildArmatureDisplay(armatureNames[1])
        local armature = armatureDisplay:getArmature()
        local animation = armatureDisplay:getAnimation()
        local animationNames = armatureDisplay:getAnimation():getAnimationNames()
        armatureDisplay:addTo(self.csb_node:getChildByName('node_girl'))
        animation:play(animationNames[1], 0)
    end

    -- 公会公告
    local notice_content_visible = true

    local node_notice_qipao = self.csb_node:getChildByName('hall_notice_qipao')
    local node_notice_content = self.csb_node:getChildByName('node_notice_content')
    button('btn_girl_notice', function()
        notice_content_visible = not notice_content_visible
        node_notice_qipao:setVisible(not notice_content_visible)
        node_notice_content:setVisible(notice_content_visible)
    end, self.csb_node)
    node_notice_content:setVisible(false)   -- 第一次在赋值后才显示

    local notice_label = cc.Label:createWithTTF('', 'font/fzzyjt.ttf', 20, cc.size(300, 0))
    notice_label:setAnchorPoint(0, 0)
    notice_label:setPosition(120, 150)
    node_notice_content:addChild(notice_label)

    self:appendView('update_guild_notice', function(notice_text)
        local text = '会长给您发送了消息：\n' .. notice_text
        --local text = '会长给您发送了消息：\n亲爱的会员，友间麻将全新改版了，优惠多多，赶紧成为VIP，享受永久福利吧。月卡好礼同时上线，早买早享受~'

        notice_label:setString(text)

        local text_size = notice_label:getContentSize()

        local notice_bg = node_notice_content:getChildByName('iv_notice_bg')
        notice_bg:setContentSize(cc.size(342, text_size.height + 20))

        -- 避免第一次
        node_notice_content:setVisible(notice_content_visible)
    end)
end

function new_hall_scene:updateGuildNameAndID(user_info)
    if user_info.m_ghinfo then
        if user_info.m_ghinfo.m_ghname then
            self.label_title:setString(user_info.m_ghinfo.m_ghname)
        end

        if user_info.m_ghinfo.m_proid then
            self.label_guild_id:setString(string.format("公会ID: %d", tonumber(user_info.m_ghinfo.m_proid or 0)))
            self.label_game_name:setString(user_info.m_ghinfo.m_gamename)
        end
    end
end

function new_hall_scene:changeRankListVisible()
    self.node_rank_lucky:stopAllActions()

    local mv_action = cc.MoveTo:create(0.1, self.is_rank_list_hide and self.node_rank_lucky_show_pos or self.node_rank_lucky_hide_pos)
    self.node_rank_lucky:runAction(mv_action)

    self.is_rank_list_hide = not self.is_rank_list_hide
end

function new_hall_scene:on_touch_began(touch, event)
    local touch_pos = touch:getLocation()
    for index, v in ipairs(self.alpha_button_config) do
        if v.is_enable then
            local distance = cc.pGetDistance(touch_pos, v.center_pos)
            if distance <= v.radius then
                self.down_alpha_button_index = index
                self.down_alpha_sprite = v.sprite

                v.sprite:stopAllActions()
                v.sprite:runAction(cc.ScaleTo:create(0.05, 0.9))

                break
            end
        end
    end

    -- 如果没有点在这四个按钮上
    if not self.down_alpha_button_index and not self.is_rank_list_hide then
        local size = self.rank_lucky_background:getContentSize()
        local pos = self.rank_lucky_background:convertToNodeSpace(touch_pos)
        local rc = { x = 0, y = 0, width = size.width, height = size.height }
        if not cc.rectContainsPoint( rc, pos) then
            self.is_down_blank_area = true
        end
    end

    return true
end

function new_hall_scene:on_touch_moved(touch, event)
end

function new_hall_scene:on_touch_ended(touch, event)
    -- 如果没有点在这四个按钮上，处于显示状态，并且在按下的时候按的是空白区域
    -- 那么，如果弹起的时候，也是在空白区域，就隐藏吧
    if not self.down_alpha_button_index and not self.is_rank_list_hide and self.is_down_blank_area then
        local touch_pos = touch:getLocation()

        local size = self.rank_lucky_background:getContentSize()
        local pos = self.rank_lucky_background:convertToNodeSpace(touch_pos)
        local rc = { x = 0, y = 0, width = size.width, height = size.height }
        if not cc.rectContainsPoint( rc, pos) then
            self.is_down_blank_area = false

            self:changeRankListVisible()
        end

        self.is_down_blank_area = false
    end

    -- 
    if self.down_alpha_button_index then
        local touch_pos = touch:getLocation()

        for index, v in ipairs(self.alpha_button_config) do
            if v.is_enable then
                local distance = cc.pGetDistance(touch_pos, v.center_pos)
                if distance <= v.radius then
                    if self.down_alpha_button_index == index then
                        v:onclick()
                    end

                    break
                end
            end
        end

        -- 
        self.down_alpha_sprite:stopAllActions()
        self.down_alpha_sprite:runAction(cc.ScaleTo:create(0.05, 1.0))

        self.down_alpha_sprite = nil
        self.down_alpha_button_index = nil
    end
end

function new_hall_scene:initDataFromServer()
    model_base.initDataFromServer(self)

    -- 
    m_clientmain:get_instance():get_rank_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_RANK_EVENT, function(event) self:onRankEvent(event) end) 
    m_clientmain:get_instance():get_user_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_USER_EVENT, function(event) self:onUserEvent(event) end)
    m_clientmain:get_instance():get_game_manager():get_event_mgr():BsAddEventListener(m_def.NOTIFY_GAME_EVENT, self, function(event) self:onGameEvent(event) end)
    m_clientmain:get_instance():get_welfare_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_TASK_EVENT, function(event) self:onTaskEvent(event) end)
    m_clientmain:get_instance():get_keepalive_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_KEEPALIVE_EVENT, function(event) self:onHeartBeatEvent(event) end)
    m_clientmain:get_instance():get_notice_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_NOTICE_EVENT, function(event) self:onGuildNoticeEvent(event) end)
    m_clientmain:get_instance():get_active_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_ACTIVITY_SPECIAL_EVENT, function(event) self:onSpecialActivityEvent(event) end)
    m_clientmain:get_instance():get_push_mgr():get_listener_mgr():BsAddEventListener(m_def.NOTIFY_PUSH_EVENT, self, function(event) self:onPushEvent(event) end)
    m_clientmain:get_instance():get_room_mgr():get_event_mgr():BsAddEventListener(m_def.NOTIFY_ROOM_EVENT, self, function(event) self:onRoomEvent(event) end)

    -- 在这里只请求公会胜局榜的数据，因为一开始，显示的界面只是公会胜局榜，
    m_clientmain:get_instance():get_rank_mgr():requst_win_rank(1)
    --m_clientmain:get_instance():get_rank_mgr():request_luck()

    m_clientmain:get_instance():get_room_mgr():request_game_list()
    m_clientmain:get_instance():get_room_mgr():request_desk_owner()

    -- 领取打赏
    m_clientmain:get_instance():get_user_mgr():request_user_getaward_query()  

    -- 更新房卡，礼券
    m_clientmain:get_instance():get_user_mgr():request_user_info()

    -- 品牌值,牌友口碑,常玩牌友
    m_clientmain:get_instance():get_user_mgr():request_userbrand_query()
    m_clientmain:get_instance():get_user_mgr():request_uservalue_query()
    m_clientmain:get_instance():get_user_mgr():request_oftenplay_query()

    -- 公会公告
    m_clientmain:get_instance():get_notice_mgr():request_guild_notice()

    -- 推送公告
    m_clientmain:get_instance():get_push_mgr():get_sys_notice()

    -- 公会会长设置的跑马灯公告
    m_clientmain:get_instance():get_notice_mgr():request_marquee_notice()

    m_clientmain:get_instance():get_active_mgr():request_active_task_list()

    m_clientmain:get_instance():get_user_mgr():request_user_identifyinfo()
    -- 
    if G_is_GameOver == true then
        G_is_GameOver = false

        local game_list = m_clientmain:get_instance():get_room_mgr():get_game_list()
        dump(game_list)
        if not game_list then return api_show_Msg_Tip('正在获取游戏列表，请稍后...') end
        if table.getn(game_list) <= 0 then return api_show_Msg_Tip('该公会还没有游戏') end

        self:showCreateRoomView(game_list)
    end
end

function new_hall_scene:onRankEvent(event)
    if not tolua.cast(self.csb_node, 'Node') then return end
    if not event or not event.args then return end

    if event.args.event_data.ret ~= 0 then return api_show_Msg_Tip(event.args.event_data.desc) end

    local data = event.args.event_data.data
    local rank_events = {
        --[m_def.NOTIFY_RANK_EVENT_LIKE] = function()
        --    m_clientmain:get_instance():get_rank_mgr():request_comments_list(1) 
        --end,
        [m_def.NOTIFY_RANK_EVENT_COMMENTS] = function()
            self.btn_zan:setEnabled(false)
            self.text_zan_count:setVisible(true)
            self.text_zan_count:setString(tostring(self.recv_lucky_data.zan_count + 1))

            m_clientmain:get_instance():get_rank_mgr():request_comments_list(1)  
        end,
        [m_def.NOTIFY_RANK_EVENT_COMMENTS_LIST] = function()
            self.recv_lucky_data.comment_list = {}

            for _, v in ipairs(data or {}) do
                table.insert(self.recv_lucky_data.comment_list, {
                    head_id = 1,
                    head_url = v.m_head_url,
                    user_name = v.m_name,
                    user_id = v.m_uid,
                    comment_text = v.m_conent,
                })
            end

            self:updateView('update_lucky_comment_list')
        end,
        [m_def.NOTIFY_RANK_EVENT_LUCK_INFO] = function()
            -- local is_valid = ((not G_is_close) and (not data))
            dump(data)

            self.recv_lucky_data.is_valid = data and true or false
            self.recv_lucky_data.head_id = 0

            if data then
                self.recv_lucky_data.can_zan = (data.m_good ~= 1)
                self.recv_lucky_data.zan_count = data.m_like
                self.recv_lucky_data.user_name = data.m_name
                self.recv_lucky_data.user_id = data.m_uid
                self.recv_lucky_data.score = data.m_score
                self.recv_lucky_data.win_style = data.m_desc
                self.recv_lucky_data.head_id = 0
                self.recv_lucky_data.head_url = data.m_head_url
                self.recv_lucky_data.game_type = data.m_game_type
                self.recv_lucky_data.block_info = data.m_blockinfo
                --self.recv_lucky_data.hand_card = data.m_handcard
                self.recv_lucky_data.win_card = data.m_win_card
                self.recv_lucky_data.ghost_mode = data.m_king_mode
                self.recv_lucky_data.ghost_cards = data.m_king_card
                self.recv_lucky_data.game_id = data.m_game_id
                self.recv_lucky_data.is_banker = data.m_banker

                -- 麻将
                if data.m_game_type == 1 then self.recv_lucky_data.hand_card = data.m_handcard end

                -- 牛牛
                if data.m_game_type == 2 then self.recv_lucky_data.hand_card = data.m_handcard.list end

                -- 斗地主
                if data.m_game_type == 3 then self.recv_lucky_data.hand_card = data.m_handcard.list end
            end

            self:updateView('update_lucky')
        end,
        [m_def.NOTIFY_RANK_EVENT_SCORE_RANK] = function() end,
        [m_def.NOTIFY_RANK_EVENT_WIN_RANK] = function()
            self.recv_guild_rank_data = {
                my_rank = (data.m_ower_rank.m_win > 0 and data.m_ower_rank.m_ranking or -1),
                my_count = data.m_ower_rank.m_win,
                rank_list = {},
            }

            for _, v in ipairs(data.m_list or {}) do
                table.insert(self.recv_guild_rank_data.rank_list, {
                    user_name = v.m_name,
                    user_id = v.m_id,
                    head_id = 0,
                    head_url = v.m_head_url,
                    count = v.m_win,
                })
            end

            self:updateView('update_guild_rank')
        end,
    }

    local fn = rank_events[event.args.event_id]
    if fn then fn() end
end

local function __check_event__(event, ignore_ids, pass_ids, cb)
    if not event or not event.args then return false end

    if event.args.event_data.ret ~= 0 then
        if table.hasValue(pass_ids or {}, event.args.event_id) then return true end

        if table.hasValue(ignore_ids or {}, event.args.event_id) then return false end

        if event.args.event_data.desc and event.args.event_data.desc ~= '' then
            Msg:showMsgBox(3, event.args.event_data.desc, cb)

            return false
        end
    end

    return true
end

function new_hall_scene:onUserEvent(event)
    if not __check_event__(event, {m_def.NOTIFY_USER_EVENT_GETAWARD_INFO}) then return end

    local data = event.args.event_data.data
    local user_events = {
        [m_def.NOTIFY_USER_EVENT_UPDATE_GHINFO] = function()
            if data.m_ghname ~= nil then self.csb_node:getChildByName('text_guild_name'):setString(data.m_ghname) end

            if data.m_proid ~= nil then
                local text_guild_id_node = self.csb_node:getChildByName('text_guild_id')
                local guild_id_string = string.format("公会ID: %d", tonumber(data.m_proid or 0))
                text_guild_id_node:setString(guild_id_string)
                text_guild_id_node:setVisible(true)
            end
        end,
        [m_def.NOTIFY_USER_EVENT_UPDATE_INFO] = function()
            local userinfo = m_clientmain:get_instance():get_user_mgr():get_user_info()
            if userinfo ~= nil then
                self.csb_node:getChildByName('node_text'):getChildByName('text_room_card'):setString(tostring(userinfo.m_roomcard))
                self.csb_node:getChildByName('node_text'):getChildByName('text_ticket'):setString(tostring(userinfo.m_voucher or 0))
            end
        end,
        [m_def.NOTIFY_USER_EVENT_GETAWARD_INFO] = function()
            local userinfo = m_clientmain:get_instance():get_user_mgr():get_user_info()
            if userinfo ~= nil then
                self.csb_node:getChildByName('node_text'):getChildByName('text_room_card'):setString(tostring(userinfo.m_roomcard))
                self.csb_node:getChildByName('node_text'):getChildByName('text_ticket'):setString(tostring(userinfo.m_voucher or 0))
            end

            local label_string = ''
            for i=1, 7 do
                if data[i] then
                    local data_string = string.format('恭喜收到土豪"%s",打赏的%d张房卡,快继续游戏吧。\n', tostring(data[i].nickname), tonumber(data[i].roomcard))
                    label_string = string.format('%s%s', label_string, data_string)
                end
            end
            api_show_Msg_Box(label_string)
        end,
        [m_def.NOTIFY_USER_EVENT_USERBRAND_INFO] = function()
            self.userbrand = data
        end,
        [m_def.NOTIFY_USER_EVENT_USERVALUE_INFO] = function()
            self.uservalue = data
        end,
        [m_def.NOTIFY_USER_EVENT_OFTENPLAY_INFO] = function()
            self.oftenplay = data
        end,
        [m_def.NOTIFY_USER_EVENT_USER_IDENTIFY_INFO] = function()
            self.btn_real_name:setVisible(data.is_pd == 0)
        end,
        [m_def.NOTIFY_USER_EVENT_USER_IDENTIFY_RESULT] = function()
            self.btn_real_name:setVisible(false)
            api_show_Msg_Box('认证成功')
            if tolua.cast(self.id_verified_view, 'Node') then
                self.id_verified_view:onClose()
                self.id_verified_view = nil
            end
        end,
    }

    local fn = user_events[event.args.event_id]
    if fn then fn() end
end

function new_hall_scene:onPushEvent(event)
    if not __check_event__(event) then return end

    local data = event.args.event_data.data
    local push_events = {
        [m_def.NOTIFY_PUSH_EVENT_LOGIN_OUT] = function()
            UserData:set_weixin_openid(0)
            Msg:showMsgBox(3, '您的账号已在其他地方登录', function() self:enterLoginScene() end)
        end,
        [m_def.NOTIFY_PUSH_EVENT_SYS_NOTICE] = function()
            local pushinfo = data[1] or {}
            if next(pushinfo) then self:popupNode('app.platform.room.new_view.notice_view_2', pushinfo) end
        end,
    }

    local fn = push_events[event.args.event_id]
    if fn then fn() end
end

function new_hall_scene:onGuildNoticeEvent(event)
    if not __check_event__(event) then return end

    local data = event.args.event_data.data
    dump(data)

    local guild_notice_events = {
        [m_def.NOTIFY_NOTICE_EVENT_NOTICE] = function()
            if data.marquee == 1 then
                if data.action == 2 then
                    local msg = ''
                    for _, v in ipairs(data.list or {}) do
                        if v.m_context then
                            msg = msg .. v.m_context .. '\n'
                        end
                    end
                    -- 这个在当前界面里面，没有地方放了，先注释掉
                    --self:setGuildNoticeText(msg)
                    self:updateView('update_guild_notice', msg)
                else
                    --for k, v in pairs(data.list or {}) do
                    --    if v.m_context ~= nil then
                    --        local context = string.gsub(v.m_context, '\n', '')
                    --        table.insert(self.static_marquee_list, context)
                    --    end
                    --end
                end
            elseif data.marquee == 2 then
                for _, v in ipairs(data.list or {}) do
                    if v.m_context then
                        local context = string.gsub(v.m_context, '\n', '')
                        --table.insert(self.static_marquee_list, context)
                        self.static_marquee_list[2] = context
                    end
                end
            end
        end,
    }

    local fn = guild_notice_events[event.args.event_id]
    if fn then fn() end
end

function new_hall_scene:onSpecialActivityEvent(event)
    if not __check_event__(event) then return end

    local data = event.args.event_data.data
    local activity_events = {
        [m_def.NOTIFY_ACTIVITY_SPECIAL_EVENT_WY_GET_ROOM_CARD] = function()
            if data.roomcard ~= nil then 
                Msg:showMsgBox(3, string.format('恭喜您获得%d张房卡，祝您游戏愉快！', data.roomcard), function()
                    m_clientmain:get_instance():get_user_mgr():request_user_info()
                    m_clientmain:get_instance():get_active_mgr():request_active()
                end)
            else
                m_clientmain:get_instance():get_user_mgr():request_user_info() 
                m_clientmain:get_instance():get_active_mgr():request_active()
            end
        end,
        [m_def.NOTIFY_ACTIVITY_SPECIAL_EVENT_WY] = function()
        end,
        [m_def.NOTIFY_ACTIVITY_SPECIAL_EVENT_TASK_LIST] = function()
            print('活动信息....................')
            --self:updateView('update_active_buttons', data)
        end,
        [m_def.NOTIFY_ACTIVITY_SPECIAL_EVENT_INOF] = function()
            print('活动信息....................') 
            --if self.m_activitynotice ~= nil then 
            --    self.m_activitynotice:choseShowSubView(param.event_data.data)
            --end
        end,
        [m_def.NOTIFY_ACTIVITY_SPECIAL_EVENT_GET_AWARD] = function()
            if data.m_room_card ~= nil then
                Msg:showMsgBox(3, string.format('恭喜您获得%d张房卡，祝您游戏愉快！', data.m_room_card), function()
                    m_clientmain:get_instance():get_user_mgr():request_user_info()
                    m_clientmain:get_instance():get_active_mgr():request_active_info(data.m_active_index) 
                end)
            else
                m_clientmain:get_instance():get_user_mgr():request_user_info()
                m_clientmain:get_instance():get_active_mgr():request_active_info(data.m_active_index) 
            end
        end,
        [m_def.NOTIFY_ACTIVITY_SPECIAL_EVENT_GET_GIFT] = function()
            Msg:showMsgBox(3, string.format('领取红包成功，获得%d张房卡和%d礼券。', data.m_room_card, data.m_voucher), function()
                m_clientmain:get_instance():get_user_mgr():request_user_info()
                m_clientmain:get_instance():get_active_mgr():request_active_info(data.m_active_index) 
            end)   
        end,
        [m_def.NOTIFY_ACTIVITY_SPECIAL_EVENT_RECEIVE_CARD] = function()
            m_clientmain:get_instance():get_user_mgr():request_user_info()
            Msg:showMsgBox(3, string.format('领取成功，获得%d张房卡。', data.giftcard))
        end,
    }

    local fn = activity_events[event.args.event_id]
    if fn then fn() end
end

function new_hall_scene:onHeartBeatEvent(event)
    __check_event__(event, nil, nil, function() self:enterLoginScene() end)
end

function new_hall_scene:onTaskEvent(event)
    if not __check_event__(event) then return end

    local data = event.args.event_data.data
    local task_events = {
        [m_def.NOTIFY_TASK_EVENT_GIFT_VOUCHER] = function()
            Msg:showMsgBox(3, '领取红包成功', function() m_clientmain:get_instance():get_welfare_mgr():request_gift_info() end)  
        end,
        [m_def.NOTIFY_TASK_EVENT_TASK_CARD_GIFT] = function()
            if data.roomcard ~= nil then
                Msg:showMsgBox(3, string.format('恭喜您获得%d张房卡，祝您游戏愉快！', data.roomcard), function()
                    m_clientmain:get_instance():get_user_mgr():request_user_info()
                    m_clientmain:get_instance():get_welfare_mgr():request_task_list()
                end)
            else
                m_clientmain:get_instance():get_user_mgr():request_user_info()
                m_clientmain:get_instance():get_welfare_mgr():request_task_list()
            end
        end,
        [m_def.NOTIFY_TASK_EVENT_VIP_ROOM_CARD] = function() end,
        [m_def.NOTIFY_TASK_EVENT_VIP_GIFT_ROOM_CARD] = function() end,
        [m_def.NOTIFY_TASK_EVENT_GIFT_ROOM_CARD] = function()
            if data.roomcard ~= nil then
                Msg:showMsgBox(3, string.format('恭喜您获得%d张房卡，祝您游戏愉快！', data.roomcard), function()
                    m_clientmain:get_instance():get_user_mgr():request_user_info()
                    m_clientmain:get_instance():get_welfare_mgr():request_gift_info()
                end)
            else
                m_clientmain:get_instance():get_user_mgr():request_user_info()
                m_clientmain:get_instance():get_welfare_mgr():request_gift_info()
            end
        end,
        [m_def.NOTIFY_TASK_EVENT_GIFTINFO] = function()
            if tolua.cast(self.free_card_view, 'Node') then self.free_card_view:onClose() end
            self.free_card_view = self:popupNode('app.platform.room.new_view.free_card_view', data)
        end,
        [m_def.NOTIFY_TASK_EVENT_LIST] = function()
            if self.current_active_index == 3 then
                local win_task_data = nil
                for _, v in pairs(data or {}) do
                    if tonumber(v.id) == 6 then
                        win_task_data = v

                        break
                    end
                end

                if win_task_data then
                    self:popupNode('app.platform.room.new_view.new_activity_win_task', win_task_data)
                end
            end
            if self.current_active_index == 2 then
                local daily_task_data = nil
                for _, v in pairs(data or {}) do
                    if tonumber(v.id) == 5 then
                        daily_task_data = v

                        break
                    end
                end

                if daily_task_data then
                    self:popupNode('app.platform.room.new_view.new_activity_daily_task', daily_task_data)
                end
            end
        end,
        [m_def.NOTIFY_TASK_EVENT_TASK_ROOMCARD] = function()
            -- 领取任务奖励回调, 更新玩家信息和任务信息
            Msg:showMsgBox(3, '领取任务奖励成功', function()
                m_clientmain:get_instance():get_welfare_mgr():request_task_list()
                m_clientmain:get_instance():get_welfare_mgr():request_gift_info()
            end)
        end,
    }

    local fn = task_events[event.args.event_id]
    if fn then fn() end
end

function new_hall_scene:onGameEvent(event)
    if not event or not event.args then return false end

    local data = event.args.event_data.data
    local game_events = {
        [m_def.NOTIFY_GAME_EVENT_LOGIN_FINISH] = function() end,        -- 登陆成功
        [m_def.NOTIFY_GAME_EVENT_CONNECT] = function()
            if event.args.event_data.ret == 0 then
                if event.args.event_data.result == 1 then
                    if #event.args.event_data.data == 6 then
                        local reconnect_layer = m_reconnectlayer.new(self, event.args.event_data.data)
                        self:addChild(reconnect_layer, 14)
                    else
                        api_show_Msg_Tip('抱歉，由于网络原因，加入包间失败，请重新加入包间')
                    end
                elseif event.args.event_data.result == 2 then
                    api_show_Msg_Tip('连接服务器失败!')
                end
            end
        end,
        [m_def.NOTIFY_GAME_EVENT_SIT_DOWN] = function() end,
        [m_def.NOTIFY_GAME_EVENT_STAND_UP] = function() end,
        [m_def.NOTIFY_GAME_EVENT_SETUP_GUILD_SCENE] = function()
            api_hide_loading_ext()
            api_show_Msg_Box(GAME_TEST and event.args.event_data or '您选择的包间中的好友已开始游戏，邀请你的好友，开始新的游戏吧!')

            local game_list = m_clientmain:get_instance():get_room_mgr():get_game_list()
            dump(game_list)
            if not game_list then return api_show_Msg_Tip('正在获取游戏列表，请稍后...') end
            if table.getn(game_list) <= 0 then return api_show_Msg_Tip('该公会还没有游戏') end

            self:showCreateRoomView(game_list)
        end,
    }

    local fn = game_events[event.args.event_id]
    if fn then fn() end
end

function new_hall_scene:onRoomEvent(event)
    if not tolua.cast(self.csb_node, 'Node') then return end
    if not event or not event.args then return false end

    local data = event.args.event_data.data
    local room_events = {
        [m_def.NOTIFY_ROOM_EVENT_BUILD_DESK] = function()
            api_hide_loading()

            if tonumber(event.args.event_data.ret) == 200108 then     -- 房卡不足，无法创建包间
                Msg:showMsgBox(1, '您的房卡不足，请先购买房卡，以便畅快游戏', function() self:bugRoomCard() end)
            end
        end,
        [m_def.NOTIFY_ROOM_EVENT_GAME_INFO] = function() end,
        [m_def.NOTIFY_ROOM_EVENT_ROOM_INFO] = function() end,
        [m_def.NOTIFY_ROOM_EVENT_DESK_OWNER] = function()
            api_hide_loading()

            -- 更新创建包间和加入包间的状态
            local userinfo = m_clientmain:get_instance():get_user_mgr():get_user_info()
            if userinfo and userinfo.m_desk_info and userinfo.m_desk_info.m_desk_room_no then
            --if true then
                self.alpha_button_config[4].sprite:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('ShaderUIGrayScale'))
                self.alpha_button_config[4].is_enable = false       -- 创建包间不可用
                self.alpha_button_config[1].sprite:setTexture('hall_res/hall/hall_return_room.png')       -- 加入包间还成返回包间
                self.alpha_button_config[1].is_back_room = true
            else
                self.alpha_button_config[4].sprite:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('ShaderPositionTextureColor_noMVP'))
                self.alpha_button_config[4].is_enable = true
                self.alpha_button_config[1].sprite:setTexture('hall_res/hall/hall_join_room.png')       -- 加入包间还成返回包间
                self.alpha_button_config[1].is_back_room = false
            end

            -- 
            if event.args.event_data.ret == 0 or G_in_Hall then return end

            local game_list = m_clientmain:get_instance():get_room_mgr():get_game_list()
            dump(game_list)
            if not game_list then return api_show_Msg_Tip('正在获取游戏列表，请稍后...') end
            if table.getn(game_list) <= 0 then return api_show_Msg_Tip('该公会还没有游戏') end

            self:showCreateRoomView(game_list)
        end,
        [m_def.NOTIFY_ROOM_EVENT_QUERY_DESK] = function() end,
        [m_def.NOTIFY_ROOM_EVENT_CHECK_GAME_UPDATE] = function()
            self:popupNode('app.platform.room.new_view.game_update_view', {
                game_id = tonumber(data.m_room_info.m_gameid),
                callback = function(result)
                    if result then
                        m_clientmain:get_instance():login_wserver(data.m_room_info, data.m_desk_num, 0, data)
                    end
                end,
            })
            end,
        [m_def.NOTIFY_ROOM_EVENT_QUERY_ROOM] = function()
            local lack_flag = false

            if data.m_desk_info ~= nil then
                if data.m_desk_info.m_roomcard_count ~= nil then

                    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info()
                    if user_info ~= nil then
                        if user_info.m_roomcard ~= nil then
                            if tonumber(user_info.m_roomcard) < tonumber(data.m_desk_info.m_roomcard_count) then
                                lack_flag = true
                                api_show_Msg_Box("房卡不足，请充值")
                            end
                        end
                    end

                end
            end

            if lack_flag == false then
                api_show_loading('------login_wserver--------')
                m_clientmain:get_instance():login_wserver(data.m_room_info,data.m_desk_info.m_desk_num,0,data.m_desk_info)
            end
        end,
    }

    local fn = room_events[event.args.event_id]
    if fn then fn() end
end

function new_hall_scene:showMahjongCardList(show_card_node)
    cc.SpriteFrameCache:getInstance():addSpriteFrames('mahjong/game_card/game_card.plist')
    require 'app.platform.game.game_common.game_card_config'

    local offset_x, offset_y = 0, 0
    local show_card_interval = 30

    -- block card list
    if self.recv_lucky_data.block_info then
        for i=1, self.recv_lucky_data.block_info.block_count do
            local bi = self.recv_lucky_data.block_info.list[i]
            if bi then
                local count = (bi.m_block_type == 4 and 4 or 3)
                for index=1, count do
                    local card_node = create_card_front(USER_LOCATION_SELF, CARD_AREA.TAN, bi['m_block_card_' .. index])
                    card_node:setScale(0.5)

                    local z_order = 0
                    if bi.m_block_type == 4 and index == 3 then
                        card_node:setPosition(offset_x - show_card_interval, offset_y + 12)
                        z_order = 1
                    else
                        card_node:setPosition(offset_x, offset_y)
                        offset_x = offset_x + show_card_interval
                    end

                    show_card_node:addChild(card_node, z_order)
                end

                offset_x = offset_x + 5
            end
        end

        offset_x = offset_x + 10
    end

    local function __create_ghost_flag__(card_id, game_id)
        if self.recv_lucky_data.ghost_mode and self.recv_lucky_data.ghost_mode ~= 0 and self.recv_lucky_data.ghost_cards then
            for i=1, self.recv_lucky_data.ghost_mode do
                if card_id == self.recv_lucky_data.ghost_cards[i] then
                    local file_path = string.format('hall_res/lucky/%d.png', game_id)
                    file_path = cc.FileUtils:getInstance():fullPathForFilename(file_path)
                    if cc.FileUtils:getInstance():isFileExist(file_path) then
                        return cc.Sprite:create(string.format('hall_res/lucky/%d.png', game_id))
                    end

                    return cc.Sprite:create('hall_res/lucky/default_ghost_flag.png')
                end
            end
        end

        return nil
    end

    local function __create_win_flag__(card_id)
        if self.recv_lucky_data.win_card == card_id then
            return cc.Sprite:createWithSpriteFrameName('mahjong_subscript_win.png')
        end
    end

    local hand_card_interval = 33
    if self.recv_lucky_data.hand_card then
        for index, card_id in ipairs(self.recv_lucky_data.hand_card.list or {}) do
            local card_node = create_card_front(USER_LOCATION_SELF, CARD_AREA.HAND, card_id)
            card_node:setScale(0.39)
            show_card_node:addChild(card_node)

            local ghost_flag = __create_ghost_flag__(card_id, self.recv_lucky_data.game_id)
            if ghost_flag then
                ghost_flag:setPosition(-17, 22)
                ghost_flag:setScale(2)
                card_node:addChild(ghost_flag)
            end

            -- 
            if index == #self.recv_lucky_data.hand_card.list then
                local win_flag = __create_win_flag__(card_id)
                if win_flag then
                    win_flag:setPosition(-17, 22)
                    win_flag:setScale(0.8)
                    card_node:addChild(win_flag)
                end

                offset_x = offset_x + 5
            end

            card_node:setPosition(offset_x, offset_y)
            offset_x = offset_x + hand_card_interval
        end
    end
end

function new_hall_scene:showNiuNiuCardList(show_card_node)
    if not self.recv_lucky_data.hand_card then return end

    dump(self.recv_lucky_data.hand_card)

    -- 
    cc.SpriteFrameCache:getInstance():addSpriteFrames('poker/poker_card/poker_card.plist')
    require 'app.platform.game.game_common.game_poker_config'

    local offset_x, offset_y = 130, 0
    for _, card_id in ipairs(self.recv_lucky_data.hand_card) do
        local card_node = create_poker_card_front(card_id, cc.p(0.5, 0.5))
        card_node:setPosition(offset_x, offset_y)
        card_node:setScale(0.3)
        show_card_node:addChild(card_node)

        offset_x = offset_x + 35
    end
end

function new_hall_scene:showDouDiZhuCardList(show_card_node)
    if not self.recv_lucky_data.hand_card then return end
    dump(self.recv_lucky_data.hand_card)

    cc.SpriteFrameCache:getInstance():addSpriteFrames('poker/poker_card/poker_card.plist')
    require 'app.platform.game.game_common.game_poker_config'

    -- 
    local offset_x, offset_y = 50, 0
    local subscript_type = nil
    if self.recv_lucky_data.is_banker == 1 then subscript_type = 'dizhu' end
    for _, card_id in ipairs(self.recv_lucky_data.hand_card) do
        local card_node = create_poker_card_front_subscript(card_id, subscript_type, cc.p(0.5, 0.5))
        card_node:setPosition(offset_x, offset_y)
        card_node:setScale(0.3)
        show_card_node:addChild(card_node)

        offset_x = offset_x + 20
    end
end

function new_hall_scene:bugRoomCard()
    local join_guild = m_clientmain:get_instance():get_user_mgr():check_user_join_guild()
    if not join_guild and G_device_platform == 0 then
        Msg:showMsgBox(3, "需加入公会才可购买房卡", function()
            self.Halljoin_layer = require("app.platform.room.new_view.halljoinguildscene").new(self, 1)
            self:addChild(self.Halljoin_layer, 200)
        end)
    else
        local pay_type = 'wechat_pay'
        if not join_guild and G_device_platform == 1 then pay_type = 'apple_pay' end
        self:popupNode('app.platform.room.new_view.mall_view', pay_type)
    end
end

function new_hall_scene:enterLoginScene()
    switchScene('app.platform.room.login_view')
end

function new_hall_scene:startMarquee()
    -- create marquee node
    self.marquee_config = {
        marquee_width = 960,
        marquee_height = 34,
        move_distance_per_second = 50,
    }

    -- 
    local node_marquee = self.csb_node:getChildByName('node_marquee')

    local rc = cc.rect(0, 0, self.marquee_config.marquee_width, self.marquee_config.marquee_height)
    self.marquee_clip_node = cc.ClippingRectangleNode:create(rc)
    self.marquee_clip_node:setPosition(-self.marquee_config.marquee_width * 0.5, -self.marquee_config.marquee_height * 0.5)
    node_marquee:addChild(self.marquee_clip_node)

    -- 
    self:scheduleMarquee_1()
end

function new_hall_scene:scheduleMarquee_1()
    local __show_next_text__ = nil
    __show_next_text__ = function()
        local text_node = cc.Label:createWithTTF(self:getNextMarqueeText(), 'font/fzzyjt.ttf', 24, cc.size(0, 24))
        --text_node:setColor(cc.c3b(234, 216, 141))
        text_node:setAnchorPoint(0, 0.5)
        self.marquee_clip_node:addChild(text_node)

        local text_size = text_node:getContentSize()
        local mv_distance_1 = text_size.width * 0.5 + self.marquee_config.marquee_width
        local mv_distance_2 = text_size.width * 0.5 + 10
        local duration_1 = mv_distance_1 / self.marquee_config.move_distance_per_second
        local duration_2 = mv_distance_2 / self.marquee_config.move_distance_per_second

        local sx = self.marquee_config.marquee_width
        local y = self.marquee_config.marquee_height * 0.5
        text_node:setPosition(sx, y)

        local tx_1 = sx - mv_distance_1
        local tx_2 = tx_1 - mv_distance_2

        local mv_action_1 = cc.MoveTo:create(duration_1, cc.p(tx_1, y))
        local next_show_action = cc.CallFunc:create(__show_next_text__)
        local mv_action_2 = cc.MoveTo:create(duration_2, cc.p(tx_2, y))
        local clean_action = cc.CallFunc:create(function() text_node:removeFromParent(true) end)
        text_node:runAction(cc.Sequence:create(mv_action_1, next_show_action, mv_action_2, clean_action))
    end

    -- start marquee after a second
    self:schedule_once_time(1.0, __show_next_text__)
end

function new_hall_scene:getNextMarqueeText()
    if #self.dynamic_marquee_list > 0 then
        local text = self.dynamic_marquee_list[0]
        table.remove(self.dynamic_marquee_list, 0)

        return text
    end

    if #self.static_marquee_list > 0 then
        local text = self.static_marquee_list[self.next_static_marquee_index]

        self.next_static_marquee_index = self.next_static_marquee_index + 1
        if self.next_static_marquee_index > #self.static_marquee_list then
            self.next_static_marquee_index = 1
        end

        if text then return text end
    end

    return default_marquee_msg
end

function new_hall_scene:UserCanPlay()
    local userip_area = m_clientmain:get_instance():get_config_mgr():get_userip_area()
    local join_flag = m_clientmain:get_instance():get_user_mgr():check_user_join_guild() 

    if G_device_platform == 1 then
        if userip_area == 1 then 
            return true     -- 海外苹果玩家一律可以玩
        elseif G_isGuest == true then
            return true     -- 苹果设备,游客
        else
            -- 国内微信, 未加入公会的，不能玩，需要加公会
            return join_flag
        end
    else
        -- 安卓, 国内微信, 未加入公会的，不能玩，需要加公会
        return join_flag
    end

    return false
end

function new_hall_scene:showCreateRoomView(game_list)
    self.csb_node:setVisible(false)
    self.node_rank_lucky:setVisible(false)
    self:popupNode('app.platform.room.new_view.new_create_room_view', game_list, function(_, _, cb) if cb then cb() end end, function(popup_self, node, cb)
        popup_self:removeFromParent()
        if cb then cb() end

        self.csb_node:setVisible(true)
        self.node_rank_lucky:setVisible(true)
    end)
end

return new_hall_scene
