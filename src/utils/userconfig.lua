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
    for name, tp in pairs(fields) do
        obj['get'..name] = function()
			if default and default[name] then 
				return UserConfig['get'..tp](prefix..name, default[name])
			else
				return UserConfig['get'..tp](prefix..name)
			end
        end
        obj['set'..name] = function(v)
            UserConfig['set'..tp](prefix..name, v)
        end
    end
    function obj.flush()
        UserConfig.flush()
    end
    return obj
end

local function define_role_config(fields, default)
    local obj = {}
    for name, tp in pairs(fields) do
        obj['get'..name] = function()
			if default and default[name] then 
				return UserConfig['get'..tp](name..(g_player and g_player.entityID or 'default'), default[name])
			else
				return UserConfig['get'..tp](name..(g_player and g_player.entityID or 'default'))
			end
        end
        obj['set'..name] = function(v)
            UserConfig['set'..tp](name..(g_player and g_player.entityID or 'default'), v)
        end
    end
    function obj.flush()
        UserConfig.flush()
    end
    return obj
end

RoleConfig = define_role_config({
    FightSpeed = 'Integer',
	AutoFight = 'Bool',
},{
    FightSpeed = 1,
    AutoFight = false,
})

PlayerConfig = define_config('Player', {
    AccountName = 'String',
    Password = 'String',
	LastLoginServerID = 'Integer',
	LastLoginServerName = 'String',
	LastLoginServerID2 = 'Integer',
	LastLoginServerName2 = 'String',
    QuickRegister = 'Bool',
    QuickRegisterAccountName = 'String',
    QuickRegisterPassword = 'String',
}, {
    AccountName = '',
    Password = '',
    LastLoginServerID = -1,
    LastLoginServerName = '',
    LastLoginServerID2 = -1,
    LastLoginServerName2 = '',
    QuickRegister = false,
    QuickRegisterAccountName = '',
    QuickRegisterPassword = '',
})

SystemConfig = define_config('System', {
	BGMusic = 'Bool',
	SoundEffect = 'Bool',
	BGVolume = 'Double',
	EffectVolume = 'Double',
	HidePlayer = 'Bool',
	Use3G = 'Bool',
    CGPlay = 'Bool',
    ShowLoadbarReward = 'Bool',
    Storage = 'String',
    WakeLock = 'Bool',
    PushNotification1 = 'Bool',
    PushNotification2 = 'Bool',
    PushNotification3 = 'Bool',
    PushNotification4 = 'Bool',
    FirstInstall = 'Bool',
    ShowCG = 'Bool',
    ShowFakeFight = 'Bool',
}, {
	BGMusic = false,
	SoundEffect = false,
	BGVolume = 1,
	EffectVolume = 1,
	HidePlayer = false,
	Use3G = false,
    CGPlay = true,
    ShowLoadbarReward = true,
    Storage = '', -- sdcard or system
    WakeLock = true,
    PushNotification1 = false,
    PushNotification2 = false,
    PushNotification3 = false,
    PushNotification4 = false,
    FirstInstall = true,
    ShowCG = true,
    ShowFakeFight = true,
})

