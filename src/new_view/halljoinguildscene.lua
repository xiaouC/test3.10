require 'app.platform.room.new_view.loading'
local m_clientmain = require 'app.platform.room.clientmain'
local m_def = require 'app.platform.room.module.basicnotifydef'

local HallJoinGuildScene = class("HallJoinGuildScene", function()
    local layer = cc.LayerColor:create(cc.c4b(0,0,0,125))
    return layer
end)


function HallJoinGuildScene:ctor(scene,showtype)
    self.scene = scene
    self.showtype = showtype -- 1 邀请码 公会ID  2 包间ID
    self.guild_id = ""

    self.node = cc.CSLoader:createNode("hall_res/HallJoinGuildScene.csb")
    self:addChild(self.node)
    self.node:setAnchorPoint(1,1)
    self.node:setScale(1)
    self.node:setPosition(display.width,display.height)
    self.node:runAction(cc.EaseBackOut:create(cc.ScaleTo:create(0.5,1,1)))

    local function onTouchBegan(touch, event)
        printf('on HallJoinGuildScene TouchBegan')
        return true
    end

    local listener = cc.EventListenerTouchOneByOne:create()
    listener:setSwallowTouches(true)
    listener:registerScriptHandler(onTouchBegan,cc.Handler.EVENT_TOUCH_BEGAN)
    local eventDispatcher = self:getEventDispatcher()
    eventDispatcher:addEventListenerWithSceneGraphPriority(listener, self)


    local function onNodeEvent(event)
        if event == "enter" then
        elseif event == "exit" then
            m_clientmain:get_instance():get_room_mgr():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_ROOM_EVENT,self)
            m_clientmain:get_instance():get_game_manager():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_GAME_EVENT,self)
        end
    end

    self:registerScriptHandler(onNodeEvent)

    self.Text_tips = nil    --键盘提示语
    self.Text_num = nil     --键盘显示输入的数值
    self.btn_num_0 = nil    --对应键盘0按钮
    self.btn_num = {}       --对应键盘1-9按钮
    self.text_num = {}      --对应键盘1-9数字
    self.btn_delete = nil   --对应删除按钮
    self.num_count = 0      --计算输入多少个数字
    self.num_string = nil   --显示的数字
    self.num_record = {}    --数字记录
    -------------------------------------------公会--------------------
    self.btn_rename = nil   --对应重输按钮
    self.img_search_bg = nil --搜索信息公布底图
    self.user_head = nil    --头像
    self.Text_guildname = nil --公会名称
    self.Text_president = nil --会长名称
    self.btn_join = nil       --加入公会
    -------------------------------------------包间--------------------
    self.btn_join_game = nil    --加入游戏
    self.Text_username = nil    --房主名称
    self.Text_roomid = nil      --房间ID
    -------------------------------------------加入公会并开始游戏------
    self.img_tips_bg = nil      --对话框背景
    self.Text_content = nil     --对话框内容
    self.Text_ps = nil          --对话框提示语
    self.btn_close = nil        --关闭按钮
    self.btn_join_sure = nil    --加入公会并进游戏
    self.Text_title = nil       --加入标题
    --------------------------------------------用户信息--------
    self.login_user_head = nil  --用户头像
    self.login_head_frame = nil --用户头像框
    self.login_userinfo_bg = nil --用户信息背景框
    self.login_user_name = "用户昵称"   --用户昵称
    self.login_user_id = 9527       --用户ID
    ------------------------------------------------------------
    self.inviteuser_flag = false
        
    self.Text_tips = self.node:getChildByName("Text_tips")
    self.Text_num = self.node:getChildByName("Text_num")
    if self.showtype == 1 then
        self.Text_tips:setString("请输入邀请码或公会ID")
    else    
        self.Text_tips:setString("请输入六位包间号")
    end
    self.Text_tips:setVisible(true)
    self.img_search_bg = self.node:getChildByName("img_search_bg")
    self.user_head = self.node:getChildByName("user_head")
    self.Text_guildname = self.node:getChildByName("Text_guildname")
    self.Text_president = self.node:getChildByName("Text_president")
    self.btn_join = self.node:getChildByName("Button_join_guild")     
    self.btn_join_game = self.node:getChildByName("Button_join_game")  
    self.Text_username = self.node:getChildByName("Text_username")  
    self.Text_roomid = self.node:getChildByName("Text_roomid")  
    self.img_tips_bg = self.node:getChildByName("img_tips_bg")  
    self.Text_content = self.node:getChildByName("Text_content")  
    self.Text_ps = self.node:getChildByName("Text_ps")  
    self.btn_close = self.node:getChildByName("Button_close")  
    self.btn_join_sure = self.node:getChildByName("Button_join_sure") 
    self.Text_title =  self.node:getChildByName("Text_title") 

    --self.girl_bg = self.node:getChildByName("girl_bg")
    --self.FileNode_Girl = self.node:getChildByName("FileNode_Girl")  

    self.login_user_head = self.node:getChildByName("login_user_head")
    self.login_head_frame = self.node:getChildByName("login_head_frame")
    self.login_userinfo_bg = self.node:getChildByName("login_userinfo_bg")
    self.login_user_name = self.node:getChildByName("login_user_name")
    self.login_user_id = self.node:getChildByName("login_user_id")
    self.Button_close_all = self.node:getChildByName("Button_close_all")

    -- 
    local btn_join_size = self.btn_join:getContentSize()
    local btn_join_guild_text_label = cc.Label:createWithTTF('加入公会', 'res/font/jxk.TTF', 40)
    btn_join_guild_text_label:setColorTextureIndex(2)
    btn_join_guild_text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    btn_join_guild_text_label:setPosition(btn_join_size.width * 0.5, btn_join_size.height * 0.5 + 10)
    btn_join_guild_text_label:enableOutline(cc.c3b(28, 118, 14), 2)
    btn_join_guild_text_label:enableShadow()
    self.btn_join:getRendererNormal():addChild(btn_join_guild_text_label)

    local btn_join_game_size = self.btn_join:getContentSize()
    local btn_join_game_text_label = cc.Label:createWithTTF('加入游戏', 'res/font/jxk.TTF', 40)
    btn_join_game_text_label:setColorTextureIndex(2)
    btn_join_game_text_label:setGLProgram(cc.GLProgramCache:getInstance():getGLProgram('color_texture_label'))
    btn_join_game_text_label:setPosition(btn_join_game_size.width * 0.5, btn_join_game_size.height * 0.5 + 10)
    btn_join_game_text_label:enableOutline(cc.c3b(28, 118, 14), 2)
    btn_join_game_text_label:enableShadow()
    self.btn_join_game:getRendererNormal():addChild(btn_join_game_text_label)

--    if G_is_close == true then
--        self.girl_bg:setVisible(true) 
--        self.FileNode_Girl:setVisible(false)   
--    else
--        self.girl_bg:setVisible(false) 
--        self.FileNode_Girl:setVisible(true)   
--        local action = self.FileNode_Girl:getActionByTag(self.FileNode_Girl:getTag())
--        action:gotoFrameAndPlay(0,true)
--        action:setTimeSpeed(24/60)
--    end

    self.img_search_bg:setVisible(false)
    self.user_head:setVisible(false)
    self.Text_guildname:setVisible(false)
    self.Text_president:setVisible(false)
    self.btn_join:setVisible(false)
    self.Text_username:setVisible(false)
    self.Text_roomid:setVisible(false)
    self.img_tips_bg:setVisible(false)
    self.Text_content:setVisible(false)
    self.Text_ps:setVisible(false)
    self.Text_title:setVisible(false)
    self.btn_join:addClickEventListener(function ()
            Music:playEffect(GAME_SFX.tapButton)
            self:SendJoinGuildRequest()
        end)
    self.btn_join_game:setVisible(false)
    self.btn_join_game:addClickEventListener(function ()
            Music:playEffect(GAME_SFX.tapButton)
            self.btn_rename:setEnabled(false)
            self:onOpenScene()
        end)
    self.btn_close:setVisible(false)
    self.btn_close:addClickEventListener(function ()
        Music:playEffect(GAME_SFX.tapButton)
        self.btn_rename:setEnabled(true)
        self:onCloseScene()
    end)
    self.btn_join_sure:setVisible(false)
    self.btn_join_sure:addClickEventListener(function ()
        Music:playEffect(GAME_SFX.tapButton)
        self:JoinGuildandJoinGame()
    end)

    
    for i=1,7 do
        self.num_record[i] = nil
    end

    for i=1,9 do
        self.btn_num[i] = self.node:getChildByName("Button_"..i)
        
        local text_x = self.btn_num[i]:getPositionX()
        local text_y = self.btn_num[i]:getPositionY()
        self.text_num[i] = cc.LabelAtlas:_create(tostring(100), "hall_res/common/join_room_num.png", 34, 50, string.byte('0'))
        self.text_num[i]:setAnchorPoint(0.5,0.5)
        self.text_num[i]:setPosition(text_x, text_y)
        self.text_num[i]:setString(tostring(i))
        self.text_num[i]:setScale(1)
        self:addChild(self.text_num[i])
        self.text_num[i]:setVisible(true)

        self.btn_num[i]:addClickEventListener(function ()
            Music:playEffect(GAME_SFX.tapButton)
            self:ClickNum(i)
        end)
        
    end

    self.btn_num_0 = self.node:getChildByName("Button_0")
    self.btn_num_0:addClickEventListener(function ()
            Music:playEffect(GAME_SFX.tapButton)
            self:ClickNum(0)
        end)

    self.btn_delete = self.node:getChildByName("Button_delete")
    self.btn_delete:addClickEventListener(function ()
            Music:playEffect(GAME_SFX.tapButton)
            self:DeleteNum()
        end)

    self.btn_rename = self.node:getChildByName("Button_rename")
    self.btn_rename:addClickEventListener(function ()
            Music:playEffect(GAME_SFX.tapButton)
            self:Rename()
        end)

    self.Button_close_all:addClickEventListener(function ()
            Music:playEffect(GAME_SFX.tapButton)
            self:onClose()
        end)

    m_clientmain:get_instance():get_room_mgr():get_event_mgr():BsAddEventListener(m_def.NOTIFY_ROOM_EVENT,self,handler(self,self.onHallEvent))
    m_clientmain:get_instance():get_game_manager():get_event_mgr():BsAddEventListener(m_def.NOTIFY_GAME_EVENT,self,handler(self,self.onHallEvent))
    
    --self:onShowUserInfo()

    local callback = function ()
        self:onInviteUser() 
    end
    performWithDelay(self,callback,0.1)

end

--没加入公会，点击链接进游戏
function HallJoinGuildScene:onInviteUser()

    local user_desk_no = m_clientmain:get_instance():get_sdk_mgr():get_user_desk_no() 

    if user_desk_no == nil then
        return 
    end

    m_clientmain:get_instance():get_sdk_mgr():set_user_desk_no(nil)

    local desk_no = tostring(user_desk_no)

    local desk_no_num = #desk_no
    if desk_no_num == 6 then   --加入包间
        self.num_count = 6
        self.Text_num:setString(tostring(desk_no))
        self.num_string = string.format(tostring(desk_no))
        self.inviteuser_flag = true
        local callback = function ()
            m_clientmain:get_instance():get_room_mgr():query_guild(tonumber(desk_no))
        end
        performWithDelay(self,callback,0.2)
    elseif desk_no_num == 7 then   --加入公会
        self.num_count = 7
        self.Text_num:setString(tostring(desk_no))
        self.num_string = string.format(tostring(desk_no))
        local callback = function ()
            m_clientmain:get_instance():get_room_mgr():query_guild(tonumber(desk_no))
        end
        performWithDelay(self,callback,0.2)
    end

end

function HallJoinGuildScene:onShowUserInfo()
     local userInfo =  m_clientmain:get_instance():get_user_mgr():get_user_info()

     if userInfo == nil then
        return 
     end
     --头像
     local idx = userInfo.m_icon_id
     --self.login_user_head:setTexture(getUserHead(idx+1))

     local head_id = idx+1
     local url = userInfo.m_headurl--"http://192.168.1.21/46.jpg"
     local head_sprite = NetSprite.new(head_id,url)
     head_sprite:setPosition(50,50)
     self.login_user_head:addChild(head_sprite) 

     --self.login_head_frame
     --self.login_userinfo_bg 
     --昵称
     self.login_user_name:ignoreContentAdaptWithSize(false)
     self.login_user_name:setContentSize(cc.size(120, 22))
     self.login_user_name:setString(userInfo.m_nickname)
     --用户ID
     local string_id = string.format("ID:%d",userInfo.m_uid)
     self.login_user_id:setString(string_id)
end

function HallJoinGuildScene:onCloseScene()
    self.img_tips_bg:setVisible(false)
    self.Text_content:setVisible(false)
    self.Text_ps:setVisible(false)
    self.btn_close:setVisible(false)
    self.btn_join_sure:setVisible(false)
    self.Text_title:setVisible(false)
end

function HallJoinGuildScene:onOpenScene()
    self.img_tips_bg:setVisible(true)
    
    local content_string = string.format("您还未加入公会，是否加入您朋友的公会\"%s\",并进入游戏",self.query_guild_info.m_guild_name)
    self.Text_content:setString(content_string)
    self.Text_content:setVisible(true)
    self.Text_ps:setVisible(true)
    self.btn_close:setVisible(true)
    self.btn_join_sure:setVisible(true)
    self.Text_title:setVisible(true)
end

--加入公会并开始游戏
function HallJoinGuildScene:JoinGuildandJoinGame()
    if self.guild_id ~= nil then
        if #self.guild_id == 6 then
            print("JoinLayer:ClickNum self.num_count == 6  num:"..self.guild_id)
            BASIC_LOG_INFO("xxm: HallJoinGuildScene:JoinGuildandJoinGame ========================")
            BASIC_LOG_INFO("xxm: HallJoinGuildScene:JoinGuildandJoinGame Begin")
            --api_show_loading("JoinGuildandJoinGame")
            new_show_loading()
            m_clientmain:get_instance():get_room_mgr():join_guild(tonumber(self.query_guild_info.m_guild_no))
        end
    end
end


--加入公会请求
function HallJoinGuildScene:SendJoinGuildRequest()
    if self.guild_id ~= nil then
        if #self.guild_id == 7 then
            print("JoinLayer:ClickNum self.num_count == 7  num:"..self.guild_id)
            --api_show_loading("SendJoinGuildRequest")
            new_show_loading()
            m_clientmain:get_instance():get_room_mgr():join_guild(tonumber(self.guild_id))
        end
    end
end

--重新输入数字
function HallJoinGuildScene:Rename()
    self.Text_tips:setVisible(true)    --键盘提示语
    self.Text_num:setString("")
    self.Text_num:setVisible(false)     --键盘显示输入的数值
    self.btn_num_0:setVisible(true)    --对应键盘0按钮
    for i=1,9 do
        self.btn_num[i]:setVisible(true)  --对应键盘1-9按钮
        self.text_num[i]:setVisible(true)
    end
    self.btn_delete:setVisible(true)   --对应删除按钮
    self.num_count = 0                  --计算输入多少个数字
    self.num_string = nil               --显示的数字  
    for i=1,7 do
        self.num_record[i] = nil        --数字记录
    end

    self.btn_rename:setVisible(false)    --对应重输按钮
    self.img_search_bg:setVisible(false)    --搜索结果背景

    self.user_head:setVisible(false)        --公会会长头像
    self.Text_guildname:setVisible(false)   --公会名称
    self.Text_president:setVisible(false)   --公会会长昵称
    self.btn_join:setVisible(false)         --加入按钮

    self.btn_join_game:setVisible(false)    --加入游戏
    self.Text_username:setVisible(false)    --房主名称
    self.Text_roomid:setVisible(false)      --房间ID

end

--显示搜索的公会信息/包间信息
function HallJoinGuildScene:ShowGuildInfo(search_id)

    self.Text_tips:setVisible(false)    --键盘提示语
    self.Text_num:setVisible(true)     --键盘显示输入的数值
    self.btn_num_0:setVisible(false)    --对应键盘0按钮
    for i=1,9 do
        self.btn_num[i]:setVisible(false)  --对应键盘1-9按钮
        self.text_num[i]:setVisible(false)
    end
    self.btn_delete:setVisible(false)   --对应删除按钮
    self.num_count = 0                  --计算输入多少个数字
    self.num_string = nil               --显示的数字  
    for i=1,7 do
        self.num_record[i] = nil        --数字记录
    end

    ---------------------公共---------------------
    self.btn_rename:setVisible(true)    --对应重输按钮
    self.img_search_bg:setVisible(true)    --搜索结果背景
    ---------------------公会---------------------
    if search_id == 1 then
        dump(self.query_guild_info)
        --公会会长头像
        local idx = tonumber(self.query_guild_info.m_guild_icon_id) or 0
        self.user_head:setTexture(getUserHead(idx+1))
        self.user_head:setVisible(true) 

        local head_id = idx+1
        local url = self.query_guild_info.m_head_url--"http://192.168.1.21/46.jpg"
        local head_sprite = NetSprite.new(head_id,url)
        head_sprite:setPosition(50,50)
        --self.head_sprite:setScale()
        self.user_head:addChild(head_sprite)       

        --公会名称
        self.Text_guildname:setString(self.query_guild_info.m_guild_name)
        self.Text_guildname:setVisible(true)   

        --公会会长昵称
        local username_string = string.format("会长: %s",self.query_guild_info.m_guild_nickname)
        self.Text_president:setString(username_string)
        self.Text_president:setVisible(true)   
        self.btn_join:setVisible(true)         --加入按钮

        self.btn_join_game:setVisible(false)    --加入游戏
        self.Text_username:setVisible(false)    --房主名称
        self.Text_roomid:setVisible(false)      --房间ID
    else
        self.Text_president:setVisible(false)   --公会会长昵称
        self.btn_join:setVisible(false)         --加入按钮

        dump(self.query_guild_info)

        --房主头像
        local idx = tonumber(self.query_guild_info.m_icon_id)
        self.user_head:setTexture(getUserHead(idx+1))
        self.user_head:setVisible(true)  

        local head_id = idx+1
        local url = self.query_guild_info.m_head_url--"http://192.168.1.21/46.jpg"
        local head_sprite = NetSprite.new(head_id,url)
        head_sprite:setPosition(50,50)
        --self.head_sprite:setScale()
        self.user_head:addChild(head_sprite)    

        --公会名称   
        self.Text_guildname:setString("包间信息")
        self.Text_guildname:setVisible(true)   
        --房主名称
        local username_string = string.format("好友: %s",self.query_guild_info.m_nickname)--self.query_guild_info.m_nickname)
        self.Text_username:ignoreContentAdaptWithSize(false)
        self.Text_username:setContentSize(cc.size(280, 36))
        self.Text_username:setString(username_string)
        --self.Text_username:setString(username_string)
        self.Text_username:setVisible(true)    
        --房间ID
        local roomid_string = string.format("包间号: %d",self.query_guild_info.m_cardno)
        self.Text_roomid:setString(roomid_string)
        self.Text_roomid:setVisible(true)  
        --加入游戏按钮
        self.btn_join_game:setVisible(true)    
    end
end

--输入数字
function HallJoinGuildScene:ClickNum(click_num)

    self.Text_tips:setVisible(false)

    if self.num_count < 8 then

        if self.num_string == nil then
            self.num_string = string.format("%d",click_num)
        else
            self.num_string = string.format(tostring(self.num_string).."%d",click_num)   
        end

        self.Text_num:setString(tostring(self.num_string))
        self.Text_num:setVisible(true)

        self.num_count = self.num_count + 1

        self.num_record[self.num_count] = tonumber(click_num)

--        if self.num_count == 7 then
--            print("JoinLayer:ClickNum self.num_count == 6  num:"..self.num_string)
--            m_clientmain:get_instance():get_room_mgr():join_guild(tonumber(self.num_string))
--        end

        --搜包间
        if self.num_count == 6 and self.num_record[1] == 9 and self.showtype == 2 then
            print("JoinLayer:ClickNum self.num_count == 6  num:"..self.num_string)
            BASIC_LOG_INFO("xxm: HallJoinGuildScene:ClickNum  Begin ")
            self.guild_id = self.num_string
            m_clientmain:get_instance():get_room_mgr():query_guild(tonumber(self.num_string))
        --搜公会
        elseif self.num_count == 7 and self.showtype == 1 then
            print("JoinLayer:ClickNum self.num_count == 7  num:"..self.num_string)
            self.guild_id = self.num_string
            m_clientmain:get_instance():get_room_mgr():query_guild(tonumber(self.num_string))
        end
    else
        return 
    end
end


--删除数字
function HallJoinGuildScene:DeleteNum()
    
    if self.num_count > 0 then
        self.num_count = self.num_count - 1
    else
        self.Text_tips:setVisible(true)
        return 
    end

    if self.num_count ~= 0 then

        self.num_string = nil
        for i=1,self.num_count do
            if self.num_string == nil then
                if self.num_record[i] ~= nil then
                    self.num_string = string.format("%d",self.num_record[i])
                end
            else
                if self.num_record[i] ~= nil then
                    self.num_string = string.format(tostring(self.num_string).."%d",self.num_record[i])   
                end
            end
        end

        self.Text_num:setString(tostring(self.num_string))
        self.Text_num:setVisible(true)
    else
        self.num_string = nil
        self.Text_num:setVisible(false)
        self.Text_tips:setVisible(true)
    end
end

function HallJoinGuildScene:setMainScene(scene)
  self.scene = scene
end


function HallJoinGuildScene:onHallEvent(event)
    new_hide_loading()
    if nil == event or nil == event.args then
        return
    end

    local param = event.args

    if event.id == m_def.NOTIFY_ROOM_EVENT then
        if(m_def.NOTIFY_ROOM_EVENT_JOIN_GUILD == param.event_id) then
            if(param.event_data.ret == 0) then
                dump(param.event_data)
                --公会搜索进入大厅
                if #self.guild_id == 7 then
                    --api_show_Msg_Box(param.event_data.desc)
                    self:enterHallScene()
                    self:onClose()
                else
                --包间搜索进公会后，查询包间，进入游戏
                --查询包间
                    BASIC_LOG_INFO("xxm: HallJoinGuildScene:onHallEvent NOTIFY_ROOM_EVENT_JOIN_GUILD")
                    BASIC_LOG_INFO("xxm: HallJoinGuildScene:onHallEvent query_desk_info")
                    local ret = m_clientmain:get_instance():get_room_mgr():query_desk_info(tonumber(self.guild_id))      
                end
            else
                dump(param.event_data)
                local userinfo = m_clientmain:get_instance():get_user_mgr():get_user_info()
                local ghid = 0
                if userinfo.m_ghinfo ~= nil then
                    if userinfo.m_ghinfo.m_ghid ~= nil then
                        ghid = tonumber(userinfo.m_ghinfo.m_ghid)    
                    end
                end
                
                local proid = 0
                if userinfo.guild_info ~= nil then
                    if userinfo.guild_info.m_proid ~= nil then
                        ghid = tonumber(userinfo.guild_info.m_proid)   
                    end
                end
                
                if ghid ~= 0 and proid ~= 0 then
                    api_show_Msg_Box("您已加入公会。")
                    self:enterHallScene()
                    self:onClose()
                else
                    api_show_Msg_Box(param.event_data.desc)
                    self:onClose()
                end
                --api_show_Msg_Box("加入公会失败!")

            end
        elseif(m_def.NOTIFY_ROOM_EVENT_QUERY_GUILD == param.event_id) then
            if(param.event_data.ret == 0) then
                dump(param.event_data)
                BASIC_LOG_INFO("xxm: HallJoinGuildScene:onHallEvent NOTIFY_ROOM_EVENT_QUERY_GUILD")
                --搜索公会或包间
                self.query_guild_info = param.event_data.data
                BASIC_LOG_INFO("xxm: m_guild_icon_id("..tostring(self.query_guild_info.m_guild_icon_id)..")")
                BASIC_LOG_INFO("xxm: m_guild_name("..tostring(self.query_guild_info.m_guild_name)..")")
                BASIC_LOG_INFO("xxm: m_guild_nickname("..tostring(self.query_guild_info.m_guild_nickname)..")")
                BASIC_LOG_INFO("xxm: m_guild_no("..tostring(self.query_guild_info.m_guild_no)..")")
                BASIC_LOG_INFO("xxm: m_cardno("..tostring(self.query_guild_info.m_cardno)..")")
                BASIC_LOG_INFO("xxm: m_icon_id("..tostring(self.query_guild_info.m_icon_id)..")")
                --BASIC_LOG_INFO("xxm: m_nickname("..tostring(self.query_guild_info.m_nickname)..")")    

                self.guild_id = self.num_string
                if self.num_count == 6 then
                    self:ShowGuildInfo(2)
                    if self.inviteuser_flag == true then
                        self.inviteuser_flag = false
                        local callback = function ()
                            self:onOpenScene()
                        end
                        performWithDelay(self,callback,0.5)
                    end
                elseif self.num_count == 7 then
                    if self.query_guild_info.m_guild_no ~= nil then
                        self.guild_id = tostring(self.query_guild_info.m_guild_no)
                    end
                    self:ShowGuildInfo(1)
                end
            else
                dump(param.event_data)
                BASIC_LOG_INFO("xxm: HallJoinGuildScene:onHallEvent Error")

                if self.inviteuser_flag == true then
                    self.inviteuser_flag = false
                    self:Rename()
                end

                if param.event_data.ret == -1 then
                    api_show_Msg_Box("业务繁忙，请重试")
                elseif param.event_data.ret == -2 then
                    api_show_Msg_Box("请检查网络连接后再尝试")
                else
                    if self.showtype == 1 then
                        api_show_Msg_Box("您输入的邀请码或公会ID不存在!") 
                    else
                        api_show_Msg_Box("您输入的包间ID不存在!") 
                    end
                end
            end
        elseif(m_def.NOTIFY_ROOM_EVENT_QUERY_DESK == param.event_id) then
            if(param.event_data.ret == 0) then
                --api_show_Msg_Box("包间存在") 
            else

--                    self:enterHallScene()
--                    m_clientmain:get_instance():get_game_manager():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_GAME_EVENT,self)
--                    self:removeFromParent(true)

                --api_show_Msg_Box("您输入的包间ID不存在!")
            end
        elseif(m_def.NOTIFY_ROOM_EVENT_QUERY_ROOM == param.event_id) then
            BASIC_LOG_INFO("xxm: HallJoinGuildScene:onHallEvent NOTIFY_ROOM_EVENT_QUERY_ROOM JoinGame WEB End")
            if(param.event_data.ret == 0) then
                dump(param.event_data.data)
                ----包间搜索进公会后，查询包间，进入游戏
                --进入游戏
                local data = param.event_data.data
                local lack_flag = false

                if data.m_desk_info ~= nil then
                    if data.m_desk_info.m_roomcard_count ~= nil then

                        local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info()
                        if user_info ~= nil then
                            if user_info.m_roomcard ~= nil then
                                if tonumber(user_info.m_roomcard) < tonumber(data.m_desk_info.m_roomcard_count) then
                                    lack_flag = true
                                    api_show_Msg_Box("房卡不足，请充值")
                                    self:enterHallScene()
                                    self:onClose()
                                end
                            end
                        end
                    
                    end
                end
                if lack_flag == false then
                    api_show_loading('------login_wserver--------')
                    new_show_loading()
                    m_clientmain:get_instance():login_wserver(data.m_room_info,data.m_desk_info.m_desk_num,0,data.m_desk_info)
                end
            else
                api_show_Msg_Box("加入包间失败!")
                self:enterHallScene()
                self:onClose()
            end
        elseif(m_def.NOTIFY_ROOM_EVENT_CHECK_GAME_UPDATE == param.event_id) then
            if(param.event_data.ret == 0) then  
                api_hide_loading_ext()
                local  desk_info = param.event_data.data
                self:on_check_game_update(param.event_data.data)
            end
        end
    elseif event.id == m_def.NOTIFY_GAME_EVENT then
        if(m_def.NOTIFY_GAME_EVENT_SETUP_GUILD_SCENE == param.event_id) then 
            --if(param.event_data.result == 0) then
                --用户坐下错误
                BASIC_LOG_INFO("xxm: HallJoinGuildScene:onHallEvent NOTIFY_GAME_EVENT_SETUP_GUILD_SCENE JoinGame ERROR 00")
                --api_show_Msg_Box(param.event_data)
                
                api_hide_loading_ext()
                api_show_Msg_Box("您选择的包间中的好友已开始游戏，邀请你的好友，开始新的游戏吧!")
                BASIC_LOG_INFO("xxm: HallJoinGuildScene:onHallEvent NOTIFY_GAME_EVENT_SETUP_GUILD_SCENE JoinGame ERROR 01")
--                if G_is_close == true then
--                    --local setup_layer = SetupLayerVersion.new(self,2)
--                    local setup_layer = SetupLayerNew.new(self,2)
--                    self:addChild(setup_layer,10,100)
--                else
--                    --local setup_layer = SetupLayer.new(self,2)
--                    local setup_layer = SetupLayerNew.new(self,2)
--                    self:addChild(setup_layer,10,100)
--                end
                BASIC_LOG_INFO("xxm: HallJoinGuildScene:onHallEvent NOTIFY_GAME_EVENT_SETUP_GUILD_SCENE JoinGame ERROR 02")
                self:onClose()
            --end
        end
    end
end

--初始化游戏检测更新信息
function HallJoinGuildScene:on_check_game_update(desk_info)
    --self.m_check_desk_info = desk_info
    local function callback( ... )
        -- body
        --local desk_info = self.m_check_desk_info
        m_clientmain:get_instance():login_wserver(desk_info.m_room_info,desk_info.m_desk_num,0,desk_info)
    end
    local game_id = tonumber(desk_info.m_room_info.m_gameid)

    local game_loading = require("app.platform.room.view.gameloadingnew")
    local game_loading_layer = game_loading.new(self,game_id,callback)
    self:addChild(game_loading_layer,100)  
    return
end

--切换大厅场景
function HallJoinGuildScene:enterHallScene(event)
    --switchScene('app.platform.room.new_view.new_hall_scene')
end

function HallJoinGuildScene:onClose()
    -- 更新一下公会信息吧
    local user_info = m_clientmain:get_instance():get_user_mgr():get_user_info() or {}
    self.scene:updateGuildNameAndID(user_info)

    m_clientmain:get_instance():get_room_mgr():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_ROOM_EVENT,self)
    m_clientmain:get_instance():get_game_manager():get_event_mgr():BsRemoveEventListener(m_def.NOTIFY_GAME_EVENT,self)
    self.scene.Halljoin_layer = nil
    self:removeFromParent(true)
end


return HallJoinGuildScene
