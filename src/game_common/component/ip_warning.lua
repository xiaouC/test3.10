-- ./app/platform/game/game_common/ip_warning.lua
require 'app.platform.game.game_common.game_component_base'

local ip_warning = class('ip_warning_component', view_component_base)
function ip_warning:ctor(game_scene)
    view_component_base.ctor(self, game_scene)

    self.csb_file = 'game_common_res/component/ip_warning/ip_warning.csb'
    self.csb_z_order = 300
end

function ip_warning:init(args)
    view_component_base.init(self)

    self.all_user_ip = {}

    -- 
    self.node_warning_1 = self.csb_node:getChildByName('node_warning_1')
    self.node_warning_2 = self.csb_node:getChildByName('node_warning_2')

    button('btn_warning', function()
        show_msg_box_2('', self.gps_warn_text or '')
    end, self.node_warning_2)

    button('btn_detail', function()
        show_msg_box_2('', self.gps_warn_text or '')
        --[[
        -- test
        for index, v in pairs(self.game_scene.all_user_info) do
            self.game_scene:fire('user_ip_addr', v.m_dwUserID, (index == 1 or index == 2 ) and '192.168.1.1' or '192.168.0.1')
        end
        --]]
    end, self.node_warning_2)

    -- 
    self:listenGameSignal('update_gps_data', function() self:update_gps_data() end)
    self:listenGameSignal('user_ip_addr', function(user_id, ip_data)
        self.all_user_ip[user_id] = ip_data
        self:update_user_ip()
    end)

    --[[
    -- test
    self.game_scene.gps_data = {
        gps_info = { true, false, false, true },
        gps_distance = { {0.1, 0.1, 0.1, 0.1}, {0.1, 0.1, 0.1, 0.1}, {0.1, 0.1, 0.1, 0.1}, {0.1, 0.1, 0.1, 0.1} },
        gps_city = { '北京', '上海', '广州', '深圳' },
    }
    self.game_scene:fire('update_gps_data')
    --]]

    self:update_gps_data()
end

function ip_warning:on_game_state(game_state)
    view_component_base.on_game_state(self, game_state)

    if game_state ~= 'waiting' then
        self.csb_node:setVisible(false)
    end
end

function ip_warning:update_gps_data()
    if not self.game_scene.gps_data then return end
    dump(self.game_scene.gps_data)

    -- gps information
    local gps_info = self.game_scene.gps_data.get_gps_info or {}
    local gps_distance = self.game_scene.gps_data.distance or {}
    local gps_city = self.game_scene.gps_data.city or {}

    -- 
    self.gps_warn_text = ''
    local all_user_info = self.game_scene.all_user_info

    -- 
    for server_index=1, 4 do
        local user_info = all_user_info[server_index]
        if gps_info[server_index] and user_info then
            local text = user_info.m_nickName .. ' 与 '

            local name_list = {}
            for i=1, 4 do
                if server_index ~= i and gps_info[i] and all_user_info[i] and gps_distance[server_index][i] <= 0.1 then
                    table.insert(name_list, all_user_info[i].m_nickName)
                end
            end

            if #name_list > 0 then
                self.gps_warn_text = self.gps_warn_text .. text .. table.concat(name_list, ',') .. '距离过近\n'
            end
        else
            if user_info then
                self.gps_warn_text = self.gps_warn_text .. string.format('%s　未开启定位\n', user_info.m_nickName)
            end
        end
    end

    self.node_warning_2:setVisible(self.gps_warn_text ~= '')
end

function ip_warning:update_user_ip()
    local ip_groups = {}

    local all_user_info = self.game_scene.all_user_info
    for server_index=1, 4 do
        local user_info = all_user_info[server_index]
        if user_info then
            local ip = self.all_user_ip[user_info.m_dwUserID]
            if ip then
                if not ip_groups[ip] then ip_groups[ip] = {} end
                table.insert(ip_groups[ip], user_info.m_nickName)
            end
        end
    end

    if self.rt_ip_warning then self.rt_ip_warning:removeFromParent(true) end

    self.rt_ip_warning = ccui.RichText:create()
    self.rt_ip_warning:ignoreContentAdaptWithSize(false)
    self.rt_ip_warning:setAnchorPoint(cc.p(0, 1.0))
    self.rt_ip_warning:setContentSize(cc.size(350, 0) )
    self.node_warning_1:getChildByName('node_text_users'):addChild(self.rt_ip_warning)

    local flag = false
    for _, v in pairs(ip_groups) do
        if #v >= 2 then
            flag = true

            local text = table.concat(v, ',')

            local msg_label = ccui.RichElementText:create(1, cc.c3b(255, 234, 0), 255, 'IP相同：', 'font/fzzyjt.ttf', 24)
            self.rt_ip_warning:pushBackElement(msg_label)

            local msg_label = ccui.RichElementText:create(2, cc.c3b(255, 255, 255), 255, text, 'font/fzzyjt.ttf', 24)
            self.rt_ip_warning:pushBackElement(msg_label)

            self.rt_ip_warning:formatText()
        end
    end

    self.node_warning_1:setVisible(flag)
end

return ip_warning
