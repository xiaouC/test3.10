import sys
from protocol import poem_pb
from protocol.poem_pb import *  # NOQA
from test.utils import request_msg
from test.utils import auto_http_enter
from expecter import expect


def send(name, msgid, data="", resp_struct="", allow_error=True):
    try:
        msgid = int(msgid)
    except ValueError:
        pass
    if isinstance(msgid, basestring):
        msgid = getattr(poem_pb, msgid)
    assert isinstance(data, basestring),\
        "Sending data(%r) not supported" % data
    data = eval(data)  # TODO ugly
    sock = auto_http_enter(name)
    sock.sendall(request_msg(msgid, data))
    if resp_struct:
        resp_struct = getattr(poem_pb, resp_struct)
    else:
        resp_struct = None
    return expect(msgid, klass=resp_struct, allow_error=allow_error)


if __name__ == "__main__":
    print send(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
