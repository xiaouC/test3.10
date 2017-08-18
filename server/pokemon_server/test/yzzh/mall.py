#coding:utf-8
from test.utils import *
from protocol import poem_pb
import protocol.poem_pb as msgid

def buy_sp():
    print 'buy_sp'
    req = poem_pb.BuySPRequest()
    sock = get_peer(getcurrent())
    try:
        sock.sendall(request_msg(msgid.BUY_SP, req))
        rsp = expect(msgid.BUY_SP)
    except ExpectException as e:
        if e.body == '恢复药不足':
            req.usegold = True
            sock.sendall(request_msg(msgid.BUY_SP, req))
            rsp = expect(msgid.BUY_SP)
        elif e.body.startswith('能量恢复'):
            return
    return rsp

def expand_pet_box():
    print 'expand_pet_box'
    sock = get_peer(getcurrent())
    sock.sendall(request_msg(msgid.EXPAND_PET_BOX))
    return expect(msgid.EXPAND_PET_BOX)
