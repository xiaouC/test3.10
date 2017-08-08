-- 

local game_scene_manager_base = import('...game_common.game_scene_manager_base')

local GameSceneManager = class('GameSceneManager', game_scene_manager_base)
function GameSceneManager:ctor()
    game_scene_manager_base.ctor(self)
end

function GameSceneManager:init_module(game_handle_impl)
    game_scene_manager_base.init_module(self, game_handle_impl)
end

function GameSceneManager:leave_game_scene()
    game_scene_manager_base.leave_game_scene(self)
end

return GameSceneManager
