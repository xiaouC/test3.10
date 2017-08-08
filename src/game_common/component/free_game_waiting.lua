-- ./app/platform/game/game_common/free_game_waiting.lua
require 'app.platform.game.game_common.game_component_base'

local free_game_waiting = class('free_game_waiting_component', component_base)
function free_game_waiting:init(args)
    component_base.init(self)

    -- 
    self.csb_node = nil
    self.total_user_count = 4
    self.agree_user_ids = {}
    self.cd_handler = nil

    -- 
    self:listenGameSignal('user_free_result', function(server_index, user_id, result)
        if self.cd_handler then
            self.game_scene:unschedule(self.cd_handler)
            self.cd_handler = nil
        end

        self.agree_user_ids = {}
        if self.csb_node then self.csb_node:setVisible(false) end
    end)
    self:listenGameSignal('user_free_operate', function(apply_server_index, apply_user_id, op_user_server_index, op_user_id, is_agree)
        self:user_free_operate(apply_server_index, apply_user_id, op_user_server_index, op_user_id, is_agree)
    end)
    self:listenGameSignal('reconn_user_free_operate', function(apply_server_index, apply_user_id, op_user_server_index, op_user_id, is_agree)
        self:reconn_user_free_operate(apply_server_index, apply_user_id, op_user_info, free_remain_time)
    end)
end

function free_game_waiting:show_view(remain_time)
    if not self.csb_node then
        self.csb_node = cc.CSLoader:createNode('game_common_res/component/dissolve_room/dissolve_room_view.csb')
        self.csb_node:setVisible(false)
        self.csb_node:setPosition(display.width * 0.5, display.height * 0.5)
        self.game_scene:addChild(self.csb_node, GAME_VIEW_Z_ORDER.FREE_GAME)

        -- 
        self.btn_agree = button('btn_confirm', function()
            self.game_scene:requestAction('free_game', true)
        end, self.csb_node)

        self.btn_refuse = button('btn_cancel', function()
            self.game_scene:requestAction('free_game', false)
        end, self.csb_node)

        -- 
        self.total_user_count = self.game_scene:getUserCount()
    end

    -- 刚显示的话，就要启动倒计时咯
    if not self.csb_node:isVisible() then
        self.csb_node:setVisible(true)

        self.btn_agree:setEnabled(true)
        self.btn_refuse:setEnabled(true)

        -- 先停止上一个，如果有的话
        if self.cd_handler then self.game_scene:unschedule(self.cd_handler) end

        -- 
        self.cd_handler = self.game_scene:schedule_circle(1, function()
            remain_time = remain_time - 1
            self.csb_node:getChildByName('text_remain_time'):setString(string.format('%ds', remain_time))

            if remain_time < 0 then
                self.game_scene:unschedule(self.cd_handler)
                self.cd_handler = nil
            end
        end, true)
    end
end

function free_game_waiting:update_view()
    local agree_count = table.len(self.agree_user_ids)
    self.csb_node:getChildByName('text_agree'):setString(string.format('%d 人', agree_count))
    self.csb_node:getChildByName('text_waiting'):setString(string.format('%d 人', self.total_user_count - agree_count))

    -- 
    if self.agree_user_ids[self.game_scene.self_user_id] then
        self.btn_agree:setEnabled(false)
        self.btn_refuse:setEnabled(false)

        self.csb_node:getChildByName('text_static_1'):setString(apply_server_index == self.game_scene.my_server_index and '您请求解散包间！' or '您已同意解散包间！')
    end
end

function free_game_waiting:user_free_operate(apply_server_index, apply_user_id, op_user_server_index, op_user_id, is_agree)
    self:show_view(self.game_scene.free_game_duration)

    -- 
    self.agree_user_ids[op_user_id] = 1

    --
    self:update_view()
end

function free_game_waiting:reconn_user_free_operate(apply_server_index, apply_user_id, op_user_info, free_remain_time)
    self:show_view(free_remain_time)

    -- 
    self.total_user_count = 0
    self.agree_user_ids = {}
    for _, v in ipairs(op_user_info) do
        if v.user_id ~= 0 then
            self.total_user_count = self.total_user_count + 1
        end

        if v.is_agree then
            self.agree_user_ids[v.user_id] = 1
        end
    end

    --
    self:update_view()
end

return free_game_waiting
