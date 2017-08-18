#coding:utf-8
from yy.entity import create_class, define, init_fields
from yy.entity.formulas import register_formula

import ujson as json

extra_imports = '''
'''

mail_fields = init_fields([
    define(0x0001, 'entityID',   'integer',   '邮件ID',   save=True),
    define(0x0002, 'playerID',   'integer',   '玩家ID',   save=True),
    define(0x0003, 'title',      'string',    '邮件标题', save=True),
    define(0x0004, 'content',    'string',    '邮件内容', save=True),
    define(0x0005, 'type',       'integer',   '邮件类型', save=True),
    define(0x0006, 'addtime',    'integer',   '添加时间', save=True),
    define(0x0007, 'addition',   'dict',      '邮件附件', save=True, decoder=json.decode, encoder=json.encode),
    define(0x0008, 'isread',     'boolean',   '是否已读', save=True),
    define(0x0009, 'isreceived', 'boolean',   '是否已领', save=True),
    define(0x000c, 'mailID',     'integer',   '邮件ID',   formula='entityID'),
    define(0x000d, 'limitdata',  'dict',      '用户限制条件', save=True, decoder=json.decode, encoder=json.encode),
    define(0x000e, 'cd',         'integer',   '剩余时间,自动销毁', save=True, default=0),
    define(0x000f, "configID",   "integer",   "配置ID,可能没有", save=True, default=0),
])
store_tag = 'm'
MailBase = create_class('MailBase', mail_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(mail_fields.values(), 'c_MailBase', 'from mail.define import MailBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_mail.pyx'), 'w').write(c)
