# coding:utf-8
import random
import logging
logger = logging.getLogger('role')

from protocol import poem_pb
import protocol.poem_pb as msgid
from yy.rpc import RpcService, rpcmethod
from yy.message.header import success_msg, fail_msg
from yy.entity.base import EntityExistsException
from yy.entity.index import DuplicateIndexException
from yy.utils import trie
from session.sessstore import SessionStore
from user.model import User
from player.model import Player, PlayernameIndexing, PlayerLevelRanking
from player.model import PlayerDuplicateNamesIndexing
from common import msgTips, get_session_pool
from config.configs import NameprefixEConfig, NameprefixFConfig, MalenameConfig, FemalenameConfig
from config.configs import forbid_names_trie, get_config
from entity.constants import Sex
from i18n import _YYTEXT
import settings

MAXIDVALUE = 2147483647
NAME_LENGTH_MAX = 7
NAME_LENGTH_MIN = 2

def validate_name(name):
    name = name.strip()
    uname = unicode(name)
    if not uname:
        return uname, msgTips.FAIL_MSG_LOGIN_PLAYERNAME_ISEMPTY
    if len(uname) > NAME_LENGTH_MAX:
        return uname, msgTips.FAIL_MSG_NAME_TOOLONG_TO_CREATE
    if len(uname) < NAME_LENGTH_MIN:
        return uname, msgTips.FAIL_MSG_NAME_TOOSHORT_TO_CREATE
    if trie.trie_contains(forbid_names_trie, uname):
        return uname, msgTips.FAIL_MSG_LOGIN_PLAYERNAME_FORBIDDEN
    return name, 0

def get_names_by_sex(sex, count=10):
    prefix_e = get_config(NameprefixEConfig)
    prefix_f = get_config(NameprefixFConfig)
    if sex == Sex.Male:
        cfgs = get_config(MalenameConfig)
    else:
        cfgs = get_config(FemalenameConfig)
    names = set()
    while len(names) < count:
        name = ""
        for each in [prefix_e, prefix_f, cfgs]:
            i = random.randint(1, len(each))
            name += each[i].name
        names.add(name)
    return list(names)


class RoleService(RpcService):
    access_limited_message = '''服务器已满。 [endl:num=1]
您在队列中的位置：%d[endl:num=1]
估计等待时间：%d秒'''

    def access_limited(self):
        from player.manager import g_playerManager
        if g_playerManager.count() < settings.MAX_ONLINES:
            return False, ''
        import random
        rancount = random.randint(600, 800)
        rantime = rancount / 18
        # self.peer.sender(fail_msg(msgtype, code=1000))
        return True, _YYTEXT(self.access_limited_message % (rancount, rantime))

    @rpcmethod(msgid.LOGIN_WORLD)
    def login(self, msgtype, body):
        limited, message = self.access_limited()
        if limited:
            return fail_msg(msgtype, reason=message)
        req = poem_pb.LoginWorldRequest()
        req.ParseFromString(body)
        if not req.verify_code:
            logger.error(
                'invalid verify_code %s, body %r', req.verify_code, body)
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        session = SessionStore(get_session_pool(), str(req.verify_code))
        if not req.userID or session.uid != req.userID:
            return fail_msg(msgtype, reason="登录超时，请重试")
        self.userID = req.userID
        # get role list
        user = User.load(self.userID)
        rsp = poem_pb.LoginWorldResponse()
        entityIDs = user.roles.get(settings.REGION['ID'])
        if not entityIDs:
            return success_msg(msgtype, rsp)
        #  if len(entityIDs) == 1:
        #      entityID = entityIDs[0]
        #  else:
        #      entityID = req.entityID
        if not req.entityID:
            entityID = min(entityIDs)
        else:
            entityID = req.entityID
        rsp.roles.add(id=entityID)
        rsp.need_rename = PlayerDuplicateNamesIndexing.exists(entityID)
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ALTER_ACTOR_NAME)
    def alter_name(self, msgtype, body):
        limited, message = self.access_limited()
        if limited:
            return fail_msg(msgtype, reason=message)
        req = poem_pb.AlterNameRequest()
        req.ParseFromString(body)
        entityID = req.entityID
        if not entityID:
            user = User.load(self.userID)
            entityIDs = user.roles.get(settings.REGION['ID'])
            if len(entityIDs) > 1:
                return fail_msg(msgtype, reason="未指定角色")
            if entityIDs:
                entityID = entityIDs[0]
        if not PlayerDuplicateNamesIndexing.exists(entityID):
            return fail_msg(msgtype, reason="不可修改名称")
        session = SessionStore(get_session_pool(), str(req.verify_code))
        if not req.userID or session.uid != req.userID:
            return fail_msg(msgtype, reason="登录超时，请重试")
        name, error = validate_name(req.name)
        if error:
            return fail_msg(msgtype, error)
        # 名字去重复
        try:
            PlayernameIndexing.register(0, name)  # 占位
            p = Player.simple_load(entityID, ["name"])
            p.name = name
            p.save()
            PlayernameIndexing.pool.execute(
                'HSET', PlayernameIndexing.key, name, entityID)  # 更新
        except DuplicateIndexException:
            return fail_msg(msgtype, reason=_YYTEXT('该名称已存在'))
        PlayerDuplicateNamesIndexing.unregister(entityID)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.RANDOM_ACTOR_NAME)
    def random_name(self, msgtype, body):
        limited, message = self.access_limited()
        if limited:
            return fail_msg(msgtype, reason=message)
        req = poem_pb.RandomNameRequest()
        req.ParseFromString(body)
        rsp = poem_pb.RandomNameResponse()
        names = get_names_by_sex(Sex.Male)
        for name in names:
            rsp.names.append(name)
        namefemales = get_names_by_sex(Sex.Female)
        for name in namefemales:
            rsp.namefemales.append(name)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.NEW_ACTOR)
    def create_role(self, msgtype, body):
        limited, message = self.access_limited()
        if limited:
            return fail_msg(msgtype, reason=message)
        req = poem_pb.CreateRoleRequest()
        req.ParseFromString(body)
        modelID = req.iconID
        user = User.load(self.userID)
        roleID = user.roles.get(settings.REGION['ID'])
        if roleID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_ALREADY_CREATEROLE)
        name, error = validate_name(req.name)
        if error:
            return fail_msg(msgtype, error)

        # 名字去重复
        try:
            PlayernameIndexing.register(0, name)  # 占位
            player = Player.create(name=name, modelID=modelID, sex=req.sex, level=1, career=req.school)
            player.save()
            PlayernameIndexing.pool.execute('HSET', PlayernameIndexing.key, name, player.entityID)  # 更新
        except DuplicateIndexException:
            return fail_msg(msgtype, reason=_YYTEXT('该名称已存在'))
        except EntityExistsException:  # 已经存在的entityID, 一般由于自增ID被清零，但entityID数据还存在
            return fail_msg(msgtype, reason=_YYTEXT('该名称已存在'))
        if not player or not player.entityID:
            PlayernameIndexing.unregister(name)
            return fail_msg(msgtype, reason=_YYTEXT('该名称已存在'))
        PlayerLevelRanking.update_score(player.entityID, player.level)
        user.roles[settings.REGION['ID']] = player.entityID
        user.save()
        rsp = poem_pb.CreateRoleResponse()
        rsp.roleId = player.entityID
        role = rsp.roles.add()
        role.name, role.level, role.resourceId, role.school, role.sex = \
            player.name, player.level, player.modelID, player.career, player.sex

        from common.log import gm_logger
        gm_logger.info({'createrole': {'entityID': player.entityID,
                                       'userID': self.userID,
                                       'type': 'createrole',
                                       'username': player.username,
                                       'playername': player.name,
                                       'worldID': settings.SESSION['ID'],
                                       'createrolename': player.name,
                                       'career': player.career,
                                       'username_alias': user.username_alias}})
        role.id = rsp.roleId
        return success_msg(msgtype, rsp)
