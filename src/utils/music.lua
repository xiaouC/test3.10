-- ./utils/music.lua

local _current_music = nil
local _music_mute = nil
local _sound_mute = nil

function play_music(path, loop)
    if not path then return end
    if path == _current_music then return end

    _current_music = path
    if not _music_mute then
        SimpleAudioEngine:sharedEngine():playBackgroundMusic(getFullPath(path), loop)
    end
end

function stop_music()
    _current_music = nil
    SimpleAudioEngine:sharedEngine():stopBackgroundMusic(true)
end

function pause_music()
    SimpleAudioEngine:sharedEngine():pauseBackgroundMusic()
end

function resume_music()
    if not _music_mute then
        SimpleAudioEngine:sharedEngine():resumeBackgroundMusic()
    end
end

-- 播放音效 path表示路径，loop是循环次数
function play_effect(path, loop)
    if not _sound_mute then
        return SimpleAudioEngine:sharedEngine():playEffect(getFullPath(path), loop or false)
    end
end

-- 停止音效
function stop_effect(handler)
    SimpleAudioEngine:sharedEngine():stopEffect(handler)
end

function stop_all_effect()
    SimpleAudioEngine:sharedEngine():stopAllEffects()
end

-- 设置音量大小
function set_music_volume(value)
    SimpleAudioEngine:sharedEngine():setBackgroundMusicVolume(value)
end

-- 设置音效大小
function set_effect_volume(value)
    SimpleAudioEngine:sharedEngine():setEffectsVolume(value)
end

-- 设置音乐开关
function set_music_mute(mute)
	if _music_mute == mute then return end

	_music_mute = mute
    SystemConfig.setBGMusic(_music_mute)

	if mute then
		SimpleAudioEngine:sharedEngine():stopBackgroundMusic()
	else
		if _current_music then SimpleAudioEngine:sharedEngine():playBackgroundMusic(getFullPath(_current_music), true) end
	end
end

function get_music_mute()
    return _music_mute
end

-- 设置音效开关
function set_effect_mute(mute)
	if _sound_mute == mute then return end

	_sound_mute = mute
	SystemConfig.setSoundEffect(_sound_mute)

	if mute then stop_all_effect() end
end

function get_effect_mute()
    return _sound_mute
end
