-- ./utils/schedule.lua

local scheduler = cc.Director:getInstance():getScheduler()

local all_circle_handles = {}
local all_handlers = {}

function schedule_once(fn)
    return schedule_frames(1, fn)
end

function schedule_once_time(time, fn)
    local handler = nil
    handler = scheduler:scheduleScriptFunc(function()
        scheduler:unscheduleScriptEntry(handler)
        all_handlers[handler] = nil
        fn()
    end, time, false)
    all_handlers[handler] = 0
    return handler
end

function schedule_frames(n, fn)
    if n < 1 then return end

    local handler = nil
    handler = scheduler:scheduleScriptFunc(function()
        if n==1 then
            scheduler:unscheduleScriptEntry(handler)
            all_circle_handles[handler] = nil
            all_handlers[handler] = nil
            fn()
        else
            n = n-1
        end
    end, 0, false)
    all_handlers[handler] = 0
    all_circle_handles[handler] = 0
    return handler
end

function schedule_circle(time, fn, execute_immediately)
    local handler = scheduler:scheduleScriptFunc(fn, time, false)
    all_handlers[handler] = 0
    all_circle_handles[handler] = 0
    if execute_immediately then fn() end
    return handler
end

function unschedule(handler)
    if not handler then return end
    if not all_handlers[handler] then return end

    scheduler:unscheduleScriptEntry(handler)
    all_handlers[handler] = nil
    all_circle_handles[handler] = nil
end

function unscheduleAll()
    for handler, _ in pairs(all_handlers) do
        scheduler:unscheduleScriptEntry(handler)
    end
    all_handlers = {}
    all_circle_handles = {}
end
