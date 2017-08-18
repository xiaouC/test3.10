# coding: utf-8
from utils import *

def delete_role(sock, entityID):
    sock.sendall(request_msg(msgid.DELETE_ACTOR, role_pb2.DeleteRoleRequest(roleId=entityID, password='')))
    return expect(msgid.DELETE_ACTOR, role_pb2.DeleteRoleResponse)

def random_name(sock, sex):
    sock.sendall(request_msg(msgid.RANDOM_ACTOR_NAME, role_pb2.RandomNameRequest(sex=sex)))
    return expect(msgid.RANDOM_ACTOR_NAME, role_pb2.RandomNameResponse)

def create_role(sock, sex, school, name=None):
    if not name:
        name = random_name(sock, sex).names[0]
    sock.sendall(request_msg(msgid.NEW_ACTOR, role_pb2.CreateRoleRequest(
        name=name[:6],
        sex=sex,
        school=school,
        iconID=1,
    )))
    return expect(msgid.NEW_ACTOR, role_pb2.CreateRoleResponse, allow_error=True)

def run(verify_code, ip, port):
    sock = socket.create_connection((ip, port))
    set_expect_sock(sock)
    rsp = login_world(sock, verify_code)
    # delete role
    if rsp.roles:
        print 'delete role', delete_role(sock, rsp.roles[0].id)
    rsp = create_role(sock, 1, 3, u'法轮功')
    assert rsp==msgTips.FAIL_MSG_LOGIN_PLAYERNAME_FORBIDDEN, rsp
    rsp = create_role(sock, 1, 3, u'赵云')
    assert rsp==msgTips.FAIL_MSG_LOGIN_PLAYERNAME_FORBIDDEN, rsp
    rsp = create_role(sock, 1, 3)
    print 'new role rsp', rsp
    rsp = enter(sock, rsp.roleId, True)
    print 'enter rsp', rsp
    return rsp

if __name__ == '__main__':
    import sys
    if len(sys.argv)>1:
        rsp = ensure_sdk_login(sys.argv[1])
    else:
        rsp = ensure_sdk_login()
    info = rsp.servers[0]
    print run(rsp.verify_code, info.ip, int(info.port))
