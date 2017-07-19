--./utils/common.lua

-- 获取文件的扩展名
function get_extension(file_name) return file_name:match('.+%.(%w+)$') end

function strip_extension(file_name)
    local idx = file_name:match('.+()%.%w+$')
    if idx then
        return file_name:sub(1, idx - 1)
    else
        return file_name
    end
end

function get_external_path()
    local storage = SystemConfig.getStorage()
    if storage == 'sdcard' then
        local sdcard = getSDCardPath()
        if sdcard ~= '' then return sdcard end
    end
    return CCFileUtils:sharedFileUtils():getWritablePath()
end

function get_device_id()
    if GameSettings.devicesID then return GameSettings.devicesID end
    return getDeviceId()
end

function removeUnusedTextures( enforce )
    -- 强制清理的话，就一定会清理
    -- 不强制的话，只要当前可用内存大于 100 M，就不会执行清理
    if enforce then
        ParticleSystemManager:sharedParticleSystemManager():cleanupCache()
        CCSpriteFrameCache:sharedSpriteFrameCache():removeUnusedSpriteFrames()
        CCTextureCache:sharedTextureCache():removeUnusedTextures()

        return
    end

    if tonumber(getAvailMemory()) >= 100 then return end

    cc.SpriteFrameCache:sharedSpriteFrameCache():removeUnusedSpriteFrames()
    cc.TextureCache:sharedTextureCache():removeUnusedTextures()
end


function dumpall(msg)
    print('dump:' .. tostring(msg))
    dump_rusage()
    dump_texture()
    print('lua:' .. collectgarbage('count'))
end

function _YYTEXT(s)
    return s
end
