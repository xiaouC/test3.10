# coding=utf-8

import sys
import urllib
import urllib2
from urllib2 import URLError
from xml.dom import minidom

sender = 'luaerror'
pwd = '123456yy'
receiver_list = [
    'fenghualiang',
    'linliecheng',
    'longtengfei',
    'caokun',
    'von',
    'huboqing',
    'weijian',
    'caiwenhao',
    'zhenghuisheng',
    'yellowhuang',
    'xiaou',
    'qiuzq',
    'fissionzheng',
    'jdz',
    'sherry',
    'madailun',
]


def get_receivers():
    with open("all-users.xml", 'r') as f:
        f.readline()
        source = f.read()
    source = unicode(source, "cp936").encode("utf-8")
    doc = minidom.parseString(source)
    items = doc.getElementsByTagName("Item")
    return filter(lambda s: s, [
        i.getAttribute("UserName").encode("utf-8") for i in items])


def encode(msg):
    try:
        return msg.decode("utf-8").encode("cp936")
    except:
        return msg


def send(msg):
    receivers = ';'.join(receiver_list)
    args = urllib.urlencode({
        'sender': sender,
        'pwd': pwd,
        'msg': msg,
        'receivers': receivers,
        })

    url = "http://192.168.0.253:8012/SendIM_2.cgi?"+args
    req = urllib2.Request(url)

    try:
        res_data = urllib2.urlopen(req)
    except URLError, e:
        if hasattr(e, 'reason'):
            print >> sys.stderr, '[sendIM] We failed to reach a server.'
            print >> sys.stderr, '[sendIM] Reason : ', e.reason.decode("cp936")
        elif hasattr(e, 'code'):
            print >> sys.stderr, '[sendIM] The server could \
                    not fulfill the request.'
            print >> sys.stderr, '[sendIM] Error code : ', e.code
        else:
            pass
            print >> sys.stderr, '[sendIM] send failed'
            return False
    else:
        res = res_data.read()
        print >> sys.stderr, '[sendIM]', res.decode("cp936")
        return True


def pretty(msg, d="@"):
    msg = encode(msg)
    ss = [d] * 4 + [msg] + [d] * 4
    wrap = "%s%s%s%s    %s    %s%s%s%s" % tuple(ss)
    prev = ((len(wrap) - len(msg)) + len(msg) / 3 * 2) * d
    post = prev
    return prev + "\n" + wrap + "\n" + post


def commit_message():
    try:
        with open(".git/COMMIT_EDITMSG", "r") as f:
            return encode(f.read()).strip("\n")
    except IOError:
        return ""


if __name__ == "__main__":
    msg = "重启西游外网服务器"
    msg = pretty(msg)
    send(msg)
    cmsg = commit_message()
    cmsg = pretty(cmsg)
    if cmsg:
        send(cmsg)
