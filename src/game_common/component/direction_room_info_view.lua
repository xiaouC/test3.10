-- ./app/platform/game/game_common/direction_and_room_info_view.lua
require 'app.platform.game.game_common.game_component_base'

local m_clientmain = require 'app.platform.room.clientmain'

local DirectionRoomInfoView = class('DirectionRoomInfoView', view_component_base)
function DirectionRoomInfoView:ctor(game_scene)
    view_component_base.ctor(self, game_scene)

    self.csb_file = 'mahjong/component/direction_and_room_info/direction_and_room_info.csb'
    self.csb_z_order = GAME_VIEW_Z_ORDER.DIRECTION_NODE
end

function DirectionRoomInfoView:clear()
    view_component_base.clear(self)
end

function DirectionRoomInfoView:init()
    view_component_base.init(self)

    -- 
    self.csb_node:setVisible(false)
    self.csb_node:setPosition(display.width * 0.5 - 10, display.height * 0.5 + 22)

    -- 
    local node_dir = self.csb_node:getChildByName('node_dir')
    if self.game_scene.my_server_index then
        local angle = (self.game_scene.my_server_index - 2) * 90
        node_dir:setRotation(angle)
    end
    self:listenGameSignal('my_server_index', function(server_index)
        local angle = (server_index - 2) * 90
        node_dir:setRotation(angle)
    end)

    local all_turn_dirs = {}
    for i=1, 4 do
        all_turn_dirs[i] = node_dir:getChildByName('blank_dir_' .. i)
        all_turn_dirs[i]:setVisible(false)
    end
    self:listenGameSignal('user_turn', function(server_index)
        for _, turn_dir in ipairs(all_turn_dirs) do
            turn_dir:stopAllActions()
            turn_dir:setVisible(false)
        end

        all_turn_dirs[server_index]:runAction(cc.RepeatForever:create(cc.Blink:create(1, 1)))
    end)

    local text_game_round = label('text_game_round', '', self.csb_node)
    self:listenGameSignal('play_count', function(cur_play_count, total_play_count)
        text_game_round:setString(string.format('%s/%d', cur_play_count, total_play_count))
    end)

    local text_room_id = label('text_room_id', '', self.csb_node)
    self:listenGameSignal('room_id', function(room_id) text_room_id:setString(tostring(room_id)) end)

    label('text_game_name', tostring(self.game_scene.scene_config.game_name), self.csb_node)

    if self.game_scene.is_replay then
        self.csb_node:getChildByName('text_static_game_round'):setVisible(false)
    end

    -- 
    if self.game_scene.scene_config.ghost_card_name then
        local text_label_2 = cc.Label:createWithTTF(self.game_scene.scene_config.ghost_card_name, 'font/jxk.TTF', 35, cc.size(35, 0))
        text_label_2:setColorTextureIndex(2)
        text_label_2:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
        text_label_2:setAnchorPoint(0.5, 1)
        text_label_2:enableShadow()
        self.csb_node:getChildByName('node_ghost_text'):addChild(text_label_2)
    end

    local node_ghost_card = self.csb_node:getChildByName('node_ghost_card')
    self:listenGameSignal('ghost_card_confirm', function(fake_card_ids, really_card_ids, dice_num_1, dice_num_2)
        node_ghost_card:removeAllChildren()

        local card_width = 85
        local card_scale = 0.6
        local card_interval = 5
        local card_count = #really_card_ids
        local total_width = card_width * card_scale * card_count + (card_count - 1 ) * card_interval

        local start_x = card_width * card_scale * 0.5 - total_width * 0.5
        for _, card_id in ipairs(really_card_ids) do
            local card = create_card_front(USER_LOCATION_SELF, CARD_AREA.HAND, card_id)
            card:setPosition(start_x, 0)
            card:setScale(card_scale)
            node_ghost_card:addChild(card)

            start_x = start_x + card_width * card_scale + card_interval
        end
    end)
    self:listenGameSignal('roll_dice', function(banker_server_index, dice_num_1, dice_num_2)
        local node_dice = self.csb_node:getChildByName('node_dice')
        local dice_sprite_1 = node_dice:getChildByName('dice_1') 
        dice_sprite_1:setSpriteFrame(cc.SpriteFrameCache:getInstance():getSpriteFrame(string.format('dice_1_%d.png', dice_num_1)))
        local dice_sprite_2 = node_dice:getChildByName('dice_2') 
        dice_sprite_2:setSpriteFrame(cc.SpriteFrameCache:getInstance():getSpriteFrame(string.format('dice_2_%d.png', dice_num_2)))
    end)
    self:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        if block_type == 'win' then
            for _, turn_dir in ipairs(all_turn_dirs) do
                turn_dir:stopAllActions()
                turn_dir:setVisible(false)
            end
        end
    end)
end

function DirectionRoomInfoView:on_game_state(game_state)
    view_component_base.on_game_state(self, game_state)

    self.csb_node:setVisible(game_state ~= 'waiting' and true or false)
end

function DirectionRoomInfoView:on_prepare_next_round()
    local node_ghost_card = self.csb_node:getChildByName('node_ghost_card')
    node_ghost_card:removeAllChildren()
end

return DirectionRoomInfoView
