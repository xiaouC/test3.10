-- ./app/platform/room/new_view/hall_update_view.lua
require 'update_config'
require 'app.platform.common.script_api'
g_checkupdate = require 'app.platform.common.checkupdate_api'

local LoginView = class('LoginView', cc.Scene)
function LoginView:ctor()
end

function LoginView:init()
    -- 检查更新
    self:checkUpdate()
    --self:updateComplete()
end

function LoginView:checkUpdate()
    if not g_update_url then
        require 'app.platform.common.basiclog'
        BASIC_LOG_ERROR('g_update_url is nil !!!!!!!!!!!!!!!')

        return self:updateComplete()
    end

    -- 
    self.csb_node = cc.CSLoader:createNode('hall_res/login/update_scene.csb')
    self:addChild(self.csb_node)

    -- 
    local loading_node = cc.CSLoader:createNode('hall_res/common/update_loading.csb')
    loading_node:setPosition(0, -30)
	self.csb_node:getChildByName('login_node'):addChild(loading_node, 10000)

    local big_sprite = loading_node:getChildByName('big_circle')
    big_sprite:runAction(cc.RepeatForever:create(cc.RotateBy:create(0.7, 360)))

    local small_sprite = loading_node:getChildByName('small_circle')
    small_sprite:runAction(cc.RepeatForever:create(cc.RotateBy:create(0.7, -360)))

    local function register_anim_range(anim_name, pattern, range_start, range_stop, delay, loops)
        local anim_frames = {}
        for index=range_start, range_stop do
            local frame_name = string.format(pattern, index)
            local frame = cc.SpriteFrameCache:getInstance():getSpriteFrame(frame_name)
            table.insert(anim_frames, frame)
        end

        local animation = cc.Animation:createWithSpriteFrames(anim_frames, delay or 1.0 / (range_stop - range_start + 1), loops or 1)
        cc.AnimationCache:getInstance():addAnimation(animation, anim_name)
    end

    register_anim_range('loading', 'loading_%02d.png', 1, 36, 0.02)
    local action = cc.Animate:create(cc.AnimationCache:getInstance():getAnimation('loading'))
    loading_node:getChildByName('anim_roll'):runAction(cc.RepeatForever:create(action))

    -- 
    local app_id = g_update_app_id or 1
    local union_id = g_update_union_id or 0
    local game_id = 0
    local version = g_version or 100000001 
    local server_url = g_update_url 
    local app_root = device.writablePath .. Hall_Update_Dir
    local update_root = device.writablePath .. Hall_Back_Dir
    g_checkupdate:get_instance():init_updater(app_id, union_id, game_id, version, server_url, app_root, update_root, "update.xml", "update_plist.xml", g_update_agent_url)

    local update_node, loading_slider, text_node = nil, nil, nil
    local function __init_update_node__()
        -- 把转的那个菊花清理掉
        if loading_node then
            loading_node:removeFromParent(true)
            loading_node = nil
        end

        -- 开始更新
        update_node = cc.CSLoader:createNode('hall_res/login/update_node.csb')
        self.csb_node:getChildByName('login_node'):addChild(update_node)

        loading_slider = update_node:getChildByName('slider_loading')
        local btn_update = update_node:getChildByName('btn_update')
        btn_update:setVisible(false)

        text_node = update_node:getChildByName('text_msg')

        loading_slider:setMaxPercent(100.0)
        loading_slider:setPercent(0)
        loading_slider:setVisible(true)

        local btn_update = update_node:getChildByName('btn_update')
        btn_update:addClickEventListener(function()
            btn_update:setVisible(false)

            loading_slider:setMaxPercent(100.0)
            loading_slider:setPercent(0)
            loading_slider:setVisible(true)
        end)
    end

    g_checkupdate:get_instance():register_notify(function(update_type, update_state, info, param)
        if not tolua.cast(self, 'Node') then return end

        local log_value = tonumber(update_type)
        local log_state = tonumber(update_state)
        print("-------------------------------")
        print(log_value)
        if log_value == 0 then
            -- 状态通知, 2:开始升级, 3:升级配置文件, 4:检测升级列表, 5:下载升级文件, 6:替换文件, 7:升级完成, 8:升级失败
            -- 7 和 8 都可以取消升级进度
            if log_state == 2 then
            elseif log_state == 3 then
                if loading_slider then loading_slider:setPercent(10) end
            elseif log_state == 4 then
            elseif log_state == 5 then
            elseif log_state == 6 then
                if loading_slider then loading_slider:setPercent(95) end
            elseif log_state == 7 then
                print("完成更新！")
                if update_node then
                    loading_slider:setPercent(100)
                    update_node:removeFromParent(true)
                end
                self:updateComplete()
            elseif log_state == 8 then
                --self.msgLab:setString("更新失败！！！")
                self:updateComplete()
            elseif log_state == 100001 then --0: 不需要升级，1 : 正常安装包升级，2 : 强升安装包升级, 3：正常自动升级, 4:强升自动升级
                self.update_ret = tonumber(info)
                print('-------------asfasfasfasfasfas--------------'..self.update_ret)
                if tonumber(self.update_ret) ~= 0 then  --0无更新
                    --self:showUpdateLoading()
                    __init_update_node__()
                    loading_slider:setPercent(5)
                end
            elseif log_state == 100002 then --通知安装
                local path_res = cc.FileUtils:getInstance():getWritablePath()..Hall_Update_Dir.."/res"
                g_checkupdate:get_instance():delete_dir(path_res)
                local path_src = cc.FileUtils:getInstance():getWritablePath()..Hall_Update_Dir.."/src"
                g_checkupdate:get_instance():delete_dir(path_src)
                local file_xml = cc.FileUtils:getInstance():getWritablePath()..Hall_Back_Dir.."/update.xml"
                g_checkupdate:get_instance():delete_file(file_xml)
                local file_xml_cfg = cc.FileUtils:getInstance():getWritablePath()..Hall_Back_Dir.."/update.xml.cfg"
                g_checkupdate:get_instance():delete_file(file_xml_cfg)
                --安装
                g_checkupdate:get_instance():on_notice_install_apk(info)
            end
        elseif log_value == 2 then  --下载进度
            print("---------------####----------------")
            print(log_state)
            local progress = log_state * 80 / 100
            if self.update_ret == 1 then
                text_node:setString(string.format('安装包更新中 %.01f%%', 10 + progress))
            else
                text_node:setString(string.format('资源更新中 %.01f%%',10 + progress))
            end
            print("-###"..progress)
            loading_slider:setPercent(10 + progress)
        end
    end)

    g_checkupdate:get_instance():start_update()
end

function LoginView:updateComplete()
    enterLoginScene()
end

return LoginView
