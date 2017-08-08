-- ./app/platform/game/game_common/user_detail.lua
require 'app.platform.game.game_common.game_component_base'

local user_detail = class('user_detail_component', view_component_base)
function user_detail:init(args)
    view_component_base.init(self)

    self.cur_show_user_id = nil
    self.cur_server_index = -1
    self.all_user_ip = {}

    -- 
    self:listenGameSignal('show_user_detail', function(user_id, x, y) self:show_user_detail(user_id, x, y) end)
    self:listenGameSignal('user_ip_addr', function(user_id, ip_data)
        self.all_user_ip[user_id] = ip_data

        if self.cur_show_user_id == user_id and self.csb_node then
            label('text_ip', ip_data, self.csb_node)
        end
    end)
    self:listenGameSignal('update_gps_data', function() self:update_gps_data() end)
end

function user_detail:show_user_detail(user_id, x, y)
    if self.csb_node then
        self.csb_node:removeFromParent(true)
        self.csb_node = nil
    end

    self.cur_show_user_id = user_id
    self.cur_server_index = self.game_scene:get_server_index_by_user_id(user_id)

    -- 
    self.csb_node = cc.CSLoader:createNode('game_common_res/component/user_detail/user_detail_view.csb')
    self.csb_node:setPosition(x or display.width * 0.5, y or display.height * 0.5)
    self.game_scene:addChild(self.csb_node, GAME_VIEW_Z_ORDER.USER_DETAIL)

    self.csb_node:getChildByName('background_user_detail'):setTouchEnabled(true)

    local user_info = self.game_scene:get_user_info(user_id)
    if user_info then
        label('text_user_name', user_info.m_nickName, self.csb_node)
        label('text_user_id', tostring(user_id), self.csb_node)
        if not user_info.m_bBoy then self.csb_node:getChildByName('sex_sprite'):setSpriteFrame('game_common_female.png') end
        label('text_paipin', tostring(user_info.m_cardqualityvalue or 0), self.csb_node)
        label('text_ip', self.all_user_ip[user_id] or '', self.csb_node)

        local zan_num = user_info.m_praisevalue or 0
        local cha_num = user_info.m_tramplevalue or 0
        local hao_ping_num = 100
        if zan_num ~= 0 and cha_num ~= 0 then
            hao_ping_num = math.floor(zan_num/(zan_num+cha_num)*100)
        end
        label('text_zanlv', hao_ping_num..'%', self.csb_node)
    end

    self:update_gps_data()
end

function user_detail:update_gps_data()
    if not self.csb_node then return end
    if not self.game_scene.gps_data then return end
    dump(self.game_scene.gps_data)

    -- gps information
    --[[
    local gps_info = { true, false, false, true }
    local gps_distance = { {100, 100, 100, 100}, {100, 100, 100, 100}, {100, 100, 100, 100}, {100, 100, 100, 100} }
    local gps_city = { '北京', '上海', '广州', '深圳' }
    --]]
    local gps_info = self.game_scene.gps_data.get_gps_info or {}
    local gps_distance = self.game_scene.gps_data.distance or {}
    local gps_city = self.game_scene.gps_data.city or {}
    --]]

    -- 这个玩家的地址
    local function __split__(str)
        local words = {}
        for uchar in string.gfind(str, "[%z\1-\127\194-\244][\128-\191]*") do
            words[#words+1] = uchar
        end
        return words
    end
    local address = gps_city[self.cur_server_index]
    if address then
        local str_address1 = string.gsub(address, '中国，', '')
        local str_address2 = string.gsub(address, '中国,', '')
        local words = __split__(str_address2)
        local checkword = (string.find(address, '市') and '市' or '县')

        local cut_address = ''
        for _, v in ipairs(words) do
            cut_address = cut_address .. v
            if v == checkword then break end
        end

        label('text_addr', cut_address, self.csb_node)
    else
        label('text_addr', '', self.csb_node)
    end

    -- 
    local all_user_info = self.game_scene.all_user_info

    local user_gps_distance = gps_distance[self.cur_server_index] or {}
    if gps_info[self.cur_server_index] then    -- 这个玩家有定位
        for server_index=1, 4 do
            if server_index ~= self.cur_server_index then
                if gps_info[server_index] then
                    local desc_name = (server_index == self.game_scene.my_server_index ) and '您' or tostring(all_user_info[server_index] and all_user_info[server_index].m_nickName or '获取失败')
                    local dis = user_gps_distance[server_index] < 0.1 and '太近' or '正常'
                    local text = string.format('距离 %s', desc_name)
                    label('text_info_' .. server_index, text, self.csb_node)
                    local warn_lable = label('text_warn_' .. server_index, dis, self.csb_node)
                    warn_lable:setColor(user_gps_distance[server_index] < 0.1 and cc.c3b(255, 71, 71) or cc.c3b(35, 139, 90))
                else
                    if all_user_info[server_index] then
                        local desc_name = (server_index == self.game_scene.my_server_index ) and '您' or tostring(all_user_info[server_index].m_nickName)
                        local text = desc_name .. ' 没有开启GPS定位！'

                        label('text_info_' .. server_index, text, self.csb_node)
                    else
                        label('text_info_' .. server_index, '等待玩家进入...', self.csb_node)
                    end

                    label('text_warn_' .. server_index, '', self.csb_node)
                end
            else
                label('text_info_' .. server_index, '----', self.csb_node)
                label('text_warn_' .. server_index, '', self.csb_node)
            end
        end
    else        -- 没有开启定位
        for server_index=1, 4 do
            if server_index == self.cur_server_index then
                local desc_name = (server_index == self.game_scene.my_server_index ) and '您' or tostring(all_user_info[server_index] and all_user_info[server_index].m_nickName or '获取失败')
                local text = desc_name .. ' 没有开启GPS定位！'
                label('text_info_' .. server_index, text, self.csb_node)
            else
                if all_user_info[server_index] then
                    local desc_name = (server_index == self.game_scene.my_server_index ) and '您' or tostring(all_user_info[server_index].m_nickName)
                    --local text = '距离 ' .. desc_name .. ' 未知！'
                    local text = '距离 ' .. desc_name
                    label('text_info_' .. server_index, text, self.csb_node)

                    local warn_lable = label('text_warn_' .. server_index, '未知', self.csb_node)
                    warn_lable:setColor(cc.c3b(255, 71, 71))
                else
                    label('text_info_' .. server_index, '等待玩家进入...', self.csb_node)
                end
            end
        end
    end
end

function user_detail:on_touch_began(touch, event)
    if self.csb_node then
        self.csb_node:removeFromParent(true)
        self.csb_node = nil

        self.cur_show_user_id = nil

        return true
    end

    return false
end

return user_detail
