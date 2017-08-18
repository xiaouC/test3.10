#coding:utf-8
import struct

# (msglen, msgtype, msgcode)
header_format = '>III'
header_size = struct.calcsize(header_format)

def success_msg(msgtype, msg=None):
    if msg:
        body = msg.SerializeToString()
    else:
        body = ''
    msglen = len(body)+header_size
    header = struct.pack(header_format, msglen, msgtype, 0)
    return header+body

def fail_msg(msgtype, code=34, reason=''):
    msglen = len(reason)+1+header_size
    header = struct.pack(header_format, msglen, msgtype, code)
    return ''.join([header, reason, '\0'])

def request_msg(msgtype, msg=''):
    'for test'
    if msg:
        body = msg.SerializeToString()
    else:
        body = ''
    msglen = len(body)+header_size
    header = struct.pack(header_format, msglen, msgtype, 0)
    return header+body

def clean_msgtype(msgtype):
    if msgtype < 0xFFFF:
        return msgtype
    return 0xFFFF & msgtype
