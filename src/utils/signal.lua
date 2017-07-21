--./utils/signal.lua
-- 实现通用监听模式

local _listeners = {}

signal = {}

function signal.listen(key, callback, priority)
    if not _listeners[key] then _listeners[key] = {} end
    _listeners[key][callback] = priority or 0
    return callback
end

function signal.unlisten(key, callback)
    if _listeners[key] then
        _listeners[key][callback] = nil
    end
end

local function signal_cmp(a,b)
    return a.value > b.value
end

function signal.fire(key, ...)
    for cb, _ in table.orderIter(_listeners[key] or {} ,signal_cmp) do
        cb(...)
    end
end

function signal.purge()
    _listeners = {}
end
