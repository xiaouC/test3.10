-- ./utils/userconfig.lua
local _userDefault = cc.UserDefault:getInstance()

UserConfig = {}

function UserConfig.getBool(k, v)
    return _userDefault:getBoolForKey(k, v)
end
function UserConfig.setBool(k, v)
    assert(type(v)=='boolean', 'expect bool but got '..type(v))
    _userDefault:setBoolForKey(k, v)
end

function UserConfig.getInteger(k, v)
   return _userDefault:getIntegerForKey(k,0)
end

function UserConfig.setInteger(k, v)
    assert(type(v)=='number', 'expect number but got '..type(v))
    _userDefault:setIntegerForKey(k, v)
end

function UserConfig.getDouble(k, v)
    return _userDefault:getDoubleForKey(k,v)
end
function UserConfig.setDouble(k, v)
    assert(type(v)=='number', 'expect number but got '..type(v))
    _userDefault:setDoubleForKey(k, v)
end

function UserConfig.getString(k, v)
    return _userDefault:getStringForKey(k,v)
end
function UserConfig.setString(k, v)
    assert(type(v)=='string', 'expect string but got '..type(v))
    _userDefault:setStringForKey(k, v)
end

function UserConfig.flush()
    _userDefault:flush()
end
function UserConfig.purge()
    _userDefault:purgeSharedUserDefault()
end

local function define_config(prefix, fields, default)
    local obj = {}
    for name, v in pairs(fields) do
        obj['get'..name] = function() return UserConfig['get' .. v.type](prefix .. name, v.default_value) end
        obj['set'..name] = function(v) UserConfig['set' .. v.type](prefix .. name, v) end
    end
    function obj.flush() UserConfig.flush() end
    return obj
end

SystemConfig = define_config('System', {
	BGMusic         = { type = 'Bool', default_value = false, },
	SoundEffect     = { type = 'Bool', default_value = false, },
	BGVolume        = { type = 'Double', default_value = 1, },
	EffectVolume    = { type = 'Double', default_value = 1, },
})

