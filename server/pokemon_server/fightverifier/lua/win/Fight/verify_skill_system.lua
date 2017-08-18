-- ./win/Fight/verify_skill_system.lua

verify_skill_system = {}

function verify_skill_system.getRelativeParam( src_grid_obj, target_grid_obj, se_info, skill_level )
    local se_param = se_info.param + ( ( skill_level - 1 ) * se_info.lv_param ) / 100
    local se_abs_param = se_info.abs_param + ( skill_level - 1 ) * se_info.lv_abs_param
    local __relative_type__ = {
        [0] = function() return se_param / 100 end,                                                -- 取绝对值，为了可以出现小数，所以除以 100
        [1] = function() return src_grid_obj.max_hp * se_param / 100 end,                          -- 相对于自身最大生命值
        [2] = function() return target_grid_obj.max_hp * se_param / 100 end,                       -- 相对于目标最大生命值
        [3] = function() return src_grid_obj.cur_hp * se_param / 100 end,                          -- 相对于自身当前生命值
        [4] = function() return target_grid_obj.cur_hp * se_param / 100 end,                       -- 相对于目标当前生命值
        [5] = function() return src_grid_obj:getBaseAtk() * se_param / 100 end,                    -- 相对于自身基础攻击
        [6] = function() return target_grid_obj:getBaseAtk() * se_param / 100 end,                 -- 相对于目标基础攻击
        [7] = function() return src_grid_obj:getBaseDef() * se_param / 100 end,                    -- 相对于自身基础防御
        [8] = function() return target_grid_obj:getBaseDef() * se_param / 100 end,                 -- 相对于目标基础防御
        [9] = function() return src_grid_obj:getBaseCriticalRate() * se_param / 1000 end,          -- 相对于自身基础暴击
        [10] = function() return target_grid_obj:getBaseCriticalRate() * se_param / 1000 end,      -- 相对于目标基础暴击
        [11] = function() return src_grid_obj:getBaseDodgeRate() * se_param / 1000 end,            -- 相对于自身基础闪避
        [12] = function() return target_grid_obj:getBaseDodgeRate() * se_param / 1000 end,         -- 相对于目标基础闪避
    }

    local func = __relative_type__[se_info.relative] or function() return 0 end

    return func() + se_abs_param
end

-- 伤害性技能效果的范围类型
-- 'ALL', 'LINE', 'BOX', 'POINT'
function verify_skill_system.getHurtSkillEffectRangeType( se_info )
    -- 全屏
    if bit.band( se_info.rge, verify_skill_system.__se_range.ALL.value ) ~= 0 then return 'ALL' end

    -- 线状
    if bit.band( se_info.rge, verify_skill_system.__se_range.V.value ) ~= 0 or
       bit.band( se_info.rge, verify_skill_system.__se_range.H.value ) ~= 0 or
       bit.band( se_info.rge, verify_skill_system.__se_range.CL.value ) ~= 0 or
       bit.band( se_info.rge, verify_skill_system.__se_range.CR.value ) ~= 0 then
       return 'LINE'
    end

    -- 框
    if bit.band( se_info.rge, verify_skill_system.__se_range.TL.value ) ~= 0 and
       bit.band( se_info.rge, verify_skill_system.__se_range.T.value ) ~= 0 and
       bit.band( se_info.rge, verify_skill_system.__se_range.TR.value ) ~= 0 and
       bit.band( se_info.rge, verify_skill_system.__se_range.L.value ) ~= 0 and
       bit.band( se_info.rge, verify_skill_system.__se_range.R.value ) ~= 0 and
       bit.band( se_info.rge, verify_skill_system.__se_range.BL.value ) ~= 0 and
       bit.band( se_info.rge, verify_skill_system.__se_range.B.value ) ~= 0 and
       bit.band( se_info.rge, verify_skill_system.__se_range.BR.value ) ~= 0 then
       return 'BOX'
    end

    -- 其余算点状
    return 'POINT'
end

verify_skill_system.__target_type__ = {
    all         = 1,                    -- 不分敌我
    enemy       = 2,                    -- 敌方
    partner     = 3,                    -- 我方
    specified   = 4,                    -- 指定的 ID
    caster      = 5,                    -- 施法者，谁施放的，目标就是谁
    receiver    = 6,                    -- 受法者，谁被打的，目标就是谁
}

local __target_attr__ = {
    huo         = 0x00000001,           -- 火             1
    shui        = 0x00000002,           -- 水             2
    mu          = 0x00000004,           -- 木             4
    guang       = 0x00000008,           -- 光             8
    an          = 0x00000010,           -- 暗            16
}

verify_skill_system.__se_range = {
    SELF = { value = 0x00000001, desc = '自己   1   ' },
    TL   = { value = 0x00000002, desc = '左上   2   ' },
    T    = { value = 0x00000004, desc = '上     4   ' },
    TR   = { value = 0x00000008, desc = '右上   8   ' },
    L    = { value = 0x00000010, desc = '左     16  ' },
    R    = { value = 0x00000020, desc = '右     32  ' },
    BL   = { value = 0x00000040, desc = '左下   64  ' },
    B    = { value = 0x00000080, desc = '下     128 ' },
    BR   = { value = 0x00000100, desc = '右下   256 ' },
    V    = { value = 0x00000200, desc = '纵一列 512 ' },
    H    = { value = 0x00000400, desc = '横一列 1024' },
    CL   = { value = 0x00000800, desc = '左斜   2048' },
    CR   = { value = 0x00001000, desc = '右斜   4096' },
    ALL  = { value = 0x00002000, desc = '全体   8192' },
}

-- 按回合触发的方法类型
verify_skill_system.__effect_func_type__ = {
    ['Poison'] = function( src_entity_id, target_entity_id, se_type, se_info, skill_level, v, effect_attr, effect_param, call_back_func )
        local grid_obj = verify_fight_manager:getGridObjByEntityID( target_entity_id )
        if not grid_obj then return call_back_func() end

        if grid_obj.cur_hp <= v.param then grid_obj:declareDeath() end

        local _,kt_info = get_verify_kind_type_info( verify_skill_system.__kind_type__.PoisonHurt.value )
        kt_info.play_kind_effect( se_type, se_info, skill_level, grid_obj, grid_obj, v, effect_attr, effect_param, call_back_func )
    end,
}

verify_skill_system.__kind_type__ = {
    ['Hurt']            = {                     -- 直接伤害
        value = 1,
        get_skill_name = function( se_info ) return nil, nil end,
        get_pos_effect_type = function( se_info ) return 'red' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl )
            local src_hurt_param, src_abs_hurt_param = src_grid_obj:getSkillHurtParam( verify_skill_system.__kind_type__.SkillHurtUp.value )
            local target_hurt_param, target_abs_hurt_param = target_grid_obj:getSkillHurtParam( verify_skill_system.__kind_type__.SkillHurtDown.value )

            local hurt_param = 100 + src_hurt_param - target_hurt_param
            if hurt_param < 0 then hurt_param = 0 end

            local param = math.floor( verify_skill_system.getRelativeParam( src_grid_obj, target_grid_obj, se_info, skill_level ) )
            local ret_param = math.floor( src_grid_obj:getSkillAtk( target_grid_obj, param ) * ( hurt_param / 100 ) + ( src_abs_hurt_param - target_abs_hurt_param ) )

            -- 不能造成负的伤害
            return ret_param > 0 and ret_param or 0
        end,
        get_action_type = function() return 'skill_hurt' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() and not target_grid_obj:isImmunitySkillHurt() then
                -- 技能反伤触发
                local all_src_entity_id = { src_grid_obj.obj_info.entity_id }
                local all_target_entity_id = { target_grid_obj.obj_info.entity_id }
                local trigger_param_tbl = { [src_grid_obj.obj_info.entity_id] = { [target_grid_obj.obj_info.entity_id] = { damage = v.param } } }
                verify_fight_manager:triggerSkill( all_src_entity_id, all_target_entity_id, src_grid_obj, trigger_action.skill_antiInjury, trigger_param_tbl, {} )

                -- 扣血
                target_grid_obj:doSkillHurt( src_grid_obj, { real_damage = v.param, beak_back_index = v.beak_back_index }, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['Restore']         = {                     -- 直接恢复
        value = 2,
        get_skill_name = function( se_info ) return nil, nil end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) end,
        desc = 'Restore 直接恢复',
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl )
            return math.floor( verify_skill_system.getRelativeParam( src_grid_obj, target_grid_obj, se_info, skill_level ) )
        end,
        get_action_type = function() return 'skill_restore' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                target_grid_obj:restore( src_grid_obj, v.param, v.beak_back_index, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['BeakBack']        = {                     -- 击退
        value = 3,
        desc = 'BeakBack 击退',
        get_skill_name = function( se_info ) return nil, 1 end,
        get_pos_effect_type = function( se_info ) return 'red' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return target_info.beak_back_index end,
        get_action_type = function() return 'skill_beak_back' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                target_grid_obj:beakBack( src_grid_obj, v.param, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['AntiInjury']        = {                   -- 反伤
        value = 4,
        get_skill_name = function( se_info ) return nil, nil end,
        get_pos_effect_type = function( se_info ) return 'red' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl )
            local src_hurt_param, src_abs_hurt_param = src_grid_obj:getSkillHurtParam( verify_skill_system.__kind_type__.SkillHurtUp.value )
            local target_hurt_param, target_abs_hurt_param = target_grid_obj:getSkillHurtParam( verify_skill_system.__kind_type__.SkillHurtDown.value )

            local hurt_param = 100 + src_hurt_param - target_hurt_param
            if hurt_param < 0 then hurt_param = 0 end

            local src_entity_id = src_grid_obj.obj_info.entity_id
            local target_entity_id = target_grid_obj.obj_info.entity_id
            local entity_param_tbl = param_tbl[target_entity_id][src_entity_id]
            local se_param = se_info.param + ( ( skill_level - 1 ) * se_info.lv_param ) / 100
            local se_abs_param = se_info.abs_param + ( skill_level - 1 ) * se_info.lv_abs_param
            local param = math.floor( entity_param_tbl.damage * se_param / 10000 ) + se_abs_param
            local ret_param = math.floor( src_grid_obj:getSkillAtk( target_grid_obj, param ) * ( hurt_param / 100 ) + ( src_abs_hurt_param - target_abs_hurt_param ) )

            -- 不能造成负的伤害
            return ret_param > 0 and ret_param or 0
        end,
        get_action_type = function() return 'skill_hurt' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if src_grid_obj.obj_info.entity_id == target_grid_obj.obj_info.entity_id then return call_back_func() end
            if not target_grid_obj:isImmunityMagic() and not target_grid_obj:isImmunitySkillHurt() then
                target_grid_obj:doSkillHurt( src_grid_obj, { real_damage = v.param, beak_back_index = v.beak_back_index }, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['PoisonHurt']            = {                     -- 直接伤害
        value = 5,
        get_skill_name = function( se_info ) return nil, nil end,
        get_pos_effect_type = function( se_info ) return 'red' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl )
            local param = math.floor( verify_skill_system.getRelativeParam( src_grid_obj, target_grid_obj, se_info, skill_level ) )
            return src_grid_obj:getSkillAtk( target_grid_obj, param )
        end,
        get_action_type = function() return 'poison_hurt' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                -- 技能反伤触发
                local all_src_entity_id = { src_grid_obj.obj_info.entity_id }
                local all_target_entity_id = { target_grid_obj.obj_info.entity_id }
                local trigger_param_tbl = { [src_grid_obj.obj_info.entity_id] = { [target_grid_obj.obj_info.entity_id] = { damage = v.param } } }
                verify_fight_manager:triggerSkill( all_src_entity_id, all_target_entity_id, src_grid_obj, trigger_action.skill_antiInjury, trigger_param_tbl, {} )

                -- 扣血
                target_grid_obj:doSkillHurt( src_grid_obj, { real_damage = v.param, beak_back_index = v.beak_back_index }, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['AtkUp']           = {                     -- 攻击增加
        value = 10,
        get_skill_name = function( se_info ) if ( se_info.param > 0 or se_info.abs_param > 0 ) then return '60002_buff_01.png', 2 else return '60002_buff_02.png', 3 end end,
        get_pos_effect_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'green' or 'red' end,
        get_buff_debuff_icon = function( is_buff ) return is_buff and '60001_p2_buff01.png' or '60001_p2_buff02.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'skill_atk_up' or 'skill_atk_down' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, function()
                end, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['DefUp']           = {                     -- 防御增加
        value = 11,
        get_skill_name = function( se_info ) if ( se_info.param > 0 or se_info.abs_param > 0 ) then return '60002_buff_03.png', 2 else return '60002_buff_04.png', 3 end end,
        get_pos_effect_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'green' or 'red' end,
        get_buff_debuff_icon = function( is_buff ) return is_buff and '60001_p2_buff03.png' or '60001_p2_buff04.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'skill_def_up' or 'skill_def_down' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, function()
                end, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['CritUp']          = {                     -- 暴击率增加
        value = 12,
        get_skill_name = function( se_info ) if ( se_info.param > 0 or se_info.abs_param > 0 ) then return '60002_buff_05.png', 2 else return '60002_buff_06.png', 3 end end,
        get_pos_effect_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'green' or 'red' end,
        get_buff_debuff_icon = function( is_buff ) return is_buff and '60001_p2_buff05.png' or '60001_p2_buff06.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'skill_crit_up' or 'skill_crit_down' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, function()
                end, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['CritVal']         = {                     -- 暴击伤害系数
        value = 13,
        get_skill_name = function( se_info ) if ( se_info.param > 0 or se_info.abs_param > 0 ) then return '60002_buff_07.png', 2 else return '60002_buff_08.png', 3 end end,
        get_pos_effect_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'green' or 'red' end,
        get_buff_debuff_icon = function( is_buff ) return is_buff and '60001_p2_buff07.png' or '60001_p2_buff08.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'skill_crit_val_up' or 'skill_crit_val_down' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['DodgeUp']         = {                     -- 闪避增加
        value = 14,
        get_skill_name = function( se_info ) if ( se_info.param > 0 or se_info.abs_param > 0 ) then return '60002_buff_09.png', 2 else return '60002_buff_10.png', 3 end end,
        get_pos_effect_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'green' or 'red' end,
        get_buff_debuff_icon = function( is_buff ) return is_buff and '60001_p2_buff09.png' or '60001_p2_buff10.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'skill_dodge_up' or 'skill_dodge_down' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, function()
                end, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['Poison'] = {
        value = 15,
        get_skill_name = function( se_info ) return '60002_buff_11.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'red' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff15.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_poison' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() and not target_grid_obj:isImmunityPoison() then
                -- 动态创建一个根据 se_info 而直接伤害的技能效果
                -- 然后再给 target 添加一个在本方回合开始前触发的效果，每次触发的效果都是刚刚创建的这个直接伤害的技能效果
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local skill_attr = ATTR_NAME[target_grid_obj.obj_info.attr].skill_attr
                local h_se_info = {
                    id = se_info.id,
                    target_type = verify_skill_system.__target_type__.partner,                     -- 自己方
                    targets = "nil",                                                        -- 不需要指定特定目标
                    rge = verify_skill_system.__se_range.SELF.value,                               -- 自己
                    attr = skill_attr,                                                      -- 自己的属性
                    kind = verify_skill_system.__kind_type__.Hurt.value,                           -- 直接伤害类型
                    relative = se_info.relative,                                            -- 相对还是绝对的伤害数值
                    param = -se_info.param,                                                 -- 伤害参数
                    abs_param = -se_info.abs_param,
                    tri_param = nil,                                                        -- 不是触发，没有意义
                    round = se_info.round,                                                  -- 在直接伤害里面，这个值其实没有意义
                    poison = true,
                    additional = se_info.additional,
                    lv_param = -se_info.lv_param,
                    lv_abs_param = -se_info.lv_abs_param,
                    lv_probability = -se_info.lv_probability,
                }

                -- 中毒状态
                local src_entity_id = src_grid_obj.obj_info.entity_id
                local effect_name = nil
                local kt, kt_info = get_verify_kind_type_info( verify_skill_system.__kind_type__.PoisonHurt.value )
                local poison_param = kt_info.get_param( h_se_info, skill_level, src_grid_obj, target_grid_obj, {} )
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, function( cb )
                    local func_type = 'Poison'
                    local poison_effect_func = verify_skill_system.__effect_func_type__[func_type]
                    poison_effect_func( src_entity_id, target_entity_id, se_type, h_se_info, skill_level, { param = poison_param }, effect_attr, effect_param, cb )
                end, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['AtkAttr']         = {                     -- 属性攻击增加
        value = 16,
        get_skill_name = function( se_info ) return nil, 1 end,
        get_pos_effect_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'green' or 'red' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'skill_atk_attr_up' or 'skill_atk_attr_down' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['DefAttr']         = {                     -- 属性防御增加
        value = 17,
        get_skill_name = function( se_info ) return nil, 1 end,
        get_pos_effect_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'green' or 'red' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'skill_def_attr_up' or 'skill_def_attr_down' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['ImmunityPhysical']= {                   -- 无敌，物免
        value = 18,
        get_skill_name = function( se_info ) return '60002_buff_12.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff13.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_immunity_physics' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['Paralysis']       = {                     -- 麻痹
        value = 19,
        get_skill_name = function( se_info ) return '60002_buff_14.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'red' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff16.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_paralysis' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() and not target_grid_obj:isImmunityDizziness() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['ImmunityMagic']   = {                   -- 无敌，魔免
        value = 21,
        get_skill_name = function( se_info ) return '60002_buff_13.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff14.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_immunity_magic' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['HPLimit'] = {     -- 改变生命值上限
        value = 22,
        get_skill_name = function( se_info ) if ( se_info.param > 0 or se_info.abs_param > 0 ) then return '60002_buff_16.png', 2 else return '60002_buff_17.png', 3 end end,
        get_pos_effect_type = function( se_info ) return ( se_info.param > 0 or se_info.abs_param > 0 ) and 'green' or 'red' end,
        get_buff_debuff_icon = function( is_buff ) return is_buff and '60001_p2_buff11.png' or '60001_p2_buff12.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_hp_limit' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local se_param = se_info.param + ( ( skill_level - 1 ) * se_info.lv_param ) / 100

                local effect_name = nil
                local target_entity_id = target_grid_obj.obj_info.entity_id
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, function()
                    local percent = se_param / 100.0
                    target_grid_obj:setAttrMaxLimit( 'HP', percent )
                end, nil, function()
                    local grid_obj = verify_fight_manager:getGridObjByEntityID( target_entity_id )
                    if grid_obj then
                        local percent = se_param / 100.0
                        grid_obj:setAttrMaxLimit( 'HP', -percent )
                    end
                end, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['Disperse'] = {        -- 驱散
        value = 23,
        get_skill_name = function( se_info ) return '60002_buff_15.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.param end,
        get_action_type = function() return 'skill_invincible_magic' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() and not target_grid_obj:isImmunityDisperse() then
                target_grid_obj:disperseAllKind( src_grid_obj, v.param, v.beak_back_index, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['Silence'] = {        -- 沉默
        value = 24,
        get_skill_name = function( se_info ) return '60002_buff_14.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'red' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff16.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_silence' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() and not target_grid_obj:isImmunitySilence() then
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, nil, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },

    ['exp']             = {                     -- 经验加成
        value = 30,
        get_skill_name = function( se_info, is_target ) return nil, nil end,
        get_pos_effect_type = function( se_info ) return '' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return '' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func ) call_back_func() end,
    },
    ['money']           = {                     -- 金币加成
        value = 31,
        get_skill_name = function( se_info, is_target ) return nil, nil end,
        get_pos_effect_type = function( se_info ) return '' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return '' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func ) call_back_func() end,
    },

    ['Trigger'] = {                             -- 触发
        value = 40,
        get_skill_name = function( se_info, is_target ) return nil, nil end,
        get_pos_effect_type = function( se_info ) return '' end,
        get_buff_debuff_icon = function( is_buff ) end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return '' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func ) call_back_func() end,
    },

    ['AbilityFly']   = {                   -- 飞行
        value = 50,
        get_skill_name = function( se_info ) return '60002_buff_13.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff18.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_fly' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
    },
    ['AbilityShare']   = {                   -- 共享
        value = 51,
        get_skill_name = function( se_info ) return '60002_buff_22.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff19.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_share' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['ImmunityDizziness']   = {                   -- 免疫眩晕
        value = 52,
        get_skill_name = function( se_info ) return '60002_buff_29.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff20.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_immunity_dizziness' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['ImmunitySilence']   = {                   -- 免疫沉默
        value = 53,
        get_skill_name = function( se_info ) return '60002_buff_30.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff21.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_immunity_silence' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['ImmunitySkillHurt']   = {                   -- 免疫技能伤害
        value = 54,
        get_skill_name = function( se_info ) return '60002_buff_13.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff22.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_immunity_skill_hurt' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['ImmunityPoison']   = {                   -- 免疫中毒
        value = 55,
        get_skill_name = function( se_info ) return '60002_buff_32.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff23.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_immunity_poison' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['ImmunityDisperse']   = {                   -- 免疫驱散
        value = 56,
        get_skill_name = function( se_info ) return '60002_buff_33.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff24.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_immunity_disperse' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['Invincible']   = {                   -- 无敌
        value = 57,
        get_skill_name = function( se_info ) return '60002_buff_13.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff32.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_invincible' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['ReduceRestore']   = {                   -- 降低任何的治疗效果
        value = 58,
        get_skill_name = function( se_info ) return '60002_buff_13.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return is_debuff and '60001_p2_buff30.png' or '60001_p2_buff31.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_reduce_restore' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['ForbidMove']   = {                   -- 禁止移动
        value = 59,
        get_skill_name = function( se_info ) return '60002_buff_35.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff27.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_forbid_move' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['ForbidAttack']   = {                   -- 禁止攻击
        value = 60,
        get_skill_name = function( se_info ) return '60002_buff_34.png', 1 end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return '60001_p2_buff26.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_forbid_attack' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['SkillHurtUp']   = {                   -- 技能伤害增加
        value = 61,
        get_skill_name = function( se_info ) if ( se_info.param > 0 or se_info.abs_param > 0 ) then return '60002_buff_25.png', 1 else return '60002_buff_26.png', 1 end end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return is_buff and '60001_p2_buff28.png' or '60001_p2_buff29.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_hurt_up' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
    ['SkillHurtDown']   = {                   -- 技能伤害减少 -- 这里就是法防
        value = 62,
        get_skill_name = function( se_info ) if ( se_info.param > 0 or se_info.abs_param > 0 ) then return '60002_buff_27.png', 1 else return '60002_buff_28.png', 1 end end,
        get_pos_effect_type = function( se_info ) return 'green' end,
        get_buff_debuff_icon = function( is_buff ) return is_buff and '60001_p2_buff33.png' or '60001_p2_buff34.png' end,
        get_param = function( se_info, skill_level, src_grid_obj, target_grid_obj, target_info, param_tbl ) return se_info.round end,
        get_action_type = function() return 'skill_hurt_down' end,
        play_kind_effect = function( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, call_back_func )
            if not target_grid_obj:isImmunityMagic() then
                local target_entity_id = target_grid_obj.obj_info.entity_id
                local effect_name = nil
                target_grid_obj:addBuffDebuff( se_type, src_grid_obj, v, se_info, skill_level, effect_attr, effect_param, effect_name, nil, nil, nil, call_back_func )
            else
                if call_back_func then call_back_func() end
            end
        end,
        play_kind_effect_archive = function( target_grid_obj, buff_debuff_state ) target_grid_obj:addBuffDebuffArchive( buff_debuff_state, nil, nil, nil ) end,
        get_tex_list = function( se_info ) return { '60207.png' } end,
    },
}

function get_verify_kind_type_info( kind )
    for k,v in pairs( verify_skill_system.__kind_type__ ) do if v.value == kind then return k,v end end
end

---------------------------------------------------------------------------------------------------------------------------------------------
local function __has_target__( se_info, target_id )
    local function get_skill_effect_target( se_info )
        local text = 'return {' .. se_info.targets .. '}'
        local fn = loadstring( text )
        return ( fn ~= nil ) and fn() or {}
    end

    local se_targets = get_skill_effect_target( se_info )
    return table.hasValue( se_targets, target_id )
end

---------------------------------------------------------------------------------------------------------------------------------------------
-- 是否可以被击退到这个位置
local function canBeakBackPosIndex( bb_row, bb_col )
    if bb_row >= 0 and bb_row < fight_const.grid_row_per_page and bb_col >= 0 and bb_col < fight_const.grid_col_per_page then
        local grid_item = verify_fight_manager:getGridItemByRowCol( bb_row, bb_col )
        if grid_item then
            if grid_item.grid_obj then
                local obj_type = grid_item.grid_obj.obj_info.type
                -- 宠物、敌人、石头，都不可以击退过来
                -- 但是，如果这是其他的物品的话，就可以过来了
                if obj_type == 'player' or obj_type == 'enemy' or obj_type == 'stone' then return false end
            end
            return true
        end
    end
    return false
end

local function getBeakBackPosIndex( src_row, src_col, step_row, step_col, se_info )
    local bb_param = nil
    if se_info.kind == verify_skill_system.__kind_type__.BeakBack.value then bb_param = se_info.abs_param end
    if se_info.additional_beak_back then bb_param = se_info.additional_beak_back end

    if bb_param then
        -- 击退一格
        if bb_param == 1 then
            local bb_row, bb_col = src_row + step_row, src_col + step_col
            if canBeakBackPosIndex( bb_row, bb_col ) then
                return bb_row * 4 + bb_col + 1
            end
            return nil
        end

        -- 击退到边界
        if bb_param == 2 then
            local bb_index = nil
            local bb_row, bb_col = src_row + step_row, src_col + step_col
            while canBeakBackPosIndex( bb_row, bb_col ) do
                bb_index = bb_row * 4 + bb_col + 1
                bb_row = bb_row + step_row
                bb_col = bb_col + step_col
            end
            return bb_index
        end
    end

    -- 其他任何值都不带击退效果
    return nil
end

-- 目标身上的状态
verify_skill_system.__target_state_type__ = {
    --[[
    ts_info = {
        max_count = 2,          -- 最多选择的数量
        probability = 50,       -- 命中的概率

        buff_check_info = {
            kind = 15,              -- 目标身上要有这个状态
            negative = 0,           -- 这个状态是正面的还是负面的效果呢，0 正负面都行，-1 是负面效果，1 是正面效果
        },

        attr_check_info = {
            attr_type = 1,          -- 1 : max_hp, 2 : cur_hp, 3 : base_atk, 4 : base_def, 5 : base_crit, 6 : base_dodge
            relative = 1,           -- 使用相对值还是绝对值，这里，目前只对 cur_hp 有效
            param = 20,             -- 参数
            compare_type = 1,       -- 1：大于，2：大于等于，3：等于，4 ：小于，5：小于等于，6：不等于
            sort_type = 1,          -- 1：最少，2：最大
        },
    }
    --]]
    ['buff_state'] = {
        value = 1,
        check_state = function( grid_obj, buff_check_info )
            return grid_obj:hasKindTypeNegative( buff_check_info.kind, buff_check_info.negative )
        end,
    },
    ['attr_state'] = {
        value = 2,
        check_state = function( grid_obj, attr_check_info, sort_param )
            return grid_obj:checkAttrState( attr_check_info, sort_param )
        end,
    },
}

local function __check_buff_state__( grid_obj, ts_info )
    if not ts_info.buff_check_info then return true end
    return verify_skill_system.__target_state_type__.buff_state.check_state( grid_obj, ts_info.buff_check_info )
end

function __verify_check_attr_state__( grid_obj, attr_check_info, sort_param )
    if not attr_check_info then return true end
    return verify_skill_system.__target_state_type__.attr_state.check_state( grid_obj, attr_check_info, sort_param )
end

-- 判断这个位置的目标是否是有效的
local function insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
    local target_grid_obj = verify_fight_manager:getFightObjectByPosIndex( target_pos_index )
    if target_grid_obj and target_grid_obj.death_event then target_grid_obj = nil end

    local function __realInsertTargetPosIndex( has_target )
        table.insert( ret_effect_pos_index, {
            pos_index = target_pos_index,
            has_target = has_target,
            buff_check = true,
            attr_check = true,
            max_count_check = true,
            hit_check = true,
            src_attr = src_grid_obj.obj_info.attr,
            target_attr = target_grid_obj and target_grid_obj.obj_info.attr or src_grid_obj.obj_info.attr,
            beak_back_index = beak_back_index,
            mv_count = verify_fight_manager:getMoveGridCount( target_pos_index, beak_back_index ),
        })
    end

    -- 如果这个格子上没有有效的目标的话，就会有光效，但没有目标
    if not target_grid_obj then return __realInsertTargetPosIndex( false ) end

    -- 属性不对，取值在 __target_attr__
    local skill_attr = ATTR_NAME[target_grid_obj.obj_info.attr].skill_attr
    if bit.band( se_info.attr, skill_attr ) == 0 then return __realInsertTargetPosIndex( false ) end

    -- 如果不分敌我的话
    if se_info.target_type == verify_skill_system.__target_type__.all then return __realInsertTargetPosIndex( true ) end

    -- 敌方
    if se_info.target_type == verify_skill_system.__target_type__.enemy then
        return __realInsertTargetPosIndex( src_grid_obj:isEnemy( target_grid_obj ) )
    end

    -- 我方
    if se_info.target_type == verify_skill_system.__target_type__.partner then
        return __realInsertTargetPosIndex( src_grid_obj:isTeammate( target_grid_obj ) )
    end

    -- 指定 ID
    __realInsertTargetPosIndex( __has_target__( se_info, target_grid_obj.obj_info.same ) )
end

-- return 技能有效目标所在的位置，技能特效播放的位置(播放的过程有先后顺序的)，技能光圈位置(预览的技能位置)
verify_skill_system.__se_range.SELF.func = function( src_grid_obj, row, col, se_info, kt_info )
    local ret_effect_pos_index = {}

    local target_pos_index = src_grid_obj.pos_index
    insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, nil, se_info, kt_info )

    if src_grid_obj.is_big_boss then
        target_pos_index = src_grid_obj.pos_index + 1
        insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, nil, se_info, kt_info )

        target_pos_index = src_grid_obj.pos_index + 4
        insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, nil, se_info, kt_info )

        target_pos_index = src_grid_obj.pos_index + 5
        insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, nil, se_info, kt_info )
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.TL.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    if col > 0 and row > 0 then
        -- 目标位置
        local target_pos_index = pos_index - 5

        -- 击退到的位置
        local beak_back_index = getBeakBackPosIndex( row - 1, col - 1, -1, -1, se_info )

        insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.T.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    if row > 0 then
        -- 目标位置 & 击退到的位置
        local target_pos_index = pos_index - 4
        local beak_back_index = getBeakBackPosIndex( row - 1, col, -1, 0, se_info )
        insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )

        if src_grid_obj.is_big_boss then
            target_pos_index = pos_index - 3
            beak_back_index = getBeakBackPosIndex( row - 1, col + 1, -1, 0, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.TR.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    if not src_grid_obj.is_big_boss then
        if col < fight_const.grid_col_per_page - 1 and row > 0 then
            local target_pos_index = pos_index - 3
            local beak_back_index = getBeakBackPosIndex( row - 1, col + 1, -1, 1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    else
        if col < fight_const.grid_col_per_page - 2 and row > 0 then
            local target_pos_index = pos_index - 2
            local beak_back_index = getBeakBackPosIndex( row - 1, col + 2, -1, 1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.L.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    if col > 0 then
        local target_pos_index = pos_index - 1
        local beak_back_index = getBeakBackPosIndex( row, col - 1, 0, -1, se_info )
        insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )

        if src_grid_obj.is_big_boss then
            target_pos_index = pos_index + 3
            beak_back_index = getBeakBackPosIndex( row + 1, col - 1, 0, -1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.R.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    if not src_grid_obj.is_big_boss then
        if col < fight_const.grid_col_per_page - 1 then
            local target_pos_index = pos_index + 1
            local beak_back_index = getBeakBackPosIndex( row, col + 1, 0, 1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    else
        if col < fight_const.grid_col_per_page - 2 then
            local target_pos_index = pos_index + 2
            local beak_back_index = getBeakBackPosIndex( row, col + 2, 0, 1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )

            target_pos_index = pos_index + 6
            beak_back_index = getBeakBackPosIndex( row + 1, col + 2, 0, 1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.BL.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    if not src_grid_obj.is_big_boss then
        if col > 0 and row < fight_const.grid_row_per_page - 1 then
            local target_pos_index = pos_index + 3
            local beak_back_index = getBeakBackPosIndex( row + 1, col - 1, 1, -1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    else
        if col > 0 and row < fight_const.grid_row_per_page - 2 then
            local target_pos_index = pos_index + 7
            local beak_back_index = getBeakBackPosIndex( row + 2, col - 1, 1, -1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.B.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    if not src_grid_obj.is_big_boss then
        if row < fight_const.grid_row_per_page - 1 then
            local target_pos_index = pos_index + 4
            local beak_back_index = getBeakBackPosIndex( row + 1, col, 1, 0, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    else
        if row < fight_const.grid_row_per_page - 2 then
            local target_pos_index = pos_index + 8
            local beak_back_index = getBeakBackPosIndex( row + 2, col, 1, 0, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )

            target_pos_index = pos_index + 9
            beak_back_index = getBeakBackPosIndex( row + 2, col + 1, 1, 0, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.BR.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    if not src_grid_obj.is_big_boss then
        if col < fight_const.grid_col_per_page - 1 and row < fight_const.grid_row_per_page - 1 then
            local target_pos_index = pos_index + 5
            local beak_back_index = getBeakBackPosIndex( row + 1, col + 1, 1, 1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    else
        if col < fight_const.grid_col_per_page - 2 and row < fight_const.grid_row_per_page - 2 then
            local target_pos_index = pos_index + 10
            local beak_back_index = getBeakBackPosIndex( row + 2, col + 2, 1, 1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, target_pos_index, beak_back_index, se_info, kt_info )
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.V.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    local r1,r2 = row,row
    local temp_pos_index1,temp_pos_index2 = pos_index,pos_index

    -- 
    local temp_row = fight_const.grid_row_per_page - ( src_grid_obj.is_big_boss and 2 or 1 )

    while r1 > 0 or r2 < temp_row do
        -- 往上
        if r1 > 0 then
            local temp_target_pos_index = temp_pos_index1 - 4
            local beak_back_index = getBeakBackPosIndex( row - 1, col, -1, 0, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )

            if src_grid_obj.is_big_boss then
                temp_target_pos_index = temp_pos_index1 - 3
                beak_back_index = getBeakBackPosIndex( row - 1, col + 1, -1, 0, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            end

            r1 = r1 - 1
            temp_pos_index1 = temp_pos_index1 - 4
        end

        -- 往下
        if r2 < temp_row then
            if not src_grid_obj.is_big_boss then
                local temp_target_pos_index = temp_pos_index2 + 4
                local beak_back_index = getBeakBackPosIndex( row + 1, col, 1, 0, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            else
                local temp_target_pos_index = temp_pos_index2 + 8
                local beak_back_index = getBeakBackPosIndex( row + 2, col, 1, 0, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
                temp_target_pos_index = temp_pos_index2 + 9
                beak_back_index = getBeakBackPosIndex( row + 2, col + 1, 1, 0, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            end

            r2 = r2 + 1
            temp_pos_index2 = temp_pos_index2 + 4
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.H.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    local c1,c2 = col,col
    local temp_pos_index1,temp_pos_index2 = pos_index,pos_index

    local temp_col = fight_const.grid_col_per_page - ( src_grid_obj.is_big_boss and 2 or 1 )

    while c1 > 0 or c2 < temp_col do
        -- 往左
        if c1 > 0 then
            local temp_target_pos_index = temp_pos_index1 - 1
            local beak_back_index = getBeakBackPosIndex( row, col - 1, 0, -1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )

            if src_grid_obj.is_big_boss then
                temp_target_pos_index = temp_pos_index1 + 3
                beak_back_index = getBeakBackPosIndex( row + 1, col - 1, 0, -1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            end

            c1 = c1 - 1
            temp_pos_index1 = temp_pos_index1 - 1
        end

        -- 往右
        if c2 < temp_col then
            if not src_grid_obj.is_big_boss then
                local temp_target_pos_index = temp_pos_index2 + 1
                local beak_back_index = getBeakBackPosIndex( row, col + 1, 0, 1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            else
                local temp_target_pos_index = temp_pos_index2 + 2
                local beak_back_index = getBeakBackPosIndex( row, col + 1, 0, 1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
                temp_target_pos_index = temp_pos_index2 + 6
                beak_back_index = getBeakBackPosIndex( row + 1, col + 1, 0, 1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            end

            c2 = c2 + 1
            temp_pos_index2 = temp_pos_index2 + 1
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.CL.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    -- 左上
    local r1,c1,r2,c2 = row,col,row,col
    local temp_pos_index1,temp_pos_index2 = pos_index,pos_index

    local temp_row = fight_const.grid_row_per_page - ( src_grid_obj.is_big_boss and 2 or 1 )
    local temp_col = fight_const.grid_col_per_page - ( src_grid_obj.is_big_boss and 2 or 1 )

    while ( r1 > 0 and c1 > 0 ) or ( c2 < temp_col and r2 < temp_row ) do
        -- 左上
        if r1 > 0 and c1 > 0 then
            local temp_target_pos_index = temp_pos_index1 - 5
            local beak_back_index = getBeakBackPosIndex( r1 - 1, c1 - 1, -1, -1, se_info )
            insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )

            r1 = r1 - 1
            c1 = c1 - 1
            temp_pos_index1 = temp_pos_index1 - 5
        end

        -- 右下
        if c2 < temp_col and r2 < temp_row then
            if not src_grid_obj.is_big_boss then
                local temp_target_pos_index = temp_pos_index2 + 5
                local beak_back_index = getBeakBackPosIndex( r2 + 1, c2 + 1, 1, 1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            else
                local temp_target_pos_index = temp_pos_index2 + 10
                local beak_back_index = getBeakBackPosIndex( r2 + 2, c2 + 2, 1, 1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            end

            r2 = r2 + 1
            c2 = c2 + 1
            temp_pos_index2 = temp_pos_index2 + 5
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.CR.func = function( src_grid_obj, row, col, se_info, kt_info )
    local pos_index = src_grid_obj.pos_index

    local ret_effect_pos_index = {}

    -- 右上
    local r1,c1,r2,c2 = row,col,row,col
    local temp_pos_index1,temp_pos_index2 = pos_index,pos_index

    local temp_row = fight_const.grid_row_per_page - ( src_grid_obj.is_big_boss and 2 or 1 )
    local temp_col = fight_const.grid_col_per_page - ( src_grid_obj.is_big_boss and 2 or 1 )

    while ( c1 < temp_col and r1 > 0 ) or ( c2 > 0 and r2 < temp_row ) do
        -- 右上
        if c1 < temp_col and r1 > 0 then
            if not src_grid_obj.is_big_boss then
                local temp_target_pos_index = temp_pos_index1 - 3
                local beak_back_index = getBeakBackPosIndex( r1 - 1, c1 + 1, -1, 1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            else
                local temp_target_pos_index = temp_pos_index1 - 2
                local beak_back_index = getBeakBackPosIndex( r1 - 1, c1 + 2, -1, 1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            end

            r1 = r1 - 1
            c1 = c1 + 1
            temp_pos_index1 = temp_pos_index1 - 3
        end

        -- 左下
        if c2 > 0 and r2 < temp_row then
            if not src_grid_obj.is_big_boss then
                local temp_target_pos_index = temp_pos_index2 + 3
                local beak_back_index = getBeakBackPosIndex( r1 + 1, c1 - 1, 1, -1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            else
                local temp_target_pos_index = temp_pos_index2 + 7
                local beak_back_index = getBeakBackPosIndex( r1 + 2, c1 - 1, 1, -1, se_info )
                insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, temp_target_pos_index, beak_back_index, se_info, kt_info )
            end

            c2 = c2 - 1
            r2 = r2 + 1
            temp_pos_index2 = temp_pos_index2 + 3
        end
    end

    return ret_effect_pos_index
end

verify_skill_system.__se_range.ALL.func = function( src_grid_obj, row, col, se_info, kt_info )
    local ret_effect_pos_index = {}
    for i=1,verify_fight_manager.grid_count_per_page do
        insertTargetPosIndex( src_grid_obj, ret_effect_pos_index, i, nil, se_info, kt_info )
    end

    return ret_effect_pos_index
end

function getVerifySkillEffectRange( src_grid_obj, se_info, skill_level )
    local ret_effect_pos_index = {}

    -- 
    local row = math.floor( ( src_grid_obj.pos_index - 1 ) / 4 )
    local col = ( src_grid_obj.pos_index - 1 ) % 4

    local kt, kt_info = get_verify_kind_type_info( se_info.kind )

    local temp_pos_index = {}
    local temp_targets = {}
    local function __is_valid__( v )
        -- 如果已经存在这个位置了，就是无效的
        if temp_pos_index[v.pos_index] then return false end

        -- 如果这个位置有目标，但目标已经存在的话，那么该位置的目标就重置为无效，这是大BOSS特有
        temp_pos_index[v.pos_index] = 1
        if v.has_target then
            local grid_obj = verify_fight_manager:getFightObjectByPosIndex( v.pos_index )
            if grid_obj then
                if temp_targets[grid_obj] then v.has_target = false end
                temp_targets[grid_obj] = 1
            end
        end
        return true
    end

    local function updatePosIndex( rge, func )
        if bit.band( se_info.rge, rge ) ~= 0 then
            local effect_pos_index = func( src_grid_obj, row, col, se_info, kt_info )
            for _,v in ipairs( effect_pos_index ) do
                if __is_valid__( v ) then table.insert( ret_effect_pos_index, v ) end
            end
        end
    end

    -- 这是根据技能效果的范围和属性得出的
    for k,v in pairs( verify_skill_system.__se_range ) do updatePosIndex( v.value, v.func ) end

    verify_buff_attr_max_count_hit_check( src_grid_obj, ret_effect_pos_index, se_info, skill_level )

    return ret_effect_pos_index
end

function verify_buff_attr_max_count_hit_check( src_grid_obj, effect_pos_index, se_info, skill_level )
    -- 
    local default_ts_info = { max_count = 8, probability = 100, }
    local function __convert_state__()
        if not se_info.state_param then return default_ts_info end
        local text = 'return {' .. se_info.state_param .. '}'
        local fn = loadstring( text )
        return ( fn ~= nil ) and fn() or default_ts_info
    end
    local ts_info = __convert_state__()
    ts_info.max_count = ts_info.max_count or default_ts_info.max_count
    ts_info.probability = ( ts_info.probability and ( ts_info.probability + ( ( skill_level - 1 ) * se_info.lv_probability ) / 100 ) or default_ts_info.probability )

    -- 判断状态
    if ts_info.buff_check_info then
        for _,v in ipairs( effect_pos_index ) do
            if v.has_target then
                local grid_obj = verify_fight_manager:getFightObjectByPosIndex( v.pos_index )
                v.buff_check = __check_buff_state__( grid_obj, ts_info )
            end
        end
    end

    -- 属性
    local temp_count = 0
    local max_check_flag = false
    if ts_info.attr_check_info then
        local sort_param = {}
        -- 单体属性判断
        for _,v in ipairs( effect_pos_index ) do
            if v.has_target and v.buff_check then
                local grid_obj = verify_fight_manager:getFightObjectByPosIndex( v.pos_index )
                v.attr_check = __verify_check_attr_state__( grid_obj, ts_info.attr_check_info, sort_param )
                if v.attr_check then temp_count = temp_count + 1 end
            end
        end

        -- 群体属性判断
        if ts_info.attr_check_info.sort_type and sort_param then
            max_check_flag = true

            local temp_sort_param = {}
            for attr_param,_ in pairs( sort_param ) do
                table.insert( temp_sort_param, attr_param )
            end
            table.sort( temp_sort_param )

            local s_index = ts_info.attr_check_info.sort_type == 1 and 1 or #temp_sort_param
            local e_index = ts_info.attr_check_info.sort_type == 1 and #temp_sort_param or 1
            local step = ts_info.attr_check_info.sort_type == 1 and 1 or -1

            local cur_count = 0
            local valid_pos_index = {}
            for i=s_index,e_index,step do
                if cur_count >= ts_info.max_count then break end

                local value = temp_sort_param[i]
                local attr_param_values = sort_param[value]
                for _,pos_index in ipairs( attr_param_values ) do
                    table.insert( valid_pos_index, pos_index )
                    cur_count = cur_count + 1
                    if cur_count >= ts_info.max_count then break end
                end
            end

            for _,v in ipairs( effect_pos_index ) do
                v.attr_check = table.hasValue( valid_pos_index, v.pos_index )
                v.max_count_check = v.attr_check
            end
        end
    else
        for _,v in ipairs( effect_pos_index ) do
            if v.has_target and v.buff_check then
                temp_count = temp_count + 1
            end
        end
    end

    -- 最大数量判断
    if not max_check_flag then
        if temp_count > ts_info.max_count then
            local valid_index_1 = stack.new()
            local valid_index_2 = {}
            for i=1,temp_count do
                valid_index_1:push( i )
                table.insert( valid_index_2, true )
            end
            while valid_index_1:getElementCount() > ts_info.max_count do
                local rm_index = math.floor( src_grid_obj:getRandomNumber( 1, valid_index_1:getElementCount() ) + 0.5 )

                local real_index = valid_index_1:getAt( rm_index )
                valid_index_2[real_index] = false

                valid_index_1:remove( rm_index )
            end

            local cur_index = 1
            for _,v in ipairs( effect_pos_index ) do
                if v.has_target and v.buff_check and v.attr_check then
                    v.max_count_check = valid_index_2[cur_index]
                    cur_index = cur_index + 1
                end
            end
        end
    end

    -- 命中判断
    for _,v in ipairs( effect_pos_index ) do
        -- 通过了 buff 判断，通过了属性判断，通过了数量判断后的
        if v.has_target and v.buff_check and v.attr_check and v.max_count_check then
            v.hit_check = ( ts_info.probability >= src_grid_obj:getRandomNumber( 0, 100 ) )
        end
    end
    --]]
end

function verify_calculate_skill_effect( grid_obj, all_src_entity_id, all_target_entity_id, se_info, skill_level, param_tbl )
    -- 
    if se_info.target_type == verify_skill_system.__target_type__.caster or se_info.target_type == verify_skill_system.__target_type__.receiver then
        local temp_all_entity_id = ( se_info.target_type == verify_skill_system.__target_type__.caster and all_src_entity_id or all_target_entity_id )
        local effect_pos_index = {}
        for _,entity_id in ipairs( temp_all_entity_id or {} ) do
            local temp_grid_obj = verify_fight_manager:getGridObjByEntityID( entity_id )
            if temp_grid_obj and not temp_grid_obj.death_event then
                -- 属性不对，取值在 __target_attr__
                local skill_attr = ATTR_NAME[temp_grid_obj.obj_info.attr].skill_attr
                if bit.band( se_info.attr, skill_attr ) ~= 0 then
                    local v = {
                        pos_index = temp_grid_obj.pos_index,
                        has_target = true,
                        buff_check = true,
                        attr_check = true,
                        max_count_check = true,
                        hit_check = true,
                        src_attr = grid_obj.obj_info.attr,
                        target_attr = temp_grid_obj.obj_info.attr,
                        beak_back_index = nil,
                    }

                    if se_info.kind == verify_skill_system.__kind_type__.BeakBack.value or se_info.additional_beak_back then
                        local grid_item_1 = verify_fight_manager:getGridItemByPosIndex( grid_obj.pos_index )
                        local grid_item_2 = verify_fight_manager:getGridItemByPosIndex( temp_grid_obj.pos_index )

                        local row = grid_item_2.row
                        local col = grid_item_2.col

                        local step_row = 0
                        if grid_item_1.row > grid_item_2.row then step_row = -1 end
                        if grid_item_1.row < grid_item_2.row then step_row = 1 end

                        local step_col = 0
                        if grid_item_1.col > grid_item_2.col then step_col = -1 end
                        if grid_item_1.col < grid_item_2.col then step_col = 1 end

                        v.beak_back_index = getBeakBackPosIndex( row, col, step_row, step_col, se_info )
                    end

                    local kt, kt_info = get_verify_kind_type_info( se_info.kind )
                    v.param = kt_info.get_param( se_info, skill_level, grid_obj, temp_grid_obj, v, param_tbl )

                    table.insert( effect_pos_index, v )
                end
            end
        end

        verify_buff_attr_max_count_hit_check( grid_obj, effect_pos_index, se_info, skill_level )

        return effect_pos_index
    end

    -- 
    local effect_pos_index = getVerifySkillEffectRange( grid_obj, se_info, skill_level )
    for _,v in ipairs( effect_pos_index ) do
        if v.has_target then
            local target_grid_obj = verify_fight_manager:getFightObjectByPosIndex( v.pos_index )
            local kt, kt_info = get_verify_kind_type_info( se_info.kind )
            v.param = kt_info.get_param( se_info, skill_level, grid_obj, target_grid_obj, v )
        end
    end

    return effect_pos_index
end

function verify_play_skill_effect( se_type, se_info, skill_level, src_grid_obj, effect_pos_index, shock_screen, effect_attr, param_tbl, call_back_func )
    local counter = #effect_pos_index
    if counter <= 0 then return call_back_func() end
    local kt, kt_info = get_verify_kind_type_info( se_info.kind )

    -- 
    for _,v in ipairs( effect_pos_index ) do
        local target_grid_obj = verify_fight_manager:getFightObjectByPosIndex( v.pos_index )
        if not target_grid_obj or target_grid_obj.cur_hp <= 0 then v.has_target = false end

        -- 有效的目标，播放受击光效
        local target_effect_flag = false
        if v.has_target and v.buff_check and v.attr_check and v.max_count_check and v.hit_check then
            counter = counter + 1

            local function __get_mv_count__()
                local src_entity_id = src_grid_obj.obj_info.entity_id
                local target_entity_id = target_grid_obj.obj_info.entity_id
                if not param_tbl[target_entity_id] or not param_tbl[target_entity_id][src_entity_id] then return nil end
                return param_tbl[target_entity_id][src_entity_id].mv_count
            end
            local effect_param = __get_mv_count__()
            kt_info.play_kind_effect( se_type, se_info, skill_level, src_grid_obj, target_grid_obj, v, effect_attr, effect_param, function()
                counter = counter - 1
                if counter <= 0 then call_back_func() end
            end)
        else
            target_effect_flag = true
        end

        -- 每个位置都会自动减一
        counter = counter - 1
        if counter <= 0 then call_back_func() end
    end
end

function processVerifyTriggerFunc( temp_trigger_func, call_back_func )
    -- 中途触发的效果，现在开始起作用
    local __execute_trigger_func__ = nil
    __execute_trigger_func__ = function( index, cb )
        if index > #temp_trigger_func then return cb() end
        local func = temp_trigger_func[index]
        func( function() __execute_trigger_func__( index + 1, cb ) end )
    end
    __execute_trigger_func__( 1, call_back_func )
end

function processVerifyTriggerSkillFunc( call_back_func )
    local __process__ = nil
    __process__ = function( cb )
        if #verify_fight_manager.all_trigger_skill_func == 0 then return cb() end

        local temp_trigger_func = verify_fight_manager.all_trigger_skill_func
        verify_fight_manager.all_trigger_skill_func = {}

        processVerifyTriggerFunc( temp_trigger_func, function() __process__( cb ) end )
    end
    __process__( function() processVerifyDeathTriggerFunc( call_back_func ) end )
end

function processVerifyDeathTriggerFunc( call_back_func )
    local temp_trigger_func = verify_fight_manager.death_trigger_func
    verify_fight_manager.death_trigger_func = {}

    processVerifyTriggerFunc( temp_trigger_func, function()
        for _,grid_obj in ipairs( verify_fight_manager:getAllFighterObjects() ) do
            if grid_obj.death_event then
                grid_obj.death_cb_count:popEnd()
                grid_obj:tryDoDeath()
            end
        end

        call_back_func()
    end)
end
