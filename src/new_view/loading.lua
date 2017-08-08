-- ./app/platform/room/new_view/loading.lua

local loading_node = nil
function new_show_loading(tips)
    if not tolua.cast(loading_node, 'Node') then
        loading_node = cc.CSLoader:createNode('hall_res/common/loading.csb')
        loading_node:setPosition(display.width * 0.5, display.height * 0.5)
        cc.Director:getInstance():getRunningScene():addChild(loading_node, 10000)
    end

    local big_sprite = loading_node:getChildByName('big_circle')
    big_sprite:runAction(cc.RepeatForever:create(cc.RotateBy:create(0.7, 360)))

    local small_sprite = loading_node:getChildByName('small_circle')
    small_sprite:runAction(cc.RepeatForever:create(cc.RotateBy:create(0.7, -360)))

    registerAnimationRange('loading', 'loading_%02d.png', 1, 36, 0.2)
    local action = cc.Animate:create(cc.AnimationCache:getInstance():getAnimation('loading'))
    loading_node:getChildByName('anim_roll'):runAction(cc.RepeatForever:create(action))

    loading_node:getChildByName('text_loading'):setString(tips or '')
end

function new_hide_loading()
    if tolua.cast(loading_node, 'Node') then
        loading_node:removeFromParent(true)
        loading_node = nil
    end
end

LOADING_VIEWS = {}

function LOADING_VIEWS.create_loading_node()
    local loading_node = cc.CSLoader:createNode('hall_res/common/update_loading.csb')

    local big_sprite = loading_node:getChildByName('big_circle')
    big_sprite:runAction(cc.RepeatForever:create(cc.RotateBy:create(0.7, 360)))

    local small_sprite = loading_node:getChildByName('small_circle')
    small_sprite:runAction(cc.RepeatForever:create(cc.RotateBy:create(0.7, -360)))

    registerAnimationRange('loading', 'loading_%02d.png', 1, 36, 0.2)
    local action = cc.Animate:create(cc.AnimationCache:getInstance():getAnimation('loading'))
    loading_node:getChildByName('anim_roll'):runAction(cc.RepeatForever:create(action))

    return loading_node
end
