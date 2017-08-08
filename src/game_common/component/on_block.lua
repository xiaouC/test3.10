-- ./app/platform/game/game_common/component/on_block.lua
require 'app.platform.game.game_common.game_card_config'
require 'app.platform.game.game_common.game_component_base'

local on_block = class('on_block_component', component_base)
function on_block:ctor(game_scene)
    component_base.ctor(self, game_scene)

    self.block_config = {
        {
            level = 0x00,       -- 取消
            sprite_file = 'mahjong/common/cancel.png',
            is_valid = function(v, block_info, block_level, card_id, is_out, block_index) return true end,
            onclick = function(v, btn_node, block_info, block_level, card_id, is_out, block_index)
                if v.confirm_cancel then
                    v.confirm_cancel = nil

                    game_scene:requestAction('block', v.level, { card_id }, is_out, block_index)

                    return true
                end

                if bit.band(block_level, 0x10) > 0 then
                    btn_node:loadTextureNormal('mahjong/common/confirm_pass.png', ccui.TextureResType.localType)

                    v.confirm_cancel = true

                    return false
                end

                game_scene:requestAction('block', v.level, { card_id }, is_out, block_index)

                return true
            end,
        },
        {
            level = 0x10,       -- 胡
            sprite_file = 'default.png',
            anim_file = 'mahjong/anim/anim_win.csb',
            anim_offset = { x = 2, y = 35 },
            is_valid = function(v, block_info, block_level, card_id, is_out, block_index) return bit.band(block_level, v.level) > 0 end,
            onclick = function(v, btn_node, block_info, block_level, card_id, is_out, block_index)
                game_scene:requestAction('block', v.level, { card_id }, is_out, block_index)

                return true
            end,
        },
        {
            level = 0x08,       -- 听
            sprite_file = 'mahjong/common/listen.png',
            is_valid = function(v, block_info, block_level, card_id, is_out, block_index) return bit.band(block_level, v.level) > 0 end,
            onclick = function(v, btn_node, block_info, block_level, card_id, is_out, block_index)
                game_scene:requestAction('block', v.level, { card_id }, is_out, block_index)

                return true
            end,
        },
        {
            level = 0x04,       -- 杠
            sprite_file = 'mahjong/common/kong.png',
            is_valid = function(v, block_info, block_level, card_id, is_out, block_index) return bit.band(block_level, v.level) > 0 end,
            onclick = function(v, btn_node, block_info, block_level, card_id, is_out, block_index)
                local count = 0
                for s=1, 5 do
                    if bit.band(block_info[s][1], v.level) > 0 then
                        count = count + 1
                    end
                end

                if count <= 1 then
                    local card_ids = { block_info[1][2], block_info[1][3], block_info[1][4], block_info[1][5] }
                    game_scene:requestAction('block', v.level, card_ids, is_out, block_index)

                    return true
                end

                -- 
                if not v.kong_node then
                    local item_width, item_interval = 180, 10
                    local bg_edge_width = 20
                    local total_width = count * item_width + (count - 1) * item_interval + bg_edge_width * 2
                    local total_height = 120

                    v.kong_node = cc.CSLoader:createNode('mahjong/component/on_block/kong_node_bg.csb')
                    v.kong_node:getChildByName('bg_scale9'):setContentSize(cc.size(total_width, total_height))
                    btn_node:addChild(v.kong_node)

                    --
                    local btn_size = btn_node:getContentSize()

                    local x, y = 80, 250
                    local pos = btn_node:convertToWorldSpace(cc.p(x, 0))
                    if pos.x + total_width * 0.5 > display.width then x = display.width - pos.x + total_width * 0.5 end
                    if pos.x < total_width * 0.5 then x = total_width * 0.5 - pos.x end
                    v.kong_node:setPosition(x, y)

                    -- 
                    local next_x = bg_edge_width + item_width * 0.5 - total_width * 0.5
                    local next_index = 1
                    for s=1, 5 do
                        if bit.band(block_info[s][1], v.level) > 0 then
                            local node = cc.CSLoader:createNode('mahjong/component/on_block/kong_node.csb')
                            node:setPosition(next_x, 5)
                            v.kong_node:addChild(node)

                            button('btn_selected', function()
                                local card_ids = { block_info[s][2], block_info[s][3], block_info[s][4], block_info[s][5] }
                                game_scene:requestAction('block', v.level, card_ids, is_out, block_index)
                            end, node)

                            next_x = next_x + item_width + item_interval
                        end
                    end 
                end

                return false
            end,
        },
        {
            level = 0x02,       -- 碰
            sprite_file = 'mahjong/common/pong.png',
            is_valid = function(v, block_info, block_level, card_id, is_out, block_index) return bit.band(block_level, v.level) > 0 end,
            onclick = function(v, btn_node, block_info, block_level, card_id, is_out, block_index)
                game_scene:requestAction('block', v.level, { card_id, card_id, card_id }, is_out, block_index)

                return true
            end,
        },
        {
            level = 0x01,       -- 吃
            sprite_file = 'mahjong/common/chow.png',
            is_valid = function(v, block_info, block_level, card_id, is_out, block_index) return bit.band(block_level, v.level) > 0 end,
            onclick = function(v, btn_node, block_info, block_level, card_id, is_out, block_index)
                game_scene:requestAction('block', v.level, { card_id }, is_out, block_index)

                return true
            end,
        },
    }
end

function on_block:init(args)
    component_base.init(self, args)

    -- 
    self.csb_node = cc.CSLoader:createNode('mahjong/common/block_operation.csb')
    self.csb_node:setVisible(false)
    self.csb_node:setPosition(display.width * 0.5, 200)
    self.game_scene:addChild(self.csb_node, GAME_VIEW_Z_ORDER.BLOCK)

    self.all_block_btn_nodes = {}
    for i=1, 6 do
        local btn_node = self.csb_node:getChildByName('btn_block_' .. i)
        btn_node:setVisible(false)

        self.all_block_btn_nodes[i] = btn_node
    end

    self:listenGameSignal('on_block', function(block_info, block_level, card_id, is_out, block_index) self:on_block(block_info, block_level, card_id, is_out, block_index) end)
    self:listenGameSignal('on_block_result', function(block_type, show_card_list, src_location_index, src_card_list, dest_location_index, dest_card_list)
        self.csb_node:setVisible(false)
    end)
end

function on_block:on_block(block_info, block_level, card_id, is_out, block_index)
    for _, btn_node in ipairs(self.all_block_btn_nodes) do btn_node:setVisible(false) end
    for _, anim_node in ipairs(self.all_anim_nodes or {}) do
        anim_node:removeFromParent(true)
    end
    self.all_anim_nodes = {}

    -- 
    local valid_flag = false

    -- 
    local btn_index = 1
    for _, v in ipairs(self.block_config) do
        if v:is_valid(block_info, block_level, card_id, is_out, block_index) then
            local btn_node = nil
            btn_node = button('btn_block_' .. btn_index, function()
                v:onclick(btn_node, block_info, block_level, card_id, is_out, block_index)
            end, self.csb_node)

            btn_node:loadTextureNormal(v.sprite_file, ccui.TextureResType.localType)
            btn_node:setVisible(true)

            if v.anim_file then
                local btn_size = btn_node:getContentSize()

                local anim_node = createAnimNode(v.anim_file)
                anim_node:setPosition(btn_size.width * 0.5 + v.anim_offset.x, btn_size.height * 0.5 + v.anim_offset.y)
                btn_node:getRendererNormal():addChild(anim_node)

                table.insert(self.all_anim_nodes, anim_node)
            end

            btn_index = btn_index + 1
            valid_flag = true
        end
    end

    self.csb_node:setVisible(valid_flag)
end

return on_block
