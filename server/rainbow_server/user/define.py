# coding: utf-8
from yy.entity import create_class, define, init_fields

extra_imports = '''
'''

user_fields = init_fields([
    define(1,   'userID',           'integer',      '用户ID',               save=True),
    define(2,   'username',         'string',       '用户名',               save=True,          event=True),
    define(3,   'password',         'string',       '密码',                 save=True),
    define(4,   'imsi',             'string',       'imsi',                 save=True),
    define(5,   'createtime',       'datetime',     '创建时间',             save=True),
    define(6,   "blocktime",        "integer",      "限制登录时间",         save=True),
    define(7,   "lock_device",      "string",       "锁定登录设备",         save=True),
])
store_tag = 'u'
UserBase = create_class('UserBase', user_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(user_fields.values(), 'c_UserBase', 'from user.define import UserBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_user.pyx'), 'w').write(c)
