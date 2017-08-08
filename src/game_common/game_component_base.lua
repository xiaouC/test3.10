-- ./app/platform/game/game_common/game_component_base.lua

GAME_VIEW_Z_ORDER = {
    DIRECTION_NODE          = 10,
    HAND_CARD_FACING        = 50,
    LEI_CARD_FACING         = 70,
    OUT_CARD_FACING         = 75,
    OUT_CARD_LEFT           = 75,
    OUT_CARD_RIGHT          = 75,
    OUT_CARD_SELF           = 75,
    OUT_CARD_TIPS           = 80,
    LEI_CARD_LEFT           = 80,
    LEI_CARD_RIGHT          = 80,
    TAN_CARD_LEFT           = 85,
    TAN_CARD_RIGHT          = 85,
    TAN_CARD_SELF           = 85,
    TAN_CARD_FACING         = 85,
    LEI_CARD_SELF           = 90,
    HAND_CARD_LEFT          = 90,
    HAND_CARD_RIGHT         = 90,
    TAN_CARD_SELF           = 95,
    HAND_CARD_SELF          = 100,
    TING_CARD               = 200,
    BLOCK                   = 300,
    DICE                    = 300,
    USER_HEAD               = 400,
    BATTERY_NET_STATE       = 400,
    USER_DETAIL             = 450,
    CHAT                    = 500,
    ROUND_SETTLE            = 600,
    FREE_GAME               = 700,
    VOICE_CHAT              = 800,
    REPLAY_CTRL             = 1000,
}

---------------------------------------------------------------------------------------------------------------------
component_base = class('component_base')
function component_base:ctor(game_scene)
    self.game_scene = game_scene

    self.unlisten_signal_cb = {}
end

function component_base:cleanup()
    self:unlistenAllGameSignal()
end

function component_base:init(args)
    self.game_scene:listenGameSignal('game_state', function(game_state) self:on_game_state(game_state) end)
end

-- game signal
function component_base:listenGameSignal(name, callback)
    if not self.unlisten_signal_cb[name] then self.unlisten_signal_cb[name] = {} end
    self.unlisten_signal_cb[name][callback] = 1

    self.game_scene:listenGameSignal(name, callback)

    return callback
end

function component_base:listenGameSignalList(name_list, callback)
    for _, name in ipairs(name_list or {}) do
        self:listenGameSignal(name, callback)
    end
end

function component_base:unlistenGameSignal(name, callback)
    if self.unlisten_signal_cb[name] then
        self.unlisten_signal_cb[name][callback] = nil
    end

    self:unlistenGameSignal(name, callback)
end

function component_base:unlistenAllGameSignal()
    for name, v in pairs(self.unlisten_signal_cb) do
        for cb, _ in pairs(v) do
            self.game_scene:unlistenGameSignal(name, cb)
        end
    end

    self.unlisten_signal_cb = {}
end

function component_base:on_game_state(game_state)
    local all_game_states = {
        ['waiting']             = function() self:on_game_waiting() end,
        ['game_start']          = function() self:on_game_start() end,
        ['playing']             = function() self:on_game_playing() end,
        ['round_end']           = function() self:on_round_end() end,
        ['prepare_next_round']  = function() self:on_prepare_next_round() end,
        ['game_end']            = function() self:on_game_end() end,
        ['game_quit']           = function() self:on_game_quit() end,
    }

    all_game_states[game_state]()
end

function component_base:on_game_waiting()
end

function component_base:on_game_start()
end

function component_base:on_game_playing()
end

function component_base:on_round_end()
end

function component_base:on_prepare_next_round()
end

function component_base:on_game_end()
end

function component_base:on_game_quit()
end

---------------------------------------------------------------------------------------------------------------------
view_component_base = class('view_component_base', component_base)
function view_component_base:ctor(game_scene)
    component_base.ctor(self, game_scene)

    self.need_swallow = true
end

function view_component_base:init(args)
    component_base.init(self, args)

    -- background color
    self.bg_layer = createBackgroundLayer(
                            self.bg_color or cc.c4b(0, 0, 0, 0),
                            self.need_swallow,
                            function(touch, event) return self:on_touch_began(touch, event) end,
                            function(touch, event) self:on_touch_moved(touch, event) end,
                            function(touch, event) self:on_touch_ended(touch, event) end
                        )
    self.game_scene:addChild(self.bg_layer, self.csb_z_order or 0)

    -- 
    if self.csb_file then
        self.csb_node = cc.CSLoader:createNode(self.csb_file)
        self.csb_node:setPosition(display.width * 0.5, display.height * 0.5)
        self.bg_layer:addChild(self.csb_node, self.csb_z_order or 0)
    end
end

function view_component_base:on_touch_began(touch, event)
    return false
end

function view_component_base:on_touch_moved(touch, event)
end

function view_component_base:on_touch_ended(touch, event)
end

