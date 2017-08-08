-- ./app/platform/room/new_view/personal_view.lua
require 'app.platform.room.new_view.loading'

local popup_base = require 'app.platform.common.popup_base'
local PersonalView = class('PersonalView', popup_base)
function PersonalView:ctor(model_install, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/personal/personal.csb'
    self.recv_personal_data = {}

    popup_base.ctor(self, model_install, args, function(popup_self, node, cb)
        if cb then cb() end
    end, function(popup_self, node, cb)
        print('self.node_path : ' .. tostring(self.node_path))
        if self.node_path then package.loaded[self.node_path] = nil end
        popup_self:removeFromParent()
        if cb then cb() end
    end)
end

function PersonalView:initViews()
    popup_base.initViews(self)

    -- layer color
    local layer_color = cc.LayerColor:create(cc.c4b(24, 9, 8, 125), 260, 585)
    self.csb_node:getChildByName('node_layer_color'):addChild(layer_color)

    -- 
    local lv_radio = self.csb_node:getChildByName('lv_radio')
    lv_radio:setScrollBarEnabled(false)
    lv_radio:setItemsMargin(20)

    local rb_group = ccui.RadioButtonGroup:create()
    self.anim_node:addChild(rb_group)

    local personal_options = {
        {
            name = '个人信息',
            csb_file = 'hall_res/personal/item_personal.csb',
            init_func = function(node) self:initPersonalView(node) end,
        },
        {
            name = '游戏人生',
        },
        {
            name = '专属语音',
        },
    }

    local all_item_node = {}
    local node_content = self.csb_node:getChildByName('node_content')
    local img_normal, img_selected = 'btn_gameselect_2.png', 'btn_gameselect_1.png'
    for _, v in ipairs(personal_options) do
        local rb_widget, rb, text_label = createRadioWidget(img_normal, img_selected, v.name, 30, ccui.TextureResType.plistType)

        local x, y = text_label:getPosition()
        text_label:setPosition(x - 20, y)

        rb_group:addRadioButton(rb)
        lv_radio:addChild(rb_widget)

        -- 
        if v.csb_file then
            local csb_item_node = cc.CSLoader:createNode(v.csb_file)
            csb_item_node:setVisible(false)
            node_content:addChild(csb_item_node)

            v.init_func(csb_item_node)

            all_item_node[rb] = csb_item_node
        end
    end

    rb_group:addEventListener(function(rb_selected, index, event_type)
        for rb, item_node in pairs(all_item_node) do
            item_node:setVisible(rb_selected == rb)
        end
    end)

    rb_group:setSelectedButton(0)
end

function PersonalView:initPersonalView(node_personal)
    local font_name, font_size = '黑体', 20
    local function __create_text_1__(text)
        local ct_label = create_color_texture_label(text, 2, nil, font_size)
        ct_label:enableShadow()
        return ct_label
    end

    local node_text_1 = node_personal:getChildByName('node_text_1')
    node_text_1:getChildByName('node_text_paipin'):addChild(__create_text_1__('牌品值'))
    node_text_1:getChildByName('node_text_zan'):addChild(__create_text_1__('好评分数'))
    node_text_1:getChildByName('node_text_cai'):addChild(__create_text_1__('差评分数'))
    node_text_1:getChildByName('node_text_fast'):addChild(__create_text_1__('快速出牌分'))
    node_text_1:getChildByName('node_text_leave'):addChild(__create_text_1__('中途离开分'))

    -- 
    local paipin_desc_label = ccui.RichText:create()
    paipin_desc_label:ignoreContentAdaptWithSize(false);
    paipin_desc_label:setSize(cc.size(850, 30));
    paipin_desc_label:setAnchorPoint(0, 0.5)
    node_personal:getChildByName('node_text_4'):addChild(paipin_desc_label)

    local font_name, font_size = '黑体', 16
    local text_color = cc.c3b(192, 116, 71)
    local rich_ele_1 = ccui.RichElementText:create(0, text_color, 255, '一次好评加 ', font_name, font_size)
    paipin_desc_label:pushBackElement(rich_ele_1)

    local rich_ele_2 = ccui.RichElementText:create(0, cc.RED, 255, '100', font_name, font_size)
    paipin_desc_label:pushBackElement(rich_ele_2)

    local rich_ele_3 = ccui.RichElementText:create(0, text_color, 255, ' 分，一次差评减 ', font_name, font_size)
    paipin_desc_label:pushBackElement(rich_ele_3)

    local rich_ele_4 = ccui.RichElementText:create(0, cc.RED, 255, '100', font_name, font_size)
    paipin_desc_label:pushBackElement(rich_ele_4)

    local rich_ele_5 = ccui.RichElementText:create(0, text_color, 255, ' 分，一次快速出牌加 ', font_name, font_size)
    paipin_desc_label:pushBackElement(rich_ele_5)

    local rich_ele_6 = ccui.RichElementText:create(0, cc.RED, 255, '1', font_name, font_size)
    paipin_desc_label:pushBackElement(rich_ele_6)

    local rich_ele_7 = ccui.RichElementText:create(0, text_color, 255, ' 分，一次中途离开减 ', font_name, font_size)
    paipin_desc_label:pushBackElement(rich_ele_7)

    local rich_ele_8 = ccui.RichElementText:create(0, cc.RED, 255, '50', font_name, font_size)
    paipin_desc_label:pushBackElement(rich_ele_8)

    local rich_ele_9 = ccui.RichElementText:create(0, text_color, 255, ' 分', font_name, font_size)
    paipin_desc_label:pushBackElement(rich_ele_9)

    -- 
    local ct_label = create_color_texture_label('牌友口碑', 3, nil, 30)
    ct_label:enableShadow()
    ct_label:enableOutline(cc.c3b(83, 30, 11), 2)
    node_personal:getChildByName('node_koubei'):addChild(ct_label)

    -- 
    local font_name, font_size = '黑体', 18
    local function __create_text_3__(text)
        local ct_label = create_color_texture_label(text, 1, nil, font_size)
        ct_label:enableShadow()
        return ct_label
    end
    local node_text_3 = node_personal:getChildByName('node_text_3')
    node_text_3:getChildByName('node_text_1'):addChild(__create_text_1__('牌品棒棒哒（           ）          人品棒棒哒（           ）            素质棒棒哒（           ）           出牌如闪电（            ）'))
    node_text_3:getChildByName('node_text_2'):addChild(__create_text_1__('牌品一般般（           ）          人品一般般（           ）            素质一般般（           ）           出牌如蜗牛（            ）'))

    --
    local atlas_label_config_1 = { 'node_paipin', 'node_zan', 'node_cai', 'node_fast', 'node_leave' }
    local atlas_label_config_2 = { 'node_bbd_1', 'node_bbd_2', 'node_bbd_3', 'node_bbd_4', 'node_ybb_1', 'node_ybb_2', 'node_ybb_3', 'node_ybb_4' }
    local node_score = node_personal:getChildByName('node_score')

    local all_score_label = {}
    local function __create_atlas_label__(apx)
        local label = cc.LabelAtlas:_create('0', "hall_res/common/num_count.png", 14, 22, string.byte('.'))
        label:setAnchorPoint(apx, 0.5)
        return label
    end
    for _, name in ipairs(atlas_label_config_1) do
        local label = __create_atlas_label__(1)
        node_score:getChildByName(name):addChild(label)
        all_score_label[name] = label
    end
    for _, name in ipairs(atlas_label_config_2) do
        local label = __create_atlas_label__(0.5)
        node_score:getChildByName(name):addChild(label)
        all_score_label[name] = label
    end

    -- friends
    local lv_friends = node_personal:getChildByName('lv_friends')
    lv_friends:setScrollBarEnabled(false)

    --
    self:appendView('update_personal_info', function()
        if not tolua.cast(node_personal, 'Node') then return end

        for name, label in pairs(all_score_label) do
            local text = string.gsub(tostring(self.recv_personal_data[name]), '-', '/')
            label:setString(text)
        end

        lv_friends:removeAllChildren()
        for _, v in ipairs(self.recv_personal_data.friend_list or {}) do
            local item_widget, item_node = createWidget('hall_res/personal/item_friends.csb', 180, 140)

            label('text_user_name', v.user_name, item_node)
            label('text_user_desc', '对局数：' .. v.game_count, item_node)

            item_node:getChildByName('node_head'):addChild(cc.Sprite:create('hall_res/head/head_7.png'))

            lv_friends:addChild(item_widget)
        end
        lv_friends:requestDoLayout()
    end)
end

function PersonalView:initDataFromServer()
    self.recv_personal_data = {
        node_paipin = 123,
        node_zan = 76,
        node_cai = -64,
        node_fast = 55,
        node_leave = -20,
        node_bbd_1 = 25,
        node_bbd_2 = 23,
        node_bbd_3 = 13,
        node_bbd_4 = 35,
        node_ybb_1 = 1,
        node_ybb_2 = 2,
        node_ybb_3 = 3,
        node_ybb_4 = 4,
        friend_list = {
            {
                user_name = '沙丁鱼',
                game_count = 545,
            },
            {
                user_name = '沙丁鱼',
                game_count = 545,
            },
            {
                user_name = '沙丁鱼',
                game_count = 545,
            },
            {
                user_name = '沙丁鱼',
                game_count = 545,
            },
            {
                user_name = '沙丁鱼',
                game_count = 545,
            },
            {
                user_name = '沙丁鱼',
                game_count = 545,
            },
            {
                user_name = '沙丁鱼',
                game_count = 545,
            },
            {
                user_name = '沙丁鱼',
                game_count = 545,
            },
        },
    }

    self:updateViews()
end

return PersonalView
