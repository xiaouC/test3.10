# coding:utf-8
from test.patch_socket import start_replay, start_record
import cProfile, pstats, timeit
from cStringIO import StringIO
from yy.utils import load_settings
load_settings()


def set_poolmax(n):
    import settings
    for p in settings.REDISES.values():
        p.max_count = 1

set_poolmax(1)


def get_all_socks():
    import settings
    socks = []
    for p in settings.REDISES.values():
        with p.ctx() as conn:
            conn.connect()
            socks.append(conn._sock)
    return socks


from yy.rpc.http import Request
from session.views import login
import protocol.poem_pb as msgid
from protocol import poem_pb


def profile(socks):
    def decorator(func):
        def _inner(*args, **kwargs):
            start_record(socks)
            results = func(*args, **kwargs)

            def tmp():
                start_replay(socks)
                func(*args, **kwargs)

            pr = cProfile.Profile()
            pr.enable()

            for i in xrange(1000):
                tmp()

            pr.disable()
            pstats.Stats(pr).sort_stats('time').print_stats()

            # timeit
            globals()['__tmp'] = tmp
            timeit.main(['-s', 'from __main__ import __tmp',
                        '-n', '1000', '__tmp()'])

            return results
        return _inner
    return decorator


@profile(get_all_socks())
def do_login(body):
    #for i in range(1000):
    request = Request(msgid.LOGIN, {
        "REQUEST_METHOD": "POST",
        "wsgi.input": StringIO(body)
    })
    login(request)

if __name__ == "__main__":
    body = poem_pb.HTTPLoginRequest(
        username="test_robot2_1",
        password="testtesttest",
        regionID=100,
        sdkType=poem_pb.SDK_YY,
    ).SerializeToString()
    do_login(body)
