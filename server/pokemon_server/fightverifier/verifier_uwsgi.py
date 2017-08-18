# coding: utf-8
''
import uwsgi
import uwsgidecorators
import cgi
import raven
import logging
# import lupa
from .verifier import new_runtime, verify
import traceback
import settings
sentry_dsn = settings.SENTRY_DSN


rt = None
sentry_client = None


@uwsgidecorators.postfork
def init():
    global rt, sentry_client
    rt = new_runtime()


def send_sentry(entityID, worldID, sdkType, name, fbID, body='', reason=''):
    message = '角色ID：%s，服务器ID：%s，角色名称：%s' % (entityID, worldID, name)
    sentry_client = raven.Client(dsn=sentry_dsn)
    payload = sentry_client.build_msg('raven.events.Message',
                                      message=message)
    payload.pop('sentry.interfaces.Message')
    addition_encode = 'base64'
    payload.update({'culprit': message,
                    'extra': {
                        'addition': body.encode(addition_encode),
                        'fbID': fbID,
                        'reason': reason,
                        'addition_name': 'fight_replay',
                        'addition_encode': addition_encode
                    },
                    'level': logging.ERROR,
                    'message': message,
                    'modules': {},
                    'platform': 'other',
                    'tags': {'server_id': worldID, 'SDK': sdkType},
                    })
    sentry_client.send(**payload)


def fight_verify_spooler(env):
    try:
        body = env.get('body', "")
        if not body:
            return uwsgi.SPOOL_OK
        result = verify(rt, env['body'])
        result = None
    except:
        send_sentry(
            env['entityID'],
            env['worldID'],
            env['sdkType'],
            env['name'],
            env['fbID'],
            env['body'],
            'verify error:\n' + traceback.format_exc())
    else:
        if not result:
            send_sentry(
                env['entityID'],
                env['worldID'],
                env['sdkType'],
                env['name'],
                env['fbID'],
                env['body'],
                'verify failed')
    return uwsgi.SPOOL_OK

uwsgi.spooler = fight_verify_spooler


def application(env, start_response):
    body = env['wsgi.input'].read()
    qs = cgi.parse_qs(env['QUERY_STRING'])
    entityID = int(qs['entityID'][0])
    uwsgi.spool(body=body,
                entityID=entityID,
                name=qs['name'][0],
                worldID=qs['worldID'][0],
                sdkType=qs['sdkType'][0],
                fbID=qs['fbID'][0])
    start_response('200 OK', [])
    return 'OK'
