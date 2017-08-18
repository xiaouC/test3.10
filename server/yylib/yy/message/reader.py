# coding: utf-8
import struct
from header import header_format, header_size
from gevent import Timeout
import settings
from exceptions import CloseServer
from exceptions import ConnectionClosed

BUFFER_SIZE = 1024
class MessageReader(object):
    def __init__(self, sock, server= None):
        self._socket = sock
        self._server = server

    # 获取信息
    def getMessageContext(self):
        if settings.TIMEOUTCLOSESERVER:
            # 加入超时检测
            while True:
                s = 'timed out'
                with Timeout(10, False):
                    s = self._socket.recv(BUFFER_SIZE)
                if self._server and self._server.closeserver:
                    raise CloseServer
                if s ==  'timed out':
                    continue
                break
        else:
            s = self._socket.recv(BUFFER_SIZE)
        return s
        
    def read_message(self):
        leftover = ''
        while True:
            # read header
            while len(leftover)<header_size:
                s = self.getMessageContext()
#                    print 'recv:', repr(s)
                if not s:
                    raise ConnectionClosed
                leftover += s
            
            msglen, msgtype, code = struct.unpack(header_format, leftover[:header_size])
            leftover = leftover[header_size:]
            bodysize = msglen-header_size

            while len(leftover) < bodysize:
                s = self.getMessageContext()
                #print 'recv:', repr(s)
                if not s:
                    raise ConnectionClosed
                leftover += s

            body = leftover[:bodysize]
            leftover = leftover[bodysize:]

            yield msgtype, body, code

def simple_read(fp, rspcls):
    'for test client'
    s = fp.read(header_size)
    assert s, u'异常断开'
    msglen, msgtype, code = struct.unpack(header_format, s)
    if msglen>header_size:
        body = fp.read(msglen-header_size)
        assert body, u'异常断开'
    else:
        body = ''
    if code==0:
        rsp = rspcls()
        rsp.ParseFromString(body)
        return rsp
    else:
        return body[:-1]
