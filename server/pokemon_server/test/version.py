from utils import *

if __name__ == '__main__':
    import sys
    sock = conn_session()
    set_expect_sock(sock)
    sock.sendall(request_msg(msgid.CHECK_UPGRADE, session_pb2.CheckUpgrade(version=int(sys.argv[1]))))
    rsp = expect(msgid.CHECK_UPGRADE, session_pb2.CheckUpgradeResponse)
    print rsp
