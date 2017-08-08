-- ./app/platform/room/new_view/login_account_view.lua

local popup_base = require 'app.platform.common.popup_base'
local LoginAccountView = class('LoginAccountView', popup_base)
function LoginAccountView:ctor(scene_instance, args, show_anim_func, hide_anim_func)
    self.csb_file = 'hall_res/login/account_login.csb'

    popup_base.ctor(self, scene_instance, args, show_anim_func, hide_anim_func)
end

function LoginAccountView:initViews()
    popup_base.initViews(self)

    -- 
    self.account_label = self.csb_node:getChildByName('input_account')
    self.account_label:setString(UserData:getUserName())

    self.password_label = self.csb_node:getChildByName('input_password')
    self.password_label:setString(UserData:getUserPwd())

    button('btn_login', function()
        local account = self.account_label:getString()
        local password = self.password_label:getString()
        self.scene_instance:onLogin(account, password)
    end, self.csb_node)
end

return LoginAccountView
