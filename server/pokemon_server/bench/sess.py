# coding: utf-8
import os
from session.main import application
from cStringIO import StringIO
from protocol import poem_pb
from session.regions import reload_regions
reload_regions()


def build_env(msgid, body):
    return {
        'REQUEST_METHOD': 'POST',
        'wsgi.input': StringIO(body),
        'PATH_INFO': '/%s' % msgid,
        'HTTP_COOKIE': '',
    }


def get_tester(msgid, body):
    env = build_env(msgid, body)
    bodyfile = env['wsgi.input']
    app = application
    status = [None]

    def start_response(st, headers):
        status[0] = st

    cb = start_response

    def test():
        bodyfile.reset()
        return app(env, cb), status[0]

    return test, env, body


class Tester(object):
    msgid = None
    request_cls = None
    response_cls = None
    data = None

    def __init__(self, data=None):
        if data:
            self.data = data
        body = self.build_request(self.data)
        self.tester, self.env, self.body = get_tester(self.msgid, body)

    def build_request(self, data):
        return self.request_cls(**data).SerializeToString()

    def verify(self):
        data, status = self.tester()
        code = status.split(' ', 1)[0]
        if code == '200':
            rsp = self.response_cls()
            rsp.ParseFromString(str(data[0]))
            print rsp
        else:
            print status, data[0]


class LoginTester(Tester):
    msgid = poem_pb.LOGIN_KEY
    request_cls = poem_pb.HTTPLoginRequest
    response_cls = poem_pb.HTTPLoginResponse
    data = dict(username='test_robot2_7', password='testtesttest', regionID=100, sdkType=poem_pb.SDK_YY)

class RegisterTester(Tester):
    msgid = poem_pb.CREATE_USER
    request_cls = poem_pb.RegisterRequest
    response_cls = poem_pb.RegisterResponse
    data = dict(username='test_robot2_7', password='testtesttest', imsi='test', tid='test', sdkType=poem_pb.SDK_YY)

def run_bench(cls):
    import patch_socket
    t = cls()
    # record once
    patch_socket.run_with_recording(rds._sock, bench)
    t.verify()

    import timeit
    timeit.main(['-s', 'from __main__ import t',
                '-n', '100', 't.tester()'])
    #import cProfile
    #cProfile.run('for i in xrange(100):t.tester()',
    #             sort='time')

def run_ab(cls):
    t = cls()
    t.verify()
    open('/tmp/tmp-http-body', 'wb').write(t.body)
    cmd = 'ab -p /tmp/tmp-http-body http://127.0.0.1:29000%s' % t.env['PATH_INFO']
    print cmd
    #os.system(cmd)

if __name__ == '__main__':
    run_ab(RegisterTester)
    run_ab(LoginTester)
