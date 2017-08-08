-- ./app/platform/room/new_view/new_create_room_view.lua

local m_clientmain = require 'app.platform.room.clientmain'

local create_room_view_base = require 'app.platform.room.new_view.create_room_view_base'
local new_create_room_view = class('new_create_room_view', create_room_view_base)
function new_create_room_view:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/hall/new_create_room.csb'
    self.z_order = 100

    self.game_list = args
    dump(self.game_list)

    -- 
    create_room_view_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function new_create_room_view:initViews()
    create_room_view_base.initViews(self)

    -- 
    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info() or {}
    label('text_room_card', tostring(user_info.m_roomcard or 0), self.csb_node)

    -- 
    local lv_radio = self.csb_node:getChildByName('lv_radio')
    lv_radio:setScrollBarEnabled(false)

    local rb_group = ccui.RadioButtonGroup:create()
    self.csb_node:addChild(rb_group)

    local function __sort_game_list__(a, b)
        if test_game_id then
            if tonumber(a.value.m_gameid) == test_game_id then return true end
            if tonumber(b.value.m_gameid) == test_game_id then return false end
        end

        local a_push = tonumber(a.value.m_is_push)
        local b_push = tonumber(b.value.m_is_push)
        if a_push == 1 and b_push == 1 then return a.key < b.key end
        if a_push == 1 then return true end
        if b_push == 1 then return false end
        return a.key < b.key
    end

    local cur_selected_game_id = nil
    for index, v in table.orderIter(self.game_list or {}, __sort_game_list__) do
        local rb_widget, rb, text_label = nil, nil, nil
        rb_widget, rb, text_label = createRadioWidget{
            img_normal = 'btn_gameselect_2.png',
            img_selected = 'btn_gameselect_1.png',
            tex_res_type = ccui.TextureResType.plistType,
            text = v.m_gamename,
            text_color = cc.c3b(71, 10, 10),
            font_name = 'font/fzzyjt.ttf',
            font_size = 36,
            enable_outline = false,
            onchanged = function(rb_self, event_type)
                if event_type == ccui.RadioButtonEventType.selected then
                    cur_selected_game_id = tonumber(v.m_gameid)

                    local room_settings = self:getRoomSettings(cur_selected_game_id)
                    self:initSections(room_settings, cur_selected_game_id)
                end
            end
        }
        local size = rb:getContentSize()
        text_label:setPosition(size.width * 0.5 - 20, size.height * 0.5)

        -- 限时免费/即将上线
        if v.m_free_card then
            local flags = { 'limit_free.png', 'coming_soon.png' }
            local flag_file = flags[v.m_free_card]
            if flag_file then
                local limit_free = cc.Sprite:createWithSpriteFrameName(flag_file)
                limit_free:setPosition(114, 86)
                rb:addChild(limit_free)
            end
        end

        rb_group:addRadioButton(rb)
        lv_radio:addChild(rb_widget)

        if not cur_selected_game_id then
            cur_selected_game_id = v.m_gameid

            local room_settings = self:getRoomSettings(cur_selected_game_id)
            self:initSections(room_settings, cur_selected_game_id)
        end
    end
    lv_radio:requestDoLayout()

    button('btn_create', function()
        local room_settings = self:getRoomSettings(cur_selected_game_id)
        local game_id = tonumber(cur_selected_game_id)

        --require 'app.platform.room.new_view.game_update_view'
        dump(self.create_attributes)

        local function __create_room__()
            local max_count = room_settings.max_count
            local desc = room_settings.name
            local card_num = self.create_attributes[room_settings.bottom_section.attr_name]

            m_clientmain:get_instance():get_room_mgr():build_desk(game_id, max_count, desc, self.create_attributes, "", card_num)

            -- 
            self:saveRoomRecord(game_id, self.create_attributes)
        end

        if not G_is_update then
            __create_room__()
        else
            self.scene_instance:popupNode('app.platform.room.new_view.game_update_view', {
                game_id = game_id,
                callback = function(result)
                    if result then
                        __create_room__()
                    else
                        -- show_msg_box_2('游戏更新', '游戏更新失败!!!')
                    end
                end,
            })
        end
    end, self.csb_node)

    button('btn_game_rule', function()
        local room_settings = self:getRoomSettings(cur_selected_game_id)

        -- 
        self.scene_instance:popupNode('app.platform.game.game_common.game_more_view', {
            type = 'RULE_DETAIL',
            rules_config = room_settings.rules_config or {
                {
                    name = '基本玩法',
                    help_contents = { string.format('%s/%d/rule_1.png', g_game_rules_url, cur_selected_game_id) },
                },
                {
                    name = (room_settings.is_poker and '基本牌型' or '基本番型'),
                    help_contents = { string.format('%s/%d/rule_2.png', g_game_rules_url, cur_selected_game_id) },
                },
                {
                    name = '特殊规则',
                    help_contents = { string.format('%s/%d/rule_3.png', g_game_rules_url, cur_selected_game_id) },
                },
                {
                    name = '结算规则',
                    help_contents = { string.format('%s/%d/rule_4.png', g_game_rules_url, cur_selected_game_id) },
                },
            },
        })
    end, self.csb_node)

    button('btn_buy', function() self.scene_instance:bugRoomCard() end, self.csb_node)
end

return new_create_room_view
