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
# from yy.entity.storage.redis import make_key
from yy.db.redisscripts import load_redis_script

import settings
from common import msgTips, ClientConfig
from common.log import gm_logger, account_login, account_register, launch
import protocol.poem_pb as msgid
from protocol import poem_pb
from i18n import _YYTEXT
from utils import is_chinese
from utils import sdk_username, unpack_login_info, get_device_id
from user.model import User
from user.model import UsernameIndexing
from player.model import Player
from player.model import PlayerOnlineIndexing
from session.sessstore import SessionStore
from common import get_session_pool
from common.redishelpers import EntityIdentityGenerator

from session.regions import g_whitelist_regions
from session.regions import g_whitelist
from session.regions import g_regions
from session.regions import g_block_devices
from session.regions import get_loginlimitmsg
from session.regions import get_g_version
from yy.rpc.http import get_random_string

from .app import application as app


class RegisterError(Exception):
    '''注册信息校验失败'''
    pass


SAME_SDKS = (poem_pb.SDK_YY, poem_pb.SDK_YYLH)


def gen_user_info():
    '取时间片加英文字母生成帐号'
    baseKey = 10000000
    sUserName = "Guest%d" % GuestIdentityGenerator.gen()
    passwordKey = random.randint(1, baseKey)
    sPassword = baseKey + passwordKey % baseKey
    return u"%s" % sUserName, u"%d" % sPassword

GuestIdentityGenerator = EntityIdentityGenerator(
    settings.REDISES["index"], "identity_guest", initial=1000)


def register(username, password, sdkType, imsi, label="", origin_username="", origin_password="", channel=''):
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

    if sdkType in SAME_SDKS and is_chinese(username):
        raise RegisterError(_YYTEXT(u'帐号不支持中文，请重新输入'))
    if sdkType in SAME_SDKS and len(username) < 6:
        raise RegisterError(_YYTEXT(u'该帐号位数不足6位，请重新输入'))
    if password != 'dummy' and len(password) < 6:
        raise RegisterError(_YYTEXT(u'密码位数不足6位，请重新输入'))
    if username.startswith("IOS"):
        raise RegisterError(_YYTEXT(u'帐号不合法，请重新输入'))
    if imsi in g_block_devices:
        raise RegisterError(_YYTEXT(u'该设备已被禁止注册，如有疑问请联系客服'))

    username = sdk_username(sdkType, username, label=label)
    if UsernameIndexing.exists(username):
        raise RegisterError(_YYTEXT(u'该帐号已被注册，请重新输入'))

    hashed = utils.make_password(password)
    try:
        UsernameIndexing.register(0, username)  # 先占位
        # bind origin user
        if origin_username:
            origin_username = sdk_username(
                sdkType, origin_username, label=label)
            origin_userID = UsernameIndexing.get_pk(origin_username)
            user = User.get(origin_userID)
            if not utils.check_password(origin_password, user.password):
                raise RegisterError(_YYTEXT(u'原帐号密码错误'))
            user.username_alias = username
            user.password = hashed
            user.save()
        else:
            user = User.create(username=username, password=hashed, imsi=imsi, channel=channel)
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


# @load_redis_script(pool=Player.pool)
# def last_world(roleID, worldID):
#     '''\
#     local pk      = KEYS[1]
#     local k       = ARGV[1]
#     local worldID = ARGV[2]
#     if tonumber(redis.call('EXISTS', pk)) == 0 then
#         return worldID
#     elseif tonumber(redis.call("HSETNX", pk, k, worldID)) == 1 then
#         return worldID
#     else
#         return redis.call("HGET", pk, k)
#     end\
#     '''
#     return (make_key(Player.store_tag, roleID), ), ('worldID', worldID)


@load_redis_script(pool=PlayerOnlineIndexing.pool)
def last_world(regionID, roleID, worldID):
    '''
    local key = KEYS[1]
    local member = ARGV[1]
    local value = ARGV[2]
    if tonumber(redis.call("HEXISTS", key, member)) == 0 then
        return value
    elseif tonumber(redis.call("HSETNX", key, member, value)) == 1 then
        return value
    else
        return redis.call("HGET", key, member)
    end\
    '''
    return ("index_p_online{%d}{%d}" % (
        regionID, settings.SESSION["ID"]), ), (roleID, worldID)
    return worldID


def route(regionID, roleID=None):
    region = g_regions[regionID]
    if not region.worlds:
        raise ApplicationError(0,  get_loginlimitmsg())
    sorted_worlds = sorted(region.worlds.values(), key=lambda w: w.online)
    world = sorted_worlds[0]
    if roleID:
        worldID = int(last_world(regionID, roleID, world.id))
        try:
            world = region.worlds[worldID]
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
        if req.sdkType in SAME_SDKS:
            for sdk in SAME_SDKS:
                if sdk == req.sdkType:
                    continue
                un = sdk_username(sdk, username)
                if UsernameIndexing.exists(un):
                    raise RegisterError(_YYTEXT(u'该帐号已被注册，请重新输入'))
        user = register(
            username, password,
            req.sdkType, get_device_id(req.deviceInfo),
            origin_username=req.origin_username,
            origin_password=req.origin_password,
            channel=req.channel)
    except RegisterError as e:
        raise ApplicationError(0, e.message)
    if req.origin_username:  # 旧帐号绑定不计入注册
        pass
    else:
        info = unpack_login_info(
            req.deviceInfo,
            userID=user.userID,
            username=user.username,
            featureCode=req.featureCode,
            clientIP=clientIP,
            channel=req.channel)
        info.update({
            'userID': user.userID,
            'username': user.username,
            'type': 'register'})
        gm_logger.info({'sessionaccess': info})
        account_register.info(**info)
    return poem_pb.RegisterResponse(sdk_username=user.username)


@app.rpcmethod(msgid.AUTO_REGISTER)
def auto_register(request):
    req = poem_pb.AutoRegisterRequest()
    req.ParseFromString(request.body)
    clientIP = request.env.get('REMOTE_ADDR', '')
    username, password = gen_user_info()
    # 大小包处理
    try:
        if req.sdkType in SAME_SDKS:
            for sdk in SAME_SDKS:
                if sdk == req.sdkType:
                    continue
                un = sdk_username(sdk, username)
                if UsernameIndexing.exists(un):
                    raise RegisterError(_YYTEXT(u'该帐号已被注册，请重新输入'))
        user = register(
            username, password, req.sdkType, get_device_id(req.deviceInfo), channel=req.channel)
    except RegisterError as e:
        raise ApplicationError(0, e.message)
    info = unpack_login_info(
        req.deviceInfo,
        userID=user.userID,
        username=user.username,
        featureCode=req.featureCode,
        clientIP=clientIP,
        channel=req.channel)
    info.update({
        'userID': user.userID,
        'username': user.username,
        'type': 'register'})
    gm_logger.info({'sessionaccess': info})
    account_register.info(**info)
    rsp = poem_pb.AutoRegisterResponse(
        username=username,
        sdk_username=user.username, password=password)
    rsp.regionID = 0
    return rsp


def do_login(request, uid):
    sid = get_random_string(32)
    # sid = 'test'
    ss = SessionStore(get_session_pool(), sid)
    ss.uid = uid
    ss.save()
    request.sid = sid


def common_login(
        request, raw_username, req,
        auto_register=False, check_password=True, label=''):
    # 检查版本
    try:
        clientversion = int(getattr(req.deviceInfo, 'clientVersion', 1))
    except ValueError:
        clientversion = 1

    if get_device_id(req.deviceInfo) in g_block_devices:
        raise ApplicationError(0, u"该设备已被禁止登录 如有疑问请联系客服")
    if get_g_version() and clientversion and get_g_version() > clientversion:
        raise ApplicationError(msgTips.FAIL_MSG_LOGIN_OLDVERSION, settings.CLIENTOLDVERSION_NOTICE)

    # 检查屏蔽的sdk
    sdks = settings.DISALLOW_SDKS.get(req.regionID)
    if sdks and req.sdkType in sdks:
        raise ApplicationError(0,  get_loginlimitmsg())

    username = sdk_username(req.sdkType, raw_username, label=label)
    # 大小包处理
    if req.sdkType in SAME_SDKS:
        for sdk in SAME_SDKS:
            un = sdk_username(sdk, raw_username, label=label)
            if UsernameIndexing.exists(un):
                username = un
                break

    # 检查白名单
    if req.regionID in g_whitelist_regions:
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
            user = register(
                raw_username, password, req.sdkType, get_device_id(req.deviceInfo), label=label, channel=getattr(req, "channel", ""))
        except RegisterError as e:
            raise ApplicationError(0, e.message)
        # 创建成功
        userID = user.userID
        info = unpack_login_info(
            req.deviceInfo,
            userID=userID,
            username=user.username,
            featureCode=req.featureCode,
            clientIP=clientIP,
            channel=getattr(req, "channel", ""))
        info.update({
            'userID': userID, 'username': user.username, 'type': 'register'})
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
    info = unpack_login_info(
        req.deviceInfo,
        userID=userID,
        username=user.username,
        featureCode=req.featureCode,
        clientIP=clientIP,
        channel=user.channel)
    info.update({'userID': userID, 'username': user.username, 'type': 'login'})
    gm_logger.info({'sessionaccess': info})
    account_login.info(**info)

    # 响应
    entityIDs = user.roles.get(req.regionID, [])
    if isinstance(entityIDs, int):
        # 兼容旧数据格式
        entityIDs = [entityIDs]
    if len(entityIDs) <= 1:  # 只有一个角色，兼容旧模式，客户端直接登录游戏服
        rsp = poem_pb.HTTPLoginResponse(
            userID=userID,
            sdk_username=user.username,
            world=encode_world(
                route(req.regionID, entityIDs[0] if entityIDs else None)),
            verify_code=request.sid,
        )
    else:
        if entityIDs:
            players = Player.batch_load(
                entityIDs, [
                    'name',
                    'prototypeID',
                    'level',
                    'vip_offline',
                    'last_region_name',
                    'borderID'])
        else:
            players = []
        entityID = min(entityIDs) if entityIDs else None
        rsp = poem_pb.HTTPLoginResponse(
            userID=userID,
            sdk_username=user.username,
            world=encode_world(
                route(req.regionID, entityID)),
            verify_code=request.sid,
            roles=[{
                'entityID': p.entityID,
                'name': p.name,
                'iconID': p.prototypeID,
                'borderID': p.borderID,
                'vip': p.vip_offline,
                'level': p.level,
                'last_region_name': p.last_region_name
            } for p in players if p is not None]
        )
    return rsp


@app.rpcmethod(msgid.SESSION_RECONNECT)
def session_reconnect(request):
    req = poem_pb.SessionReconnect()
    req.ParseFromString(request.body)
    session = SessionStore(get_session_pool(), str(req.verify_code))
    if not req.userID or session.uid != req.userID:
        raise ApplicationError(0, u"登录超时，请重试")
    user = User.get(req.userID)
    if not user:
        logger.debug("wrong userID %d" % req.userID)
        raise ApplicationError(msgTips.FAIL_MSG_INVALID_REQUEST)
    if req.roleID not in user.roles.get(req.regionID, []):
        logger.debug("wrong roleID %d" % req.roleID)
        raise ApplicationError(msgTips.FAIL_MSG_INVALID_REQUEST)
    rsp = poem_pb.SessionReconnectResponse()
    rsp.world = encode_world(route(req.regionID, req.roleID))
    logger.debug("reconnect session")
    return rsp


@app.rpcmethod(msgid.LOGIN)
def login(request):
    req = poem_pb.HTTPLoginRequest()
    req.ParseFromString(request.body)
    return common_login(request, req.username, req, auto_register=False)


@app.rpcmethod(msgid.SDK_CHECK_LOGIN)
def sdk_check_login(request):
    req = poem_pb.SDKLoginRequest()
    req.ParseFromString(request.body)
    # username = req.uin
    label = req.ljsdkInfo.channelLabel or ''
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

    rsp = common_login(request, req.uin,
                       req, auto_register=True,
                       check_password=False, label=label)
    rsp.extra = extra
    return rsp


@app.rpcmethod(msgid.LOGIN_KEY)
def login_key(request):
    req = poem_pb.HTTPLoginRequest()
    req.ParseFromString(request.body)
    if req.username == "":
        raise ApplicationError(msgTips.FAIL_MSG_LOGIN_WRONG_ACCOUNT)

    return common_login(
        request, req.username, req, auto_register=True, check_password=False)


@app.rpcmethod(msgid.CHECK_LAUCH)
def launch_log(request):
    req = poem_pb.CheckUpgrade()
    req.ParseFromString(request.body)
    rsp = poem_pb.CheckUpgradeResponse(isbigupgrade=False)
    rsp.isbigupgrade = False
    clientIP = request.env.get('REMOTE_ADDR', '')
    info = unpack_login_info(
        req.deviceInfo,
        featureCode=req.featureCode,
        clientIP=clientIP)
    launch.info(**info)
    return rsp


@app.rpcmethod(msgid.REGION_LIST)
def region_list(request):
    from session.regions import g_sdks
    from session.regions import g_versions
    from session.utils import sdks as sdk_table
    req = poem_pb.RequestRegionList()
    req.ParseFromString(request.body)
    # 白名单不推荐，id大的在前
    sorted_regions = sorted(
        g_regions.items(),
        key=lambda s: (s[0] not in g_whitelist_regions, s[0]),
        reverse=True)
    version = int(req.deviceInfo.clientVersion or 0)
    sdk = sdk_table.get(req.sdkType, "")
    rsp = poem_pb.RegionList()
    for index, (k, v) in enumerate(sorted_regions):
        # versions
        deny_versions = g_versions.get(k, {}).get("deny_versions", [])
        if version and deny_versions and version in deny_versions:
            continue
        allow_versions = g_versions.get(k, {}).get("allow_versions", [])
        if version and allow_versions and version not in allow_versions:
            continue
        # sdks
        deny_sdks = g_sdks.get(k, {}).get("deny_sdks", [])
        if sdk and deny_sdks and sdk in deny_sdks:
            continue
        allow_sdks = g_sdks.get(k, {}).get("allow_sdks", [])
        if sdk and allow_sdks and sdk not in allow_sdks:
            continue
        if index == 0:  # 第一个显示NEW
            state = poem_pb.Region.NEW
        else:
            if v.total_online > 500:
                state = poem_pb.Region.BUSY
            elif v.id in g_whitelist_regions:
                state = poem_pb.Region.HALT
            else:
                state = poem_pb.Region.BEST
        rsp.regions.add(
            id=k, name=v.name,
            state=state,  # depend on region.total_online
        )
    return rsp


@app.rpcmethod(999)
def show_regions(request):
    return str(g_regions)


@app.rpcmethod(msgid.CHECK_CONFIG)
def check_config(request):
    req = poem_pb.incrementRequest()
    req.ParseFromString(request.body)
    version = req.config_version
    rsp = poem_pb.incrementConfigs()
    for v in count(version + 1):
        data = ClientConfig().get(v)
        if not data:
            break
        config = poem_pb.incrementResponse()
        config.ParseFromString(data)
        rsp.configs.append(config)
    return rsp


@app.rpcmethod(msgid.CHOOSE_ROLE)
def choose_role(request):
    req = poem_pb.HTTPChooseRoleRequest()
    req.ParseFromString(request.body)
    rsp = poem_pb.HTTPChooseRoleResponse()
    # TODO validate entityID and regionID and userID
    rsp.world = encode_world(route(req.regionID, req.roleID))
    rsp.verify_code = request.sid
    rsp.roleID = req.roleID
    return rsp
