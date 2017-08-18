# coding:utf-8
import time
import operator
import logging
logger = logging.getLogger("mail")
from .model import Mail, EmailByTimeIndexing
from .constants import MailType
from entity.manager import g_entityManager
from player.model import Player
from config.configs import get_config
from config.configs import MailConfig
from mail.constants import MailConfigID
from gm.proxy import proxy


def validate_mail_condition(player, conditions):
    slevel = conditions.get('slevel', 0)
    elevel = conditions.get('elevel', 0)
    fbID = conditions.get('fbID', 0)
    if slevel and elevel:
        if player.level <= slevel or player.level >= elevel:
            return False
    if fbID and fbID not in player.fbscores:
        return False
    return True


def check_condition(p, condition):
    for k, except_value in condition.items():
        try:
            attr, cond = k.split("__")
            op = getattr(operator, cond)
            actual_value = getattr(p, attr)
            if actual_value is None:
                return False
            if not op(actual_value, except_value):
                return False
        except Exception as e:
            logger.error(
                "Check mail condition %r raise %r", condition, e)
            return False
    return True


def apply_condition_mail(p):
    lct = p.last_check_mail_time
    now = time.time()
    # 这里可以优化
    mails = Mail.batch_load(
        EmailByTimeIndexing.get_by_range(
            lct, now))
    for mail in mails:
        if not check_condition(p, mail.limitdata):
            continue
        p.add_mail(
            mail.title,
            mail.content,
            mail.addition,
            mail.addtime,
            type=mail.type,
            cd=mail.cd,
        )
    p.last_check_mail_time = now
    p.save()
    p.sync()


@proxy.rpc_batch
def sync_condition_mail():
    from entity.manager import g_entityManager
    for p in g_entityManager.players.values():
        apply_condition_mail(p)


def send_mail(
        entityID, title, content,
        addition=None,
        addtime=None,
        cd=0,
        type=MailType.System, configID=0):
    if not addition:
        addition = {}
    if not addtime:
        addtime = int(time.time())
    if not cd and configID:
        config = get_config(MailConfig).get(configID)
        if config:
            cd = config.time
    mail = Mail.create(
        playerID=entityID,
        title=title,
        content=content,
        addition=addition,
        addtime=addtime,
        cd=cd,
        configID=configID,
        type=type)
    mail.save()
    p = g_entityManager.get_player(entityID)
    if p:
        p.mails[mail.mailID] = mail
        # p.touch_mails()
        p.mailset.add(mail.mailID)
        p.save()
        p.sync()
    else:
        p = Player.simple_load(entityID, ['mailset'])
        p.mailset.add(mail.mailID)
        p.save()
    return mail


def get_mail(tag):
    ID = getattr(MailConfigID, tag)
    config = get_config(MailConfig).get(ID)
    if not config:
        return "", ""
    return config.title, config.content, ID
