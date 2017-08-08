-- ./app/platform/room/new_view/record_view.lua
require 'app.platform.room.new_view.loading'

local popup_base = require 'app.platform.common.popup_base'
local RecordView = class('RecordView', popup_base)
function RecordView:ctor(model_install, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/record/game_record.csb'
    self.recv_data = {
        total_count = 0,
        win_count = 0,
        score = 0,
        ticket = 0,
        record_list = {},
    }

    popup_base.ctor(self, model_install, args, function(popup_self, node, cb)
        if cb then cb() end
    end, function(popup_self, node, cb)
        popup_self:removeFromParent()
        if cb then cb() end
    end)
end

function RecordView:initViews()
    popup_base.initViews(self)

    -- 
    local lv_content = self.csb_node:getChildByName('lv_content')
    lv_content:setScrollBarEnabled(false)
    lv_content:setItemsMargin(20)

    self:appendView('update_record', function()
        if not tolua.cast(self.csb_node, 'Node') then return end

        -- 
        local total_count_label = cc.LabelAtlas:_create(tostring(self.recv_data.total_count), "hall_res/common/img_num.png", 30, 42, string.byte('0'))
        total_count_label:setAnchorPoint(0, 0.5)
        total_count_label:setScale(0.6)
        self.csb_node:getChildByName('node_total_count'):addChild(total_count_label)

        local win_count_label = cc.LabelAtlas:_create(tostring(self.recv_data.win_count), "hall_res/common/img_num.png", 30, 42, string.byte('0'))
        win_count_label:setAnchorPoint(0, 0.5)
        win_count_label:setScale(0.6)
        self.csb_node:getChildByName('node_win_count'):addChild(win_count_label)

        local score_label = cc.LabelAtlas:_create(tostring(self.recv_data.score), "hall_res/common/img_num.png", 30, 42, string.byte('0'))
        score_label:setAnchorPoint(0, 0.5)
        score_label:setScale(0.6)
        self.csb_node:getChildByName('node_score'):addChild(score_label)

        local ticket_label = cc.LabelAtlas:_create(tostring(self.recv_data.ticket), "hall_res/common/img_num.png", 30, 42, string.byte('0'))
        ticket_label:setAnchorPoint(0, 0.5)
        ticket_label:setScale(0.6)
        self.csb_node:getChildByName('node_ticket'):addChild(ticket_label)

        -- 
        lv_content:removeAllChildren()
        for _, v in ipairs(self.recv_data.record_list or {}) do
            local item_widget, item_node = createWidget('hall_res/record/item_record.csb', 1260, 140)

            -- game id, game name, game time
            label('text_game_id', '牌局ID：' .. v.game_id, item_node)
            label('text_game_name', v.game_name, item_node)

            local dt = os.date("*t", tonumber(v.game_time));
            label('text_game_time', string.format("%d/%02d/%02d %02d:%02d", dt.year, dt.month, dt.day, dt.hour, dt.min), item_node)

            -- user
            local function __create_user_item__(user_info)
                if not user_info then return end

                local user_item_node = cc.CSLoader:createNode('hall_res/record/item_user.csb')

                local head_sprite = cc.Sprite:create('hall_res/head/head_7.png')
                head_sprite:setScale(0.8)
                user_item_node:getChildByName('node_head'):addChild(head_sprite)

                label('text_name', user_info.user_name, user_item_node)
                label('text_id', user_info.user_id, user_item_node)
                label('text_score', '成绩：' .. user_info.score, user_item_node)
                label('text_total_score', '总积分：' .. user_info.total_score, user_item_node)

                return user_item_node
            end

            for i=1, 4 do
                local user_item_node = __create_user_item__(v.user_info[i])
                if user_item_node then
                    item_node:getChildByName('node_' .. i):addChild(user_item_node)
                end
            end

            button('btn_save', function() end, item_node)
            button('btn_share', function() end, item_node)
            button('btn_watch', function() end, item_node)

            -- 
            lv_content:addChild(item_widget)
        end
        lv_content:requestDoLayout()
    end)
end

function RecordView:initDataFromServer()
    self.recv_data = {
        total_count = 10,
        win_count = 5,
        score = 64,
        ticket = 56,
        record_list = {},
    }
    for i=1, 10 do
        table.insert(self.recv_data.record_list, {
            game_id = 123456,
            game_name = '红中麻将（自摸）',
            game_time = os.time(),
            user_info = {
                {
                    user_name = '沙丁鱼',
                    user_id = 100861,
                    score = 8,
                    total_score = 23,
                },
                {
                    user_name = '沙丁鱼',
                    user_id = 100861,
                    score = 8,
                    total_score = 23,
                },
                {
                    user_name = '沙丁鱼',
                    user_id = 100861,
                    score = 8,
                    total_score = 23,
                },
                {
                    user_name = '沙丁鱼',
                    user_id = 100861,
                    score = 8,
                    total_score = 23,
                },
            },
        })
    end

    self:updateViews()
end

return RecordView
