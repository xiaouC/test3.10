-- ./app/platform/room/new_view/mall_view.lua

require 'app.platform.room.new_view.loading'
local m_clientmain = require 'app.platform.room.clientmain'
local m_def = require 'app.platform.room.module.basicnotifydef'

local pay_mode = {
    ['apple_pay'] = function(pay_id) m_clientmain:get_instance():get_sdk_mgr():request_product_weixin(pay_id, PAY_TYPE_APPLE_IAP) end,
    ['wechat_pay'] = function(pay_id) m_clientmain:get_instance():get_sdk_mgr():request_product_weixin(pay_id, PAY_TYPE_WECHAT) end,
    ['ali_pay'] = function(pay_id) end,
}

local popup_base = require 'app.platform.common.popup_base'
local MallView = class('MallView', popup_base)
function MallView:ctor(model_install, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/mall/mall_view.csb'
    self.z_order = 200
    self.goods_data = {}

    -- 默认微信支付
    self.pay_func = pay_mode[args] or pay_mode['wechat_pay']

    popup_base.ctor(self, model_install, args, show_anim_func, hide_anim_func)
end

function MallView:initViews()
    popup_base.initViews(self)

    local function __init_item__(item_index, item_info)
        local node_item = self.csb_node:getChildByName('node_item_' .. item_index)
        if node_item then
            label('text_desc', item_info.desc, node_item)
            node_item:getChildByName('mall_recommend'):setVisible(item_info.is_recommend == 1 and true or false)
            node_item:getChildByName('node_content'):addChild(cc.CSLoader:createNode(string.format('hall_res/mall/mall_item_content_%d.csb', item_index)))

            local btn_buy = button('btn_buy', function() self.pay_func(item_info.id) end, node_item)
            local size = btn_buy:getContentSize()

            local text_label = cc.Label:createWithTTF(item_info.price .. '元', 'font/fzzyjt.ttf', 30)
            text_label:setAnchorPoint(0.5, 0.5)
            text_label:setPosition(size.width * 0.5, size.height * 0.5)
            text_label:enableOutline(cc.c3b(211, 107, 23), 2)
            btn_buy:getRendererNormal():addChild(text_label)
        end
    end

    -----------------------------------------------------------------------------------------------------------------------------------------------------
    self:appendView('goods_list', function()
        if not tolua.cast(self.csb_node, 'Node') then return end

        -- item 1 - 4
        for index, v in ipairs(self.goods_data.goods or {}) do
            __init_item__(index, v)
        end

        -- 
        local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info() 
        local csb_node_file = (user_info.m_vip_level == '0' and 'hall_res/mall/mall_left_content_2.csb' or 'hall_res/mall/mall_left_content_1.csb')
        local node_left = cc.CSLoader:createNode(csb_node_file)
        self.csb_node:getChildByName('node_left'):addChild(node_left)

        -- 
        local vg = (user_info.m_vip_level == '0' and self.goods_data.vip_good[1] or self.goods_data.vip_good[2])
        node_left:getChildByName('text_desc'):setString(vg.desc)

        button('btn_sale', function() self.pay_func(vg.id) end, node_left)
    end)

end

function MallView:clear()
    new_hide_loading()

    popup_base.clear(self)
end

function MallView:initDataFromServer()
    popup_base.initDataFromServer(self)

    m_clientmain:get_instance():get_product_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_GOODS_EVENT, function(event)
        new_hide_loading()

        if not event or not event.args then return end
        if event.args.event_data.ret ~= 0 then return Msg:showMsgBox(3, event.args.event_data.desc, nil) end

        self.goods_data = event.args.event_data.data
        dump(self.goods_data)

        self:updateViews()
    end)

    -- request goods list
    new_show_loading()
    m_clientmain:get_instance():get_product_mgr():request_goods_list_new(self.pay_mode == 'apple_pay' and 1 or 0)
end

return MallView
