# coding:utf-8
import re
import json
import logging
import sys
import logging.handlers
import settings
SESSION = settings.SESSION
WORLD = settings.WORLD
LOG = settings.LOG
PROJECT = settings.PROJECT
REGION = settings.REGION
from session.utils import username2sdk
from bson import objectid

logger = logging.getLogger('log')


class StreamHandler(logging.StreamHandler):

    def __init__(self, stream=None):
        super(StreamHandler, self).__init__(stream=stream)
        if stream is None:
            stream = sys.stderr
        self.stream = stream

    def flush(self):
        """Flushes the stream."""
        if self.stream and hasattr(self.stream, "flush"):
            self.stream.flush()

    def emit(self, msg):
        fs = "%s\n"
        self.stream.write(fs % msg)
        self.flush()

    def close(self):
        if self.stream:
            self.flush()
            if hasattr(self.stream, "close"):
                self.stream.close()
            self.stream = None


class WatchedFileHandler(logging.handlers.WatchedFileHandler):

    def __init__(self, filename, **kw):
        filename = filename.format(**serverInfo)
        super(WatchedFileHandler, self).__init__(filename, **kw)


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):

    def __init__(self, filename, **kw):
        filename = filename.format(**serverInfo)
        super(TimedRotatingFileHandler, self).__init__(filename, **kw)


class JsonLoggerAdapter(logging.LoggerAdapter):

    ''' 直接encode msg 为 json'''

    def __init__(self, logger, extra=None):
        self.logger = logger
        self.extra = extra

    def process(self, msg, kwargs):
        value = msg.items()[0][1]
        entityID = value.get('entityID')
        if entityID:
            from entity.manager import g_entityManager
            player = g_entityManager.get_player(entityID)
            if player:
                value.update(
                    playername=player.name,
                    username=player.username,
                    channel=player.channel,
                    userID=player.userID,
                    level=player.level,
                    vip=player.vip,
                    totalfp=player.totalfp,
                    fbprocess=player.fbprocess,
                    appid=player.appid,
                    UDID=player.UDID,
                    idfa=player.idfa,
                    IMEI=player.IMEI,
                    MAC=player.MAC,)
            value['worldID'] = REGION['ID']  # WORLD['ID']
        value['sessionID'] = SESSION['ID']
        value['_id'] = str(objectid.ObjectId())
        return json.dumps(msg), kwargs

formatter_pattern = re.compile(r'\%\(([_A-Za-z0-9]+)\)s')


class LongLoggerAdapter(logging.LoggerAdapter):
    # 消费类型
    Gain = 1
    Cost = 2

    def __init__(self, logger, extra=None, skip_error=False, **kwargs):
        if settings.LONGLOG:
            self.prefix = '_'
            self.logger = logger
            self.serverInfo = extra
            self.skip_error = skip_error
            # self.extra = dict(extra) or {}#引用了同一个字典
            self.serverInfo.update(kwargs)
            self.args = re.findall(
                formatter_pattern,
                LOG['formatters'][
                    logger.name]['format'])
            self.args.remove('asctime')

    def info(self, **kwargs):
        if settings.LONGLOG:
            # msg, kwargs = self.process('', kwargs)
            player = kwargs.pop('player', None)
            if not player and self.skip_error:
                # 心跳可能没有玩家实例
                return None
            self.extra = dict(self.serverInfo)
            self.extra.update(kwargs)
            for field in self.args:
                if player and field.startswith(self.prefix):
                    v = getattr(player, field.split(self.prefix, 1)[1], '')
                    if v is None:
                        v = ''
                    self.extra[field] = v
            if self.extra.get('username'):
                self.extra['sdkType'] = username2sdk(self.extra['username'])
            elif self.extra.get('_username'):
                self.extra['sdkType'] = username2sdk(self.extra['_username'])
            itemType = self.extra.get('itemType')
            if itemType:
                self.extra.update(itemType=itemType)
            for field in self.args:
                if field not in self.extra:
                    self.extra[field] = ''
                    # logger.warning('%s is empty in log', field)
            self.logger.info('', extra=self.extra)

    __call__ = info

serverInfo = {
    'sessionID': SESSION['ID'],
    'worldID': REGION['ID'],
    'real_worldID': WORLD["ID"],
    'worldVersion': WORLD.get('version', '100000'),
    'clientIP': '',
    'project': PROJECT,
}


class RQHandler(logging.StreamHandler):
    def __init__(self, redis_url, name, handler, include=[]):
        from redis import Redis
        from rq import Queue
        self.queue = Queue(name, connection=Redis.from_url(redis_url))
        self.handler = handler
        self.include = include
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        message = record.getMessage()
        kind = message.split(':')[0][2:-1]
        if kind not in self.include:
            return
        self.queue.enqueue(self.handler, '[%s] %s' % (record.asctime, message))


gm_logger = JsonLoggerAdapter(logging.getLogger("gmflow"))

role_credit = LongLoggerAdapter(
    logging.getLogger('role-credit'),
    extra=serverInfo)  # 角色充值
role_register = LongLoggerAdapter(
    logging.getLogger('role-register'),
    extra=serverInfo)  # 角色注册
role_login = LongLoggerAdapter(
    logging.getLogger('role-login'),
    extra=serverInfo)  # 角色登陆
account_register = LongLoggerAdapter(
    logging.getLogger('account-register'),
    logto="s{}.{}.yunyue.hgame.account-register".format(
        SESSION['ID'],
        PROJECT),
    extra={
        'sessionID': SESSION['ID']})  # 帐号注册
account_login = LongLoggerAdapter(
    logging.getLogger('account-login'),
    logto="s{}.{}.yunyue.hgame.account-login".format(
        SESSION['ID'],
        PROJECT),
    extra={
        'sessionID': SESSION['ID']})  # 帐号登陆
role_heartbeat = LongLoggerAdapter(
    logging.getLogger('role-heartbeat'),
    extra=serverInfo,
    skip_error=True)  # 心跳
role_debit = LongLoggerAdapter(
    logging.getLogger('role-debit'),
    extra=serverInfo)  # 角色消费
launch = LongLoggerAdapter(
    logging.getLogger('launch'),
    logto="s{}.{}.yunyue.hgame.lauch".format(
        SESSION['ID'],
        PROJECT),
    extra=serverInfo)  # 联网日志
role_custom = LongLoggerAdapter(
    logging.getLogger('role-custom'),
    extra=serverInfo)  # 自定义日志

role_custom.Retry = 1  # 花费钻石战斗复活通关关卡统计
role_custom.Consume = 2  # 付费记录
role_custom.FB = 3  # 副本统计
