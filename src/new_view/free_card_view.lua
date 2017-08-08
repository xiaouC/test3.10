-- ./app/platform/room/new_view/buy_card_view.lua
require 'app.platform.room.new_view.loading'

local m_clientmain = require 'app.platform.room.clientmain'

local popup_base = require 'app.platform.common.popup_base'
local FreeCardView = class('FreeCardView', popup_base)
function FreeCardView:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/activity/free_card.csb'
    dump(args)

    popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function FreeCardView:initViews()
    popup_base.initViews(self)

    -- 
    local rb_group = ccui.RadioButtonGroup:create()
    self.anim_node:addChild(rb_group)

    -- tab 1
    local tab_node_1, rb_1, tab_onchanged_1 = create_activity_radio_button('  拉好友\n一起游戏', true)
    rb_group:addRadioButton(rb_1)
    self.csb_node:getChildByName('btn_node_1'):addChild(tab_node_1)

    local tab_item_node_1 = self.csb_node:getChildByName('tab_item_1')
    rb_1:addEventListener(function(_, event_type)
        tab_onchanged_1(event_type)
        tab_item_node_1:setVisible(event_type == ccui.RadioButtonEventType.selected)
    end)

    -- tab 2
    local tab_node_2, rb_2, tab_onchanged_2 = create_activity_radio_button('  输入\n推广码', false)
    rb_group:addRadioButton(rb_2)
    self.csb_node:getChildByName('btn_node_2'):addChild(tab_node_2)

    local tab_item_node_2 = self.csb_node:getChildByName('tab_item_2')
    rb_2:addEventListener(function(_, event_type)
        tab_onchanged_2(event_type)
        tab_item_node_2:setVisible(event_type == ccui.RadioButtonEventType.selected)
    end)

    -- init tab item 1
    self:initTabItem1(tab_item_node_1)
    self:initTabItem2(tab_item_node_2)

    -- 
    label('invite_name', self.args.invite_name or '', self.csb_node)
    label('invite_id', self.args.invite_id ~= 0 and self.args.invite_id or '', self.csb_node)
    label('invite_count', string.format('X%d', self.args.invite_count), self.csb_node)
    label('invite_card', string.format('X%d', self.args.already_get_count), self.csb_node)

    local status_config = {
        [0] = { -- 
            status_text = '完成游戏',
            visible = true,
            enable = false,
            background_color = cc.c3b(255, 186, 110),
        },
        [1] = { -- 完成推荐
            status_text = '完成推荐',
            visible = true,
            enable = true,
            background_color = cc.c3b(255, 220, 119),
        },
        [2] = { -- 已领取
            status_text = '',
            visible = false,
            enable = false,
            background_color = cc.WHITE,
        },
    }

    --[[ test data
    self.args.user_data = {
        {
            m_head_url = '',
            m_status = 0,
            m_user_name = 'kkkkk',
            m_gift_count = 2,
        },
        {
            m_head_url = '',
            m_status = 1,
            m_user_name = 'mmmmmmmmm',
            m_gift_count = 2,
        },
        {
            m_head_url = '',
            m_status = 2,
            m_user_name = 'bbbbb',
            m_gift_count = 2,
        },
    }
    --]]

    -- 
    local lv = self.csb_node:getChildByName('lv_invite')
    lv:setDirection(ccui.ListViewDirection.vertical)
    lv:setScrollBarEnabled(false)
    for _, v in ipairs(self.args.user_data or {}) do
        local item_node = cc.CSLoader:createNode('hall_res/activity/invite_item.csb')

        local head_sprite = createUserHeadSprite({m_bLogoID = 1, m_headurl = v.m_head_url}, 0.97)
        item_node:getChildByName('head_node'):addChild(head_sprite)

        local sc = status_config[v.m_status]
        item_node:getChildByName('background'):setColor(sc.background_color)

        label('text_name', v.m_user_name, item_node)
        label('text_state', sc.status_text, item_node)
        label('text_count', string.format('X%s', tostring(v.m_gift_count)), item_node:getChildByName('node_1'))

        local btn_receive = button('btn_receive', function()
            m_clientmain:get_instance():get_welfare_mgr():request_gift_roomcard(2, v.m_type, v.m_index)
        end, item_node:getChildByName('node_1'))
        btn_receive:setVisible(sc.visible)
        btn_receive:setEnabled(sc.enable)
        item_node:getChildByName('img_finish'):setVisible(not sc.visible)

        local size = item_node:getChildByName('background'):getContentSize()
        local item_widget = ccui.Widget:create()
        item_widget:setContentSize(size)
        item_node:setPosition(size.width * 0.5, size.height * 0.5)
        item_widget:addChild(item_node)

        lv:addChild(item_widget)
    end
    lv:requestDoLayout()
end

local function create_text_label(text, font_size)
    -- label shader
    local p = cc.GLProgramCache:getInstance():getGLProgram('color_texture_label')

    -- 
    local text_label = cc.Label:createWithTTF(text, 'res/font/jxk.TTF', font_size or 22)
    text_label:setColorTextureIndex(6)
    text_label:setGLProgram(p)
    text_label:setAnchorPoint(0, 0.5)
    text_label:enableOutline(cc.c3b(83, 30, 11), 2)

    return text_label
end

function FreeCardView:initTabItem1(node)
    local text_label_1 = create_text_label('1、开设包间发送邀请链接给好友')
    text_label_1:setPosition(node:getChildByName('node_text_1'):getPosition())
    node:addChild(text_label_1)

    local text_label_2 = create_text_label('2、好友下载游戏后再次点击您的邀请链接加入包间')
    text_label_2:setPosition(node:getChildByName('node_text_2'):getPosition())
    node:addChild(text_label_2)

    --
    local node_text_3 = node:getChildByName('node_text_3')

    local text_label_3 = create_text_label('与好友一起打完游戏，你可得', 24)
    text_label_3:setPosition(-320, 0)
    node_text_3:addChild(text_label_3)

    local text_label_4 = create_text_label('好友得', 24)
    node_text_3:addChild(text_label_4)
    text_label_4:setPosition(80, 0)

    label('text_card_num_1', 'X' .. tostring(self.args.gift_card_num[3]), node)
    label('text_card_num_2', 'X' .. tostring(self.args.gift_card_num[4]), node)

    -- 
    local btn_invite = button('btn_invite', function()
        self:onClose()

        G_in_Hall = false
        api_show_loading()
        m_clientmain:get_instance():get_user_mgr():request_user_info()
        m_clientmain:get_instance():get_room_mgr():request_desk_owner()
    end, node)

    local btn_invite_size = btn_invite:getContentSize()

    local btn_text_label = cc.Label:createWithTTF('立即去邀请', 'res/font/jxk.TTF', 40)
    btn_text_label:setColorTextureIndex(2)
    btn_text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    btn_text_label:setPosition(btn_invite_size.width * 0.5, btn_invite_size.height * 0.5 + 10)
    btn_text_label:enableOutline(cc.c3b(28, 118, 14), 2)
    btn_text_label:enableShadow()
    btn_invite:getRendererNormal():addChild(btn_text_label)
end

function FreeCardView:initTabItem2(node)
    local text_label_1 = create_text_label('1、推荐好友下载友间麻将')
    text_label_1:setPosition(node:getChildByName('node_text_1'):getPosition())
    node:addChild(text_label_1)

    local text_label_2 = create_text_label('2、好友登陆后输入您的邀请码')
    text_label_2:setPosition(node:getChildByName('node_text_2'):getPosition())
    node:addChild(text_label_2)

    --
    local node_text_3 = node:getChildByName('node_text_3')

    local text_label_3 = create_text_label('好友点击加入公会后，你可得', 24)
    text_label_3:setPosition(-320, 0)
    node_text_3:addChild(text_label_3)

    local text_label_4 = create_text_label('好友得', 24)
    node_text_3:addChild(text_label_4)
    text_label_4:setPosition(80, 0)

    label('text_card_num_1', 'X' .. tostring(self.args.gift_card_num[1]), node)
    label('text_card_num_2', 'X' .. tostring(self.args.gift_card_num[2]), node)

    -- 
    local node_share = node:getChildByName('node_share')
    local btn_share = button('btn_share', function() node_share:setVisible(not node_share:isVisible()) end, node)

    local btn_share_size = btn_share:getContentSize()

    local btn_text_label = cc.Label:createWithTTF('分享邀请码', 'res/font/jxk.TTF', 40)
    btn_text_label:setColorTextureIndex(2)
    btn_text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    btn_text_label:setPosition(btn_share_size.width * 0.5, btn_share_size.height * 0.5 + 10)
    btn_text_label:enableOutline(cc.c3b(28, 118, 14), 2)
    btn_text_label:enableShadow()
    btn_share:getRendererNormal():addChild(btn_text_label)

    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info()
    local url = string.format('%s?day=%s&gid=%s&playerid=%s', self.args.share_url, tostring(user_info.m_reg_time), tostring(user_info.m_ghinfo.m_proid), tostring(user_info.m_uid))
    init_share_view(node_share, url)
end

return FreeCardView
