
fight_const = {
    batch_node_texture_name = 'mc/60001.png',            --
    grid_row_per_page = 4,                                  -- 每页的格子行数
    grid_col_per_page = 4,                                  -- 每页的格子列数

    prepare_attack_delay = 0.1,                             -- 准备攻击的延迟
    prepare_attack_time = 0.2,                              -- 准备攻击的时间
    prepare_attack_height = 20,                             -- 把模型往上提起来，准备攻击的高度

    smooth_move_duration_one_grid = 0.2,                    -- 移动一个格子宽度所需的时间

    hp_bg_offset_x_0 = -7,
    hp_bg_offset_x_1 = 0,
    hp_offset_x_0 = -2,
    hp_offset_x_1 = 3,
    hp_offset_y_0 = -65,                                     -- 血条的偏移
    hp_offset_y_1 = -145,                                    -- 血条的偏移
    hp_bg_png_0 = '60001_p3_0.png',
    hp_bg_png_1 = '60001_p3_11.png',
    hp_sprite_width_0 = 90,
    hp_sprite_width_1 = 190,
    hp_attr_icon_offset_x_0 = 40,
    hp_attr_icon_offset_x_1 = 100,
    hp_attr_icon_offset_y_0 = 7,
    hp_attr_icon_offset_y_1 = 7,
    leader_offset_x_0 = -55,
    leader_offset_x_1 = -100,
    leader_offset_y_0 = 55,
    leader_offset_y_1 = 100,
    ability_offset_x_0 = -40,
    ability_offset_x_1 = -100,
    ability_offset_y_0 = -40,
    ability_offset_y_1 = -100,
    buff_offset_x_0 = 55,
    buff_offset_x_1 = 120,
    buff_offset_y_0 = 55,
    buff_offset_y_1 = 120,
    buff_item_offset_x_0 = 0,
    buff_item_offset_x_1 = 0,
    buff_item_offset_y_0 = -40,
    buff_item_offset_y_1 = 0,

    attack_ready = 0.1,
    attack_delay = 0.2,
    attack_delay_combo = 0.4,
    attack_time = 0.125,

    hit_effect_delay = 0.2,                                 -- combo 被击的时候，光效的延迟
    skill_effect_delay = 0.15,                              -- 全屏技能光效是以十字型扩散的，这个值是每轮扩散的延迟

    buff_item_probability = 16,                             -- 恢复道具出现的概率

    -- 战斗里面的音效
    fight_bg_music = 'music/BM_Battle_Master.mp3',
    fight_bg_boss_music = 'music/BM_Boss_Master.mp3',
    fight_boss_alert = 'music/jingle_boss_alert.mp3',
    fight_lose = 'music/jingle_battle_lose.mp3',
    fight_win = 'music/jingle_battle_win.mp3',
    fight_skill_ok = 'music/se_skill_full.mp3',
    fight_skill_standby = 'music/se_skill_standby.mp3',
    fight_skill_window = 'music/se_window_skill.mp3',
    fight_heal = 'music/se_heal.mp3',
    fight_attack_combo = 'music/se_attack_combo.mp3',
    fight_attack_common = 'music/se_attack_common.mp3',
    fight_attack_critical = 'music/se_attack_critical.mp3',
    fight_attack_miss = 'music/se_attack_miss.mp3',
    fight_attack_paralyze = 'music/se_attack_paralyze.mp3',
    fight_attack_poison = 'music/se_attack_poison.mp3',
    fight_boss_dead = 'music/se_boss_dead.mp3',
    fight_enemy_dead = 'music/se_enemy_dead.mp3',
    fight_item_drop = 'music/se_item_drop.mp3',
    fight_treasure_appear = 'music/se_treasure_appear.mp3',
    fight_treasure_open = 'music/se_treasure_open.mp3',
    fight_monster_move = 'music/se_monster_move.mp3',
    fight_unit_stop = 'music/se_unit_stop.mp3',
    fight_cursor = 'music/se_cursor.mp3',

    critical_rate = 1.5,                -- 暴击
    critical_hp_100_to_70_rate = 5,     -- 当前 HP 对应的被爆概率
    critical_hp_70_to_30_rate = 10,
    critical_hp_30_to_10_rate = 20,
    critical_hp_10_to_0_rate = 30,

    gain_reward_count = 10,             -- 金银山捡到奖励的数量
}

-- 克制对方的话，return 2
-- 相互之间没有克制关系的话，return 1
-- 被克制的话，return 0
function attrRestrain( src, target )
    -- 火克木
    if src.obj_info.attr == hero_attr_fire and target.obj_info.attr == hero_attr_wood then return 2 end
    if src.obj_info.attr == hero_attr_wood and target.obj_info.attr == hero_attr_fire then return 0 end

    -- 木克水
    if src.obj_info.attr == hero_attr_wood and target.obj_info.attr == hero_attr_water then return 2 end
    if src.obj_info.attr == hero_attr_water and target.obj_info.attr == hero_attr_wood then return 0 end

    -- 水克火
    if src.obj_info.attr == hero_attr_water and target.obj_info.attr == hero_attr_fire then return 2 end
    if src.obj_info.attr == hero_attr_fire and target.obj_info.attr == hero_attr_water then return 0 end

    -- 光暗互克
    if src.obj_info.attr == hero_attr_light and target.obj_info.attr == hero_attr_dark then return 2 end
    if src.obj_info.attr == hero_attr_dark and target.obj_info.attr == hero_attr_light then return 2 end

    return 1
end

function getModelDetailOffset( model_size )
    return {
        hp_bg_offset_x = fight_const[string.format('hp_bg_offset_x_%d',model_size)],
        hp_offset_x = fight_const[string.format('hp_offset_x_%d',model_size)],
        hp_offset_y = fight_const[string.format('hp_offset_y_%d',model_size)],
        hp_bg_png = fight_const[string.format('hp_bg_png_%d',model_size)],
        hp_sprite_width = fight_const[string.format('hp_sprite_width_%d',model_size)],
        hp_attr_icon_offset_x = fight_const[string.format('hp_attr_icon_offset_x_%d',model_size)],
        hp_attr_icon_offset_y = fight_const[string.format('hp_attr_icon_offset_y_%d',model_size)],
        leader_offset_x = fight_const[string.format('leader_offset_x_%d',model_size)],
        leader_offset_y = fight_const[string.format('leader_offset_y_%d',model_size)],
        ability_offset_x = fight_const[string.format('ability_offset_x_%d',model_size)],
        ability_offset_y = fight_const[string.format('ability_offset_y_%d',model_size)],
        buff_offset_x = fight_const[string.format('buff_offset_x_%d',model_size)],
        buff_offset_y = fight_const[string.format('buff_offset_y_%d',model_size)],
        buff_item_offset_x = fight_const[string.format('buff_item_offset_x_%d',model_size)],
        buff_item_offset_y = fight_const[string.format('buff_item_offset_y_%d',model_size)],
    }
end

function getBuffState( all_buff_debuff_type, attr )
    -- 攻击
    if all_buff_debuff_type['AtkUp'] then return 'AtkUp', true, all_buff_debuff_type['AtkUp'].remain_round end

    -- 防御
    if all_buff_debuff_type['DefUp'] then return 'DefUp', true, all_buff_debuff_type['DefUp'].remain_round end

    -- 属性防御
    if all_buff_debuff_type['DefAttr'] then
        if all_buff_debuff_type['DefAttr'].value2 == 31 or all_buff_debuff_type['DefAttr'].value2 == attr then
            return 'DefUp', true, all_buff_debuff_type['DefAttr'].remain_round
        end
        return nil, nil, nil
    end

    -- 暴击
    if all_buff_debuff_type['CriticalUp'] then return 'CriticalUp', true, all_buff_debuff_type['CriticalUp'].remain_round end

    -- 反击
    if all_buff_debuff_type['Counter'] then return 'Counter', true, all_buff_debuff_type['Counter'].remain_round end

    -- 无敌
    if all_buff_debuff_type['Invincible'] then return 'Invincible', true, all_buff_debuff_type['Invincible'].remain_round end

    -- 闪避
    if all_buff_debuff_type['DodgeUp'] then return 'DodgeUp', true, all_buff_debuff_type['DodgeUp'].remain_round end

    return nil, nil, nil
end

function getDebuffState( all_buff_debuff_type, attr )
    -- 攻击
    if all_buff_debuff_type['AtkDown'] then return 'AtkDown', false, all_buff_debuff_type['AtkDown'].remain_round end

    -- 防御
    if all_buff_debuff_type['DefDown'] then return 'DefDown', false, all_buff_debuff_type['DefDown'].remain_round end

    -- 暴击
    if all_buff_debuff_type['CriticalDown'] then return 'CriticalDown', false, all_buff_debuff_type['CriticalDown'].remain_round end

    -- 闪避
    if all_buff_debuff_type['DodgeDown'] then return 'DodgeDown', false, all_buff_debuff_type['DodgeDown'].remain_round end

    -- 中毒
    if all_buff_debuff_type['Poison'] then return 'Poison', false, all_buff_debuff_type['Poison'].remain_round end

    -- 麻痹
    if all_buff_debuff_type['Paralysis'] then return 'Paralysis', false, all_buff_debuff_type['Paralysis'].remain_round end

    return nil, nil, nil
end

local combo_addition_config = {
    [1] = 0.00,
    [2] = 0.25,
    [3] = 0.38,
    [4] = 0.50,
    [5] = 0.63,
    [6] = 0.75,
    [7] = 0.88,
    [8] = 1.00,
    [9] = 1.13,
    [10] = 1.25,
    [11] = 1.38,
    [12] = 1.50,
    [13] = 1.63,
    [14] = 1.75,
    [15] = 1.88,
    [16] = 2.00,
    [17] = 2.13,
    [18] = 2.25,
    [19] = 2.38,
    [20] = 2.50,
    [21] = 2.63,
    [22] = 2.75,
    [23] = 2.88,
    [24] = 3.00,
}

function getComboAddition( total_combo )
    if total_combo < 2 then return 0.00 end

    if total_combo > #combo_addition_config then total_combo = #combo_addition_config end

    return combo_addition_config[total_combo]
end

function __transfer__( color_index, num )
    local function __convert__( ch )
        if ch == '-' then return '60002_zi10.png' end       -- 减号
        if ch == '+' then return '60002_zi15.png' end       -- 加号
        if ch == '%' then return '60002_zi16.png' end       -- 百分号
        if ch == '.' then return '60002_zi17.png' end       -- 小数点
        return string.format( '60002_zi0%s.png', ch )
    end

    local ret_text = string.format( '[colorindex:colorIndex=%d]', color_index )
    for _, ch in ipairs( string.toArray( tostring( num ) ) ) do
        local sprite_text = string.format( '[sprite:fileName="%s"]', __convert__( ch ) )
        ret_text = ret_text .. sprite_text
    end

    return ret_text
end

function fightFloatText( parent_node, s_x, s_y, text, mc_name, font_size )
    local node = TLLabelRichTex:create( text, font_size or 22, CCSize( 0, 0 ), CCImage.kAlignCenter )

    local float_mc = createMovieClipWithName( mc_name )
    float_mc:setAutoClear( false )
    float_mc:setPosition( s_x, s_y )
    parent_node:addChild( float_mc )

    local frame = MCLoader:sharedMCLoader():loadSpriteFrame( 'default.png' )
    local sprite = toSprite( float_mc:getChildByName( 'zi' ):getChildByName( 'bitmap' ) )
    sprite:setDisplayFrame( frame )
    sprite:addChild( node )

    float_mc:RegisterPlayEndCallbackHandler( function() float_mc:removeFromParentAndCleanup( true ) end )
    float_mc:play( 0, -1 )
end

function hurtFloatText( parent_node, s_x, s_y, num, is_crit, restrain )
    local restrain_text = ''
    if restrain == 0 then restrain_text = '[colorindex:colorIndex=0][sprite:fileName="60002_zi14.png"]' end     -- 被克
    if restrain == 2 then restrain_text = '[colorindex:colorIndex=0][sprite:fileName="60002_zi13.png"]' end     -- 克

    local color_index = 5
    local text = __transfer__( color_index, -num )
    local mc_name = is_crit and '60002/60002_kouxue2' or '60002/60002_kouxue1'
    fightFloatText( parent_node, s_x, s_y, text .. restrain_text, mc_name )
end

function restoreFloatText( parent_node, s_x, s_y, num, is_crit, restrain )
    local mc_name = is_crit and '60002/60002_jiaxue2' or '60002/60002_jiaxue1'
    local color_index = 3
    local text = __transfer__( color_index, num )
    fightFloatText( parent_node, s_x, s_y, text, mc_name )
end

function rewardFloatText( parent_node, s_x, s_y, reward_icon_text, num )
    local mc_name = '60002/60002_word_5'
    local color_index = 0
    --local text = reward_icon_text .. ' +' .. __transfer__( color_index, num )
    local text = reward_icon_text .. '+' .. tostring( num )
    fightFloatText( parent_node, s_x, s_y, text, mc_name, 35 )
end

function skillNameFloatText( parent_node, s_x, s_y, skill_name )
    if tostring( skill_name ) == 'nil' or skill_name == '' then return end

    local root_node = CCNode:create()
    root_node:setScale( 0.7 )
    root_node:setPosition( s_x, s_y )
    parent_node:addChild( root_node )

    local float_node = CCNodeExtend.extend( CCNode:create() )
    root_node:addChild( float_node )

    local sprite = MCLoader:sharedMCLoader():loadSpriteAsync( '60002_piao5.png' )
    float_node:addChild( sprite )

    local n = TLLabelRichTex:create( skill_name, 22, CCSize( 25, 25 ), CCImage.kAlignCenter )
    n:setScale( 2 )
    float_node:addChild( n )

    float_node:tweenFromToOnce( LINEAR_IN, NODE_PRO_ALPHA, 0, 0.15, 100, 255 )
    float_node:tweenFromToOnce( LINEAR_IN, NODE_PRO_SCALE, 0, 0.15, 4.0, 0.9, function()
        float_node:tweenFromToOnce( LINEAR_IN, NODE_PRO_ALPHA, 0.4, 0.15, 255, 0 )
        float_node:tweenFromToOnce( LINEAR_IN, NODE_PRO_SCALE, 0.4, 0.25, 0.9, 1.0, function()
            float_node:removeFromParentAndCleanup( true )
        end)
    end)
end

function skillEffectNameFloatText( parent_node, s_x, s_y, scale, float_type, skill_effect_name )
    if not skill_effect_name then return end

    -- 1、不区分上升还是下降
    -- 2、上升
    -- 3、下降
    local __float_type__ = { '60002/60002_word_1', '60002/60002_word_3', '60002/60002_word_4' }

    if skill_effect_name == 'nil' or skill_effect_name == '' then return end
    local float_mc = createMovieClipWithName( __float_type__[float_type] )
    float_mc:setAutoClear( false )
    float_mc:setScale( scale )
    float_mc:setPosition( s_x, s_y )
    parent_node:addChild( float_mc )

    local sprite_frame = MCLoader:sharedMCLoader():loadSpriteFrame( skill_effect_name )
    local sprite = toSprite( float_mc:getChildByName( 'zi' ):getChildByName( 'bitmap' ) )
    sprite:setDisplayFrame( sprite_frame )

    float_mc:RegisterPlayEndCallbackHandler( function() float_mc:removeFromParentAndCleanup( true ) end )
    float_mc:play( 0, -1 )
end

function floatImmunityText( target_grid_obj, call_back_func )
    local s_x, s_y = target_grid_obj:getSkillEffectNameFloatPosition()
    local skill_effect_name, float_type = '60002_buff_19.png', 1
    local scale = target_grid_obj.is_big_boss and 1 or 0.7
    skillEffectNameFloatText( fight_manager.effect_node, s_x, s_y, scale, float_type, skill_effect_name )

    if call_back_func then call_back_func() end
end

---------------------------------------------------------------------------------------------------------------------------------
-- HERO的 ability 扩展
hero_ability_fly                    = 0x00000001                    -- 飞行
hero_ability_share                  = 0x00000002                    -- 共享
hero_ability_immunity_magic         = 0x00000004                    -- 魔免
hero_ability_immunity_physical      = 0x00000008                    -- 物免
hero_ability_immunity_dizziness     = 0x00000010                    -- 免疫眩晕
hero_ability_immunity_silence       = 0x00000020                    -- 免疫沉默
hero_ability_immunity_skill_hurt    = 0x00000040                    -- 免疫技能伤害，中毒除外
hero_ability_immunity_poison        = 0x00000080                    -- 免疫中毒
hero_ability_immunity_disperse      = 0x00000100                    -- 免疫驱散

function __has_ability__( ability, sub_type ) return bit.band( ability, sub_type) ~= 0 end
function hasAbilityFly( ability ) return __has_ability__( ability, hero_ability_fly ) end
function hasAbilityShare( ability ) return __has_ability__( ability, hero_ability_share ) end
function hasAbilityImmunityMagic( ability ) return __has_ability__( ability, hero_ability_immunity_magic ) end
function hasAbilityImmunityPhysical( ability ) return __has_ability__( ability, hero_ability_immunity_physical ) end
function hasAbilityImmunityDizziness( ability ) return __has_ability__( ability, hero_ability_immunity_dizziness ) end
function hasAbilityImmunitySilence( ability ) return __has_ability__( ability, hero_ability_immunity_silence ) end
function hasAbilityImmunitySkillHurt( ability ) return __has_ability__( ability, hero_ability_immunity_skill_hurt ) end
function hasAbilityImmunityPoison( ability ) return __has_ability__( ability, hero_ability_immunity_poison ) end
function hasAbilityImmunityDisperse( ability ) return __has_ability__( ability, hero_ability_immunity_disperse ) end

