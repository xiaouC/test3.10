-- ./app/scene_base.lua

local scene_base = class('scene_base', cc.Scene)
function scene_base:ctor()
    self:onNodeEvent('enter', function() self:on_enter() end)
    self:onNodeEvent('cleanup', function() self:on_cleanup() end)
end

function scene_base:on_enter()
    self:init_views()
    self:init_data_from_server()
end

function scene_base:on_cleanup()
end

function scene_base:init_views()
end

function scene_base:init_data_from_server()
end

return scene_base
