# coding:utf-8
import time
import random
import logging
logger = logging.getLogger('session')
from itertools import count
# from datetime import datetime

from yy import utils
from yy.rpc.http import ApplicationError
from yy.entity.base import EntityExistsException
from yy.entity.index import DuplicateIndexException
from yy.entity.storage.redis import make_key
from yy.db.redisscripts import load_redis_script

import settings
from common import msgTips, ClientConfig
from common.log import gm_logger, account_login, account_register, launch
import protocol.poem_pb as msgid
from protocol import poem_pb
from i18n import _YYTEXT
from utils import is_chinese
from utils import unpack_login_info, get_device_id
from user.model import User
from user.model import UsernameIndexing
from player.model import Player
from player.model import PlayerOnlineIndexing
from session.sessstore import SessionStore
from common import get_session_pool
from common.redishelpers import EntityIdentityGenerator

from session.regions import g_whitelist_regions
from session.regions import g_whitelist
from session.regions import g_worlds
from session.regions import g_block_devices
from session.regions import get_loginlimitmsg
from session.regions import get_g_version
from yy.rpc.http import get_random_string

from .app import application as app


class RegisterError(Exception):
    '''注册信息校验失败'''
    pass


GuestIdentityGenerator = EntityIdentityGenerator(
    settings.REDISES["index"], "identity_guest", initial=1000)


def gen_user_info():
    '取时间片加英文字母生成帐号'
    baseKey = 10000000
    sUserName = "Guest%d" % GuestIdentityGenerator.gen()
    passwordKey = random.randint(1, baseKey)
    sPassword = baseKey + passwordKey % baseKey
    return u"%s" % sUserName, u"%d" % sPassword


def register(username, password, imsi):
    '''
    # 注册限制暂不支持
    # f sdks.get(sdkType) and settings.REGISTERLIMIT :
    #    if imsi and not register_imei(imsi):
    #        raise RegisterError(_YYTEXT(u'您今天已注册三个账户，请明天再试。'))
    '''
    if settings.ISUSECLOSESERVERTIME:
        closetime = time.strptime(settings.CLOSEREGTIME, '%Y-%m-%d %H:%M:%S')
        curtime = time.localtime()
        if curtime > closetime:
            raise RegisterError(_YYTEXT(u'服务器维护中，请稍后再试'))

    if is_chinese(username):
        raise RegisterError(_YYTEXT(u'帐号不支持中文，请重新输入'))
    if len(username) < 6:
        raise RegisterError(_YYTEXT(u'该帐号位数不足6位，请重新输入'))
    if password != 'dummy' and len(password) < 6:
        raise RegisterError(_YYTEXT(u'密码位数不足6位，请重新输入'))
    if username.startswith("IOS"):
        raise RegisterError(_YYTEXT(u'帐号不合法，请重新输入'))
    if imsi in g_block_devices:
        raise RegisterError(_YYTEXT(u'该设备已被禁止注册，如有疑问请联系客服'))

    username = username
    if UsernameIndexing.exists(username):
        raise RegisterError(_YYTEXT(u'该帐号已被注册，请重新输入'))

    hashed = utils.make_password(password)
    try:
        UsernameIndexing.register(0, username)  # 先占位
        user = User.create(username=username, password=hashed, imsi=imsi)
        user.save()
        UsernameIndexing.pool.execute(
            'HSET',
            UsernameIndexing.key,
            username,
            user.userID)  # 更新
    except DuplicateIndexException:
        raise RegisterError(_YYTEXT(u'该帐号已被注册，请重新输入'))
    except EntityExistsException:
        UsernameIndexing.unregister(username)
        raise RegisterError(_YYTEXT(u'该帐号已被注册，请重新输入'))
    except Exception as e:
        UsernameIndexing.unregister(username)
        logger.exception('register')
        raise e
    return user


@load_redis_script(pool=Player.pool)
def last_world(roleID, worldID):
    '''\
    local pk      = KEYS[1]
    local k       = ARGV[1]
    local worldID = ARGV[2]
    if tonumber(redis.call('EXISTS', pk)) == 0 then
        return worldID
    elseif tonumber(redis.call("HSETNX", pk, k, worldID)) == 1 then
        return worldID
    else
        return redis.call("HGET", pk, k)
    end\
    '''
    return (make_key(Player.store_tag, roleID), ), ('worldID', worldID)


def route(roleID=None):
    sorted_worlds = sorted(g_worlds.values(), key=lambda w: w.online)
    world = sorted_worlds[0]
    if roleID:
        worldID = int(last_world(roleID, world.id))
        try:
            world = g_worlds[worldID]
        except KeyError:
            PlayerOnlineIndexing.register(world.id, roleID)
    return world


def encode_world(world):
    return poem_pb.World(
        ID=world.id,
        ip=world.ip,
        port=world.port,
        online=world.online,
        mode=world.mode,
    )


@app.rpcmethod(msgid.CREATE_USER)
def create_user(request):
    req = poem_pb.RegisterRequest()
    req.ParseFromString(request.body)
    clientIP = request.env.get('REMOTE_ADDR', '')
    username = req.username
    password = req.password
    # 大小包处理
    try:
        if UsernameIndexing.exists(username):
            raise RegisterError(_YYTEXT(u'该帐号已被注册，请重新输入'))
        user = register(
            username,
            password,
            get_device_id(req.deviceInfo))
    except RegisterError as e:
        raise ApplicationError(0, e.message)

    info = unpack_login_info(
        req.deviceInfo,
        userID=user.userID,
        username=user.username,
        featureCode=req.featureCode,
        clientIP=clientIP)

    info.update({
        'userID': user.userID,
        'username': user.username,
        'type': 'register'})
    gm_logger.info({'sessionaccess': info})
    account_register.info(**info)

    return poem_pb.RegisterResponse(username=user.username)


def do_login(request, uid):
    sid = get_random_string(32)
    # sid = 'test'
    ss = SessionStore(get_session_pool(), sid)
    ss.uid = uid
    ss.save()
    request.sid = sid


def common_login(request, raw_username, req, auto_register=False, check_password=True):
    # 检查版本
    try:
        clientversion = int(getattr(req.deviceInfo, 'clientVersion', 1))
    except ValueError:
        clientversion = 1

    if get_device_id(req.deviceInfo) in g_block_devices:
        raise ApplicationError(0, u"该设备已被禁止登录 如有疑问请联系客服")
    if get_g_version() and clientversion and get_g_version() > clientversion:
        raise ApplicationError(msgTips.FAIL_MSG_LOGIN_OLDVERSION, settings.CLIENTOLDVERSION_NOTICE)

    username = raw_username

    # 检查白名单
    if username not in g_whitelist:
        raise ApplicationError(0,  get_loginlimitmsg())

    # 查找用户
    userID = UsernameIndexing.get_pk(username)
    if userID:
        user = User.get(userID)
        user.load_containers()

        # 检查设备锁定
        if user.lock_device and get_device_id(req.deviceInfo) != user.lock_device:
            raise ApplicationError(0,  u'该帐号为试玩帐号，只能在注册时的使用的设备上登录！')
    else:
        user = None

    clientIP = request.env.get('REMOTE_ADDR', '')
    password = getattr(req, 'password', '') or "dummy"

    if not user and auto_register:
        # register
        try:
            user = register(raw_username, password, get_device_id(req.deviceInfo))
        except RegisterError as e:
            raise ApplicationError(0, e.message)

        # 创建成功
        userID = user.userID
        info = unpack_login_info(req.deviceInfo, userID=userID, username=user.username, featureCode=req.featureCode, clientIP=clientIP)
        info.update({'userID': userID, 'username': user.username, 'type': 'register'})
        gm_logger.info({'sessionaccess': info})
        account_register.info(**info)

    if not user:
        raise ApplicationError(msgTips.FAIL_MSG_LOGIN_WRONG_ACCOUNT)

    # 检查密码
    userID = user.userID
    if check_password:
        hashed = user.password
        if not utils.check_password(password, hashed):
            raise ApplicationError(msgTips.FAIL_MSG_INVALID_PASSWORD)

    # 检查封停
    now = int(time.time())
    if user.blocktime and user.blocktime > now:
        raise ApplicationError(0, u"该账号已被禁止登录 如有疑问请联系客服")
    if user.imsi in g_block_devices:
        raise ApplicationError(0, u"该账号已被禁止登录 如有疑问请联系客服")

    do_login(request, userID)
    user.lastserver = req.regionID
    user.save()

    # log
    info = unpack_login_info(req.deviceInfo, userID=userID, username=user.username, featureCode=req.featureCode, clientIP=clientIP)
    info.update({'userID': userID, 'username': user.username, 'type': 'login'})
    gm_logger.info({'sessionaccess': info})
    account_login.info(**info)

    # 响应
    entityIDs = user.roles.get(req.regionID, [])
    return poem_pb.HTTPLoginResponse(
        userID=userID,
        sdk_username=user.username,
        world=encode_world(route(req.regionID, entityIDs[0] if entityIDs else None)),
        verify_code=request.sid,
    )


@app.rpcmethod(msgid.ACCOUNT_LOGIN)
def account_login(request):
    req = poem_pb.HTTPLoginRequest()
    req.ParseFromString(request.body)

    if req.username == '':
        raise ApplicationError(msgTips.FAIL_MSG_LOGIN_WRONG_ACCOUNT)

    return common_login(request, req.username, req, auto_register=False)


@app.rpcmethod(msgid.QUICK_LOGIN)
def quick_login(request):
    req = poem_pb.HTTPLoginRequest()
    req.ParseFromString(request.body)
    return common_login(request, req.username, req, auto_register=True, check_password=False)


@app.rpcmethod(msgid.WX_LOGIN)
def wx_login(request):
    req = poem_pb.SDKLoginRequest()
    req.ParseFromString(request.body)
    # username = req.uin
    # call sdk http api
    from sdk.client import check_login
    r = check_login(request, req.sdkType, req)

    extra = None
    if isinstance(r, tuple):
        r, extra = r

    if not r:
        raise ApplicationError(msgTips.FAIL_MSG_SDK_LOGIN_FAILED)

    if isinstance(r, (str, unicode)):
        req.uin = r

    rsp = common_login(request, req.uin, req, auto_register=True, check_password=False)
    rsp.extra = extra
    return rsp


@app.rpcmethod(999)
def show_worlds(request):
    return str(g_worlds)



