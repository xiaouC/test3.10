require 'app.platform.room.new_view.loading'

local m_clientmain = require 'app.platform.room.clientmain'

local popup_base = require 'app.platform.common.popup_base'
local ActiveView = class('ActiveView', popup_base)
function ActiveView:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/activity/active_view.csb'
    self.cur_sel_index = args.index or 1

    for _, v in pairs(args.data or {}) do
        if tonumber(v.id) == 5 then self.daily_data = v end
        if tonumber(v.id) == 6 then self.win_data = v end
        if tonumber(v.id) == 7 then self.vip_data = v end
    end

    popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function ActiveView:initViews()
    popup_base.initViews(self)

    -- 
    local text_label = cc.Label:createWithTTF('活跃任务', 'res/font/jxk.TTF', 40)
    text_label:setAnchorPoint(0.5, 0.5)
    text_label:setColorTextureIndex(3)
    text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    text_label:enableOutline(cc.c3b(80, 27, 7), 2)
    text_label:enableShadow()
    self.csb_node:getChildByName('node_title'):addChild(text_label)

    -- 
    button('btn_share', function()
        self.scene_instance.current_active_index = 1
        m_clientmain:get_instance():get_welfare_mgr():request_gift_info()

        self:onClose()
    end, self.csb_node)

    -- 
    local rb_group = ccui.RadioButtonGroup:create()
    self.anim_node:addChild(rb_group)

    local tab_active_config = {
        {
            text = '永久VIP',
            node_name = 'node_vip',
            init = function(node)
                local node_vip = node:getChildByName('node_vip')
                local node_receive = node:getChildByName('node_receive')
                node_vip:setVisible(self.vip_data.m_vip_status ~= 1)
                node_receive:setVisible(self.vip_data.m_vip_status == 1)

                -- 
                button('btn_vip', function() m_clientmain:get_instance():get_sdk_mgr():request_product_weixin(self.vip_data.uid) end, node_vip)
                local btn_receive = button('btn_receive', function() m_clientmain:get_instance():get_welfare_mgr():request_task_card_gift(self.vip_data.uid, 0) end, node_receive)
                btn_receive:setEnabled(self.vip_data.m_already_get == 0)
            end,
        },
        {
            text = '每日任务',
            node_name = 'node_daily',
            init = function(node)
                dump(self.daily_data.list)
                local lv_content = node:getChildByName('lv_content')
                for i, v in ipairs(self.daily_data.list or {}) do
                    local item_widget, item_node = createWidget('hall_res/activity/daily_item.csb', 665, 120)
                    lv_content:addChild(item_widget)

                    item_node:getChildByName('node_icon'):addChild(cc.Sprite:create(i == 1 and 'hall_res/activity/img_day_1.png' or 'hall_res/activity/img_day_2.png'))

                    label('text_desc', v.task_desc, item_node)
                    label('text_reward_count', v.m_gift_num, item_node)
                    label('text_task_count', v.m_play_num, item_node)

                    local btn_game = button('btn_game', function()
                        -- 开包间
                        if v.m_status == 0 then
                            api_show_loading()

                            G_in_Hall = false

                            m_clientmain:get_instance():get_user_mgr():request_user_info()
                            m_clientmain:get_instance():get_room_mgr():request_desk_owner()

                            self:onClose()

                            return
                        end

                        -- 领取奖励
                        m_clientmain:get_instance():get_welfare_mgr():request_task_card_gift(v.m_task_type, v.m_task_id) 
                    end, item_node)
                    if v.m_status == 1 then btn_game:getRendererNormal():loadTextureNormal('hall_res/activity/btn_day_task_get.png') end
                    if v.m_status == 2 then btn_game:setEnabled(false) end
                end
                lv_content:requestDoLayout()
            end,
        },
        {
            text = '胜局任务',
            node_name = 'node_win',
            init = function(node)
                local btn_receive = button('btn_receive', function() m_clientmain:get_instance():get_welfare_mgr():request_task_card_gift(tostring(self.win_data.uid), 0) end, node)
                btn_receive:setTitleText(self.win_data.task_record == 1 and '领  取' or '已领取')
                btn_receive:setEnabled(self.win_data.state == 1)

                local rank_label = label('text_rank', self.win_data.ranking, node)
                if self.win_data.state == 0 then
                    label('text_task_state', '当前任务状态：第      名', node)
                elseif self.win_data.state == 1 then
                    label('text_task_state', '当前任务状态：已完成', node)
                    rank_label:setVisible(false)
                else
                    label('text_task_state', '当前任务状态：已领取', node)
                    rank_label:setVisible(false)
                end
            end,
        },
    }

    self.cur_active_node = nil
    for i, v in ipairs(tab_active_config) do
        local tab_node, rb, tab_onchanged = create_activity_radio_button(v.text, self.cur_sel_index == i)
        rb_group:addRadioButton(rb)
        self.csb_node:getChildByName('btn_node_' .. i):addChild(tab_node)

        local item_node = self.csb_node:getChildByName(v.node_name)
        item_node:setVisible(self.cur_sel_index == i)
        v.init(item_node)

        rb:addEventListener(function(_, event_type)
            tab_onchanged(event_type)
            item_node:setVisible(event_type == ccui.RadioButtonEventType.selected)
        end)

        if self.cur_sel_index == i then
            rb_group:setSelectedButton(rb)
        end
    end
end

return ActiveView
