#coding:utf-8
import random
from test.utils import *
from gevent import getcurrent
from protocol import poem_pb
from yy.utils import choice_one

def faction_info(sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_INFO))
    return expect(msgid.FACTION_INFO, poem_pb.FactionInfo)

def create_faction(name, sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_CREATE, poem_pb.AlterNameFaction(name=name)))
    return expect(msgid.FACTION_CREATE, poem_pb.FactionInfo)

def members_info(sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_MEMBER_INFOS))
    return expect(msgid.FACTION_MEMBER_INFOS, poem_pb.MemberInfos)

def applys_info(sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_APPLY_INFOS))
    return expect(msgid.FACTION_APPLY_INFOS, poem_pb.MemberInfos)

def dismiss_faction(sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_DISMISS))
    return expect(msgid.FACTION_DISMISS)

def alter_faction_name(name, sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_ALTER_NAME, poem_pb.AlterNameFaction(name=name)))
    return expect(msgid.FACTION_ALTER_NAME)

def alter_faction_mode(sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_ALTER_MODE))
    return expect(msgid.FACTION_ALTER_MODE, poem_pb.AlterModeFaction)

def alter_faction_notice(notice, sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_ALTER_NOTICE, poem_pb.AlterNoticeFaction(notice=notice)))
    return expect(msgid.FACTION_ALTER_NOTICE, poem_pb.AlterNoticeFaction)

def quit_faction(sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_QUIT))
    return expect(msgid.FACTION_QUIT)

def search_faction(sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_SEARCH))
    return expect(msgid.FACTION_SEARCH, poem_pb.FactionInfos)

def apply_faction(factionID, sock=None):
    sock = sock or get_peer()
    sock.sendall(request_msg(msgid.FACTION_APPLY, poem_pb.ApplyFaction(factionID=factionID)))
    return expect(msgid.FACTION_APPLY)

def review_member(entityID=None, sock=None, player=None):
    sock = sock or get_peer()
    player = player or get_player()
    rsp = applys_info()
    if not entityID:
        applys = [i.entityID for i in rsp.members]
    else:
        applys = [entityID]
    for index, entityID in enumerate(applys):
        isallow = (index % 2 == 0)
        sock.sendall(request_msg(msgid.FACTION_REVIEW, poem_pb.ReviewMember(entityID=entityID, isallow=isallow)))
        err = expect(msgid.FACTION_REVIEW)
        print err

def strengthen(sock, player=None):
    type = random.randint(1, 3)
    cost = 10
    sock.sendall(request_msg(msgid.FACTION_STRENGTHEN, poem_pb.FactionStrengthen(type=type, cost=cost)))
    prefix = {
        poem_pb.FactionStrengthen.hp:'strengthen_hp',
        poem_pb.FactionStrengthen.at:'strengthen_at',
        poem_pb.FactionStrengthen.ct:'strengthen_ct',
    }[type]
    player = player or get_player()
    rsp = expect(msgid.FACTION_STRENGTHEN)
    return rsp

def apply(sock, player=None):
    rsp = search_faction()
    factionIDs = [i.factionID for i in rsp.infos]
    player = player or get_player()
    factionID = choice_one(factionIDs)
    #review_member()
    return apply_faction(factionID)

def create(sock, player=None):
    player = player or get_player()
    try:
        faction = create_faction(u"烈焰骑士团{}".format(player.entityID))
    except ExpectException as e:
        if e.body == '已经有公会了。':
            faction = faction_info()
        else:
            print e.body
            raise e
    faction2 = faction_info()
    assert faction.factionID == faction2.factionID
    members = members_info()
    assert members.members[0].name == player.name
    try:
        alter_name = u"燃烧军团{}".format(player.entityID)
        alter_faction_name(alter_name)
        faction3 = faction_info()
        assert faction3.name == alter_name
    except ExpectException as e:
        print e.body

    try:
        rsp = alter_faction_mode()
        assert faction.mode != rsp.mode
    except ExpectException as e:
        print e.body

    try:
        notice = u"会长太懒了，什么都没写。"
        rsp = alter_faction_notice(notice)
        assert notice == rsp.notice
    except ExpectException as e:
        print e.body

    #dismiss_faction()
