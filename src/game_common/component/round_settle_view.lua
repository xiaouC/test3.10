-- ./app/platform/game/game_common/round_settle_view.lua
require 'app.platform.game.game_common.game_component_base'

----------------------------------------------------------------------------------------------------------
local RoundSettleView = class('RoundSettleView', view_component_base)
function RoundSettleView:ctor(game_scene)
    view_component_base.ctor(self, game_scene)
end

function RoundSettleView:init(args)
    view_component_base.init(self)

    -- 
    self.game_result_draw_sprite_file = args.draw_sprite_file

    --
    registerAnimationRange('anim_fan_ma', 'anim_zhong_ma_%d.png', 1, 5, 0.3/4)
    registerAnimationIndices('mopai', 'draw_card_hand_%d.png', { 1, 1, 2, 2, 2, 3, 4 }, 1.0/7)

    -- 断线重连回来
    -- 如果有小局结算界面，则什么也不做
    -- 如果没有小局结算界面，则需要有个按钮，让玩家可以继续游戏
    self:listenGameSignal('reconn_no_ready', function()
        if self.csb_node or self.csb_reconn_no_ready_node then return end

        -- 
        self.csb_reconn_no_ready_node = cc.CSLoader:createNode('mahjong/settle_round/reconn_no_ready.csb')
        self.csb_reconn_no_ready_node:setPosition(display.width * 0.5, 90)
        self.game_scene:addChild(self.csb_reconn_no_ready_node, GAME_VIEW_Z_ORDER.ROUND_SETTLE)

        button('btn_continue', function()
            self.game_scene:restart()

            self.csb_reconn_no_ready_node:removeFromParent(true)
            self.csb_reconn_no_ready_node = nil
        end, self.csb_reconn_no_ready_node)
    end)

    -- 小局结算
    self:listenGameSignal('round_settle', function(result_info) self:on_round_settle(result_info) end)
end

function RoundSettleView:on_touch_began(touch, event)
    if self.csb_node then
        for index, v in pairs(self.user_click_nodes or {}) do
            local pos = v[1]:convertToNodeSpace(touch:getLocation())
            if self.round_settle_data[index] and cc.rectContainsPoint(self.click_rect, pos) then
                self:setCurSel(index)

                break
            end
        end
    end

    return view_component_base.on_touch_began(self, touch, event)
end

function RoundSettleView:get_score(server_index, result_info)
    return result_info.m_win_score[server_index]
end

function RoundSettleView:get_special_status(server_index, result_info) return '' end
function RoundSettleView:get_line_simple_1(server_index, result_info) return '' end
function RoundSettleView:get_line_simple_2(server_index, result_info) return '' end
function RoundSettleView:get_line_simple_3(server_index, result_info) return '' end

function RoundSettleView:get_block_cards(server_index, result_info)
    -- 如果服务器没有下发的话，就用客户端记录下来的数据
    if not result_info.m_block_info or not result_info.m_block_info[server_index] then
        return self.game_scene.block_cards[server_index]
    end

    -- 
    local block_cards = {}

    local user_block_info = result_info.m_block_info[server_index]
    for _, block_info in ipairs(user_block_info) do
        if block_info.m_block_type == 0x01 or block_info.m_block_type == 0x02 or block_info.m_block_type == 0x04 then
            local card_ids = { block_info.m_block_data[1], block_info.m_block_data[2], block_info.m_block_data[3] }

            if block_info.m_block_type == 0x04 then table.insert(card_ids, block_info.m_block_data[4]) end

            table.insert(block_cards, card_ids)
        end
    end

    return block_cards
end

function RoundSettleView:get_hand_cards(server_index, result_info)
    local card_list = result_info.m_hand_card[server_index] or {}

    local hand_cards = {}
    for _, card_id in pairs(card_list) do
        if card_id > 0 then
            table.insert(hand_cards, card_id)
        end
    end

    return hand_cards
end

function RoundSettleView:get_card_data(server_index, result_info)
    -- local card_data = {
    --     block_cards = { { 1, 1, 1 }, { 2, 2, 2, 2 }, },
    --     hand_cards = { 3, 4, 5, 6, 7, 8, 9 },
    --     win_card = 9,
    --     ghost_card_ids = {},
    --     additional_reward = {
    --         text_1 = '一张定码：',
    --         text_2 = '码',
    --         cards = { 17, 18, 19 },
    --         num = 3,
    --     },
    -- }

    return {
        block_cards = self:get_block_cards(server_index, result_info),
        hand_cards = self:get_hand_cards(server_index, result_info),
        win_card = result_info.m_win[server_index] and result_info.m_win_card or nil,
        ghost_card_ids = self.game_scene.really_card_ids,
        additional_reward = nil,
    }
end

-- local line_detail = {
--     {
--         text_1 = '胡牌分：',
--         text_2 = '+18',
--     },
--     {
--         text_1 = '底分：',
--         text_2 = '+1',
--     },
--     {
--         text_1 = '七对：',
--         text_2 = '+1',
--     },
--     {
--         text_1 = '抓五魁：',
--         text_2 = '+1',
--     },
-- }
-- return line_detail
function RoundSettleView:get_line_detail_1(server_index, result_info) return {} end
function RoundSettleView:get_line_detail_2(server_index, result_info) return {} end
function RoundSettleView:get_line_detail_3(server_index, result_info) return {} end

function RoundSettleView:parseResultInfo(result_info)
    local round_settle_data = {}

    for server_index=1, 4 do
        local location_index = self.game_scene.server_index_to_local_index[server_index]

        local user_info = self.game_scene.all_user_info[server_index]
        if user_info then
            local line_detail_1 = self:get_line_detail_1(server_index, result_info)
            local line_detail_2 = self:get_line_detail_2(server_index, result_info)
            local line_detail_3 = self:get_line_detail_3(server_index, result_info)
            local user_data = {
                head_id = user_info.m_bLogoID or 0,
                head_url = user_info.m_headurl,
                user_name = user_info.m_nickName,
                is_banker = self.game_scene.banker_server_index == server_index,
                ticket = result_info.m_reward_gift[server_index] or 0,
                score = self:get_score(server_index, result_info),
                special_status = self:get_special_status(server_index, result_info),
                is_win = result_info.m_win[server_index],
                line_simple_1 = self:get_line_simple_1(server_index, result_info),
                line_simple_2 = self:get_line_simple_2(server_index, result_info),
                line_simple_3 = self:get_line_simple_3(server_index, result_info),
                card_data = self:get_card_data(server_index, result_info),
                line_detail = { line_detail_1, line_detail_2, line_detail_3 },
            }

            round_settle_data[location_index] = user_data
        end
    end

    return round_settle_data
end

function RoundSettleView:hasZhongMa(result_info)
    if result_info.m_luck_card and result_info.m_luck_card[1] ~= 0 then
        return true
    end

    return false
end

function RoundSettleView:showZhongMaView(result_info, callback_func)
    if self.game_scene.game_rule.m_luck_mode > 0 and not result_info.m_all_king then
        local card_id, num = self:getMoMaCardID(result_info)
        self:showMoMaAnim(card_id, function()
            self:showFanMaAnim({ card_list = { card_id }, num = num }, false, callback_func)
        end)
    else
        self:showFanMaAnim(self:getFanMaCardData(result_info), true, callback_func)
    end
end

function RoundSettleView:getMoMaTitleText(result_info)
    if self.game_scene.game_rule.m_luck_mode ~= 2 then
        return '一张定马'
    end

    return '一马全中'
end

function RoundSettleView:getMoMaCardID(result_info)
    local card_id = result_info.m_luck_card[1]

    local num = 0
    for server_index=1, 4 do
        if result_info.m_win[server_index] then
            num = result_info.m_user_luck_count[server_index]

            break
        end
    end

    return card_id, num
end

function RoundSettleView:showMoMaAnim(card_id, callback_func)
    local mopai_bg = cc.Sprite:create('mahjong/component/roll_dice/roll_dice_background.png')
    mopai_bg:setPosition(display.width * 0.5, display.height * 0.5)
    self.game_scene:addChild(mopai_bg, GAME_VIEW_Z_ORDER.ROUND_SETTLE)

    local bg_size = mopai_bg:getContentSize()

    -- 
    local title_sprite = cc.Sprite:createWithSpriteFrameName('flop_background_title.png')
    title_sprite:setPosition(bg_size.width * 0.5 + 5, bg_size.height - 25)
    mopai_bg:addChild(title_sprite)

    -- 
    local text_label = cc.Label:createWithTTF(self:getMoMaTitleText(result_info), 'font/jxk.TTF', 60)
    text_label:setColorTextureIndex(10)
    text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    text_label:setPosition(bg_size.width * 0.5 - 10, bg_size.height - 15)
    text_label:enableShadow(cc.c4b(0, 0, 0, 255), cc.size(0, -5), 2)
    mopai_bg:addChild(text_label)

    -- 
    local node = cc.Node:create()
    node:setPosition(50, 100)
    mopai_bg:addChild(node)

    local mopai_hand_bg = cc.Sprite:createWithSpriteFrameName('draw_card_hand_5.png')
    mopai_hand_bg:setPosition(262, 162)
    node:addChild(mopai_hand_bg, 92)

    local card = create_card_sprite(card_id)
    card:setPosition(237, 212)
    card:setScale(0.7)
    card:setRotation(-40)
    node:addChild(card, 93)

    local mopai_hand = cc.Sprite:createWithSpriteFrameName('draw_card_hand_1.png')
    mopai_hand:setPosition(262, 162)
    node:addChild(mopai_hand, 94)

    local action_1 = cc.Animate:create(cc.AnimationCache:getInstance():getAnimation('mopai'))
    local action_2 = cc.DelayTime:create(0.8)
    local action_3 = cc.CallFunc:create(function()
        mopai_bg:removeFromParent(true)
        if callback_func then callback_func() end
    end)
    mopai_hand:runAction(cc.Sequence:create(action_1, action_2, action_3))
end

function RoundSettleView:getFanMaTitleText(result_info) return '奖码' end
function RoundSettleView:getFanMaLeftTopText(result_info) return '中马数：' end
function RoundSettleView:getFanMaRepeatCardText(result_info) return '余牌不足，尾牌重复记马' end

function RoundSettleView:getFanMaCardData(result_info)
    local card_list = {}
    for _, card_id in ipairs(result_info.m_luck_card) do
        if card_id > 0 then table.insert(card_list, card_id) end
    end

    return {
        -- card_list = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 17, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, },
        -- card_list = { 1, 2, 3, 4, 5, 6, 7, 8, 9, },
        -- card_list = { 1, 2 },
        -- repeated_count = 2,
        card_list = card_list,
        repeated_count = nil,
    }
end

function RoundSettleView:showFanMaAnim(card_data, anim_flag, callback_func)
    local node_zhong_ma = cc.Node:create()
    node_zhong_ma:setPosition(display.width * 0.5, display.height * 0.5)
    self.game_scene:addChild(node_zhong_ma, GAME_VIEW_Z_ORDER.ROUND_SETTLE)

    -- background
    local iv_background = ccui.ImageView:create('zha_ma_background.png', ccui.TextureResType.plistType)
    iv_background:setAnchorPoint(0.5, 0.5)
    iv_background:setScale9Enabled(true)
    iv_background:setCapInsets(cc.rect(25, 25, 5, 5))
    node_zhong_ma:addChild(iv_background)

    local card_count = #card_data.card_list
    local card_width, card_height = 92, 110

    local bg_width, border_width = 1150, 60
    if card_count < 12 then
        bg_width = card_count * card_width + border_width
        if bg_width < 560 then
            bg_width = 560
        end
    end

    -- 
    local row_count = math.floor((card_count - 1) / 12)
    if card_data.repeated_count then
        local col = math.floor((card_count - 1) % 12)
        if col ~= 0 then
            row_count = row_count + 1
        end
    end

    local row_height = 120
    local bg_height = 260 + row_count * row_height
    iv_background:setContentSize(cc.size(bg_width, bg_height))

    local top_y = bg_height * 0.5

    -- title background
    local title_sprite = cc.Sprite:createWithSpriteFrameName('flop_background_title.png')
    title_sprite:setPosition(0, top_y)
    node_zhong_ma:addChild(title_sprite)

    -- title text
    local text_label = cc.Label:createWithTTF(self:getFanMaTitleText(result_info), 'font/jxk.TTF', 60)
    text_label:setColorTextureIndex(10)
    text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    text_label:setPosition(-10, top_y)
    text_label:enableShadow(cc.c4b(0, 0, 0, 255), cc.size(0, -5), 2)
    node_zhong_ma:addChild(text_label)

    local function __show_ma_count__(x, y)
        local left_top_bg_sprite = cc.Sprite:create('mahjong/component/round_settle/zhong_ma_num_bg.png')
        left_top_bg_sprite:setPosition(x + 100, y)
        node_zhong_ma:addChild(left_top_bg_sprite)

        -- 
        local text_label = cc.Label:createWithTTF(self:getFanMaLeftTopText(result_info), 'font/jxk.TTF', 30)
        text_label:setColorTextureIndex(10)
        text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
        text_label:setAnchorPoint(0, 0.5)
        text_label:setPosition(x, y)
        text_label:enableShadow(cc.c4b(0, 0, 0, 255), cc.size(0, -2), 2)
        node_zhong_ma:addChild(text_label)
    end

    -- 中码数
    local total_count = 0
    if not anim_flag then total_count = card_data.num end

    -- 
    local row_count = math.floor((card_count - 1) / 12) + 1
    --local offset_x = -card_width * (row_count > 1 and 12 or card_count) * 0.5 + card_width * 0.5
    local offset_x = -bg_width * 0.5 + card_width * 0.5 + border_width * 0.5
    local offset_y = top_y - card_height * 0.5 - 60
    for index, card_id in ipairs(card_data.card_list) do
        play_mahjong_effect('award_card')

        local row = math.floor((index - 1) / 12)
        local col = math.floor((index - 1) % 12)

        local card_bg_sprite = cc.Sprite:createWithSpriteFrameName(anim_flag and 'anim_zhong_ma_1.png' or 'anim_zhong_ma_5.png' )
        card_bg_sprite:setPosition(offset_x + card_width * col, offset_y - row * row_height)
        node_zhong_ma:addChild(card_bg_sprite)

        local is_valid = true
        if anim_flag then
            is_valid = ((card_id % 16 == 1) or (card_id % 16 == 5) or (card_id % 16 == 9))
            if is_valid then
                total_count = total_count + 1

                -- 
                if card_data.repeated_count and index == card_count then
                    total_count = total_count + card_data.repeated_count - 1
                end
            end
        else
            is_valid = true
        end

        -- 如果最后一个是重复奖码的话，就换一行显示
        -- 当然，也必须不是在第一列
        if card_data.repeated_count and index == card_count then
            local x, y = offset_x, offset_y - row * row_height
            if col ~= 0 then y = offset_y - (row + 1) * row_height end

            card_bg_sprite:setPosition(x, y)

            -- 
            local repeated_card_text = self:getFanMaRepeatCardText(result_info)

            -- 
            local repeated_count_label = cc.Label:createWithTTF('X' .. card_data.repeated_count .. '　' .. repeated_card_text, 'font/jxk.TTF', 30)
            repeated_count_label:setColorTextureIndex(10)
            repeated_count_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
            repeated_count_label:setPosition(x + card_width * 0.5, y)
            repeated_count_label:setAnchorPoint(0, 0.5)
            repeated_count_label:enableShadow(cc.c4b(0, 0, 0, 255), cc.size(0, -2), 2)
            node_zhong_ma:addChild(repeated_count_label)
        end

        local function __card_show__()
            local card_sprite = create_card_sprite(card_id)
            card_sprite:setPosition(73, 85)
            card_sprite:setScale(0.9)
            card_bg_sprite:addChild(card_sprite)

            if not is_valid then
                card_sprite:setColor(cc.c3b(125, 125, 125))
                card_bg_sprite:setColor(cc.c3b(125, 125, 125))
            end

            -- 
            if index == 1 then
                local show_ma_x, show_ma_y = -100, 50 - bg_height * 0.5
                __show_ma_count__(show_ma_x, show_ma_y)

                -- 
                self.game_scene:schedule_once_time(0.3, function()
                    -- 中码数
                    local count_label = cc.LabelAtlas:_create(tostring(total_count), 'game_common_res/settle_count_1.png', 26, 30, string.byte('/'))
                    count_label:setPosition(show_ma_x + 150, show_ma_y)
                    count_label:setAnchorPoint(0, 0.5)
                    count_label:setScale(8)
                    node_zhong_ma:addChild(count_label)

                    local action_scale = cc.ScaleTo:create(0.1, 1)
                    local action_cb = cc.CallFunc:create(function()
                        self.game_scene:schedule_once_time(1.0, function()
                            node_zhong_ma:removeFromParent(true)
                            if callback_func then callback_func() end
                        end)
                    end)
                    count_label:runAction(cc.Sequence:create(action_scale, action_cb))
                end)
            end
        end

        if anim_flag then
            local action_1 = cc.DelayTime:create(0.3)
            local action_2 = cc.Animate:create(cc.AnimationCache:getInstance():getAnimation('anim_fan_ma'))
            local action_3 = cc.CallFunc:create(__card_show__)
            card_bg_sprite:runAction(cc.Sequence:create(action_1, action_2, action_3))
        else
            __card_show__()
        end
    end
end

function RoundSettleView:on_round_settle(result_info)
    -- 如果有中码的话，就展示一下中码的界面
    -- 没有就直接打开结算面板
    if self:hasZhongMa(result_info) then
        self:showZhongMaView(result_info, function()
            self:showRoundSettleDetailView(result_info)
        end)
    else
        self:showRoundSettleDetailView(result_info)
    end
end

function RoundSettleView:showRoundSettleDetailView(result_info)
    if self.csb_node then return end

    -- 
    self.round_settle_data = self:parseResultInfo(result_info)

    -- 
    self.csb_node = cc.CSLoader:createNode('mahjong/settle_round/settle_round.csb')
    self.csb_node:setPosition(display.width * 0.5, display.height * 0.5)
    self.game_scene:addChild(self.csb_node, GAME_VIEW_Z_ORDER.ROUND_SETTLE)

    -- look over
    self.node_content = self.csb_node:getChildByName('node_content')
    button('btn_look_over', function() self.node_content:setVisible(not self.node_content:isVisible()) end, self.csb_node)

    -- button continue
    local btn_continue = button('btn_continue', function()
        if self.game_scene.is_replay then return self.game_scene:onExitGame() end

        -- 
        self.csb_node:removeFromParent(true)
        self.csb_node = nil

        if self.game_scene.cur_play_count == self.game_scene.total_play_count then
            self.game_scene:tryToShowFinalSettle()
        else
            self.game_scene:restart()
        end
    end, self.node_content)

    -- 
    if self.game_scene.cur_play_count == self.game_scene.total_play_count then
        btn_continue:setTitleText('查看战绩')
    end

    if self.game_scene.is_replay then btn_continue:setTitleText('退出游戏') end

    --
    local click_width, click_height = 288, 257
    self.click_rect = { x = -click_width * 0.5, y = -click_height * 0.5, width = click_width, height = click_height }
    self.node_effect = self.node_content:getChildByName('node_effect')
    self.cur_sel_index = -1
    self.user_click_nodes = {}

    local win_index = nil

    local location_file_name = { 'location_self.png', 'location_right.png', 'location_facing.png', 'location_left.png' }
    for index=1, 4 do
        local node_user = self.node_content:getChildByName('node_user_' .. index)

        -- 
        local data = self.round_settle_data[index]
        if data then
            if data.is_win then win_index = index end

            local effect = data.is_win and string.format('mahjong/settle_round/win_effect_%d.csb', index) or string.format('mahjong/settle_round/lose_effect_%d.csb', index)
            self.user_click_nodes[index] = { node_user, nil, effect }

            local sprite_user_bg = node_user:getChildByName('settle_round_bg')
            sprite_user_bg:setColorTextureIndex(data.is_win and 7 or 8)
            sprite_user_bg:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_sprite'))

            node_user:getChildByName('banker_flag'):setVisible(data.is_banker and true or false)

            -- 
            local sprite_location = node_user:getChildByName('location_sprite')
            sprite_location:setSpriteFrame(location_file_name[index])

            node_user:getChildByName('node_head'):addChild(createUserHeadSprite{
                m_bLogoID = data.head_id,
                m_headurl = data.head_url,
            })
            local node_user_name = node_user:getChildByName('text_user_name')
            node_user_name:setColor(data.is_win and cc.c3b(123, 58, 5) or cc.WHITE)
            node_user_name:setString(data.user_name)

            if data.ticket and data.ticket > 0 then
                local node_ticket = node_user:getChildByName('node_ticket')
                node_ticket:setVisible(true)

                node_ticket:getChildByName('al_reward_ticket'):setString(tostring(data.ticket))
            end
            node_user:getChildByName('text_line_1'):setString(data.line_simple_1 or '')
            node_user:getChildByName('text_line_2'):setString(data.line_simple_2 or '')
            node_user:getChildByName('text_line_3'):setString(data.line_simple_3 or '')

            -- 
            if data.special_status then
                local node_special_status = node_user:getChildByName('node_special_status')

                local ss_label = cc.Label:createWithTTF(data.special_status, 'res/font/jxk.TTF', 30)
                ss_label:setColorTextureIndex(9)
                ss_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
                ss_label:setAnchorPoint(0.5, 0.5)
                ss_label:setColor(cc.WHITE)
                ss_label:setAdditionalKerning(-5)
                ss_label:enableOutline(cc.c3b(83, 30, 11), 2)

                local count = ss_label:getStringLength()
                local ss_black_width = 25
                local start_x = -ss_black_width * count * 0.5
                for i=0, count - 1 do
                    local ss_sprite = cc.Sprite:createWithSpriteFrameName(string.format('black_%d.png', math.random(1, 2)))
                    ss_sprite:setRotation(math.random(0, 360))
                    ss_sprite:setScale(1.1)
                    ss_sprite:setPosition(start_x + i * ss_black_width + 0.5 * ss_black_width, 0)
                    node_special_status:addChild(ss_sprite)
                end

                node_special_status:addChild(ss_label)
            end

            -- score
            local file_name = (data.score >= 0 and 'mahjong/settle_round/score_2.png' or 'mahjong/settle_round/score_1.png')
            local text_score = string.format('%s%d', data.score >= 0 and '.' or '/', math.abs(data.score))
            local score_label = cc.LabelAtlas:_create(text_score, file_name, 28, 34, string.byte('.'))
            score_label:setAnchorPoint(0.5, 0.5)
            node_user:getChildByName('node_score'):addChild(score_label)
        else
            local sprite_user_bg = node_user:getChildByName('settle_round_bg')
            sprite_user_bg:setColorTextureIndex(8)
            sprite_user_bg:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_sprite'))

            node_user:getChildByName('location_sprite'):setVisible(false)
            node_user:getChildByName('banker_flag'):setVisible(false)
            node_user:getChildByName('head_frame'):setVisible(false)

            node_user:getChildByName('text_line_1'):setString('')
            node_user:getChildByName('text_line_2'):setString('')
            node_user:getChildByName('text_line_3'):setString('')
            node_user:getChildByName('text_user_name'):setString('')
        end
    end

    -- 
    self.layer_color_line_win_1, self.layer_color_line_win_2 = nil, nil
    self.layer_color_line_lose_1, self.layer_color_line_lose_2 = nil, nil
    self.rich_text_label = { { x= -500, y = -145 }, { x= -500, y = -185 }, { x= -500, y = -225 } }   -- 3 line

    -- 
    self.bg_sprite = self.node_content:getChildByName('settle_round_bg_2')
    self.bg_sprite:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_sprite'))

    self:setCurSel(win_index or 1)

    -- 流局/荒庄/
    if not win_index then
        self.csb_node:getChildByName('node_result_draw'):addChild(cc.Sprite:create(self.game_result_draw_sprite_file))
    end
end

function RoundSettleView:setCurSel(index)
    if self.cur_sel_index ~= index then
        if self.user_click_nodes[self.cur_sel_index] then
            if self.user_click_nodes[self.cur_sel_index][2] then
                self.user_click_nodes[self.cur_sel_index][2]:setVisible(false)
            end
        end

        local v = self.user_click_nodes[index]
        if v then
            if not v[2] then
                v[2] = cc.CSLoader:createNode(v[3])
                self.node_effect:addChild(v[2])
            end

            v[2]:setVisible(true)
        end

        -- 
        local data = self.round_settle_data[index]
        self.bg_sprite:setColorTextureIndex(data.is_win and 7 or 8)

        self.cur_sel_index = index

        self:updateDetail()
    end
end

function RoundSettleView:updateDetail()
    if not self.layer_color_line_win_1 then
        local line_width, line_height = 1000, 1

        self.layer_color_line_win_1 = cc.LayerColor:create(cc.c4b(182, 151, 88, 255), line_width, line_height)
        self.layer_color_line_win_1:setPosition(-500, -190)
        self.node_content:addChild(self.layer_color_line_win_1)

        self.layer_color_line_win_2 = cc.LayerColor:create(cc.c4b(182, 151, 88, 255), line_width, line_height)
        self.layer_color_line_win_2:setPosition(-500, -150)
        self.node_content:addChild(self.layer_color_line_win_2)

        self.layer_color_line_lose_1 = cc.LayerColor:create(cc.c4b(41, 108, 122, 255), line_width, line_height)
        self.layer_color_line_lose_1:setPosition(-500, -190)
        self.node_content:addChild(self.layer_color_line_lose_1)

        self.layer_color_line_lose_2 = cc.LayerColor:create(cc.c4b(41, 108, 122, 255), line_width, line_height)
        self.layer_color_line_lose_2:setPosition(-500, -150)
        self.node_content:addChild(self.layer_color_line_lose_2)
    end

    -- 
    local data = self.round_settle_data[self.cur_sel_index]
    self.layer_color_line_win_1:setVisible(data.is_win)
    self.layer_color_line_win_2:setVisible(data.is_win)
    self.layer_color_line_lose_1:setVisible(not data.is_win)
    self.layer_color_line_lose_2:setVisible(not data.is_win)

    -- 
    self:updateCards(data)

    -- 3 lines
    local font_name, font_size = 'font/fzzyjt.ttf', 26
    local text_color = (data.is_win and cc.c3b(255, 234, 0) or cc.c3b(109, 255, 253))
    local function __init_line__(index)
        local rt = self.rich_text_label[index]

        -- create
        if not rt.line_label then
            rt.line_label = ccui.RichText:create()
            rt.line_label:ignoreContentAdaptWithSize(false);
            rt.line_label:setSize(cc.size(1050, 30));
            rt.line_label:setPosition(rt.x, rt.y)
            rt.line_label:setAnchorPoint(0, 0)
            self.node_content:addChild(rt.line_label)
        end

        -- clear
        for _, re in ipairs(rt.re_list or {}) do
            rt.line_label:removeElement(re)
        end
        rt.re_list = {}

        -- init re
        if data.line_detail then
            for _, v in ipairs(data.line_detail[index] or {}) do
                local rich_ele_1 = ccui.RichElementText:create(0, cc.WHITE, 255, v.text_1 .. '　', font_name, font_size)
                rt.line_label:pushBackElement(rich_ele_1)

                table.insert(rt.re_list, rich_ele_1)

                if v.text_2 then
                    local rich_ele_2 = ccui.RichElementText:create(0, text_color, 255, v.text_2 .. '　　', font_name, font_size)
                    rt.line_label:pushBackElement(rich_ele_2)

                    table.insert(rt.re_list, rich_ele_2)
                end
            end
        end
    end

    __init_line__(1)
    __init_line__(2)
    __init_line__(3)
end

function RoundSettleView:updateCards(data)
    local node_cards = self.node_content:getChildByName('node_cards')
    node_cards:removeAllChildren()

    -- 
    local next_x, next_y = -350, 0
    local interval_x = 20

    -- block cards
    local block_scale = 0.6
    local block_card_width = 64 * block_scale
    local kong_offset_y = 23 * block_scale
    for _, v in ipairs(data.card_data.block_cards or {}) do
        for i, card_id in ipairs(v) do
            local x, y = next_x, next_y

            local offset_y = ((#v == 4 and i == 3) and kong_offset_y or 0)
            if #v == 4 and i == 3 then
            else
                next_x = next_x + block_card_width
            end

            local card = create_card_front(USER_LOCATION_SELF, CARD_AREA.TAN, card_id)
            card:setPosition(next_x, next_y + offset_y)
            card:setScale(block_scale)
            node_cards:addChild(card, i == 3 and 1 or 0)
        end

        next_x = next_x + interval_x
    end

    -- hand cards
    local hand_scale = 0.6
    local hand_card_width = 85 * hand_scale

    next_x = next_x + hand_card_width

    for _, card_id in ipairs(data.card_data.hand_cards or {}) do
        local card = create_card_front(USER_LOCATION_SELF, CARD_AREA.HAND, card_id)
        card:setPosition(next_x, next_y)
        card:setScale(hand_scale)
        node_cards:addChild(card)

        if self.game_scene:is_ghost_card(card_id) then
            card:addChild(self.game_scene:createGhostSubscript(USER_LOCATION_SELF, CARD_AREA.HAND))
        end

        next_x = next_x + hand_card_width
    end

    next_x = next_x + hand_card_width * 0.5
    if data.card_data.win_card then
        local card = create_card_front(USER_LOCATION_SELF, CARD_AREA.HAND, data.card_data.win_card)
        card:setPosition(next_x, next_y)
        card:setScale(hand_scale)
        node_cards:addChild(card)

        card:addChild(self.game_scene:createWinSubscript(USER_LOCATION_SELF, CARD_AREA.HAND))
    end

    -- additional reward
    local node_additional_reward_1 = self.node_content:getChildByName('node_additional_reward_1')
    node_additional_reward_1:removeAllChildren()

    local node_additional_reward_2 = self.node_content:getChildByName('node_additional_reward_2')
    node_additional_reward_2:removeAllChildren()

    if data.card_data.additional_reward then
        local text_label = cc.Label:createWithTTF(data.card_data.additional_reward.text_1, 'font/jxk.TTF', 30)
        text_label:setColorTextureIndex(11)
        text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
        text_label:setPosition(0, 0)
        text_label:enableOutline(cc.c3b(0, 0, 0), 3)
        text_label:enableShadow(cc.c4b(0, 0, 0, 255), cc.size(0, -4), 2)
        node_additional_reward_1:addChild(text_label)


        -- 
        local card_scale = 0.5
        local card_width = 85 * card_scale
        local text_size = text_label:getContentSize()
        local card_offset_x = text_size.width * 0.5 + card_width * 0.5 + 10

        for index, card_id in ipairs(data.card_data.additional_reward.cards or {}) do
            --local is_valid = ((card_id % 16 == 1) or (card_id % 16 == 5) or (card_id % 16 == 9))
            --if card_id > 0 and is_valid then
            if card_id > 0 then
                local card = create_card_front(USER_LOCATION_SELF, CARD_AREA.HAND, card_id)
                card:setPosition(card_offset_x, 0)
                card:setScale(card_scale)
                node_additional_reward_1:addChild(card)

                card_offset_x = card_offset_x + card_width
            end
        end

        --
        local text_label_2 = cc.Label:createWithTTF('共　　' .. data.card_data.additional_reward.text_2, 'font/jxk.TTF', 30)
        text_label_2:setColorTextureIndex(11)
        text_label_2:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
        text_label_2:setAnchorPoint(0, 0.5)
        text_label_2:setPosition(card_offset_x, 0)
        text_label_2:enableOutline(cc.c3b(0, 0, 0), 3)
        text_label_2:enableShadow(cc.c4b(0, 0, 0, 255), cc.size(0, -4), 2)
        node_additional_reward_1:addChild(text_label_2)

        local text_2_size = text_label_2:getContentSize()

        -- 
        local text_count = tostring(data.card_data.additional_reward.num)
        local count_label = cc.LabelAtlas:_create(text_count, 'game_common_res/settle_count_1.png', 26, 30, string.byte('/'))
        count_label:setPosition(card_offset_x + text_2_size.width * 0.5, 0)
        count_label:setAnchorPoint(0.5, 0.5)
        node_additional_reward_1:addChild(count_label)
    end
end

return RoundSettleView
