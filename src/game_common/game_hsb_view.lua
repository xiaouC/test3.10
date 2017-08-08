-- ./app/platform/game/game_common/game_hsb_view.lua

----------------------------------------------------------------------------------------------------------
local game_scene_popup_base = require 'app.platform.game.game_common.game_scene_popup_base'

local game_hsb_view = class('game_hsb_view', game_scene_popup_base)
function game_hsb_view:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.bg_color = cc.c4b(0, 0, 0, 0)
    self.csb_file = 'game_common_res/tablecloth_custom_hsv.csb'
    self.z_order = 10001

    game_scene_popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function game_hsb_view:initViews()
    game_scene_popup_base.initViews(self)

    -- 
    local min_h, max_h = -180, 180
    local min_s, max_s = -100, 100
    local min_b, max_b = -100, 100

    local old_hsb_value = UserData:getHSBValue()
    local new_hsb_value = { h = old_hsb_value.h, s = old_hsb_value.s, b = old_hsb_value.b, index = -1 }
    self.scene_instance:resetTablecloth(new_hsb_value)

    local slider_h = self.csb_node:getChildByName('slider_h')
    local text_input_h = self.csb_node:getChildByName('text_input_h')

    local slider_s = self.csb_node:getChildByName('slider_s')
    local text_input_s = self.csb_node:getChildByName('text_input_s')

    local slider_b = self.csb_node:getChildByName('slider_b')
    local text_input_b = self.csb_node:getChildByName('text_input_b')

    local text_input_keys = {
        ['h'] = function() return text_input_h, slider_h, max_h, min_h end,
        ['s'] = function() return text_input_s, slider_s, max_s, min_s end,
        ['b'] = function() return text_input_b, slider_b, max_b, min_b end,
    }

    local function __is_valid__(index, ch)
        if index == 1 and ch == '-' then return true end
        return tonumber(ch)
    end

    local function __text_input_event__(hsb_key, event_type)
        local text_input_obj, slider_obj, max_value, min_value = text_input_keys[hsb_key]()

        -- 
        local new_value = nil
        if event_type == TEXTFIELD_EVENT_INSERT_TEXT then
            local text = text_input_obj:getString()

            local new_text = ''

            local index = 1
            for c in text:gmatch('.') do
                if __is_valid__(index, c) then
                    new_text = new_text .. c
                end

                index = index + 1
            end

            if new_text ~= text then text_input_obj:setString(new_text) end

            -- 
            new_value = tonumber(new_text) or 0
        end

        if event_type == TEXTFIELD_EVENT_DETACH_WITH_IME or event_type == TEXTFIELD_EVENT_DELETE_BACKWARD then
            new_value = tonumber(text_input_obj:getString()) or 0
        end

        -- 
        if new_value and new_hsb_value[hsb_key] ~= new_value then
            new_hsb_value[hsb_key] = new_value
            if new_hsb_value[hsb_key] >= max_value then new_hsb_value[hsb_key] = max_value end
            if new_hsb_value[hsb_key] <= min_value then new_hsb_value[hsb_key] = min_value end

            slider_obj:setPercent((new_hsb_value[hsb_key] - min_value)/(max_value - min_value) * 100)
            text_input_obj:setString(tostring(new_hsb_value[hsb_key]))

            self:update_hsb_value(new_hsb_value)
        end
    end

    local function __slider_event__(hsb_key, event_type)
        if event_type == ccui.SliderEventType.percentChanged then
            local text_input_obj, slider_obj, max_value, min_value = text_input_keys[hsb_key]()

            new_hsb_value[hsb_key] = slider_obj:getPercent() / slider_obj:getMaxPercent() * (max_value - min_value) + min_value

            text_input_obj:setString(math.floor(new_hsb_value[hsb_key]))

            self:update_hsb_value(new_hsb_value)
        end
    end

    -- h
    text_input_h:setTextHorizontalAlignment(cc.TEXT_ALIGNMENT_CENTER)
    text_input_h:setTextVerticalAlignment(cc.VERTICAL_TEXT_ALIGNMENT_CENTER)
    text_input_h:addEventListener(function(_, event_type) __text_input_event__('h', event_type) end)
    text_input_h:setString(math.floor(old_hsb_value.h))

    slider_h:addEventListener(function(slider, event_type) __slider_event__('h', event_type) end)
    slider_h:setPercent((old_hsb_value.h - min_h)/(max_h - min_h) * 100)

    -- s
    text_input_s:setTextHorizontalAlignment(cc.TEXT_ALIGNMENT_CENTER)
    text_input_s:setTextVerticalAlignment(cc.VERTICAL_TEXT_ALIGNMENT_CENTER)
    text_input_s:addEventListener(function(_, event_type) __text_input_event__('s', event_type) end)
    text_input_s:setString(math.floor(old_hsb_value.s))

    slider_s:addEventListener(function(slider, event_type) __slider_event__('s', event_type) end)
    slider_s:setPercent((old_hsb_value.s - min_s)/(max_s - min_s) * 100)

    -- b
    text_input_b:setTextHorizontalAlignment(cc.TEXT_ALIGNMENT_CENTER)
    text_input_b:setTextVerticalAlignment(cc.VERTICAL_TEXT_ALIGNMENT_CENTER)
    text_input_b:addEventListener(function(_, event_type) __text_input_event__('b', event_type) end)
    text_input_b:setString(math.floor(old_hsb_value.s))

    slider_b:addEventListener(function(slider, event_type) __slider_event__('b', event_type) end)
    slider_b:setPercent((old_hsb_value.b - min_b)/(max_b - min_b) * 100)

    -- 
    button('btn_close', function() self:update_hsb_value(old_hsb_value, true) self:onClose() end, self.csb_node)
    button('btn_confirm', function() self:update_hsb_value(new_hsb_value, true) self:onClose() end, self.csb_node)
    button('btn_default', function()
        new_hsb_value = { h = 0, s = 0, b = 0, index = 1 }

        slider_h:setPercent((new_hsb_value.h - min_h)/(max_h - min_h) * 100)
        slider_s:setPercent((new_hsb_value.s - min_s)/(max_s - min_s) * 100)
        slider_b:setPercent((new_hsb_value.b - min_b)/(max_b - min_b) * 100)
        text_input_h:setString(math.floor(new_hsb_value.h))
        text_input_s:setString(math.floor(new_hsb_value.s))
        text_input_b:setString(math.floor(new_hsb_value.b))

        self:update_hsb_value(new_hsb_value)
    end, self.csb_node)
end

function game_hsb_view:update_hsb_value(hsb_value, save)
    if save then UserData:setHSBValue(hsb_value) end

    local op_config = {
        ['tablecloth'] = function()
            self.scene_instance:resetTablecloth(hsb_value)
        end,
        ['mahjong_card'] = function()
        end,
    }

    op_config[self.args.type]()
end

return game_hsb_view
