-- ./win/game_scene.lua

local game_id = 20000001
local game_scene_mahjong = require('app.platform.game.game_common.game_scene_mahjong')

local GameScene = class('GameScene', game_scene_mahjong)
function GameScene:ctor(self_user_id)
    game_scene_mahjong.ctor(self, game_id, self_user_id, {
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
            ['game_waiting_view']           = { file_name = 'game_waiting_view', args = { min_count = 2 } },                                   -- 等待玩家界面
            ['round_settle'] = { file_name = 'round_settle_view', args = { draw_sprite_file = 'mahjong/common/game_result_draw_4.png' } },     -- 小局结算界面
            ['ting_card']    = { file_name = 'ting_card', args = { x = 1230, y = 135, has_fan_count = false } },                               -- 听牌，不带番
        },
    })
end

function GameScene:on_maker_info(data)
    game_scene_mahjong.on_maker_info(self, data)

    self:on_ghost_card( {}, { 0x35 }, 1, 1)
end

function GameScene:on_game_state(data)
    -- 怎一个恨字了得
    data.m_base_info.m_private_station = data.m_base_info.m_privater_station

    -- 
    game_scene_mahjong.on_game_state(self, data)
end

function GameScene:on_reconn_ghost_card(data)
    self.fake_card_ids = {}
    self.really_card_ids = { 0x35 }

    self:fire('ghost_card_confirm', { }, { 0x35 }, 1, 1)
end

function GameScene:getGameRuleConfig()
    -- 玩法
    local desc_1 = '四红中胡牌、抢杠胡(公杠)'
    if self.game_rule.m_allow_zp then desc_1 = desc_1 .. '、无红中可抓跑' end
    if self.game_rule.m_hu_qxd then desc_1 = desc_1 .. '、可胡七对' end

    local zha_ma_list = {}
    if self.game_rule.m_all_ma then table.insert(zha_ma_list, '四红中全码') end
    if self.game_rule.m_luck_mode == 1 then table.insert(zha_ma_list, '一张定码') end
    if self.game_rule.m_luck_mode == 2 then table.insert(zha_ma_list, '一码全中') end

    if self.game_rule.m_award_ma > 0 then
        table.insert(zha_ma_list, string.format('胡牌奖%d个码', self.game_rule.m_award_ma))
    else
        table.insert(zha_ma_list, '胡牌不奖码')
    end

    if self.game_rule.m_hongaward_ma == 0 then
        table.insert(zha_ma_list, '无红中不加码')
    else
        table.insert(zha_ma_list, string.format('无红中加%d码', self.game_rule.m_hongaward_ma))
    end

    -- 
    return {
        game_name = '红中麻将',
        section_height = 80,       -- 这个值可以控制高度，因为个别游戏的规则比较复杂，有可能太多 section 而导致看不见，可以尝试修改这个
        sections = {
            {
                section_name = '玩法',
                section_desc = desc_1,
            },
            {
                section_name = '赖子',
                section_desc = '红中做赖子',
            },
            {
                section_name = '扎马',
                section_desc = table.concat(zha_ma_list, '、'),
            },
        },
    }
end

function GameScene:get_win_effect_type(data)
    if data.m_win_type == 2 and data.m_dianpao_id < 4 then return 'fp' end

    if data.m_win_type == 1 then return 'zm' end

    if data.m_win_type == 3 then return 'qgh' end

    if data.m_win_type == 4 then return 'gskh' end

    if data.m_all_king then return 'szh' end

    return game_scene_mahjong.get_win_effect_type(self, data)
end

return GameScene
