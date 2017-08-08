-- ./app/platform/room/new_view/new_hall_personal.lua

local m_clientmain = require 'app.platform.room.clientmain'
local m_def = require 'app.platform.room.module.basicnotifydef'

local popup_base = require 'app.platform.common.popup_base'
local new_hall_personal = class('new_hall_personal', popup_base)
function new_hall_personal:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/personal/new_hall_personal.csb'
    self.z_order = 100

    -- 
    popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function new_hall_personal:initViews()
    popup_base.initViews(self)

    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info() or {}
    label('text_room_card', tostring(user_info.m_roomcard or 0), self.csb_node)

    button('btn_buy', function() self.scene_instance:bugRoomCard() end, self.csb_node)

    -- 
    local lv_radio = self.csb_node:getChildByName('lv_radio')
    lv_radio:setScrollBarEnabled(false)
    lv_radio:setItemsMargin(20)

    local rb_group = ccui.RadioButtonGroup:create()
    self:addChild(rb_group)

    local personal_options = {
        {
            name = '个人信息',
            csb_file = 'hall_res/personal/item_personal.csb',
            init_func = function(node) self:initPersonalView(node) end,
        },
        --[[
        {
            name = '游戏人生',
        },
        {
            name = '专属语音',
        },
        --]]
    }

    local all_item_node = {}
    local node_content = self.csb_node:getChildByName('node_content')
    local img_normal, img_selected = 'btn_gameselect_2.png', 'btn_gameselect_1.png'
    for _, v in ipairs(personal_options) do
        local rb_widget, rb, text_label = createRadioWidget{
            img_normal = 'btn_gameselect_2.png',
            img_selected = 'btn_gameselect_1.png',
            tex_res_type = ccui.TextureResType.plistType,
            text = v.name,
            font_size = 30,
            enable_outline = true,
        }

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

function new_hall_personal:initPersonalView(node_personal)
    -- friends
    local lv_friends = node_personal:getChildByName('lv_friends')
    lv_friends:setScrollBarEnabled(false)

    --
    self:appendView('update_personal_info', function()
        if not tolua.cast(node_personal, 'Node') then return end

        -- 牌品，人品，素质，出牌
        local atlas_labels = { 'al_paipin', 'al_haoping', 'al_chaping', 'al_fast', 'al_leave', 'al_bbd_1', 'al_bbd_2', 'al_bbd_3', 'al_bbd_4', 'al_ybb_1', 'al_ybb_2', 'al_ybb_3', 'al_ybb_4' }
        for _, name in pairs(atlas_labels) do
            print('name : ' .. tostring(name))
            local text = string.gsub(tostring(self.recv_personal_data[name] or 0), '-', '/')
            print('text : ' .. tostring(text))
            node_personal:getChildByName(name):setString(text)
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

function new_hall_personal:initDataFromServer()
    self.recv_personal_data = { friend_list = {} }

    if self.scene_instance.userbrand then
        local ub = self.scene_instance.userbrand[1]
        if ub and ub.high then
            self.recv_personal_data.al_haoping = tonumber(ub.high)
            self.recv_personal_data.al_chaping = tonumber(ub.balance)
            self.recv_personal_data.al_fast = tonumber(ub.quick)
            self.recv_personal_data.al_leave = tonumber(ub.halfway)
            self.recv_personal_data.al_paipin = self.recv_personal_data.al_haoping + self.recv_personal_data.al_chaping + self.recv_personal_data.al_fast - self.recv_personal_data.al_leave
        end
    end

    if self.scene_instance.uservalue then
        local uv = self.scene_instance.uservalue[1]
        if uv and uv.goodpp then
            self.recv_personal_data.al_bbd_1 = tonumber(uv.goodpp)    --牌品
            self.recv_personal_data.al_bbd_2 = tonumber(uv.goodrb)    --人品
            self.recv_personal_data.al_bbd_3 = tonumber(uv.goodsz)    --素质
            self.recv_personal_data.al_bbd_4 = tonumber(uv.goodsd)    --出牌闪电
            self.recv_personal_data.al_ybb_1 = tonumber(uv.sopp)    
            self.recv_personal_data.al_ybb_2 = tonumber(uv.sorb)
            self.recv_personal_data.al_ybb_3 = tonumber(uv.sosz)
            self.recv_personal_data.al_ybb_4 = tonumber(uv.sosd)
        end
    end

    for _, v in ipairs(self.scene_instance.oftenplay or {}) do
        table.insert(self.recv_personal_data.friend_list, {
            head_url = v.headurl,
            user_name = v.nickname,
            game_count = v.count,
        })
    end

    self:updateViews()
end


return new_hall_personal
