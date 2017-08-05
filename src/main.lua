
cc.FileUtils:getInstance():setPopupNotify(false)
cc.FileUtils:getInstance():addSearchPath("src/")
cc.FileUtils:getInstance():addSearchPath("res/")

require "config"
require "cocos.init"

function enterBackground()
end

function enterForeground()
    enterForegroundReloadShaders()
end

local function main()
end

local status, msg = xpcall(main, __G__TRACKBACK__)
if not status then
    print(msg)
end
