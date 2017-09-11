-- ./app/platform/game/game_common/final_settle_view.lua
require 'app.platform.game.game_common.game_component_base'

local m_clientmain = import('app.platform.room.clientmain')

----------------------------------------------------------------------------------------------------------
local FinalSettleView = class('FinalSettleView_component', component_base)
function FinalSettleView:init(args)
    component_base.init(self)

    -- 
    self:listenGameSignal('final_settle', function(result_info, user_count)
        self.total_user_count = user_count
        self.dashang_user_ids = {}
        self:conversion_data(result_info)
        self:on_final_settle()
    end)
end

function FinalSettleView:getUserScore(result_info, server_index)
    return tonumber(result_info.m_total_score[server_index])
end

function FinalSettleView:getFinalSettleMoreCount(result_info, server_index)
    return {}
end

function FinalSettleView:conversion_data(result_info)
    -- 
    self.final_settle_data = {
        play_game_count = result_info.m_play_count,
        max_game_count = self.game_scene.total_play_count,
        self_data = {},
        othsers_data = {
            item_csb_file = 'game_common_res/settle/final_settle_item.csb',
            items_margin = 20,
            item_width = 520,
            item_height = 150,
        },
    }

    local max_score = 1     -- 如果都是 0 的，那就没有大赢家
    for server_index=1, 4 do
        local score = tonumber(result_info.m_total_score[server_index])
        if score > max_score then
            max_score = score
        end
    end

    -- 
    for server_index=1, 4 do
        local user_info = self.game_scene.all_user_info[server_index]
        if user_info then
            local user_data = {
                is_homeower = self.game_scene.homeowner_server_index == server_index,
                head_id = user_info.m_bLogoID,
                head_url = user_info.m_headurl,
                user_name = user_info.m_nickName,
                user_id = user_info.m_dwUserID,
                score = self:getUserScore(result_info, server_index),
                ticket = result_info.m_reward_gift[server_index],
                win_count = result_info.m_win_count[server_index],
                is_big_winner = tonumber(result_info.m_total_score[server_index]) == max_score,
            }

            if server_index == self.game_scene.my_server_index then
                self.final_settle_data.self_data = user_data
                self.final_settle_data.self_data.more_count = self:getFinalSettleMoreCount(result_info, server_index) or {}
            else
                table.insert(self.final_settle_data.othsers_data, user_data)
                table.insert(self.dashang_user_ids, user_data.user_id)
            end
        end
    end
end

function FinalSettleView:on_final_settle()
    self.csb_node = cc.CSLoader:createNode('game_common_res/settle/final_settle_view.csb')
    self.csb_node:setPosition(display.width * 0.5, display.height * 0.5)
    self.game_scene:addChild(self.csb_node, GAME_VIEW_Z_ORDER.FINAL_SETTLE)

    --
    local node_content = self.csb_node:getChildByName('node_content')

    -- button close
    button('btn_close', function() self.game_scene:onExitGame() end, node_content)

    local text = string.format('包间号：%d %s %s', self.game_scene.room_id, self.game_scene.scene_config.game_name, os.date('%Y-%m-%d %H:%M', os.time()))
    label('text_room_info', text, self.csb_node)

    ------------------------------------------------------------------------------------------------------------------------------------------------
    local function __create_score_label__(score)
        local file_name = (score >= 0 and 'game_common_res/score_num_inc.png' or 'game_common_res/score_num_dec.png')
        local score_label = cc.LabelAtlas:_create(tostring(math.abs(score)), file_name, 42, 53, string.byte('0'))
        score_label:setAnchorPoint(0.0, 0.5)

        return score_label
    end

    ------------------------------------------------------------------------------------------------------------------------------------------------
    node_content:getChildByName('homeowner_flag'):setVisible(self.final_settle_data.self_data.is_homeower and true or false)
    if self.final_settle_data.self_data.is_big_winner then
        node_content:getChildByName('node_big_winner_flag'):addChild(cc.Sprite:create('game_common_res/settle/big_winner.png'))
    end
    node_content:getChildByName('node_head'):addChild(createUserHeadSprite{
        m_bLogoID = self.final_settle_data.self_data.head_id,
        m_headurl = self.final_settle_data.self_data.head_url,
    })
    node_content:getChildByName('text_user_name'):setString(self.final_settle_data.self_data.user_name)
    if self.final_settle_data.self_data.score >= 0 then node_content:getChildByName('sprite_sign'):setTexture('game_common_res/score_sign_inc.png') end
    node_content:getChildByName('node_score'):addChild(__create_score_label__(self.final_settle_data.self_data.score))
    if self.final_settle_data.self_data.ticket >= 0 then
        local node_reward = node_content:getChildByName('node_reward')
        node_reward:setVisible(true)

        node_reward:getChildByName('al_reward_ticket'):setString(tostring(self.final_settle_data.self_data.ticket))
    end
    node_content:getChildByName('al_game_count'):setString(string.format('%d/%d', self.final_settle_data.play_game_count, self.final_settle_data.max_game_count))
    node_content:getChildByName('al_win_count'):setString(tostring(self.final_settle_data.self_data.win_count))

    -- 
    local p = cc.GLProgramCache:getInstance():getGLProgram('color_texture_label')
    local lv_self_count = node_content:getChildByName('lv_self_count')
    lv_self_count:setScrollBarEnabled(false)
    lv_self_count:setEnabled(false)

    local all_item_widgets = {}
    local total_count = #self.final_settle_data.self_data.more_count
    local offset_x = (total_count > 6 and -100 or 0)

    for index, v in ipairs(self.final_settle_data.self_data.more_count) do
        local r_index = index
        if index > 6 then
            r_index = index - 6
            offset_x = 250
        end

        -- 
        local item_width, item_height = 400, 50

        local item_widget = all_item_widgets[r_index] or ccui.Widget:create()
        item_widget:setContentSize(cc.size(item_width, item_height))
        if r_index == index then
            all_item_widgets[index] = item_widget
            lv_self_count:addChild(item_widget)
        end

        local sprite = createSpriteWithName(v.sprite_file, v.res_type)
        sprite:setAnchorPoint(1, 0.5)
        sprite:setPosition(item_width * 0.5 + offset_x, item_height * 0.5)
        item_widget:addChild(sprite)

        local num_label = cc.LabelAtlas:_create(tostring(v.num), 'game_common_res/settle_count_1.png', 26, 30, string.byte('/'))
        num_label:setAnchorPoint(0, 0.5)
        num_label:setAnchorPoint(0.5, 0.5)
        num_label:setPosition(item_width * 0.5 + offset_x + 50, item_height * 0.5)
        item_widget:addChild(num_label)
    end
    lv_self_count:requestDoLayout()

    ------------------------------------------------------------------------------------------------------------------------------------------------
    local lv_others = node_content:getChildByName('lv_others')
    lv_others:setScrollBarEnabled(false)
    lv_others:setEnabled(false)
    lv_others:setItemsMargin(self.final_settle_data.othsers_data.items_margin)

    local item_width = self.final_settle_data.othsers_data.item_width
    local item_height = self.final_settle_data.othsers_data.item_height

    local function __show_zc__(btn_click, is_zan, onclick)
        local zc_layer = nil

        local item_csb_node = cc.CSLoader:createNode(is_zan and 'game_common_res/settle/zan_list.csb' or 'game_common_res/settle/cai_list.csb')
        for zc_index=1, 4 do
            button('btn_' .. zc_index, function()
                onclick(zc_index)

                zc_layer:removeFromParent(true)
            end, item_csb_node)
        end

        local btn_size = btn_click:getContentSize()
        local pos = btn_click:convertToWorldSpace(cc.p(0, 0))
        item_csb_node:setPosition(pos.x + (is_zan and 194 or -102), pos.y + 20)

        -- 
        zc_layer = createBackgroundLayer(cc.c4b(0, 0, 0, 0), true, nil, nil, function(touch, event)
            zc_layer:removeFromParent(true)
        end)
        cc.Director:getInstance():getRunningScene():addChild(zc_layer, 10000)
        zc_layer:addChild(item_csb_node)
    end

    for index, v in ipairs(self.final_settle_data.othsers_data) do
        local item_csb_node = cc.CSLoader:createNode(self.final_settle_data.othsers_data.item_csb_file)
        item_csb_node:setPosition(item_width * 0.5, item_height * 0.5)

        item_csb_node:getChildByName('homeowner_flag'):setVisible(v.is_homeower and true or false)
        if v.is_big_winner then
            item_csb_node:getChildByName('node_big_winner_flag'):addChild(cc.Sprite:create('game_common_res/settle/big_winner.png'))
        end
        item_csb_node:getChildByName('node_head'):addChild(createUserHeadSprite{
            m_bLogoID = v.head_id,
            m_headurl = v.head_url,
        })
        item_csb_node:getChildByName('text_user_name'):setString(v.user_name)
        item_csb_node:getChildByName('text_user_id'):setString(v.user_id)
        if v.score >= 0 then item_csb_node:getChildByName('sprite_sign'):setTexture('game_common_res/score_sign_inc.png') end
        item_csb_node:getChildByName('node_score'):addChild(__create_score_label__(v.score))
        if v.ticket and v.ticket >= 0 then
            local node_reward = item_csb_node:getChildByName('node_reward')
            node_reward:setVisible(true)

            node_reward:getChildByName('al_reward_ticket'):setString(tostring(v.ticket))
        end

        -- 
        local node_zan = item_csb_node:getChildByName('node_zan')
        local node_cai = item_csb_node:getChildByName('node_cai')

        local btn_zan, btn_cai = nil, nil
        btn_cai = button('btn_cai', function()
            __show_zc__(btn_cai, false, function(click_index)
                m_clientmain:get_instance():get_user_mgr():request_user_discuss_request(click_index + 4, v.user_id)

                btn_zan:setEnabled(false)
                btn_cai:setEnabled(false)
            end)
        end, item_csb_node)

        btn_zan = button('btn_zan', function()
            __show_zc__(btn_zan, true, function(click_index)
                m_clientmain:get_instance():get_user_mgr():request_user_discuss_request(click_index, v.user_id)

                btn_zan:setEnabled(false)
                btn_cai:setEnabled(false)
            end)
        end, item_csb_node)

        -- 
        local item_widget = ccui.Widget:create()
        item_widget:setContentSize(cc.size(item_width, item_height))
        item_widget:addChild(item_csb_node)

        lv_others:addChild(item_widget)

        -- 
        if index ~= #self.final_settle_data.othsers_data then
            local im = ccui.ImageView:create('game_common_res/settle/dividing.png', ccui.TextureResType.localType)
            lv_others:addChild(im)
        end
    end
    lv_others:requestDoLayout()

    ------------------------------------------------------------------------------------------------------------------------------------------
    -- button dashang
    local btn_dashang = nil
    btn_dashang = button('btn_dashang', function()
        local per_count = self.game_scene.game_rule.m_room_card
        local total_count = (self.total_user_count - 1) * per_count
        local content = string.format('是否确认打赏桌上其他玩家，每人%d张，共计%d张房卡？', per_count, total_count)
        show_msg_box_1('打赏房卡', content, function()
            -- self.game_scene:onExitGame()
            btn_dashang:setEnabled(false)

            local desk_info = m_clientmain:get_instance():get_room_mgr():get_desk_info()
            if desk_info then
                m_clientmain:get_instance():get_user_mgr():request_user_award_other(desk_info.m_desk_id, self.dashang_user_ids, per_count)
            end
        end)
    end, node_content)
    local icon_sprite_dashang = cc.Sprite:create('hall_res/hall/common/img_room_bg.png')
    icon_sprite_dashang:setScale(0.8)
    icon_sprite_dashang:setPosition(70, 50)
    btn_dashang:getRendererNormal():addChild(icon_sprite_dashang)

    -- 房卡不足，打赏禁用
    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info()
    if tonumber(user_info.m_roomcard) < self.game_scene.game_rule.m_room_card * 3 then
        btn_dashang:setEnabled(false)
    end

    -- button jixu
    local btn_jixu = button('btn_jixu', function()
        G_is_GameOver = true
        self.game_scene:onExitGame()
    end, node_content)
    local icon_sprite_jixu = cc.Sprite:create('game_common_res/settle/touzi.png')
    icon_sprite_jixu:setPosition(70, 45)
    btn_jixu:getRendererNormal():addChild(icon_sprite_jixu)

    -- button xuanyao
    local node_share = self.csb_node:getChildByName('node_share')
    local btn_xuanyao = button('btn_xuanyao', function() node_share:setVisible(not node_share:isVisible()) end, node_content)
    local icon_sprite_xuanyao = cc.Sprite:create('game_common_res/settle/wechat.png')
    icon_sprite_xuanyao:setPosition(70, 45)
    btn_xuanyao:getRendererNormal():addChild(icon_sprite_xuanyao)

    -- 
    local share_config = {
        {
            index = 0,
            name = '微信',
            node_name = 'wechat',
            sprite_file = 'hall_res/hall/share/result_btn_WX.png',
        },
        {
            index = 1,
            name = '朋友圈',
            node_name = 'friends',
            sprite_file = 'hall_res/hall/share/result_btn_WXfriend.png',
        },
        {
            index = 4,
            name = '支付宝',
            node_name = 'ali',
            sprite_file = 'hall_res/hall/share/result_btn_ZFB.png',
        },
        {
            index = 2,
            name = 'QQ',
            node_name = 'qq',
            sprite_file = 'hall_res/hall/share/result_btn_QQ.png',
        },
        {
            index = 5,
            name = '易信',
            node_name = 'yx',
            sprite_file = 'hall_res/hall/share/result_btn_YX.png',
        },
    }

    for _, v in ipairs(share_config) do
        button('btn_' .. v.node_name, function()
            m_clientmain:get_instance():get_sdk_mgr():share_image_ext("dc_share_image.jpg", v.index)
        end, node_share)
    end
end

return FinalSettleView
