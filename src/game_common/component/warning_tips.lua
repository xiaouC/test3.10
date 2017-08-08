-- ./app/platform/game/game_common/warning_tips.lua
require 'app.platform.game.game_common.game_component_base'

local warning_tips = class('warning_tips_component', component_base)
function warning_tips:ctor(game_scene)
    component_base.ctor(self, game_scene)

    self.csb_z_order = GAME_VIEW_Z_ORDER.VOICE_CHAT
end

function warning_tips:init(args)
    component_base.init(self)

    -- 
    self.csb_node = cc.CSLoader:createNode('game_common_res/component/warning_tips/warning_tips.csb')
    self.csb_node:setPosition(args.x, args.y)
    self.csb_node:setVisible(false)
    self.game_scene:addChild(self.csb_node, self.csb_z_order)

    -- 大局结算的时候，隐藏
    self:listenGameSignal('final_settle', function(result_info, user_count) self.csb_node:setVisible(false) end)

    -- 30 秒出牌超时提示
    self:listenGameSignal('user_turn', function(server_index)
        if server_index == self.game_scene.my_server_index then
            self.out_card_warning_handler = self.game_scene:schedule_once_time(30, function()
                self.csb_node:setVisible(true)
                self.csb_node:getChildByName('text_tips'):setString('轮到你出牌了哦！')

                -- 震动一下
                if UserData:getWarnShake() == 'on' then CBsGameManager:GetI():LuaVibrate(500) end
            end)
        end
    end)
    self:listenGameSignal('out_card', function(location_index, card_id)
        if self.out_card_warning_handler then
            self.game_scene:unschedule(self.out_card_warning_handler)
            self.out_card_warning_handler = nil

            self.csb_node:setVisible(false)
        end
    end)

    -- 等待其他玩家的拦牌操作
    self:listenGameSignal('block_wait', function()
        self.csb_node:setVisible(true)
        self.csb_node:getChildByName('text_tips'):setString('等待其他玩家操作')
    end)
    self.game_scene:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        self.csb_node:setVisible(false)
    end)

    -- 等待房主开始游戏的提示
    -- 只在等待玩家进入的界面才有的提示
    self:listenGameSignal('on_user_ready', function(server_index, is_ready)
        if self.game_scene.game_state ~= 'waiting' then return end

        if server_index == self.game_scene.my_server_index and server_index ~= self.game_scene.homeowner_server_index then
            self.csb_node:setVisible(is_ready)

            if is_ready then
                self.csb_node:getChildByName('text_tips'):setString('请等待房主开始游戏')
            end
        end
    end)
end

function warning_tips:on_game_start()
    self.csb_node:setVisible(false)
end

function warning_tips:on_prepare_next_round()
    self.csb_node:setVisible(false)
end

return warning_tips
