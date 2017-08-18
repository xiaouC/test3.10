# coding:utf-8
import ujson as json
import time
# import os
# from datetime import datetime, date as datedate, timedelta
import logging
logger = logging.getLogger("gm")
from bottle import BaseRequest
BaseRequest.MEMFILE_MAX = 10240000  # POST数据大小
from bottle import route, request  # , get, post

# from yy.message.header import fail_msg

from player.manager import g_playerManager
from gm.proxy import proxy, proxy_batch_call
from gevent import spawn

SUCCESS = json.dumps('success')
FAILURE = json.dumps('failure')


def getdisplayattr(instance, s):
    try:
        v = getattr(instance, s)
    except AttributeError:
        v = None
    if s == 'sex':
        return [u'男', u'女'][v]
    elif s == 'career':
        return [None, u'瑶姬', u'嫦娥', u'白骨精'][v]
    elif s == 'pets':
        return ', '.join([e.name for e in v.values()])
    return v


@route('/RPC/:method_name', method='POST')
@proxy.specific
def rpc(method_name):
    import cPickle
    args, kwargs = cPickle.loads(request.body.read())
    module_path, method_name = method_name.rsplit('.', 1)
    try:
        method = getattr(proxy, method_name)
    except AttributeError:
        __import__(module_path)
        method = getattr(proxy, method_name)
    return cPickle.dumps(method(*args, **kwargs))


@route('/RPC_RANDOM/:method_name', method='POST')
@proxy.random
def rpc_random(method_name):
    import cPickle
    args, kwargs = cPickle.loads(request.body.read())
    module_path, method_name = method_name.rsplit('.', 1)
    try:
        method = getattr(proxy, method_name)
    except AttributeError:
        __import__(module_path)
        method = getattr(proxy, method_name)
    return cPickle.dumps(method(*args, **kwargs))


@route('/RPC_BATCH/:method_name', method='POST')
@proxy.batch
def rpc_batch(method_name):
    import cPickle
    args, kwargs = cPickle.loads(request.body.read())
    module_path, method_name = method_name.rsplit('.', 1)
    try:
        method = getattr(proxy, "pure_" + method_name)
    except AttributeError:
        __import__(module_path)
        method = getattr(proxy, "pure_" + method_name)
    # FIXME fix the "pure_" prefix
    return cPickle.dumps(method(*args, **kwargs))


@route('/resetOnZero')
def reset_on_zero():
    from entity.manager import reset_on_zero
    reset_on_zero()


@route('/clear_fbcount/:target')
@proxy.batch
def clear_fb_count(target):
    from entity.manager import g_entityManager
    from scene.manager import sync_scene_infos, FbType
    if target.isdigit():
        players = [g_entityManager.get_player(int(target))]
    elif target == 'all':
        players = g_entityManager.players.values()
    else:
        return json.dumps('invalid target')
    for player in players:
        for fbid, data in player.fbscores.items():
            data['count'] = 0
            data['refreshCount'] = 0
            player.fbscores[fbid] = data
            player.save()
        sync_scene_infos(player, FbType.Normal)
        sync_scene_infos(player, FbType.Advanced)
        sync_scene_infos(player, FbType.Campaign)
    return json.dumps('cleared %s' % target)


@route('/set_max_onlines/:value')
def set_max_online(value):
    import settings
    settings.MAX_ONLINES = int(value)
    return SUCCESS


@route('/get_max_onlines')
def get_max_online():
    import settings
    return json.dumps(str(settings.MAX_ONLINES))


@route('/reload_cron')
def reload_cron():
    import cron_settings
    import imp
    imp.reload(cron_settings)


def validate_list(s):
    result = []
    try:
        l = json.loads(s)
    except ValueError:
        return result
    else:
        if not l:
            return result
        for id, c in l:
            if id:
                result.append([int(id), int(c)])
    return result


@route("/give_gve_ranking_reward/:entityID", method="POST")
@proxy(key="entityID")
def give_gve_ranking_reward(entityID):
    from config.configs import get_config
    from config.configs import GveRankingRewardConfig
    from reward.manager import parse_reward
    from mail.manager import send_mail
    from mail.manager import get_mail
    try:
        entityID = int(entityID)
    except ValueError:
        return FAILURE
    try:
        configID = int(request.POST.getone("configID", 0))
    except ValueError:
        return FAILURE
    group_name = request.POST.getone("group_name", u"")
    group_damage = request.POST.getone("group_damage", 0)
    group_rank = request.POST.getone("group_rank", 0)
    date = request.POST.getone("date", u"")
    if not date:
        return FAILURE
    from player.model import Player
    if not int(Player.pool.execute(
            "HSET", "gve_ranking_rewards_p{%d}" % entityID, date, "")):
        # 不让重复添加
        return SUCCESS
    config = get_config(GveRankingRewardConfig).get(configID)
    if not config:
        return FAILURE
    title, content, ID = get_mail("GroupRankReward")
    try:
        content = content.format(group_name, group_damage, group_rank)
    except UnicodeDecodeError:
        pass
    rewards = parse_reward(config.rewards)
    send_mail(entityID, title, content, addition=rewards, configID=ID)
    return SUCCESS


@route("/add_condition_mail", method="POST")
@proxy.random
def add_condition_mail():
    if request.method == "POST":
        title = request.POST.getone("title", "")
        content = request.POST.getone("content", "")
        petList = validate_list(request.POST.getone("petList", ""))
        matList = validate_list(request.POST.getone("matList", ""))
        equipList = validate_list(request.POST.getone("equipList", ""))
        specPacks = validate_list(request.POST.getone("specpackList", ""))
        specPacks = specPacks or validate_list(
            request.POST.getone("specPacks", ""))
        limitdata = json.loads(request.POST.getone("limitdata", "{}"))
        reward = {}
        from reward.base import get_reward_attr_list
        for attr in get_reward_attr_list():
            value = int(request.POST.getone(attr) or 0)
            if value:
                reward[attr] = value
        if petList:
            from config.configs import get_config, PetConfig
            for id, count in petList:
                if id not in get_config(PetConfig):
                    return json.dumps({
                        'status': 1,
                        'message': '精灵`%d`不存在' % id,
                    })
            reward['petList'] = petList
        if matList:
            from config.configs import get_config, MatConfig
            for id, count in matList:
                if id not in get_config(MatConfig):
                    return json.dumps({
                        'status': 1,
                        'message': '物品`%d`不存在' % id,
                    })
            reward['matList'] = matList
        if equipList:
            from config.configs import get_config, NewEquipConfig
            for id, count in equipList:
                if id not in get_config(NewEquipConfig):
                    return json.dumps({
                        'status': 1,
                        'message': '装备`%d`不存在' % id,
                    })
            reward['equipList'] = equipList
        if specPacks:
            from config.configs import get_config, SpecpackConfig
            for id, count in specPacks:
                if id not in get_config(SpecpackConfig):
                    return json.dumps({
                        'status': 1,
                        'message': '特殊掉落`%d`不存在' % id,
                    })
            reward['specPacks'] = specPacks
        from mail.model import Mail
        from mail.constants import MailType
        cd = 7*24*60*60
        params = {
            "title": title,
            "content": content,
            "addition": reward,
            "cd": cd,
            "limitdata": limitdata,
            "type": MailType.System,
        }
        Mail.add_condition_mail(**params)
        from gm.proxy import proxy
        from mail.manager import sync_condition_mail  # NOQA
        proxy.sync_condition_mail()
    return json.dumps({
        'status': 0,
        'message': 'success',
        'params': params
    })


@route('/add_mail/:key', method='POST')
@proxy(key='key')
def add_mail(key):
    title = request.POST.getone("title", "")
    content = request.POST.getone("content", "")
    petList = validate_list(request.POST.getone("petList", ""))
    matList = validate_list(request.POST.getone("matList", ""))
    equipList = validate_list(request.POST.getone("equipList", ""))
    specPacks = validate_list(request.POST.getone("specpackList", ""))
    specPacks = specPacks or validate_list(
        request.POST.getone("specPacks", ""))
    gemList = validate_list(request.POST.getone("gemList", ""))
    entityID = int(request.POST.getone('entityID') or 0)
    reward = {}
    from reward.base import get_reward_attr_list
    for attr in get_reward_attr_list():
        value = int(request.POST.getone(attr) or 0)
        if value:
            reward[attr] = value
    if petList:
        from config.configs import get_config, PetConfig
        for id, count in petList:
            if id not in get_config(PetConfig):
                return json.dumps('failure')
        reward['petList'] = petList
    if matList:
        from config.configs import get_config, MatConfig
        for id, count in matList:
            if id not in get_config(MatConfig):
                return json.dumps('failure')
        reward['matList'] = matList
    if equipList:
        from config.configs import get_config, NewEquipConfig
        for id, count in equipList:
            if id not in get_config(NewEquipConfig):
                return json.dumps("failure")
        reward['equipList'] = equipList
    if specPacks:
        from config.configs import get_config, SpecpackConfig
        for id, count in specPacks:
            if id not in get_config(SpecpackConfig):
                return json.dumps('failure')
        reward['specPacks'] = specPacks
    if gemList:
        from config.configs import get_config, GemConfig
        for id, count in gemList:
            if id not in get_config(GemConfig):
                return json.dumps('failure')
        reward['gemList'] = gemList
    cd = 30*24*60*60
    from mail.manager import send_mail
    send_mail(entityID, title, content, addition=reward, cd=cd)
    return SUCCESS


@route('/get_players_info', method='POST')
@proxy.specific
def get_players_info():
    # 取多个玩家数据
    if request.json:
        data = request.json
    else:
        data = request.POST.dict
    playerIDs = map(lambda s: int(s), data.get('playerIDs', []))
    attrs = data.get('attrs', [])
    from entity.manager import g_entityManager
    result = g_entityManager.get_players_info(playerIDs, attrs)
    return json.dumps(result)


@route('/get_pets_info', method='POST')
@proxy.specific
def get_pets_info():
    # 取玩家阵上怪物数据
    if request.json:
        data = request.json
    else:
        data = request.POST.dict
    playerID = data.get('playerID')
    assert playerID, 'not playerID'
    attrs = data.get('attrs', [])
    from lineup.manager import get_lineup_info
    pets = get_lineup_info(playerID, attrs)
    for pos, pet in enumerate(pets):
        pet['posIndex'] = pos
    return json.dumps(pets)


@route('/rolelevel')
@proxy.random
def rolelevel():
    from player.model import Player, PlayerLevelRanking
    dd = {}
    LIMIT = 10  # 自定义
    # level_set = set()
    playerIDs = PlayerLevelRanking.get_by_range(1, LIMIT)
    levels = map(lambda p: p.level, [Player.get(id) for id in playerIDs])
    for index, value in enumerate(levels):
        career = Player.simple_load(playerIDs[index], ['career']).career
        if value in dd:
            # 有相同等级
            dd[value][career - 1] += 1
        else:
            # 没有相同等级
            v = [0, 0, 0]
            dd[value] = v
            dd[value][career - 1] = 1
    rows = []
    for k, v in dd.items():
        rows.append([k] + map(lambda r: r if r else 0, v))
    header = [u'等级', u'哪吒', u'铁扇公主', u'二郎真君']
    return dict(rows=rows, header=header)


@route('/players')
@proxy.batch
def players():
    from entity.manager import g_entityManager
    attrs = [
        'entityID', 'username',
        'name', 'sex', 'career',
        'level', 'userID']
    header = ['ID', u'用户名', u'名称', u'性别', u'职业', u'等级', u"用户ID"]
    rows = []
    for _, player in g_entityManager.players.items():
        ll = [getdisplayattr(player, s) for s in attrs]
        rows.append(ll)
    return dict(rows=rows, header=header)


@route('/player/:key')
@proxy(key='key')
def player(key):
    from entity.manager import g_entityManager
    from player.model import Player
    from pet.model import Pet
    player = g_entityManager.get_player(int(key))
    is_online = True
    if not player:
        player = Player.load(int(key))
        is_online = False
    rows = []
    for a in Player.fields_list:
        attr = getdisplayattr(player, a.name)
        if not is_online and a.name == 'pets':
            names = []
            for petID in player.petset:
                pet = Pet.simple_load(petID, ['name'])
                names.append(pet.name)
            attr = ','.join(names)
        if not isinstance(attr, (basestring, int, long, float)):
            continue
        ll = [a.description.decode('utf-8'), attr]
        rows.append(ll)
    return json.dumps(dict(attributes=rows, is_online=is_online))


@route('/playercount')
@proxy.batch
def playercount():
    return json.dumps(g_playerManager.count())


@route('/kickplayer/:key')
@proxy(key='key')
def kickplayer(key):
    # from world.service import cleanup
    # from common import msgTips
    from entity.manager import g_entityManager
    player = g_entityManager.get_player(int(key))
    if not player:
        return json.dumps("failure")
    # g_playerManager.sendto(
    #     player.entityID,
    #     fail_msg(
    #         0,
    #         msgTips.FAIL_MSG_CLOSE_SERVER))
    g_playerManager.kick_player(player.entityID)
    return SUCCESS


@route('/modifyfbId/:playerId')
@proxy(key='playerId')
def modifyfbId(playerId):
    ''' 修改用户副本进度 '''
    from scene.constants import FbType
    from scene.manager import set_fb_score, sync_scene_infos
    from config.configs import get_config, FbInfoByTypeConfig, FbInfoConfig

    from entity.manager import g_entityManager
    player = g_entityManager.get_player(int(playerId))
    if not player:
        return FAILURE

    fbID = int(request.GET.getone("fbId") or 0)
    if not fbID:
        configs = get_config(FbInfoByTypeConfig).get(FbType.Normal, [])\
            + get_config(FbInfoByTypeConfig).get(FbType.Guide,  [])\
            + get_config(FbInfoByTypeConfig).get(FbType.Advanced, [])
        for c in configs:
            if c.ID not in player.fbscores:
                set_fb_score(player, c.ID, 3)
    else:
        configs = get_config(FbInfoConfig)
        if fbID in configs:
            set_fb_and_prev_score(player, fbID, 3)
        else:
            return json.dumps('failure')
    player.save()
    sync_scene_infos(player, FbType.Normal)
    sync_scene_infos(player, FbType.Advanced)
    return SUCCESS


def set_fb_and_prev_score(player, fbID, score):
    from config.configs import get_config, FbInfoConfig
    from scene.manager import set_fb_score
    configs = get_config(FbInfoConfig)
    config = configs.get(fbID)
    if not config:
        return
    set_fb_score(player, fbID, 3)
    for i in config.prev:
        set_fb_and_prev_score(player, i, score)
    return True


# 统计当前区排行玩家等级,经验前十


@route('/player_top_ten')
@proxy.random
def player_top_ten():
    from player.model import Player, PlayerLevelRanking
    rows = []
    LIMIT = 1000  # 自定义
    playerIDs = PlayerLevelRanking.get_by_range(1, LIMIT)
    for id in playerIDs:
        p = Player.simple_load(
            id, [
                'entityID', 'name', 'level', 'exp', 'career'])
        p_message = (p.entityID, p.name, p.level, p.exp, p.career)
        rows.append(p_message)

    def compare(x, y):
        if x[2] == y[2]:
            return int(x[3]) - int(y[3])
        else:
            return int(x[2]) - int(y[2])
    rows = sorted(rows, cmp=compare, reverse=True)
    header = [u'角色ID', u'角色名字', u'等级', u'经验', u'游戏角色']
    return json.dumps(dict(header=header, rows=rows))


@route('/addRoleAttr/:entityID/:attrName/:value')
@proxy(key='entityID')
def addAttr(entityID, attrName, value):
    from entity.manager import g_entityManager
    entityID = int(entityID)
    value = int(value)
    role = g_entityManager.get_player(entityID)
    if not role:
        from player.model import Player
        Player.add_offline_attr(
            entityID,
            Player.getAttributeIDByName(attrName),
            value)
        return SUCCESS
    try:
        if not hasattr(role, attrName):
            return FAILURE
        current = getattr(role, attrName)
        if not isinstance(current, (int or long)):
            raise TypeError
        if attrName == "exp":
            from reward.base import set_exp
            set_exp(role, value)
        elif attrName == "level":
            if value == 0:
                return FAILURE
            from config.configs import get_config, LevelupConfig
            lconfigs = get_config(LevelupConfig)
            exp = 0
            for i in range(role.level + 1,  role.level + value + 1):
                c = lconfigs.get(i)
                if not c:
                    return FAILURE
                exp += c.exp
            from reward.base import set_exp
            set_exp(role, exp)
        elif attrName == "totalbp":
            from pvp.rank import incr_score
            from player.model import PlayerRankRanking
            incr_score(entityID, value)
            PlayerRankRanking.sync_player(role)
        else:
            setattr(role, attrName, current + value)
        role.save()
        role.sync()
    except:
        import traceback
        traceback.print_exc()
        return FAILURE
    return SUCCESS


@route('/setRoleAttr/:entityID/:attrName/:value')
@proxy(key='entityID')
def setAttr(entityID, attrName, value):
    from entity.manager import g_entityManager
    entityID = int(entityID)
    value = int(value)
    role = g_entityManager.get_player(entityID)
    if not role:
        from player.model import Player, OfflineAttrType
        Player.add_offline_attr(
            entityID,
            Player.getAttributeIDByName(attrName),
            value,
            type=OfflineAttrType.Set)
        return SUCCESS
    try:
        current = getattr(role, attrName)
        if not isinstance(current, (int or long)):
            raise TypeError
        setattr(role, attrName, value)
        role.save()
        role.sync()
    except:
        return FAILURE
    return SUCCESS


@route('/resetRoleAttr/:entityID/:attrName')
@proxy(key='entityID')
def resetAttr(entityID, attrName):
    from entity.manager import g_entityManager
    entityID = int(entityID)
    p = g_entityManager.get_player(entityID)
    if not p:
        from player.model import Player, OfflineAttrType
        Player.add_offline_attr(
            entityID,
            Player.getAttributeIDByName(attrName),
            None,
            type=OfflineAttrType.Reset)
        return SUCCESS
    else:
        try:
            f = p.fields[attrName]
            if callable(f.default):
                default = f.default()
            else:
                default = f.default
            setattr(p, attrName, default)
            p.save()
            p.sync()
        except:
            import traceback
            traceback.print_exc()
            return FAILURE
    return SUCCESS


def get_give_arguments(form):
    slevel = int(request.POST.getone('slevel'))
    elevel = int(request.POST.getone('elevel'))
    fbID = int(request.POST.getone('fbID'))
    title = request.POST.getone('title')
    content = request.POST.getone('content')
    reward = request.POST.getone('reward')
    value = int(request.POST.getone('value'))
    return slevel, elevel, fbID, title, content, reward, value


@route('/give', method=['POST'])
@proxy.batch
def give():
    slevel, elevel, fbID, title, content, reward, value = get_give_arguments(
        request.POST)
    reward = {reward: value}
    from entity.manager import g_entityManager
    from mail.manager import send_mail
    from mail.manager import validate_mail_condition
    for player in g_entityManager.players.values():
        if not validate_mail_condition(
            player, {
                'slevel': slevel, 'elevel': elevel, 'fbID': fbID}):
            continue
        send_mail(player.entityID, title, content, addition=reward)
    return SUCCESS


@route('/give_offline', method=['POST'])
@proxy.random
def give_offline():
    import time
    from mail.model import Mail
    from mail.constants import MailType
    slevel, elevel, fbID, title, content, reward, value = get_give_arguments(
        request.POST)
    reward = {reward: value}
    limit = {'slevel': slevel, 'elevel': elevel, 'fbID': fbID}
    atime = int(time.time())
    mail_message = {}
    mail_message['playerID'] = 0
    mail_message['title'] = title
    mail_message['content'] = content
    mail_message['addition'] = reward
    mail_message['addtime'] = atime
    mail_message['limitdata'] = limit
    mail_message['type'] = MailType.System

    Mail.add_offline_mail(**mail_message)
    return SUCCESS


@route('/gen_giftkey', method=['POST'])
def gen_cdkey():
    from giftkey import gen_key
    count = int(request.POST.getone('count'))
    giftID = int(request.POST.getone('itemID'))
    key = (request.POST.getone('key') or '').strip(' ')
    servers = ",".join(request.POST.getlist("servers"))
    channels = ",".join(request.POST.getlist("channels"))
    if count > 2000:  # 上限限制
        count = 2000
    if key:
        if len(key) < 6:
            keys = []
        else:
            keys = gen_key(
                giftID, giftkey=key, count=1,
                servers=servers, channels=channels)
    else:
        keys = gen_key(
            giftID, count=count,
            servers=servers, channels=channels)
    return json.dumps([[k, giftID] for k in keys])


@route('/whitelist_regions', method=['GET', 'POST'])
def whitelist_regions():
    from session.regions import r_whitelist_regions
    from session.regions import g_whitelist_regions
    from session.regions import reload_regions
    if request.method == 'GET':
        return json.dumps(g_whitelist_regions)
    is_enable = bool(request.POST.getone('is_enable'))
    regionIDs = request.POST.getlist('regionIDs')
    if is_enable:
        r_whitelist_regions.sadd(*regionIDs)
    else:
        r_whitelist_regions.srem(*regionIDs)
    reload_regions()
    return json.dumps({'status': 0, 'message': 'success'})


@route('/whitelist', method=['GET', 'POST'])
def whitelist():
    from session.regions import r_whitelist
    from session.regions import g_whitelist
    from session.regions import reload_whitelist
    if request.method == 'GET':
        return json.dumps(g_whitelist)
    is_add = bool(request.POST.getone('is_add'))
    usernames = request.POST.getlist('usernames')
    if is_add:
        r_whitelist.sadd(*usernames)
    else:
        r_whitelist.srem(*usernames)
    reload_whitelist()
    return json.dumps({'status': 0, 'message': 'success'})


@route('/access_control_list', method=['GET', 'POST'])
def access_control_list():
    from session.regions import g_regions
    from session.regions import g_sdks
    from session.regions import g_versions
    from session.regions import g_whitelist_regions
    from session.regions import r_regions
    from session.regions import r_sdks
    from session.regions import r_versions
    from session.regions import r_whitelist_regions
    from session.regions import r_version
    from session.regions import reload_all
    if request.method == "POST":
        if not request.json:
            return json.dumps({
                'status': 1,
                'message': 'Not arguments',
            })
        regions = request.json
        sdks = {}
        versions = {}
        whitelist = []
        for k, v in regions.items():
            r_regions.hset(k, v["name"])
            # FIXME make better
            sdk_acl = {
                "deny_sdks": v.get(
                    "deny_sdks", []),
                "allow_sdks": v.get(
                    "allow_sdks", [])}
            sdks[k] = json.dumps(sdk_acl)
            version_acl = {
                "deny_versions": v.get(
                    "version_denys", []),
                "allow_versions": v.get(
                    "allow_versions", [])}
            versions[k] = json.dumps(version_acl)
            if v.get("enable_whitelist"):
                whitelist.append(k)
            version_required = v.get("version_required", 0)
        r_sdks.hmset(**sdks)
        r_versions.hmset(**versions)
        r_whitelist_regions.clear()
        if whitelist:
            r_whitelist_regions.sadd(*whitelist)
        r_version.set(version_required)
        reload_all()
    regions = {}
    for k, v in g_regions.items():
        info = {"name": v.name}
        info.update(g_sdks.get(k, {}))
        info.update(g_versions.get(k, {}))
        info.update(enable_whitelist=(k in g_whitelist_regions))
        regions[k] = info
    return json.dumps({
        'status': 0,
        'message': 'success',
        'regions': regions
    })


@route('/loginlimitmsg', method=['POST'])
def loginlimitmsg():
    from session.regions import r_loginlimitmsg
    from session.regions import reload_loginlimitmsg
    msg = request.POST.getone('msg')
    r_loginlimitmsg.set(msg)
    reload_loginlimitmsg()
    return SUCCESS


@route("/reloadConfig/:name", method="POST")
@proxy.batch
def reloadConfig(name):
    import settings
    from common import ConfigFiles
    from config.configs import get_registereds
    from yy.config.fields import ValidationError
    from entity.manager import g_entityManager
    source = request.POST.getone("source") or ''
    config_files = ConfigFiles(settings.REGION['ID'])
    try:
        if name == "all":
            config_files.load_configs(
                get_registereds(),
                settings.CONFIG_FILE_PATH)
        else:
            configs = []
            for each in get_registereds():
                if each.__Meta__.table == name:
                    configs.append(each)
            if not configs:
                raise ValidationError("找不到文件%s对应的Config" % name)
            if source:
                data = {configs[0].__Meta__.table: source}
                config_files.load_configs(configs, '', **data)
            else:
                config_files.load_configs(configs, settings.CONFIG_FILE_PATH)
    except ValidationError as e:
        return json.dumps(e.message)
    if name == "daytime" or name == "all":
        from pvp.rank import g_rankManager
        g_rankManager.start()
    if name == "campaign" or name == "all":
        from campaign.manager import g_campaignManager
        g_campaignManager.start()
    if name == "Dlc_campaign" or name == "all":
        from explore.dlc import g_dlcCampaignManager
        g_dlcCampaignManager.start()
    if name == "gve_campaign" or name == "all":
        from campaign.manager import g_campaignManager
        g_campaignManager.gve_campaign.start()
    if name == "boss_campaign" or name == "all":
        from explore.boss import g_bossCampaignManager
        g_bossCampaignManager.start()
    if name == "ranking_campaign" or name == 'all':
        from ranking.manager import g_rankingCampaignManager
        g_rankingCampaignManager.reload()
    if name == "city_campaign" or name == 'all':
        from campaign.manager import g_campaignManager
        g_campaignManager.city_dungeon_campaign.start()
        g_campaignManager.city_dungeon_campaign.sync()
        g_campaignManager.city_contend_campaign.start()
        g_campaignManager.city_contend_campaign.sync()
    if name == "limit" or name == "all":
        from world.service import get_limited_packs_time
        t = get_limited_packs_time()
        if t:
            for p in g_entityManager.players.values():
                p.clear_limited_packs_flag()
                p.sync('limited_packs_flag')
    if name == "ExSceneInfo" or name == "all":
        from scene.constants import FbType
        from scene.manager import sync_scene_infos
        for p in g_entityManager.players.values():
            sync_scene_infos(p, FbType.Campaign)
    return SUCCESS


@route("/redumpConfig", method="POST")
def redumpConfig():
    from common import ConfigFiles
    source = request.POST.getone("source") or ''
    if not source:
        return FAILURE
    name = request.POST.getone("name")
    regionID = int(request.GET['regionID'])
    config_files = ConfigFiles(regionID)
    config_files.set_file(name, source)
    return SUCCESS


@route('/getConfig/:name')
@proxy.random
def getConfig(name):
    import settings
    from yy.config.dump import config_path
    from common import ConfigFiles
    regionID = int(request.GET['regionID'])
    config_files = ConfigFiles(regionID)
    source = config_files.get_file(name)
    if not source:
        path = config_path(name, settings.CONFIG_FILE_PATH)
        try:
            source = open(path, 'r').read()
        except IOError as e:
            return json.dumps(e.strerror)
    try:
        result = json.dumps(source)
    except UnicodeDecodeError:
        result = json.dumps(source.decode("cp936"))
    return result


@route('/redumpEveryConfig')
def redumpEveryConfig():
    '''
    将data目录下形如region100等目录的配置文件，dump到redis
    用以区分各区不同的配置
    '''
    from gm.main import check_configs
    check_configs()
    return SUCCESS


@route('/reloadEveryConfig')
@proxy.every
def reloadEveryConfig():
    return reloadConfig('all')


@route("/ping")
def ping():
    return SUCCESS


@route("/send_system_message", method=["POST"])
@proxy.batch
def send_system_message():
    message = request.POST.get("message")
    duration = request.POST.get("duration")
    from chat.manager import send_system_message
    if duration:
        send_system_message(message, duration=int(duration))
    else:
        send_system_message(message)
    return SUCCESS


@route("/broadcast_system_message", method=["POST"])
@proxy.every
def broadcast_system_message():
    message = request.POST.get("message")
    duration = request.POST.get("duration")
    from chat.manager import send_system_message
    if duration:
        send_system_message(message, duration=int(duration))
    else:
        send_system_message(message)
    return SUCCESS


@route("/set_client_config", method=["POST"])
def set_client_config():
    from protocol import poem_pb
    from common import ClientConfig
    data = request.body.read()
    obj = poem_pb.incrementResponse()
    obj.ParseFromString(data)
    version = obj.config_version
    if ClientConfig().set(version, data):
        return SUCCESS
    return FAILURE


@route("/blockdevice", method=["POST"])
def blockdevice():
    entityID = int(request.POST.get("entityID") or 0)
    block = request.POST["block"] == 'True'
    if not entityID:
        return FAILURE
    from player.model import Player
    userID = Player.simple_load(entityID, ['userID']).userID
    if not userID:
        return FAILURE
    from user.model import User
    user = User.load(userID)
    imsi = user.imsi
    if not imsi:
        return FAILURE
    from session.regions import r_block_devices
    if block:
        r_block_devices.sadd(imsi)
    else:
        r_block_devices.srem(imsi)

    if block:
        for regionID, entityIDs in user.roles.items():
            for entityID in entityIDs:
                spawn(
                    proxy_batch_call,
                    'chat.manager.clear_blocked_message',
                    regionID, entityID)

    return SUCCESS


@route("/blocktime", method=["POST"])
def blocktime():
    # userID = int(request.POST.get("userID") or 0)
    entityID = int(request.POST.get("entityID") or 0)
    blocktime = int(request.POST.get("blocktime") or 0)
    if not entityID:
        return FAILURE
    now = int(time.time())
    if blocktime and blocktime < now:
        return FAILURE
    from player.model import Player
    userID = Player.simple_load(entityID, ['userID']).userID
    if not userID:
        return FAILURE

    from user.model import User
    user = User.load(userID)
    user.blocktime = blocktime
    user.save()

    for regionID, entityIDs in user.roles.items():
        for entityID in entityIDs:
            spawn(
                proxy_batch_call,
                'chat.manager.clear_blocked_message',
                regionID, entityID)

    return SUCCESS


@route("/clear_blocked_message", method=["POST"])
def clear_blocked_message():
    userID = int(request.POST.get("userID") or 0)
    if not userID:
        return FAILURE

    from user.model import User
    user = User.load(userID)

    for regionID, entityIDs in user.roles.items():
        for entityID in entityIDs:
            spawn(
                proxy_batch_call,
                'chat.manager.clear_blocked_message',
                regionID, entityID)

    return SUCCESS


@route("/sdk_pay/:key", method=["POST"])
@proxy(key='key')
def sdk_pay(key):
    """充值"""
    from world.service import sdk_pay
    # entityID = int(request.POST.getone('entityId'))
    entityID = int(key)
    orderid = request.POST.getone('orderid')
    amount = float(request.POST.getone('amount'))
    sdata = request.POST.getone('sdata')
    rechargegold = float(request.POST.getone('rechargegold'))
    sdktype = int(request.POST.getone('sdktype'))
    goods = int(request.POST.getone('goods'))
    delay = int(request.POST.getone('delay') or 0)
    if sdk_pay(
            entityID, orderid,
            amount, rechargegold,
            sdata, sdktype, goods, delay):
        return SUCCESS
    logger.error(dict(request.params))
    return FAILURE


@route("/makeup_recharge/:key", method=["POST"])
@proxy(key="key")
def makeup_recharge(key):
    """补还充值"""
    from world.service import pay_handler
    from entity.manager import g_entityManager
    from player.model import Player
    entityID = int(key)
    goodsid = request.POST.getone("amount")  # 现在amount为商品ID
    p = g_entityManager.get_player(entityID)
    if not p:
        p = Player.simple_load(entityID, ["entityID", "username"])
    rs = pay_handler(entityID, p.username, goodsid)
    if not rs:
        return FAILURE
    return SUCCESS


@route('/lock_device_and_skip_guide/:entityID', method=['POST'])
@proxy(key='entityID')
def lock_device_and_skip_guide(entityID):
    from entity.manager import g_entityManager
    from player.model import Player, OfflineAttrType
    entityID = int(entityID)
    deviceID = request.POST.getone('deviceID', '')
    lock_level = int(request.POST.getone('lock_level', '50'))
    role = g_entityManager.get_player(entityID)
    if not role:
        Player.add_offline_attr(
            entityID,
            Player.getAttributeIDByName('skip_guide'),
            True, OfflineAttrType.Set)
        Player.add_offline_attr(
            entityID,
            Player.getAttributeIDByName('lock_level'),
            lock_level, OfflineAttrType.Set)
    else:
        role.skip_guide = True
        role.lock_level = lock_level
        role.save()
        role.sync()

    # lock device
    if not role:
        userID = Player.simple_load(entityID, ['userID']).userID
    else:
        userID = role.userID

    from user.model import User
    u = User.simple_load(userID, ['lock_device', 'imsi'])
    u.lock_device = deviceID or u.imsi
    u.save()
    return SUCCESS


@route("/query_player", method=["POST"])
def query_player():
    value = request.POST.getone('value')
    type = request.POST.getone('type')
    regionID = int(request.GET['regionID'])
    if not type or not value:
        return FAILURE
    import settings
    from player.model import Player
    from yy.entity.index import UniqueIndexing
    from user.model import User, UsernameIndexing
    if type == 'playername':
        indexing = UniqueIndexing(
            'index_p_name{%d}' % regionID, settings.REDISES['index'])
        entityID = indexing.get_pk(value)
        if entityID:
            entityIDs = [indexing.get_pk(value)]
        else:
            entityIDs = []
    elif type == 'username':
        userID = UsernameIndexing.get_pk(value)
        u = User.load(userID)
        entityIDs = u.roles[regionID]
    elif type == 'entityID':
        entityIDs = [int(value)]

    attrs = [
        'entityID', 'username',
        'name', 'sex', 'career',
        'level', 'userID']
    header = ['ID', u'用户名', u'名称', u'性别', u'职业', u'等级', u"用户ID"]
    rows = []
    players = Player.batch_load(entityIDs, attrs)
    for player in players:
        ll = [getdisplayattr(player, s) for s in attrs]
        rows.append(ll)
    return dict(rows=rows, header=header)


@route('/reset_password', method=['POST'])
def reset_password():
    userID = int(request.POST.get("userID") or 0)
    if not userID:
        return FAILURE

    from user.model import User
    from yy.rpc.http import get_random_string
    from yy.utils import make_password
    u = User.load(userID)
    s = get_random_string(8)
    if u.password == 'dummy':
        return FAILURE
    u.password = make_password(s)
    u.save()
    return json.dumps(s)


@route('/broadcast_horn', method=["POST"])
@proxy.batch
def broadcast_horn():
    message = request.POST.getone('message')
    cd = int(request.POST.getone('cd') or 0)
    from chat.red import send_horn
    send_horn(message, cd=cd)
    return SUCCESS
