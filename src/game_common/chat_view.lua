-- ./app/platform/game/game_common/chat_view.lua

local m_clientmain = require 'app.platform.room.clientmain'

----------------------------------------------------------------------------------------------------------
local game_scene_popup_base = require 'app.platform.game.game_common.game_scene_popup_base'

local ChatView = class('ChatView', game_scene_popup_base)
function ChatView:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'game_common_res/component/normal_chat/chat_view.csb'
    self.z_order = GAME_VIEW_Z_ORDER.VOICE_CHAT - 1

    --[[
    args = {
        user_id = 0,
        sound_text_list = {
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
            { text ='来啊，互相伤害啊！', index = 1 },
        },
        emoji_type = 'mahjong',
    }
    --]]

    game_scene_popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function ChatView:on_touch_began(touch, event)
    local node_bg = self.csb_node:getChildByName('background')
    local bg_width, bg_height = 1000, 550 
    local rect = { x = 0, y = 0, width = bg_width, height = bg_height }

    local pos = node_bg:convertToNodeSpace(touch:getLocation())
    if not cc.rectContainsPoint(rect, pos) then
        self:onClose()
    end

    return game_scene_popup_base.on_touch_began(self, touch, event)
end

function ChatView:initViews()
    game_scene_popup_base.initViews(self)

    -- button animation
    cc.SpriteFrameCache:getInstance():addSpriteFrames(string.format('%s/anim/emoji_preview.plist', self.args.emoji_type));
    for i=1, 12 do
        local btn_anim = button('btn_anim_' .. i, function()
            m_clientmain:get_instance():get_game_manager():get_game_room_mgr():send_game_chat_msg(self.args.user_id, 3, i, '')

            self:onClose()
        end, self.csb_node)

        local sprite = cc.Sprite:createWithSpriteFrameName(string.format('%s_preview_%02d.png', self.args.emoji_type, i))
        sprite:setPosition(57, 77)
        btn_anim:getRendererNormal():addChild(sprite)
    end

    local text_input = self.csb_node:getChildByName('text_input')
    button('btn_send', function()
        local text = text_input:getString()

        if not CheckSensitiveWords(text) then return api_show_Msg_Box('您的帐号输入了不合法词汇！') end
        if #text == 0 then return api_show_Msg_Tip('请输入文字再发送吧') end

        text_input:setString('')

        m_clientmain:get_instance():get_game_manager():get_game_room_mgr():send_game_chat_msg(self.args.user_id, 1, 0, text)

        if device.platform == 'ios' then CCDirector:getInstance():getOpenGLView():setIMEKeyboardState(false) end

        self:onClose()
    end, self.csb_node)

    -- 
    local item_count = #(self.args.sound_text_list or {})
    local item_width, item_height = 550, 46
    local item_tag = 10

    local tv = cc.TableView:create(cc.size(550, 500))
    tv:setDirection(cc.SCROLLVIEW_DIRECTION_VERTICAL)
    tv:setVerticalFillOrder(cc.TABLEVIEW_FILL_TOPDOWN)
    tv:setPosition(cc.p(-32, -286))
    tv:setDelegate()
    self.csb_node:addChild(tv)

    tv:registerScriptHandler(function() return item_count end, cc.NUMBER_OF_CELLS_IN_TABLEVIEW)
    tv:registerScriptHandler(function() return 550, 46 end, cc.TABLECELL_SIZE_FOR_INDEX)
    tv:registerScriptHandler(function(_, cell)
        local index = cell:getIdx() + 1
        local item_data = self.args.sound_text_list[index]
        m_clientmain:get_instance():get_game_manager():get_game_room_mgr():send_game_chat_msg(self.args.user_id, 4, item_data.index, item_data.text)
        self:schedule_once(function() self:onClose() end)
    end, cc.TABLECELL_TOUCHED)
    tv:registerScriptHandler(function(table, index)
        local cell = table:dequeueCell()
        if not cell then cell = CCTableViewCell:new() end

        cell:removeAllChildren()

        -- 
        local sprite = cc.Sprite:createWithSpriteFrameName('game_common_chat_unchecked.png')
        sprite:setPosition(item_width * 0.5, item_height * 0.5)
        cell:addChild(sprite)

        local selected_sprite = cc.Sprite:createWithSpriteFrameName('game_common_chat_sel_bg.png')
        selected_sprite:setPosition(item_width * 0.5, item_height * 0.5)
        selected_sprite:setVisible(false)
        cell:addChild(selected_sprite, 0, item_tag)

        local item_data = self.args.sound_text_list[index+1]
        local text_label = cc.Label:createWithTTF(item_data.text, 'font/fzzyjt.ttf', 30)
        text_label:setAnchorPoint(0.0, 0.5)
        text_label:setPosition(0, item_height * 0.5)
        text_label:setColor(cc.c3b(248, 215, 196))
        cell:addChild(text_label)

        return cell
    end, cc.TABLECELL_SIZE_AT_INDEX)
    tv:registerScriptHandler(function(_, cell) cell:getChildByTag(item_tag):setVisible(true) end, cc.TABLECELL_HIGH_LIGHT)
    tv:registerScriptHandler(function(_, cell) cell:getChildByTag(item_tag):setVisible(false) end, cc.TABLECELL_UNHIGH_LIGHT)

    tv:reloadData()
end

function ChatView:onClose(cb)
    if self.args.on_close_cb then self.args.on_close_cb() end

    game_scene_popup_base.onClose(self, cb)
end

return ChatView
