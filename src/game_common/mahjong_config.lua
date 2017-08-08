-- ./app/platform/game/game_common/mahjong_config.lua

mahjong_block_type_config = {
    [0x00] = {
        get_block_type = function() return 'pass' end,
        get_show_card_list = function() return { } end,
        get_src_location_index = function() return nil end,
        get_dest_card_list = function() return {} end,
    },
    [0x01] = {
        get_block_type = function() return 'chow' end,
        get_show_card_list = function(card_value) return { card_value[1], card_value[2], card_value[3] } end,
        get_src_location_index = function(game_scene, subtype, checked_id) return game_scene:convertStationToLocalIndex(checked_id + 1) end,
        get_dest_card_list = function(subtype, card_value) return { card_value[1], card_value[2] } end,
    },
    [0x02] = {
        get_block_type = function() return 'pong' end,
        get_show_card_list = function(card_value) return { card_value[1], card_value[2], card_value[3] } end,
        get_src_location_index = function(game_scene, subtype, checked_id) return game_scene:convertStationToLocalIndex(checked_id + 1) end,
        get_dest_card_list = function(subtype, card_value) return { card_value[1], card_value[2] } end,
    },
    [0x04] = {
        get_block_type = function(subtype)
            if subtype == 0x04 then return 'kong_bu' end
            if subtype == 0x02 then return 'kong_ming' end
            return 'kong_an'
        end,
        get_show_card_list = function(card_value) return { card_value[1], card_value[2], card_value[3], card_value[4] } end,
        get_src_location_index = function(game_scene, subtype, checked_id)
            if subtype == 0x04 or subtype == 0x01 then return nil end   -- 0x01 暗杠，0x04 补杠
            return game_scene:convertStationToLocalIndex(checked_id + 1)
        end,
        get_dest_card_list = function(subtype, card_value)
            if subtype == 0x04 then return { card_value[1] } end    -- 补杠
            if subtype == 0x02 then return { card_value[1], card_value[2], card_value[3] } end    -- 明杠
            return { card_value[1], card_value[2], card_value[3], card_value[4] }   -- 暗杠
        end,
    },
    [0x08] = {
        get_block_type = function() return 'ting' end,
        get_show_card_list = function() return { } end,
        get_src_location_index = function() return nil end,
        get_dest_card_list = function() return {} end,
    },
    [0x10] = {
        get_block_type = function() return 'win' end,
        get_show_card_list = function() return { } end,
        get_src_location_index = function(game_scene, subtype, checked_id) return game_scene:convertStationToLocalIndex(checked_id + 1) end,
        get_dest_card_list = function() return {} end,
    },
}

-- 杠次
mahjong_block_type_config[0x05] = mahjong_block_type_config[0x04]
