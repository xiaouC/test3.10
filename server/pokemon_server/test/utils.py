# coding: utf-8
from yy.utils import load_settings
load_settings()
# import bench_settings as settings
import settings

# import config.loaders # 自动加载配置
# from config.manager import get_config
# from config import configs

from collections import defaultdict
import random
import umysql
import urllib2
from gevent import socket, sleep
from yy.message.header import request_msg
import protocol.poem_pb as msgid
from protocol import poem_pb as world_pb2
from protocol import poem_pb as session_pb2
from protocol import poem_pb as role_pb2
from protocol import poem_pb as guide_pb2
from protocol import poem_pb as sdk_pb2

from expecter import set_expect_sock, expect
from common import msgTips
from yy.utils import DictObject
from gevent import getcurrent
from expecter import ExpectException  # NOQA

players = defaultdict(DictObject)


def set_player(key, player):
    if key not in players:
        players[key] = player


def get_player(key=None):
    if not key:
        key = getcurrent()
    return players.get(key, None)

peers = {}


def set_peer(key, peer):
    assert key not in peers, 'Duplicate set peer'
    peers[key] = peer


def get_peer(key=None):
    if not key:
        key = getcurrent()
    return peers.get(key, None)

NEW_ROLE_GUIDE_ID = 2

ENTER_COUNT = 0


def incr_enter_count():
    global ENTER_COUNT
    ENTER_COUNT += 1


def get_enter_count():
    return ENTER_COUNT


def conn_session():
    return socket.create_connection(settings.SESSION['client'])


def db_cfg(
        host='127.0.0.1',
        port=3306,
        user='poem',
        passwd='poem',
        name=None,
        autocommit=True,
        **kwargs):
    return host, port, user, passwd, name, autocommit


def db_conn(name):
    conn = umysql.Connection()
    conn.connect(*db_cfg(**settings.DATABASES[name]))
    return conn


def login(sock, username, password):
    '登录session'
    sock.sendall(
        request_msg(
            msgid.LOGIN,
            session_pb2.LoginRequest(
                username=username,
                password=password)))
    return expect(msgid.LOGIN, session_pb2.LoginResponse)


def login_key(sock, mid, code=None):
    sock.sendall(
        request_msg(
            msgid.LOGIN_KEY,
            session_pb2.LoginRequest(
                username=mid,
                password=code or '')))
    return expect(msgid.LOGIN_KEY, session_pb2.LoginResponse, allow_error=True)


def login_sdk(sock, uin, sdkType):
    sock.sendall(request_msg(msgid.SDK_CHECK_LOGIN, sdk_pb2.SDKLoginRequest(
        sdkType=sdkType,
        sessionId='',
        uin=uin,
        deviceId='')))
    return expect(msgid.SDK_CHECK_LOGIN, session_pb2.LoginResponse)


def ensure_sdk_login(uin='test_sdk_uin', sdkType=sdk_pb2.SDK_YY):
    sock = conn_session()
    set_expect_sock(sock)
    return login_sdk(sock, uin, sdkType)


def ensure_login(device_id='test_device_id'):
    sock = conn_session()
    set_expect_sock(sock)
    # 创建用户
    rsp = login_key(sock, device_id)
    if isinstance(rsp, int):
        print 'login failed', rsp
        if rsp == msgTips.FAIL_MSG_NOT_ACTIVATED:
            # code = get_activate_code()
            # print 'login with activate code', code
            rsp = login_key(sock, device_id)
    assert not isinstance(rsp, int), 'relogin failed'
    return rsp


def send_http_request(msgid, msg='', parse_cls=None):
    import settings
    host = settings.SESSION['host']
    port = settings.SESSION['port']
    if msg:
        data = msg.SerializeToString()
    else:
        data = msg
    try:
        rsp = urllib2.urlopen(
            "http://{}:{}/{}".format(host, port, msgid), data=data)
    except urllib2.HTTPError as e:
        print 'application error', e.read()
        raise
    raw = rsp.read()
    if not parse_cls:
        return raw
    response = parse_cls()
    response.ParseFromString(raw)
    return response


def ensure_http_login(device_id='test_device_id'):
    import settings
    rsp = send_http_request(
        msgid.LOGIN_KEY,
        session_pb2.HTTPLoginRequest(
            username=device_id,
            regionID=settings.REGION['ID']
        ),
        session_pb2.HTTPLoginResponse
    )
    return rsp

counter = 0


def get_activate_code():
    global counter
    conn = db_conn('user')
    code = conn.query(
        'select code from activate_codes where used=0 limit 1 offset %d' %
        counter,
        ()).rows[0][0]
    counter += 1
    conn.close()
    return code


def login_world(sock, userID, verify_code):
    '登录世界服务器'
    sock.sendall(
        request_msg(
            msgid.LOGIN_WORLD,
            role_pb2.LoginWorldRequest(
                userID=userID,
                verify_code=verify_code)))
    return expect(msgid.LOGIN_WORLD, role_pb2.LoginWorldResponse)


def enter(sock, entityID, newRole):
    '进入世界消息'
    sock.sendall(
        request_msg(
            msgid.ENTER_SCENE,
            world_pb2.EnterRequest(
                entityID=entityID)))
    expect(msgid.ENTER_SCENE)
    incr_enter_count()
    if newRole:
        pass
        # trigger = expect(msgid.GUIDE_TRIGGER, guide_pb2.GuideTrigger).guideId
        # save_guide(sock, trigger)
        # trigger = expect(msgid.GUIDE_TRIGGER, guide_pb2.GuideTrigger).guideId
        # save_guide(sock, trigger)


def expect_prop(tp):
    while True:
        prop = expect(msgid.SYNC_PROPERTY, world_pb2.SyncProperty)
        if prop.type == tp:
            return prop


def expect_monster():
    print 'expect monster'
    return expect_prop(world_pb2.SyncProperty.Monster)

# def expect_npc(tp):
#    print 'expecting npc type', tp
#    while True:
#        prop = expect_prop(world_pb2.SyncProperty.Npc)
#        if prop.properties.npcType & tp:
#            return prop


def expect_me():
    print 'expect me'
    return expect_prop(world_pb2.SyncProperty.Me)


def expect_player():
    return expect_prop(world_pb2.SyncProperty.Player)


def collide_npc(sock, entityID):
    sock.sendall(
        request_msg(
            msgid.COLLIDE_NPC,
            world_pb2.NpcCollideRequest(
                entityID=entityID)))


def request_sync_property(sock):
    sock.sendall(request_msg(msgid.SYNC_PROPERTY))
    return expect(msgid.SYNC_PROPERTY, world_pb2.SyncProperty)


def auto_enter(deviceid='test_device_id'):
    '全自动登录进入世界，返回世界socket'
    rsp = ensure_login(deviceid)
    # rsp = ensure_sdk_login(deviceid)
    assert rsp.servers, '服务器为空'

    # if settings.MODE == 'qq':
    #    ip = settings.SESSION['client'][0]
    # else:
    ip = rsp.servers[0].ip
    sock = socket.create_connection((ip, int(rsp.servers[0].port)))
    set_peer(getcurrent(), sock)
    set_expect_sock(sock)
    rsp = login_world(sock, rsp.verify_code)
    newRole = False
    if not rsp.roles:
        rand_sleep(5, 3)
        from role import create_role
        print 'create role'
        rsp = create_role(
            sock, random.choice([0, 1]), random.choice([1, 2, 3]))
        if isinstance(rsp, int):
            print rsp
            rsp = create_role(
                sock, random.choice([0, 1]), random.choice([1, 2, 3]))
            print 'retry create role'
        roleID = rsp.roleId
        newRole = True
    else:
        roleID = rsp.roles[0].id
    enter(sock, roleID, newRole)
    return sock


def auto_http_enter(deviceid='test_device_id'):
    '全自动登录进入世界，返回世界socket'
    # rand_sleep(10, 3)
    rsp = ensure_http_login(deviceid)
    print rsp
    # rsp = ensure_sdk_login(deviceid)
    assert rsp.world, '服务器为空'

    # if settings.MODE == 'qq':
    #    ip = settings.SESSION['client'][0]
    # else:
    ip = rsp.world.ip
    port = rsp.world.port
    sock = socket.create_connection((ip, int(port)))
    set_peer(getcurrent(), sock)
    set_expect_sock(sock)
    rsp = login_world(sock, rsp.userID, rsp.verify_code)
    newRole = False
    if not rsp.roles:
        from role import create_role
        print 'create role'
        rsp = create_role(
            sock, random.choice([0, 1]), random.choice([1, 2, 3]))
        if isinstance(rsp, int):
            print rsp
            rsp = create_role(
                sock, random.choice([0, 1]), random.choice([1, 2, 3]))
            print 'retry create role'
        elif isinstance(rsp, tuple):
            print rsp
            rsp = create_role(
                sock, random.choice([0, 1]), random.choice([1, 2, 3]))
            print 'retry create role'
        roleID = rsp.roleId
        newRole = True
    else:
        roleID = rsp.roles[0].id
    enter(sock, roleID, newRole)
    return sock


def save_guide(sock, gid):
    sock.sendall(
        request_msg(
            msgid.GUIDE_SAVE,
            guide_pb2.SignGuide(
                guideId=gid)))


def switch_scene(sock, sceneId):
    sock.sendall(
        request_msg(
            msgid.CHANGE_SCENE,
            world_pb2.EnterSceneRequest(
                sceneId=sceneId)))
    return expect_me()


def start_pay(sock, sdkType=sdk_pb2.SDK_YY):
    sock.sendall(
        request_msg(
            msgid.SDK_PAY_START,
            sdk_pb2.SDKStartPayRequest(
                sdkType=sdkType)))
    return expect(msgid.SDK_PAY_START, sdk_pb2.SDKStartPayResponse).serialNo


def rand_sleep(base, alter):
    sleep(random.randrange(base - alter, base + alter))


def is_error(rsp):
    return isinstance(rsp, (int, long))

if __name__ == '__main__':
    sock = auto_enter()
    print start_pay(sock)
