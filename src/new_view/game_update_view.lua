-- ./app/platform/room/new_view/game_update_view.lua

G_Has_Update = false --是否已经更新
G_Update_Game_Id = 0 --更新的游戏ID

local popup_base = require 'app.platform.common.popup_base'
local GameUpdateView = class('GameUpdateView', popup_base)
function GameUpdateView:ctor(model_install, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/login/game_update.csb'
    self.z_order = 10086

    popup_base.ctor(self, model_install, args, show_anim_func, hide_anim_func)
end

function GameUpdateView:initViews()
    popup_base.initViews(self)

    -- button cancel
    self.btn_cancel = button('btn_cancel', function()
        Msg:showMsgBox(1, "您将停止下载游戏", function()
            g_checkupdate:get_instance():stop_update()
            self:onClose()
        end)
    end, self.csb_node)

    -- 
    self.text_tips = label('text_tips', '', self.csb_node)

    self.update_slider = self.csb_node:getChildByName('slider_loading')
    self.update_slider:setMaxPercent(100.0)
    self.update_slider:setPercent(0)
    self.update_slider:setVisible(false)
end

function GameUpdateView:initDataFromServer()
    popup_base.initDataFromServer(self)

    -- 
    if not g_update_url then BASIC_LOG_ERROR('g_update_url is nil !!!!!!!!!!!!!!!') end

    -- 
    api_show_loading_extern(15, '检测资源中...')

    --
    local app_id = g_update_app_id or 1
    local union_id = g_update_union_id or 0
    local game_id = tonumber(self.args.game_id)
    local version = 100000001
    local server_url = g_update_url or ''
    local app_root = device.writablePath .. Game_Update_Dir
    local update_root = device.writablePath .. Game_Back_Dir
    g_checkupdate:get_instance():init_updater(app_id, union_id, game_id, version, server_url, app_root, update_root, "update_"..game_id..".xml", "update_plist_"..game_id..".xml", g_update_agent_url)

    g_checkupdate:get_instance():register_notify(function(update_type, update_state, info, param)
        api_hide_loading_ext()

        local log_value = tonumber(update_type)
        local log_state = tonumber(update_state)
        if log_value == 0 then  --状态通知
            if log_state == 1 then          --1准备升级
                --g_checkupdate:get_instance():set_semaphore(0)
                --等待玩家选择 
            elseif log_state == 2 then          --2:开始升级
                --self:game_update_begin()
                --self:showloadingbg(true)
            elseif log_state == 3 then      --3:升级配置文件
            elseif log_state == 4 then      --4:检测升级列表
            elseif log_state == 5 then      --5:下载升级文件
            elseif log_state == 6 then      --6:替换文件
            elseif log_state == 7 then      --7:升级完成 
                cclog("升级完成************************")

                unload_game_module(self.args.game_id)
                G_Update_Game_Id = self.args.game_id --更新的游戏ID
                if self.args.callback then self.args.callback(true) end
                self:onClose()
            elseif log_state == 8 then      --8:升级失败 
                api_show_Msg_Box('游戏更新失败!!!')
                if self.args.callback then self.args.callback(false) end
                self:onClose()
            elseif log_state == 100001 then      --100001:更新状态值 
                cclog("更新状态值************************")
                dump(info)
                if tonumber(info) ~= 0 then  --0无更新
                    self.btn_cancel:setVisible(true)
                    self.update_slider:setVisible(true)
                end
            end
        elseif log_value == 2 then  --下载进度
            self.update_slider:setPercent(log_state)
            self.text_tips:setString(string.format('更新进度: %.01f%%', log_state))
        end
    end)

    g_checkupdate:get_instance():start_update() 
end

return GameUpdateView
