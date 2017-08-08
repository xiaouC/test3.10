-- ./app/platform/game/game_common/game_scene_popup_base.lua

local popup_base = require 'app.platform.common.popup_base'

local GameScenePopupBase = class('GameScenePopupBase', popup_base)
function GameScenePopupBase:ctor(game_scene, args, show_anim_func, hide_anim_func)
    -- listen cb
    self.unlisten_attr_cb = {}
    self.unlisten_signal_cb = {}

    popup_base.ctor(self, game_scene, args, show_anim_func, hide_anim_func)
end

function GameScenePopupBase:clear()
    self:unlistenAllGameAttribute()
    self:unlistenAllGameSignal()

    popup_base.clear(self)
end

-- game attribute
function GameScenePopupBase:listenGameAttribute(attr_name, callback)
    if not self.unlisten_attr_cb[attr_name] then self.unlisten_attr_cb[attr_name] = {} end
    self.unlisten_attr_cb[attr_name][callback] = 1

    self.scene_instance:listenGameAttribute(attr_name, callback)

    return callback
end

function GameScenePopupBase:listenGameAttributeList(attr_list, callback)
    for _, name in ipairs(attr_list or {}) do
        self:listenGameAttribute(name, callback)
    end
end

function GameScenePopupBase:unlistenGameAttribute(attr_name, callback)
    if self.unlisten_attr_cb[attr_name] then
        self.unlisten_attr_cb[attr_name][callback] = nil
    end

    self.scene_instance:unlistenAllGameAttribute(attr_name, callback)
end

function GameScenePopupBase:unlistenAllGameAttribute()
    for attr_name, v in pairs(self.unlisten_attr_cb) do
        for cb, _ in pairs(v) do
            self.scene_instance:unlistenGameAttribute(attr_name, cb)
        end
    end
    self.unlisten_attr_cb = {}
end

-- game signal
function GameScenePopupBase:listenGameSignal(name, callback)
    if not self.unlisten_signal_cb[name] then self.unlisten_signal_cb[name] = {} end
    self.unlisten_signal_cb[name][callback] = 1

    self.scene_instance:listenGameSignal(name, callback)

    return callback
end

function GameScenePopupBase:listenGameSignalList(name_list, callback)
    for _, name in ipairs(name_list or {}) do
        self:listenGameSignal(name, callback)
    end
end

function GameScenePopupBase:unlistenGameSignal(name, callback)
    if self.unlisten_signal_cb[name] then
        self.unlisten_signal_cb[name][callback] = nil
    end

    self:unlistenGameSignal(name, callback)
end

function GameScenePopupBase:unlistenAllGameSignal()
    for name, v in pairs(self.unlisten_signal_cb) do
        for cb, _ in pairs(v) do
            self.scene_instance:unlistenGameSignal(name, cb)
        end
    end

    self.unlisten_signal_cb = {}
end

function GameScenePopupBase:listen_label(name, attr_name, init_text, convert_func, parent_node)
    local unlisten_cb = self.scene_instance:listen_label(name, attr_name, init_text, convert_func, parent_node)
    self.unlisten_attr_cb[attr_name][unlisten_cb] = 1
end

-- 
return GameScenePopupBase
