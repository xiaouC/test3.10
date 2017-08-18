-- ./win/Fight/fightConfig.lua
require 'win.Fight.fightConst'

if not ATTR_NAME then
    hero_attr_fire      = 1
    hero_attr_water     = 2
    hero_attr_wood      = 3
    hero_attr_light     = 4
    hero_attr_dark      = 5
    hero_attr_null      = 6
    hero_attr_pvp       = 7

    -- 精灵属性枚举
    ATTR_NAME = {
        [hero_attr_fire] = {
            skill_attr = 1,
        },
        [hero_attr_water] = {
            skill_attr = 2,
        },
        [hero_attr_wood] = {
            skill_attr = 4,
        },
        [hero_attr_light] = {
            skill_attr = 8,
        },
        [hero_attr_dark] = {
            skill_attr = 16,
        },
    }
end

verify_fight_object_type = {
    ['enemy'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_monster_object.new( obj_info, pos_index )
        end,
    },
    ['player'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_pet_object.new( obj_info, pos_index )
        end,
    },
    ['stone'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_stone_object.new( obj_info, pos_index )
        end,
    },
    ['boss'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_boss_object.new( obj_info, pos_index )
        end,
    },
    ['buff_atk'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_buff_atk_object.new( obj_info, pos_index )
        end,
    },
    ['buff_def'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_buff_def_object.new( obj_info, pos_index )
        end,
    },
    ['buff_mov'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_buff_mv_object.new( obj_info, pos_index )
        end,
    },
    ['buff_critical'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_buff_crit_object.new( obj_info, pos_index )
        end,
    },
    ['buff_invincible'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_buff_inv_object.new( obj_info, pos_index )
        end,
    },
    ['buff_recovery'] = {
        oncreate = function( obj_info, pos_index )
            return __verify_buff_restore_object.new( obj_info, pos_index )
        end,
    },
}

function verifyCreateGridObjByType( obj_type, obj_info, pos_index )
    local ot = verify_fight_object_type[obj_type]
    local grid_obj =  ot.oncreate( obj_info, pos_index )
    grid_obj:init()

    return grid_obj
end
