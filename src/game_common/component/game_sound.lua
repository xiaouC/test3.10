-- ./app/platform/game/game_common/game_sound.lua
require 'app.platform.common.game_music'

require 'app.platform.game.game_common.game_component_base'

local game_sound = class('game_sound_component', component_base)
function game_sound:init(args)
    component_base.init(self)

    -- 
    local function __get_sex_by_server_index__(server_index)
        local user_info = self.game_scene.all_user_info[server_index]
        return (user_info.m_bBoy and 'boy' or 'girl')
    end

    local function __get_sex_by_location_index__(location_index)
        local server_index = self.game_scene.local_index_to_server_index[location_index]
        return __get_sex_by_server_index__(server_index)
    end

    -- 打骰子
    self:listenGameSignal('roll_dice', function(banker_server_index, dice_num_1, dice_num_2, callback_func)
        self.game_scene:schedule_once_time(0.5, function()
            play_mahjong_effect('roll_dice')
        end)
    end)

    self:listenGameSignal('roll_dice_custom', function(server_index, dice_num_1, dice_num_2, callback_func)
        self.game_scene:schedule_once_time(0.5, function()
            play_mahjong_effect('roll_dice')
        end)
    end)

    -- 胡牌
    self:listenGameSignal('round_settle', function(result_info)
        for i=1, 4 do
            if result_info.m_win[i] then
                local sex = __get_sex_by_server_index__(i)

                local effect_type = nil
                if result_info.m_win_type == 1 then
                    effect_type = 'zimo'
                elseif result_info.m_win_type == 2 or result_info.m_win_type == 3 then
                    effect_type = 'win'
                end

                if effect_type then play_mahjong_sex_effect(sex, effect_type) end

                play_mahjong_effect('light')
            end
        end
    end)

    -- 出牌
    self:listenGameSignal('out_card', function(location_index, card_id)
        play_mahjong_sex_effect(__get_sex_by_location_index__(location_index), 'card', card_id)
        play_mahjong_effect('drop_card')
    end)

    -- 摸牌
    self:listenGameSignal('draw_card', function(location_index, card_id, is_kong, callback_func)
        play_mahjong_effect('draw_card')
    end)

    -- 拦牌
    self.game_scene:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        local effect_type = nil
        if block_type == 'chow' then effect_type = 'chow' end
        if block_type == 'pong' then effect_type = 'pong' end
        if block_type == 'ting' then effect_type = 'ting' end
        if block_type == 'kong_bu' or block_type == 'kong_ming' or block_type == 'kong_an' then effect_type = 'kong' end

        if effect_type then play_mahjong_sex_effect(__get_sex_by_location_index__(dest_location_index), effect_type) end
    end)
end

return game_sound
