# coding: utf-8
import time
import logging
logger = logging.getLogger('property')

from yy.message.header import success_msg
from protocol.poem_pb import SyncProperty
import protocol.poem_pb as msgid


def sync_property(role, fields=None):
    '''构造属性同步信息'''
    rsp = SyncProperty()
    rsp.entityID = role.entityID
    rsp.type = SyncProperty.Me

    fields_map = role.__class__.fields
    if fields is None:
        fields = role.__class__.fields_list
    else:
        fields = [fields_map[name] for name in fields]

    now = int(time.time())
    for field in fields:
        if field.sync:
            value = None
            try:
                value = getattr(role, field.name)
                if value is None:
                    continue
                if field.syncTimeout:
                    value -= now
                    if value < 0:
                        value = 0
                try:
                    setattr(rsp.properties, field.name, value)
                except (TypeError, ValueError):
                    setattr(rsp.properties, field.name, int(value))
            except (TypeError, AttributeError, ValueError):
                # NOTE 可能是没定义对应模块的formulas
                logger.error("attribute typeError:%s %s %s %s" % (value, type(value), field.type, field.name))
    logger.debug(rsp)
    return rsp


def sync_property_msg(role, fields=None):
    '构造属性同步的消息'
    rsp = sync_property(role, fields)
    return success_msg(msgid.SYNC_PROPERTY, rsp)
