-- ./app/platform/room/new_view/new_game_record.lua

local m_clientmain = require 'app.platform.room.clientmain'
local m_def = require 'app.platform.room.module.basicnotifydef'

local popup_base = require 'app.platform.common.popup_base'
local new_game_record = class('new_game_record', popup_base)
function new_game_record:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/record/new_hall_record.csb'
    self.z_order = 100

    self.recv_user_data = {
        total_count = 0,
        win_count = 0,
        score = 0,
        ticket = 0,
    }
    self.recv_big_record_list = {}
    self.recv_small_record_list = {}
    self.is_small_record_flag = false

    -- 
    popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function new_game_record:initViews()
    popup_base.initViews(self)

    -- 
    button('btn_close', function()
        if self.is_small_record_flag then return self:updateView('update_record', true) end
        self:onClose()
    end, self.csb_node)
    button('btn_buy', function() self.scene_instance:bugRoomCard() end, self.csb_node)

    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info() or {}
    label('text_room_card', tostring(user_info.m_roomcard or 0), self.csb_node)

    --self.csb_node:getChildByName('bg_mask'):setVisible(false)

    -- 
    local node_small_item_title = self.csb_node:getChildByName('small_item_title')
    local lv_small_record = self.csb_node:getChildByName('lv_small_record')
    lv_small_record:setScrollBarEnabled(false)

    local lv_big_record = self.csb_node:getChildByName('lv_big_record')
    lv_big_record:setScrollBarEnabled(false)

    self:appendView('update_user_data', function()
        if not tolua.cast(self.csb_node, 'Node') then return end
        self.csb_node:getChildByName('al_total_count'):setString(tostring(self.recv_user_data.total or 0))
        self.csb_node:getChildByName('al_win_count'):setString(tostring(self.recv_user_data.wintotal or 0))
        self.csb_node:getChildByName('al_score'):setString(tostring(self.recv_user_data.score or 0))
        self.csb_node:getChildByName('al_ticket'):setString(tostring(self.recv_user_data.gift or 0))
    end)

    self:appendView('update_record', function(is_big_record, big_record_data, small_record_data)
        if not tolua.cast(self.csb_node, 'Node') then return end

        self.is_small_record_flag = not is_big_record

        local record_list = (is_big_record and self.recv_big_record_list or small_record_data)
        local item_record_csb_file = (is_big_record and 'hall_res/record/big_record_item.csb' or 'hall_res/record/small_record_item.csb')
        local lv_content = (is_big_record and lv_big_record or lv_small_record)

        -- 
        if not is_big_record then
            label('text_game_name', big_record_data.game_name, node_small_item_title)
            label('text_desc', big_record_data.game_desc, node_small_item_title)
        end

        node_small_item_title:setVisible(not is_big_record)
        lv_small_record:setVisible(not is_big_record)
        lv_big_record:setVisible(is_big_record)

        -- 
        lv_content:removeAllChildren()
        for index, v in ipairs(record_list or {}) do
            local item_widget, item_node = createWidget(item_record_csb_file, 1260, 250)

            -- game id, game name, game time
            if v.game_name then label('text_game_name', v.game_name, item_node) end
            if v.game_desc then label('text_desc', v.game_desc, item_node) end
            if not is_big_record then label('text_round', string.format('第%d局', index), item_node) end

            item_node:getChildByName('node_win_flag'):addChild(cc.Sprite:createWithSpriteFrameName('hall_record_win_tag.png'))

            -- user
            local lv_user_list = item_node:getChildByName('lv_users')
            lv_user_list:setScrollBarEnabled(false)
            lv_user_list:setEnabled(false)
            for _, ui in ipairs(v.user_info or {}) do
                local user_item_widget, user_item_node = createWidget('hall_res/record/user_item.csb', 220, 140)

                local head_sprite = createUserHeadSprite({m_bLogoID = 1, m_headurl = ui.head_url}, 0.8)
                user_item_node:getChildByName('node_head'):addChild(head_sprite)

                label('text_name', ui.user_name, user_item_node)
                label('text_id', ui.user_id, user_item_node)
                label('text_total_score', ui.total_score, user_item_node)

                if is_big_record then
                    local node_ticket = user_item_node:getChildByName('node_ticket')
                    node_ticket:setVisible(true)

                    label('text_ticket', ui.ticket, node_ticket)
                else
                    label('text_win_score', '成绩：' .. ui.win_score, user_item_node)
                end

                if ui.is_big_winner then
                    user_item_node:getChildByName('node_winer'):addChild(cc.Sprite:createWithSpriteFrameName('hall_record_winner.png'))
                end

                lv_user_list:addChild(user_item_widget)
            end
            lv_user_list:requestDoLayout()

            if is_big_record then
                button('btn_record_small', function()
                    self.lv_content_inner_position = lv_content:getInnerContainerPosition()

                    self:watchSmallRecord(v)
                end, item_node)
            else
                button('btn_save', function() api_show_Msg_Tip("努力开发中，敬请期待") end, item_node)
                button('btn_share', function() api_show_Msg_Tip("努力开发中，敬请期待") end, item_node)
                button('btn_watch', function()
                    self:downloadRecord{
                        game_id = v.game_id,
                        room_id = v.room_id,
                        record_url = v.record_url,
                        cur_index = index,
                        total_count = #record_list,
                        user_list = v.user_info,
                    }
                end, item_node)
            end

            -- 
            lv_content:addChild(item_widget)
        end
        --lv_content:requestDoLayout()
        lv_content:forceDoLayout()

        if is_big_record then
            if self.lv_content_inner_position then
                lv_content:setInnerContainerPosition(self.lv_content_inner_position)
            end
        else
            lv_content:jumpToTop()
        end
    end)
end

function new_game_record:watchSmallRecord(big_record_data)
    if self.current_big_record_data then return end

    if self.recv_small_record_list[big_record_data] then
        self.scene_instance:schedule_once(function()
            self.current_big_record_data = nil

            self:updateView('update_record', false, big_record_data, self.recv_small_record_list[big_record_data])
        end)

        return
    end

    self.current_big_record_data = big_record_data

    api_show_loading('request_play_record')
    m_clientmain:get_instance():get_record_mgr():request_play_record(big_record_data.desk_id, big_record_data.uid)
end

function new_game_record:downloadRecord(record_info)
    api_show_loading_extern(10,"正在获取数据。。。")

    local url = record_info.record_url
    local file_name = device.writablePath .. MD5(url):toString() .. '.record'

    -- 
    if io.exists(file_name) then return self:playRecord(file_name, record_info) end

    -- 
    local xhr = cc.XMLHttpRequest:new()
    xhr.responseType = cc.XMLHTTPREQUEST_RESPONSE_BLOB
    xhr:open("GET", url)

    xhr:registerScriptHandler(function()
        xhr:unregisterScriptHandler()

        if xhr.readyState == 4 and (xhr.status >= 200 and xhr.status < 207) then
            if io.writefile(file_name, xhr.response) then
                if tolua.cast(self, 'Node') then
                    self:playRecord(file_name, record_info)
                end
            end
        else
            api_hide_loading_ext()
            print("xhr.readyState is:", xhr.readyState, "xhr.status is: ",xhr.status)
        end
    end)

    xhr:send()
end

function new_game_record:playRecord(file_name, record_info)
    local game_id = tonumber(record_info.game_id)

    -- 
    local replay_scene = nil
    pcall(function()
        replay_scene = require(string.format('app.platform.game.%d.ui.game_scene_replay', game_id))
    end)

    if replay_scene then
        local my_server_index = 1
        local game_scene = replay_scene.new(my_server_index, file_name)

        game_scene:init()
        cc.Director:getInstance():replaceScene(game_scene)
    else
        show_msg_box_2('', '录像看不了')
    end

    --scene:initUserInfo(user_info_list, {
    --    room_id = record_info.room_id,
    --    m_cur_play_count = record_info.cur_index,
    --    m_total_play_count = record_info.total_count,
    --    game_id = record_info.game_id,
    --})
end

function new_game_record:initDataFromServer()
    popup_base.initDataFromServer(self)

    m_clientmain:get_instance():get_record_mgr():get_event_mgr():BsAddNotifyEvent(m_def.NOTIFY_RECORD_EVENT, function(event)
        api_hide_loading('onRecordEvent')

        if not event or not event.args then return end
        if event.args.event_data.ret ~= 0 then return end

        local data = event.args.event_data.data
        if m_def.NOTIFY_RECORD_EVENT_BIGRECORD == event.args.event_id then
            self.recv_user_data = data.userinfo
            self:updateView('update_user_data')

            -- 
            self.recv_big_record_list = {}
            for _, v in ipairs(data.list or {}) do
                local max_score = -999999999
                for _, ud in ipairs(v.userdata or {}) do
                    if ud.totalscore > max_score then
                        max_score = ud.totalscore
                    end
                end

                local user_info = {}
                for _, ud in ipairs(v.userdata or {}) do
                    table.insert(user_info, {
                        user_name = string.urldecode(ud.nickname),
                        user_id = ud.uid,
                        head_url = ud.headurl,
                        ticket = ud.rewardgift,
                        total_score = ud.totalscore,
                        is_big_winner = (max_score <= ud.totalscore),
                    })
                end

                local dt = os.date("*t", tonumber(v.time or os.time())); 
                table.insert(self.recv_big_record_list, {
                    desk_id = v.desk_id,
                    uid = v.uid,
                    game_name = v.gamename,
                    game_desc = string.format('%d/%02d/%02d %02d:%02d    %s', dt.year, dt.month, dt.day, dt.hour, dt.min, v.desc or ''),
                    user_info = user_info,
                })
            end
            self:updateView('update_record', true)
        elseif m_def.NOTIFY_RECORD_EVENT_PLAYERRECORD == event.args.event_id then
            if not self.current_big_record_data then return end

            local small_record_data = {}
            for _, v in ipairs(data or {}) do
                local max_score = -999999999
                for _, ud in pairs(v.player or {}) do
                    if tonumber(ud.totalscore) > max_score then
                        max_score = tonumber(ud.totalscore)
                    end
                end

                local user_info = {}
                for k, ud in pairs(v.player or {}) do
                    user_info[tonumber(k)] = {
                        user_name = string.urldecode(ud.user),
                        user_id = ud.ID,
                        head_url = ud.headurl,
                        total_score = tonumber(ud.totalscore),    -- 总分
                        win_score = tonumber(ud.winscore),        -- 成绩
                        is_big_winner = (max_score <= tonumber(ud.totalscore)),
                    }
                end

                local dt = os.date("*t", tonumber(v.time or os.time())); 
                table.insert(small_record_data, {
                    game_id = v.gameid,
                    room_id = v.id or 0,
                    record_url = v.url,
                    game_desc = string.format('牌局ID：%d    %d/%02d/%02d %02d:%02d', v.id or 0, dt.year, dt.month, dt.day, dt.hour, dt.min),
                    user_info = user_info,
                })
            end

            self.recv_small_record_list[self.current_big_record_data] = small_record_data
            self:updateView('update_record', false, self.current_big_record_data, small_record_data)
            self.current_big_record_data = nil
        end
    end)

    api_show_loading('request_play_big_record')
    m_clientmain:get_instance():get_record_mgr():request_play_big_record()
    --]]

    --[[
    self.recv_user_data = {
        total = 10,
        wintotal = 5,
        score = 64,
        gift = 56,
    }
    self:updateView('update_user_data')

    for i=1, 10 do
        table.insert(self.recv_big_record_list, {
            game_name = '红中麻将',
            game_desc = '2017/06/19 15:35    (8局，可胡七对，四红中全码，一张定吗)',
            user_info = {
                {
                    user_name = '沙丁鱼',
                    user_id = 100861,
                    head_url = 'http://192.168.1.21/46.jpg',
                    ticket = 8,
                    total_score = 23,
                    is_big_winner = true,
                },
                {
                    user_name = '沙丁鱼',
                    user_id = 100861,
                    head_url = 'http://192.168.1.21/46.jpg',
                    ticket = 8,
                    total_score = 23,
                    is_big_winner = false,
                },
                {
                    user_name = '沙丁鱼',
                    user_id = 100861,
                    head_url = 'http://192.168.1.21/46.jpg',
                    ticket = 8,
                    total_score = 23,
                    is_big_winner = false,
                },
                {
                    user_name = '沙丁鱼',
                    user_id = 100861,
                    head_url = 'http://192.168.1.21/46.jpg',
                    ticket = 8,
                    total_score = 23,
                    is_big_winner = false,
                },
            },
        })
    end

    for i=1, 10 do
        local big_record_data = self.recv_big_record_list[i]

        self.recv_small_record_list[big_record_data] = {}
        for j=1, 8 do
            table.insert(self.recv_small_record_list[big_record_data], {
                game_id = 20000053,
                room_id = 1,
                record_url = '',
                game_desc = '牌局ID：123456    2017/06/19 15:35',
                user_info = {
                    {
                        user_name = '沙丁鱼',
                        user_id = 100861,
                        head_url = 'http://192.168.1.21/46.jpg',
                        ticket = 15,
                        total_score = 23,
                        win_score = 8,
                        is_big_winner = true,
                    },
                    {
                        user_name = '沙丁鱼',
                        user_id = 100861,
                        head_url = 'http://192.168.1.21/46.jpg',
                        ticket = 15,
                        total_score = 23,
                        win_score = 8,
                        is_big_winner = false,
                    },
                    {
                        user_name = '沙丁鱼',
                        user_id = 100861,
                        head_url = 'http://192.168.1.21/46.jpg',
                        ticket = 15,
                        total_score = 23,
                        win_score = 8,
                        is_big_winner = false,
                    },
                    {
                        user_name = '沙丁鱼',
                        user_id = 100861,
                        head_url = 'http://192.168.1.21/46.jpg',
                        ticket = 15,
                        total_score = 23,
                        win_score = 8,
                        is_big_winner = false,
                    },
                },
            })
        end
    end
    --]]

    self:updateView('update_record', true)
end

--local game_id, my_server_index, replay_file = 20000001, 2, 'hongzhong_replay.txt'
--switchScene(string.format('app.platform.game.%d.ui.game_scene_replay', game_id), my_server_index, replay_file)

return new_game_record
