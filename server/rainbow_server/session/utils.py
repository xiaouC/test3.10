# coding: utf-8
import re
import time
import random
import string
from gevent.server import StreamServer
from gevent import Greenlet
from protocol import poem_pb


def unpack_login_info(deviceInfo, **kwargs):
    dd = {}
    fields = [
        'os',
        'osVersion',
        'resolution',
        'IMEI',
        'UDID',
        'MAC',
        'UA',
        'clientVersion',
        'idfa',
        'deviceUniqueID',
        'appid']
    for f in fields:
        dd[f] = getattr(deviceInfo, f, '')
    dd.update(kwargs)
    return dd


# 是否中文
zhPattern = re.compile(u'[\u4e00-\u9fa5]+')


def is_chinese(contents):
    checkcontents = contents
    if not isinstance(contents, unicode):
        checkcontents = contents.decode('utf-8')

    match = zhPattern.search(checkcontents)

    if match:
        return True

    return False


def login_required(func):
    from session.sessstore import SessionStore
    from yy.rpc.http import ApplicationError
    from common import get_session_pool

    def wrapper(req):
        if req.sid:
            ss = SessionStore(get_session_pool(), req.sid)
            if not ss.get('uid'):
                raise ApplicationError(0, u"请先登陆")
        else:
            raise ApplicationError(0, u"请先登陆")
        return func(req)
    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    return wrapper


def get_device_id(info):
    return info.idfa or info.MAC or info.UDID or info.IMEI or info.deviceUniqueID
