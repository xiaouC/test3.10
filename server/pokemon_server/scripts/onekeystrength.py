# coding: utf-8
'''
一键变强
'''

import json
import urllib, urllib2

PROXY_URL = None
REGIONID = None
ENTITYID = None


def set_proxy_server(ip, port, regionID):
    global PROXY_URL, REGIONID
    PROXY_URL = 'http://%s:%s' % (ip, port)
    REGIONID = regionID


def set_entity_id(n):
    global ENTITYID
    ENTITYID = n


def proxy_request(path, d=None):
    if not PROXY_URL:
        print 'not set proxy host'
        return
    if '?' in path:
        path += '&regionID=%s' % REGIONID
    else:
        path += '?regionID=%s' % REGIONID
    url = PROXY_URL+path
    #print '[DEBUG] request', url, d
    rsp = urllib2.urlopen(url, urllib.urlencode(d) if d != None else None)
    return rsp.read()


def through_fb(fbID):
    print '通关副本', fbID
    print proxy_request('/modifyfbId/%s?%s' % (ENTITYID, urllib.urlencode({'fbId': fbID})))


def send_mail(title, content='', petList=None, matList=None, equipList=None, specpackList=None, specPacks=None, **attrs):
    args = {
        'entityID': ENTITYID,
        'title': title,
        'content': content,
        'petList': json.dumps(petList or []),
        'matList': json.dumps(matList or []),
        'equipList': json.dumps(equipList or []),
        'specpackList': json.dumps(specpackList or []),
        'specPacks': json.dumps(specPacks or []),
    }
    args.update(attrs)
    print '发邮件', title
    print proxy_request('/add_mail/%s' % ENTITYID, args)


def skip_guide(b=1):
    print u'跳过指引'
    print proxy_request('/setRoleAttr/%s/skip_guide/%s' % (ENTITYID, b))


def players():
    print u'在线玩家:'
    d = json.loads(proxy_request('/players'))
    print ' '.join(map(unicode, d['header']))
    for row in d['rows']:
        print ' '.join(map(unicode, row))


if __name__ == '__main__':
    set_proxy_server('120.132.50.137', 20001, 100) # 外网服务器

    players()               # 显示在线用户信息

    set_entity_id(17)       # 设置角色ID，必须
    #skip_guide()           # 跳过指引
    #through_fb(100118)     # 通关副本
    #send_mail('一键变强',  # 发送邮件
    #        petList = [(3000005, 1), (6300003, 1)],
    #        equipList = [(10013, 1), (10025, 2)],
    #        gold=100)
