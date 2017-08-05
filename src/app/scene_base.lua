-- ./app/scene_base.lua
require 'utils.schedule'

local meta_signal = require 'utils.meta_signal'
local scene_base = class('scene_base', meta_signal, cc.Scene)
function scene_base:ctor()
    meta_signal.ctor(self)

    -- 
    self.all_schedule_handlers = {}
    self.all_views = {}

    --
    self:onNodeEvent('enter', function() self:on_enter() end)
    self:onNodeEvent('cleanup', function() self:on_cleanup() end)
end

function scene_base:on_enter()
    self:init_views()
    self:init_data_from_server()
end

function scene_base:on_cleanup()
    meta_signal.unlisten_all_signal(self)

    self:unschedule_all()
    self.all_views = {}
end

function scene_base:init_views()
end

function scene_base:init_data_from_server()
end

function scene_base:schedule_once(fn)
    local handler = schedule_once(fn)

    self.all_schedule_handlers[handler] = 1

    return handler
end

function scene_base:schedule_frames(n, fn)
    local handler = schedule_frames(n, fn)

    self.all_schedule_handlers[handler] = 1

    return handler
end

function scene_base:schedule_once_time(time, fn)
    local handler = schedule_once_time(time, fn)

    self.all_schedule_handlers[handler] = 1

    return handler
end

function scene_base:schedule_circle(time, fn, execute_immediately)
    local handler = schedule_circle(time, fn, execute_immediately)

    self.all_schedule_handlers[handler] = 1

    return handler
end

function scene_base:unschedule(handler)
    unschedule(handler)

    self.all_schedule_handlers[handler] = nil
end

function scene_base:unschedule_all()
    for handler, _ in pairs(self.all_schedule_handlers) do
        unschedule(handler)
    end
    self.all_schedule_handlers = {}
end

function scene_base:append_view(view_tag, update_func)
    self.all_views[view_tag] = update_func
end

function scene_base:update_view(view_tag, ...)
    local update_func = self.all_views[view_tag]
    if update_func then update_func(...) end
end

function scene_base:update_all_views()
    for _, update_func in pairs(self.all_views) do
        update_func()
    end
end

return scene_base
