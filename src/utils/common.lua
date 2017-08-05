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

-- create popup window's background layer
function createBackgroundLayer(bg_color, need_swallow, on_touch_began, on_touch_moved, on_touch_ended)
    -- background layer color
    local bg_layer = cc.LayerColor:create(bg_color or cc.c4b(0, 0, 0, 125), display.width, display.height)

    -- listener
    local listener = cc.EventListenerTouchOneByOne:create()
    listener:setSwallowTouches(need_swallow)
    listener:registerScriptHandler(on_touch_began or function() return true end, cc.Handler.EVENT_TOUCH_BEGAN)
    listener:registerScriptHandler(on_touch_moved or function() end, cc.Handler.EVENT_TOUCH_MOVED)
    listener:registerScriptHandler(on_touch_ended or function() end, cc.Handler.EVENT_TOUCH_ENDED)
    bg_layer:getEventDispatcher():addEventListenerWithSceneGraphPriority(listener, bg_layer)

    return bg_layer
end

-- create anim csb
function createAnimNode(csb_file, is_loop)
    local anim_timeline = cc.CSLoader:createTimeline(csb_file)
    anim_timeline:gotoFrameAndPlay(0, is_loop and true or false)

    local anim_node = cc.CSLoader:createNode(csb_file)
    anim_node:runAction(anim_timeline)

    return anim_node
end

-- widget
function createWidget(csb_file, width, height)
    local csb_node = cc.CSLoader:createNode(csb_file)
    csb_node:setPosition(width * 0.5, height * 0.5)

    local csb_widget = ccui.Widget:create()
    csb_widget:setContentSize(cc.size(width, height))
    csb_widget:addChild(csb_node)

    return csb_widget, csb_node
end

-- local tbl = {
--     img_normal = '',
--     img_selected = '',
--     tex_res_type = ccui.TextureResType.localType,
--     text = '',
--     text_color = cc.WHITE,
--     text_size = cc.size(0, 0),
--     font_name = '',
--     font_size = 30,
--     enable_outline = false,
--     outline_color = cc.c3b(83, 30, 11),
--     outline_size = 2,
--     onchanged = function(rb, event_type) end,
-- }
function createRadioWidget(tbl)
    local rb = ccui.RadioButton:create(tbl.img_normal, tbl.img_normal, tbl.img_selected, tbl.img_normal, tbl.img_selected, tbl.tex_res_type or ccui.TextureResType.localType)

    local rb_widget = ccui.Widget:create()
    rb_widget:addChild(rb)

    local size = rb:getContentSize()
    rb_widget:setContentSize(size)
    rb:setPosition(size.width * 0.5, size.height * 0.5)

    local text_label = cc.Label:createWithTTF(tbl.text or '', tbl.font_name or 'font/jxk.TTF', tbl.font_size or 30, tbl.text_size or cc.size(0, 0))
    text_label:setAnchorPoint(0.5, 0.5)
    text_label:setPosition(size.width * 0.5, size.height * 0.5)
    text_label:setColor(tbl.text_color or cc.WHITE)
    if tbl.enable_outline then text_label:enableOutline(tbl.outline_color or cc.c3b(83, 30, 11), tbl.outline_size or 2) end
    rb_widget:addChild(text_label)

    rb:addEventListener(function(rb_self, event_type)
        if tbl.onchanged then tbl.onchanged(rb_self, event_type) end
    end)

    return rb_widget, rb, text_label
end

function createSpriteWithName(file, res_type)
    if res_type == ccui.TextureResType.localType then
        return cc.Sprite:create(file)
    else
        return cc.Sprite:createWithSpriteFrameName(file)
    end
end

function setSpriteTexture(sprite, file, res_type)
    if res_type == ccui.TextureResType.localType then
        sprite:setTexture(file)
    else
        sprite:setSpriteFrame(file)
    end
end

function unload_game_module(game_id)
    local loaded_files = {}

    for k, _ in pairs(package.loaded) do
        if string.match(k, tostring(game_id)) or string.match(k, 'game_common') then
            table.insert(loaded_files, k)
        end
    end

    for _,file_name in ipairs( loaded_files ) do package.loaded[file_name] = nil end
end

function switchScene(scene_path, ...)
    local next_scene = require(scene_path).new(...)
    next_scene:init()
    cc.Director:getInstance():replaceScene(next_scene)

    return next_scene
end
