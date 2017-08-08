-- ./app/platform/game/20000053/component/round_settle_view.lua
----------------------------------------------------------------------------------------------------------
local lei_card_base = require 'app.platform.game.game_common.component.lei_card'
local lei_card = class('RoundSettleView', lei_card_base)

-- 一般都需要重载这个方法，以决定从那里开始摸牌
function lei_card:on_roll_dice_end(banker_server_index, dice_num_1, dice_num_2)
    self.pickup_location_index = (self.game_scene.my_server_index + dice_num_1 + dice_num_2 - 2) % 4 + 1
    self.pickup_stack_index = math.min(dice_num_1, dice_num_2) + 1
end

-- 翻出来的鬼牌所在的牌墙位置
function lei_card:on_ghost_card_confirm(fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
end

-- 这个方法，一般也需要重载，牌墙的墩数，可能与庄家的位置有关系
function lei_card:get_lei_col_num(banker_server_index)
    return { 14, 14, 14, 14 }, 14 * 4 * 2
end

return lei_card
