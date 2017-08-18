# coding: utf-8
import re
import time
import random
import string
from itertools import cycle
from gevent.server import StreamServer
from gevent import Greenlet
from protocol import poem_pb


def start_servers(servs):
    '批量启动服务器'
    servers = []
    for (ip, port), handler in servs:
        serv = StreamServer((ip, port), handler)
        thread = Greenlet.spawn(serv.serve_forever)
        servers.append((serv, thread))
    return servers


def gen_verify_code():
    '取时间 然后随机出一个数'
    baseKey = 65535
    rander = int(time.time())
    randSeep = random.randint(1, baseKey)
    res = randSeep % baseKey
    return rander, str(res)

LETTERS = cycle(string.digits)


def gen_user_info():
    '取时间片加英文字母生成帐号'
    baseKey = 10000000
    sUserName = "Guest" + str(int(time.time())) + LETTERS.next()
    passwordKey = random.randint(1, baseKey)
    sPassword = baseKey + passwordKey % baseKey
    return u"%s" % sUserName, u"%d" % sPassword

# {{{{ 特殊处理的 SDK
sdks = {
    # poem_pb.SDK_ITUNES_STORE: 'APP',
    # poem_pb.SDK_ITUNES_STOREHD: 'APPHD',
}
# }}}
anti_sdks = {}
for name in dir(poem_pb):
    if name.startswith('SDK_') and getattr(
            poem_pb,
            name) not in sdks and name != 'SDK_UNKNOWN':
        sdks[getattr(poem_pb, name)] = name[4:]
        anti_sdks[name[4:]] = getattr(poem_pb, name)


def sdk_username(sdkType, uin, label=""):
    try:
        sdkname = sdks[sdkType]
    except KeyError:
        sdkname = None
    if sdkname:
        try:
            uin = uin.encode("utf-8")
        except UnicodeDecodeError:
            pass
        return 'sdk%s%s_%s' % (str(sdkname), str(label), uin)
    else:
        return uin

sdks_pattern = re.compile(r'(sdk[a-zA-Z0-9]+(?:_IOS)?)_')  # FIXME


def username2sdk(username):
    match = re.match(sdks_pattern, username)
    if match:
        return match.groups()[0]
    return ''


def username2type(username):
    sdk = username2sdk(username)
    type = anti_sdks.get(sdk[3:])
    if not type:
        type = anti_sdks.get(sdk[3:5])
    return type


def username2label(username):
    sdk = username2sdk(username)
    if sdk[3:] in anti_sdks:
        return ""
    return sdk[5:]


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
            ss = SessionStore(
                get_session_pool(),
                req.sid,
            )
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
