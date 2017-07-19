--./utils/signal.lua
-- 实现通用监听模式

local _listeners = {}

signal = {}

function signal.listen(key, callback, orderIndex)
    if _listeners[key] == nil then
        _listeners[key] = {}
    end
    --table.insert(_listeners[key], callback)
    _listeners[key][callback] = orderIndex or 0
    return callback
end

function signal.unlisten(key, callback)
    if _listeners[key]==nil then
        return
    end
    _listeners[key][callback] = nil
    --return table.remove(_listeners[key], callback)
end

local function signal_cmp(a,b)
    return a.value > b.value
end

function signal.fire(key, ...)
    for cb, _ in table.orderIter(_listeners[key] or {} ,signal_cmp) do
        cb(...)
    end
end

function signal.fireBool(key, ...)
    local bl = nil
    for cb, _ in table.orderIter(_listeners[key] or {} ,signal_cmp) do
        local ret = cb(...)
        -- 返回值全为真是返回真
        bl = (bl == nil and true or bl) and ret or false
    end
    return bl
end

function signal.purge()
    _listeners = {}
end
