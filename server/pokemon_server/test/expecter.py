# coding: utf-8
'测试脚本等待消息'
import time
from collections import defaultdict
import logging
logger = logging.getLogger('test')
from yy.message.reader import MessageReader
from yy.message.header import header_size
from gevent import getcurrent
from test.listener import g_listener
import traceback

class ExpectException(Exception):
    def __init__(self, message, msgtype, code, body):
        super(ExpectException, self).__init__(message%(msgtype, code, body))
        self.msgtype = msgtype
        self.code = code
        self.body = body.strip('\x00')

class MessageExpect(object):
    def __init__(self, gen):
        self.message_gen = gen
        self.stream_sum = defaultdict(int)

    def print_stream_sum(self):
        print '流量统计', sum(self.stream_sum.values())
        for k, v in sorted(self.stream_sum.items(), key=lambda (k,v):v, reverse=True):
            print k, v

    def expect(self, msgtype, klass=None, allow_error=False):
        gen = self.message_gen
        while True:
            t, body,code = gen.next()

            # 统计流量
            self.stream_sum[t] += header_size + len(body)

            if code!=0:
                if allow_error:
                    return code, body
                else:
                    raise ExpectException('got error message %d %d %s', msgtype, code, body)

            if isinstance(msgtype, dict):
                if t in msgtype:
                    klass = msgtype[t]
                    d = klass()
                    d.ParseFromString(body)
                    return d
            elif t==msgtype:
                if klass:
                    d = klass()
                    d.ParseFromString(body)
                    return d
                else:
                    return body
            else:
                #print 'unexpect msg', t, repr(body)
                g_listener.listen(t, body)
                pass

g_expecters = {}
def set_expect_sock(sock):
    g_expecters[getcurrent()] = MessageExpect(MessageReader(sock).read_message())

def expect(msgtype, klass=None, allow_error=False, key=None):
    begin = time.time()
    r = get_expector(key).expect(msgtype, klass, allow_error)
    cost = time.time()-begin
    if cost>1:
        print '延迟', msgtype, cost
    return r

def get_expector(key=None):
    key = key or getcurrent()
    return g_expecters[key]
