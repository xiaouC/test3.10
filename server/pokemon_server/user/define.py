# coding: utf-8
from yy.entity import create_class, define, init_fields
import ujson as json

extra_imports = '''
'''


def decode_roles(s):
    '兼容旧数据格式'
    o = json.decode(s)
    if isinstance(o, int):
        return [o]
    else:
        return o


user_fields = init_fields([
    define(1, 'userID',     'integer',  '用户ID',             formula="entityID"),
    define(2, 'username',   'string',   '用户名',             save=True, event=True),
    define(3, 'password',   'string',   '密码',               save=True),
    define(4, 'imsi',       'string',   'imsi',               save=True),
    define(5, 'createtime', 'datetime', '创建时间',           save=True),
    # 如果玩家不在线，且这个字段有值，表示上次没有干净退出
    define(6, 'roles',      'stored_dict',  '各区角色ID',  int_key=True, encoder=json.encode, decoder=decode_roles),
    define(7, 'entityID',   'integer',  '用户ID',             save=True),
    define(8, "blocktime",  "integer",  "限制登录时间",       save=True),
    # define(9, "createRoleReward", "integer", "创建下一个角色时奖励", save=True, default=0),
    define(10, "lastserver", "integer", "lastserver", save=True, default=0),
    define(11, "username_alias", "string", "用户名别名", save=True),
    define(12, "lock_device", "string", "锁定登录设备", save=True),
    define(13, "channel", "string", "小渠道名", save=True),
    define(14, "back_reward_received", "boolean", "上次测试充值返现", save=True, default=False),
    define(15, "back_level_reward_received", "boolean", "上次测试等级奖励", save=True, default=False),
])
store_tag = 'u'
UserBase = create_class('UserBase', user_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(user_fields.values(), 'c_UserBase', 'from user.define import UserBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_user.pyx'), 'w').write(c)
