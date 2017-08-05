-- ./utils/meta_signal.lua
require 'utils.signal'

local meta_signal = class('meta_signal')
function meta_signal:ctor()
    self.all_signal_callbacks = {}
end

function meta_signal:listen_signal(name, callback, priority)
    local cb = signal.listen(name, callback, priority)

    if not self.all_signal_callbacks[name] then self.all_signal_callbacks[name] = {} end
    self.all_signal_callbacks[name][callback] = priority

    return cb
end

function meta_signal:unlisten_signal(name, callback)
    signal.unlisten(name, callback)

    if self.all_signal_callbacks[name] then
        self.all_signal_callbacks[name][callback] = nil
    end
end

function meta_signal:fire(name, ...)
    signal.fire(name, ...)
end

function meta_signal:unlisten_all_signal()
    for name, v in pairs(self.all_signal_callbacks) do
        for cb, _ in pairs(v) do
            signal.unlisten(name, cb)
        end
    end
    self.all_signal_callbacks = {}
end

return meta_signal
