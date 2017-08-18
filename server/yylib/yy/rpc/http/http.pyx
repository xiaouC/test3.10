# coding: utf-8
import traceback
from six.moves import http_cookies
from cprotobuf import ProtoEntity, encode_data

from yy.cutils import get_cookie_value
from .session import SessionStore
from .exceptions import MethodKeyCollide, ApplicationError

cimport cython

@cython.freelist(100)
cdef class Request:
    cdef object msgid
    cdef public dict env
    cdef public bytes body

    cdef bytes _sid

    def __init__(self, msgid, env):
        self.msgid = msgid
        self.env = env
        if env['REQUEST_METHOD'] == 'POST':
            self.body = env['wsgi.input'].read()
        else:
            self.body = None

        uwsgi = env.get('uwsgi.version')
        if uwsgi:
            try:
                env['REMOTE_ADDR'] = self.remote_route[0]
            except IndexError:
                pass

    property sid:
        def __get__(self):
            if not self._sid:
                self._sid = get_cookie_value(self.env.get('HTTP_COOKIE'), 'sid')
            return self._sid
        def __set__(self, v):
            self._sid = v

    property remote_route:
        def __get__(self):
            """ A list of all IPs that were involved in this request, starting with
                the client IP and followed by zero or more proxies. This does only
                work if all proxies support the ```X-Forwarded-For`` header. Note
                that this information can be forged by malicious clients. """
            proxy = self.env.get('HTTP_X_FORWARDED_FOR')
            if proxy:
                return [ip.strip() for ip in proxy.split(',')]
            remote = self.env.get('REMOTE_ADDR')
            return [remote] if remote else []

    cdef release(self):
        pass

cdef encode_response(rsp):
    if rsp is None:
        return ''
    elif isinstance(rsp, tuple):
        bs = bytearray()
        encode_data(bs, rsp[0], rsp[1])
        return bs
    elif isinstance(rsp, ProtoEntity):
        return rsp.SerializeToString()
    else:
        return rsp

class Application(object):
    def __init__(self):
        self.rpcmap = {}

    def rpcmethod(self, key):
        def decorator(func):
            func._rpc_method_key = key
            if key in self.rpcmap:
                raise MethodKeyCollide(key)
            self.rpcmap[key] = func
            return func
        return decorator

    def __call__(self, dict env, start_response):
        cdef bytes path = env['PATH_INFO']
        cdef object msgid = int(path[1:])
        try:
            handler = self.rpcmap[msgid]
        except KeyError:
            start_response('404 Not Found', [('Content-Type', 'text/plain')
                                            ,('Content-Length', '0')])
            return []
        else:
            req = Request(msgid, env)
            try:
                response = handler(req)
            except ApplicationError as e:
                # any exception
                err = unicode(e).encode('utf-8')
                start_response('740 Computer says no', [('Content-Type', 'text/plain')
                                                       ,('Content-Length', str(len(err)))])
                return [err]
            except:
                # unknown exception
                traceback.print_exc()
                start_response('500 Internal Server Error', [('Content-Type', 'text/plain')
                                                            ,('Content-Length', '0')])
                return []
            else:
                rsp = encode_response(response)
                headers = [('Content-Type', 'application/protobuf')
                          ,('Content-Length', str(len(rsp)))]

                ## set session cookie
                if req.sid:
                    sid = http_cookies.Morsel()
                    sid.set('sid', req.sid, req.sid)
                    sid['path'] = '/'
                    sid['domain'] = ''
                    #sid['secure'] = False 
                    sid['httponly'] = True

                    headers.append( ('Set-Cookie', sid.output(header='')) )

                start_response('200 OK', headers)
                return [rsp]
            finally:
                req.release()
