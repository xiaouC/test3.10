-- ./app/platform/game/20000001/ui/game_scene_mahjong_replay.lua

local game_id = 20000001
local game_scene = require(string.format('app.platform.game.%d.ui.game_scene', game_id))
local game_scene_mahjong_replay = require('app.platform.game.game_common.game_scene_mahjong_replay')
local GameSceneReplay = class('GameSceneReplay', game_scene_mahjong_replay)
function GameSceneReplay:ctor(self_server_index, replay_file)
    game_scene_mahjong_replay.ctor(self, game_id, self_server_index, {
        replay_file = replay_file,
        preload_plist = {
        },
        listen_msg_ids = {
        },
        game_name = '红中麻将',
        has_ghost_card = true,      -- 是否有鬼牌，这个决定了是否存在翻鬼牌这回事，影响的是打骰子到摸牌间的动画控制，必须要明确指定
        need_flop_anim = false,
        ghost_card_name = '赖子',
        ghost_subscript_file = 'mahjong/common/mahjong_subscript_lai2.png',
        components = {
            ['ting_card']    = { file_name = 'ting_card', args = { x = 1230, y = 135, has_fan_count = false } },                               -- 听牌，不带番
            ['round_settle'] = { file_name = 'round_settle_view', args = { draw_sprite_file = 'mahjong/common/game_result_draw_4.png' } },     -- 小局结算界面
        },
    })
    
    -- 鬼牌是确定的，所以直接就结束吧
    self.ghost_card_anim_end = true
end

function GameSceneReplay:initReplayActionType()
    game_scene_mahjong_replay.initReplayActionType(self)

    -- 初始化手牌后，就确认鬼牌
    local super_process_func = self.preset_action_process_func['init_hand_card']
    self.preset_action_process_func['init_hand_card'] = function(action_data, callback)
        super_process_func(action_data, function()
            self:on_ghost_card( {}, { 0x35 }, 1, 1)

            self:schedule_once_time(2, callback)
        end)
    end

    -- 
    self.action_type_to_preset_name[0x01] = 'banker_server_index'           -- 庄家信息
    self.action_type_to_preset_name[0x02] = 'dice_info'                     -- 打骰子
    self.action_type_to_preset_name[0x03] = 'init_hand_card'                -- 手牌
    self.action_type_to_preset_name[0x04] = 'lei_card'                      -- 牌墙
    self.action_type_to_preset_name[0x05] = 'notify_out_card'               -- 通知玩家出牌
    self.action_type_to_preset_name[0x06] = 'user_draw_card'                -- 玩家摸牌
    self.action_type_to_preset_name[0x07] = 'notify_user_block'             -- 通知玩家拦牌
    self.action_type_to_preset_name[0x17] = 'user_block'                    -- 玩家拦牌
    self.action_type_to_preset_name[0x18] = 'block_result'                  -- 拦牌结果
    self.action_type_to_preset_name[0x15] = 'out_card'                      -- 出牌
    self.action_type_to_preset_name[0x08] = 'round_settle'                  -- 小局结算
    self.action_type_to_preset_name[0x10] = 'user_info'                     -- 玩家信息
    self.action_type_to_preset_name[0x09] = 'bu_hua'                        -- 补花
    self.action_type_to_preset_name[0x0A] = 'notify_ting_card'              -- 通知玩家听牌
    self.action_type_to_preset_name[0x0B] = 'game_rule'                     -- 游戏规则
    self.action_type_to_preset_name[0x0C] = 'ghost_card'                    -- 鬼牌信息
    self.action_type_to_preset_name[0x0D] = 'room_id'                       -- 包间号
end

function GameSceneReplay:getGameRuleConfig()
    return game_scene.getGameRuleConfig(self)
end

function GameSceneReplay:getRuleDetailConfig()
    return game_scene.getRuleDetailConfig(self)
end

return GameSceneReplay
