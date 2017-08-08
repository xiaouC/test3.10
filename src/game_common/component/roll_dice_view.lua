-- ./app/platform/game/game_common/roll_dice_view.lua
require 'app.platform.game.game_common.game_component_base'

local m_clientmain = require 'app.platform.room.clientmain'

local RollDiceView = class('RollDiceView', view_component_base)
function RollDiceView:ctor(game_scene)
    view_component_base.ctor(self, game_scene)

    self.csb_file = 'mahjong/component/roll_dice/roll_dice_node.csb'
    self.csb_z_order = GAME_VIEW_Z_ORDER.DICE
end

function RollDiceView:clear()
    view_component_base.clear(self)
end

function RollDiceView:init()
    view_component_base.init(self)

    -- 
    self.csb_node:setVisible(false)
    self.csb_node:setScale(0.9)
    self.csb_node:setPosition(display.width * 0.5, display.height * 0.5 + 25)

    registerAnimationRange('roll_dice_1', 'dice_anim_1_%d.png', 1, 6, 0.6 / 6)
    registerAnimationRange('roll_dice_2', 'dice_anim_2_%d.png', 1, 6, 0.6 / 6)

    -- 
    self:listenGameSignal('roll_dice', function(banker_server_index, dice_num_1, dice_num_2, callback_func)
        self:roll_dice(banker_server_index, dice_num_1, dice_num_2, callback_func)
    end)
    self:listenGameSignal('roll_dice_custom', function(server_index, dice_num_1, dice_num_2, callback_func)
        self:roll_dice(server_index, dice_num_1, dice_num_2, callback_func)
    end)
end

function RollDiceView:roll_dice(server_index, dice_num_1, dice_num_2, callback_func)
    local node_dice = self.csb_node:getChildByName('node_dice')

    --
    local node_dir = self.csb_node:getChildByName('node_dir')
    self.csb_node:setVisible(true)

    local angle = (self.game_scene.my_server_index - 2) * 90
    node_dir:setRotation(angle)

    -- 
    local anim_node_hand = node_dir:getChildByName('node_hand_' .. server_index)
    local anim_timeline = cc.CSLoader:createTimeline('mahjong/component/roll_dice/roll_dice_hand.csb')
    anim_timeline:setTimeSpeed(40/60)
    anim_timeline:gotoFrameAndPlay(0, false)
    anim_node_hand:runAction(anim_timeline)
    anim_node_hand:setVisible(true)

    -- 0.6 秒后
    performWithDelay(self.csb_node, function()
        local blank_node = node_dir:getChildByName('direction'):getChildByName('blank_dir_' .. server_index)
        blank_node:setVisible(true)

        local function __dice_anim__(index, num)
            local dice_sprite = node_dice:getChildByName('dice_' .. index) 

            local roll_action = cc.Animate:create(cc.AnimationCache:getInstance():getAnimation('roll_dice_' .. index))
            local cb_action = cc.CallFunc:create(function()
                blank_node:setVisible(false)
                dice_sprite:setSpriteFrame(cc.SpriteFrameCache:getInstance():getSpriteFrame(string.format('dice_%d_%d.png', index, num)))
            end) 
            dice_sprite:runAction(cc.Sequence:create(roll_action, cb_action))
            dice_sprite:runAction(cc.RotateTo:create(0.6, 1100))
        end
        __dice_anim__(1, dice_num_1)
        __dice_anim__(2, dice_num_2)
    end, 0.5)

    -- 3 秒后自动关闭
    performWithDelay(self.csb_node, function()
        anim_node_hand:setVisible(false)
        self.csb_node:setVisible(false)

        if callback_func then callback_func() end
    end, 2)
end

return RollDiceView
