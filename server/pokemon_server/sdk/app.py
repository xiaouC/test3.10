# coding: utf-8
import settings
import logging
logger = logging.getLogger('sdk')
from bottle import route, app, request
from gm.proxy import proxy
from gm.proxy import ServerProxyNode
from protocol import poem_pb
from yy.sdk import pay
from .payment import get_payment
from session.utils import sdk_username
from hashlib import md5
from datetime import datetime


PROXIES = {}


def get_proxy(worldID):
    global PROXIES
    if not PROXIES:
        for k, v in getattr(settings, "PROXIES", {}).items():
            PROXIES[k] = ServerProxyNode(*v)
    sessionID = int(worldID) / 100 * 100
    p = PROXIES.get(sessionID)
    if not p:
        return proxy
    return p


application = app()
# Now most exceptions are re-raised within bottle.
application.catchall = False


def do_pay(worldID, entityID, order_id, amount, sdata, sdktype=0, delay=0):
    '支付接口'
    if not entityID or not sdktype:
        payment = get_payment(sdk_username(sdktype, order_id))
        if not entityID:
            entityID = int(payment.get('entityID', 0))
        if not sdktype:
            sdktype = int(payment.get('sdktype', 0))
    params = dict(
        entityId=int(entityID), orderid=order_id,
        amount=str(amount*10),  sdata=sdata,
        rechargegold=str(amount*10), sdktype=sdktype,
        goods=0, delay=delay)
    rsp = get_proxy(worldID).post(
        "sdk_pay/%d?regionID=%d" % (int(entityID), int(worldID)),
        fields=params)
    return rsp.data

sdk_types = {
    'itools':     poem_pb.SDK_ITOOLS_IOS,
    'pp':         poem_pb.SDK_PP_IOS,
    'uc':         poem_pb.SDK_UC,
    'xy':         poem_pb.SDK_XY_IOS,
    'tb':         poem_pb.SDK_TB_IOS,
    'ky':         poem_pb.SDK_KY_IOS,
    'as':         poem_pb.SDK_AS_IOS,
    'iiapple':    poem_pb.SDK_IIAPPLE_IOS,
    'hm':         poem_pb.SDK_HM_IOS,
    'xiaomi':     poem_pb.SDK_XIAOMI,
    'c360':       poem_pb.SDK_C360,
    'oppo':       poem_pb.SDK_OPPO,
    'anzhi':      poem_pb.SDK_ANZHI,
    'wdj':        poem_pb.SDK_WDJ,
    'baidu':      poem_pb.SDK_BAIDU,
    'wanka':      poem_pb.SDK_WANKA,
    'yyb':        poem_pb.SDK_YYB,
    'gfan':       poem_pb.SDK_GFAN,
    'hwd':        poem_pb.SDK_HWD,
    'mm':         poem_pb.SDK_MM,
    'm4399':      poem_pb.SDK_M4399,
    'paojiao':    poem_pb.SDK_PAOJIAO,
    'pipaw':      poem_pb.SDK_PIPAW,
    'youku':      poem_pb.SDK_YOUKU,
    'yyh':        poem_pb.SDK_YYH,
    'zy':         poem_pb.SDK_ZY,
    'kugou':      poem_pb.SDK_KUGOU,
    'egame':      poem_pb.SDK_EGAME,
    'downjoy':    poem_pb.SDK_DOWNJOY,
    'pps':        poem_pb.SDK_PPS,
    'pptv':       poem_pb.SDK_PPTV,
    'mzw':        poem_pb.SDK_MZW,
    'vivo':       poem_pb.SDK_VIVO,
    'huawei':     poem_pb.SDK_HUAWEI,
    'lx':         poem_pb.SDK_LX,
    'gionee':     poem_pb.SDK_GIONEE,
    'haima':      poem_pb.SDK_HAIMA,
    'coolpad':    poem_pb.SDK_COOLPAD,
    'xx':         poem_pb.SDK_XX,
    'xx_ios':     poem_pb.SDK_XX_IOS,
    'meizu':      poem_pb.SDK_MEIZU,
    'kaopu':      poem_pb.SDK_KAOPU,
    'baidu2':     poem_pb.SDK_BAIDU2,
    'wl':         poem_pb.SDK_WL,
    'wl2':        poem_pb.SDK_WL2,
    'haomeng':    poem_pb.SDK_HAOMENG,
    'yijie':      poem_pb.SDK_YIJIE,
    'tiantian':   poem_pb.SDK_TIANTIAN,
    'mmy':        poem_pb.SDK_MMY,
    'h07073':     poem_pb.SDK_H07073,
    'pyw':        poem_pb.SDK_PYW,
}


@route("/sdk/android/sdk/egame/pay_callback", method=['POST'])
def sdk_egame_callback():
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' else request.query_string

    label = 'egame'
    cfg = settings.SDK[label]
    sdktype = sdk_types[label]

    worldID, orderID = request.params['cp_order_id'].split('_')
    if request.params['method'] == 'callback':
        tpl = '<cp_notify_resp><h_ret>%s</h_ret><cp_order_id>%s</cp_order_id></cp_notify_resp>'
        fields = ['cp_order_id', 'correlator', 'result_code', 'fee', 'pay_type', 'method']
        signed = md5(''.join(request.params[f] for f in fields) + cfg['appkey']).hexdigest()
        if signed != request.params['sign']:
            logger.error('[sdk egame] verify failed')
            return tpl % (-1, orderID)
        result = do_pay(
            int(worldID), 0, orderID,
            float(request.params['fee']),
            rawmsg, sdktype=sdktype)
        if 'success' in result:
            return tpl % (0, orderID)
        else:
            logger.error('[sdk egame] pay failed')
            return tpl % (-1, orderID)
    else:
        fields = ['cp_order_id', 'correlator', 'order_time', 'method']
        signed = md5(''.join(request.params[f] for f in fields) + cfg['appkey']).hexdigest()
        if signed != request.params['sign']:
            logger.error('[sdk egame] verify failed2')
            return tpl % (-1, orderID)
        info = get_payment(sdk_username(sdktype, orderID))
        return '''<sms_pay_check_resp>
                    <cp_order_id>%s</cp_order_id>
                    <correlator>%s</correlator>
                    <game_account>%s</game_account>
                    <fee>%s</fee>
                    <if_pay>0</if_pay>
                    <order_time>%s</order_time>
                  </sms_pay_check_resp>''' % (request.params['cp_order_id'],
                                              request.params['correlator'],
                                              request.params['order_time'],
                                              info['price'],
                                              datetime.now().strftime('%Y%m%d%H%M%S'))


@route('/sdk/android/sdk/:label/pay_callback', method=['GET', 'POST'])
@route('/sdk/:label/pay_callback', method=['GET', 'POST'])
def sdk_pay_callback(label):
    cfg = settings.SDK[label]
    mapping = {"baidu2": 'baidu'}
    handler = getattr(pay, 'sdk_%s_callback' % mapping.get(label, label))
    return handler(cfg, request, sdk_types[label], do_pay)


@route("/sdk/zcgame/pay_callback/:worldID/:transaction_id", method=['POST'])
@route("/sdk/zc_ios/pay_callback/:worldID/:transaction_id", method=['POST'])
@route("/sdk/android/zcgame/pay_callback/:worldID/:transaction_id/:sdktype", method=['POST'])
def sdk_zcgame_callback(worldID, transaction_id, sdktype=None):
    sdktype = sdktype is not None and getattr(poem_pb, sdktype, poem_pb.SDK_APP_IOS) or poem_pb.SDK_APP_IOS
    request.transaction_id = transaction_id
    request.worldID = worldID
    # if request.path.startswith('/sdk/zc_ios/'):
    #     sdktype = poem_pb.SDK_ZC_IOS
    return pay.sdk_zcgame_callback(settings.SDK['zcgame'], request, sdktype, do_pay)


@route("/sdk/android/sdk/wanka/:channel/pay_callback", method=['POST'])
def sdk_channel(channel):
    '硬核联盟专用'
    if channel == 'vivo':
        sdktype = poem_pb.SDK_VIVO
    else:
        sdktype = poem_pb.SDK_WANKA

    return pay.sdk_wanka_callback(settings.SDK.get('wanka', {}), request, sdktype, do_pay, channel)


@route("/sdk/android/sdk/wanka/create_order", method=['POST'])
def sdk_wanka_create_order():
    '硬核联盟专用'
    return pay.sdk_wanka_create_order(settings.SDK.get('wanka', {}), request)


@route("/sdk/android/sdk/yyb/info", method=["POST"])
def sdk_yyb_info():
    cfg = settings.SDK['yyb']
    zones = cfg.get("zones", {})
    zoneid = request.params.get("zoneid", 0)
    regionid = int(zones.get(int(zoneid), zoneid))
    return str(regionid)


@route("/sdk/android/sdk/yyb/create_order", method=['POST'])
def sdk_yyb_create_order():
    '应用宝专用'
    return pay.sdk_yyb_create_order(settings.SDK['yyb'], request)


@route("/sdk/android/sdk/yyb/query_balance", method=['POST'])
def sdk_yyb_query_balance():
    '应用宝专用'
    import time
    from msdks.api import Api
    from msdks.payments import get_balance, pay_m, cancel_pay_m
    cfg = settings.SDK['yyb']
    sdktype = poem_pb.SDK_YYB
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' else request.query_string
    api = Api(int(cfg['qq_appid']), cfg['qq_paykey'], [cfg['domain']])
    cookie_args = {
        'session_id': request.params['session_id'],
        'session_type': request.params['session_type'],
        'appip': cfg['qq_appid'],
    }

    worldID, entityID, orderID = request.params['callBackInfo'].split('_')
    zoneid = str(cfg.get("zones", {}).get(int(worldID), int(worldID)))
    if not zoneid:
        return 'failed'
    args = {
        'ts': int(time.time()),
        'zoneid': zoneid,
    }
    fields = ['openid', 'openkey', 'pay_token', 'pf', 'pfkey']
    for f in fields:
        args[f] = request.params[f]

    data = get_balance(api, args, cookie_args)
    logger.info('get balance %s %s %s', args, cookie_args, data)
    if data['ret'] != 0 or data['balance'] <= 0:
        # retry
        retry_count = 3 if orderID else 1
        for i in range(retry_count):
            time.sleep(20)
            data = get_balance(api, args, cookie_args)
            logger.info('retry %d get balance %s %s %s', i, args, cookie_args, data)
            if data['ret'] == 0 and data['balance'] > 0:
                break
        else:
            # retry failed
            return 'failed'

    args = {
        'ts': int(time.time()),
        'amt': data['balance'],
        "userip": request.remote_route[0],
        'zoneid': zoneid,
    }
    fields = ['openid', 'openkey', 'pay_token', 'pf', 'pfkey']
    for f in fields:
        args[f] = request.params[f]

    data = pay_m(api, args, cookie_args)
    logger.info('pay_m %s %s %s', args, cookie_args, data)
    if data['ret'] == 0:
        try:
            result = do_pay(
                int(worldID), int(entityID), orderID,
                float(args['amt']) / 10,
                rawmsg, sdktype=sdktype)
        except:
            logger.exception('do pay failed')
            result = 'fail'

        if 'success' in result:
            return 'success'
        else:
            args['billno'] = data['billno']
            data = cancel_pay_m(api, args, cookie_args)
            if data['ret'] == 0:
                return 'cancelled'
            else:
                logger.error("cancel failed, may lost money %s %s %s", data, args, cookie_args)
                return 'cancel failed'

    return 'failed'


@route("/sdk/android/sdk/huawei/buoy", method=["GET"])
def sdk_hw_buoy():
    return settings.SDK["huawei"]["BUO_SECRET"]


@route("/sdk/android/sdk/huawei/pay", method=["GET"])
def sdk_hw_pay():
    return settings.SDK["huawei"]["PAY_RSA_PRIVATE"]


@route("/sdk/android/sdk/huawei/pay_callback", method=['POST'])
@route('/sdk/huawei/pay_callback', method=['GET', 'POST'])
def sdk_huawei_callback():
    from yy.sdk.pay import rsa_verify
    cfg = settings.SDK["huawei"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    params['sign'] = params['sign'].decode("base64")
    sign = params.pop("sign", "")
    signType = "sha256" if params.pop("signType", "") == "RSA256" else "sha1"
    tosign = '&'.join('%s=%s' % (f, params[f]) for f in sorted(params))
    if not rsa_verify(cfg['PAY_RSA_PUBLIC'], tosign, sign, signType):
        logger.error('[sdk huawei] verify failed %r' % params)
        return {"result": 1}
    entityID, worldID, orderID = params['extReserved'].split('_')
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['amount']),
        rawmsg, sdktype=poem_pb.SDK_HUAWEI)
    if 'success' in result:
        return {"result": 0}
    logger.error('[sdk huawei] pay failed %r' % params)
    return {"result": 3}


def wl_callback(tag):
    import md5
    from xml.dom.minidom import parseString
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string

    def decode(content, synKey):
        # 同步算法解密
        codes = map(int, content.lstrip("@").split("@"))
        keys = map(ord, synKey)
        data = []
        for index, each in enumerate(codes):
            var = keys[index % len(keys)]
            data.append(codes[index] - (0xff & var))
        result = "".join(map(chr, data)).strip()
        return result
    cfg = settings.SDK[tag]
    params = dict(request.params)
    sign = list(decode(params["sign"], cfg["synKey"]))
    sign[1], sign[13] = sign[13], sign[1]
    sign[5], sign[17] = sign[17], sign[5]
    sign[7], sign[23] = sign[23], sign[7]
    sign = "".join(sign)
    checksum = md5.new("nt_data=%s" % params["nt_data"]).hexdigest()
    if sign != checksum:
        logger.error('[sdk %s] verify failed %r' % (tag, params))
        return "failed"
    nt_data_string = decode(params["nt_data"], cfg["synKey"])
    root = parseString(nt_data_string)
    root = root.getElementsByTagName('message')[0]
    data = {}
    for field in ["amount", "status", "order_id", "game_role"]:
        data[field] = root.getElementsByTagName(
            field)[0].childNodes[0].data.strip()
    worldID, entityID, orderID = data['game_role'].split('_')
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(data['amount']),
        rawmsg, sdktype=sdk_types[tag])
    if 'success' in result:
        return "success"
    logger.error('[sdk %s] pay failed %r' % (tag, params))
    return "failed"


@route("/sdk/android/sdk/wl/pay_callback", method=['POST'])
@route('/sdk/wl/pay_callback', method=['GET', 'POST'])
def sdk_wl_callback():
    return wl_callback('wl')


@route("/sdk/android/sdk/wl2/pay_callback", method=['POST'])
@route('/sdk/wl2/pay_callback', method=['GET', 'POST'])
def sdk_wl2_callback():
    return wl_callback('wl2')


@route("/sdk/android/sdk/gionee/create_order", method=['POST'])
def sdk_gionee_create_order():
    'gionee专用'
    import json
    from HJSDK.config import set_config
    from HJSDK import createOrder
    set_config(settings.SDK["gionee"])
    param = dict(request.params)
    channel_instance = createOrder.get_channel_instance(param['returnJson'])
    money = param['amount']
    myOrderID = param['orderid']
    title = param['productName']
    orderDesc = param['description']
    cpinfo = param['cpPrivateInfo']
    retData = channel_instance.invoke_service(
        money, myOrderID, title, orderDesc, cpinfo)
    assert 'errMsg' not in retData, retData['errMsg']
    return json.dumps(retData)


@route("/sdk/android/sdk/vivo/create_order", method=['POST'])
def sdk_vivo_create_order():
    'vivo专用'
    import json
    from HJSDK.config import set_config
    from HJSDK import createOrder
    set_config(settings.SDK["vivo"])
    param = dict(request.params)
    channel_instance = createOrder.get_channel_instance(param['returnJson'])
    money = param['amount']
    myOrderID = param['orderid']
    title = param['productName']
    orderDesc = param['description']
    cpinfo = param['cpPrivateInfo']
    retData = channel_instance.invoke_service(
        money, myOrderID, title, orderDesc, cpinfo)
    assert 'errMsg' not in retData, retData['errMsg']
    return json.dumps(retData)


CpTransSyncSignValid = None


def getCpTransSyncSignValid():
    global CpTransSyncSignValid
    if CpTransSyncSignValid:
        return CpTransSyncSignValid
    import os
    import jpype
    from jpype import JClass
    path = os.path.join(
        os.environ.get("PYTHONPATH", '.'),
        "lenovo_pay_sign-1.0.0.5.jar")
    logger.info("JVM path %s", jpype.getDefaultJVMPath())
    logger.info("class.path %s", path)
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        "-Djava.class.path=%s" % path
    )
    CpTransSyncSignValid = JClass(
        "com.lenovo.pay.sign.CpTransSyncSignValid")
    return CpTransSyncSignValid


@route("/sdk/android/sdk/lx/pay_callback", method=['POST'])
@route('/sdk/lx/pay_callback', method=['GET', 'POST'])
def sdk_lx_callback():
    import json
    cfg = settings.SDK["lx"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    sign = params["sign"]
    transdata = params["transdata"]
    if not getCpTransSyncSignValid().validSign(
            transdata, sign, cfg["LENOVO_KEY"]):
        logger.error('[sdk lx] verify failed %r' % params)
        return "FAILURE"
    params = json.loads(transdata)
    worldID, entityID = params['cpprivate'].split('_')
    result = do_pay(
        int(worldID), int(entityID), params["exorderno"],
        float(params['money']) / 100,
        rawmsg, sdktype=poem_pb.SDK_LX)
    if 'success' in result:
        return "SUCCESS"
    logger.error('[sdk lx] pay failed %r' % params)
    return "FAILURE"


@route("/sdk/android/sdk/vivo/pay_callback", method=['POST'])
@route('/sdk/vivo/pay_callback', method=['GET', 'POST'])
def sdk_vivo_callback():
    cfg = settings.SDK["vivo"]
    from HJSDK import notify
    from HJSDK.config import set_config
    set_config(cfg)
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    channel_instance = notify.get_channel_instance("Vivo")
    if channel_instance:
        retData = channel_instance.invoke_service(request.forms, request.query)
        if retData and retData['paySuccess'] == 1:
            worldID, entityID = retData['cpPrivateInfo'].split('_')
            result = do_pay(
                int(worldID), int(entityID), retData['myOrderNo'],
                float(retData['money']) / 100,
                rawmsg, sdktype=poem_pb.SDK_VIVO)
            if 'success' in result:
                return channel_instance.send_response()
            else:
                return channel_instance.send_response('fail')
    return channel_instance.send_response('fail')


@route("/sdk/android/sdk/coolpad/pay_callback", method=['POST'])
@route('/sdk/coolpad/pay_callback', method=['GET', 'POST'])
def sdk_coolpad_callback():
    cfg = settings.SDK["coolpad"]
    from HJSDK import notify
    from HJSDK.config import set_config
    set_config(cfg)
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    channel_instance = notify.get_channel_instance("Coolpad")
    if channel_instance:
        retData = channel_instance.invoke_service(request.forms, request.query)
        if retData and retData['paySuccess'] == 1:
            worldID, entityID = retData['cpPrivateInfo'].split('_')
            result = do_pay(
                int(worldID), int(entityID), retData['myOrderNo'],
                float(retData['money']) / 100,
                rawmsg, sdktype=poem_pb.SDK_COOLPAD)
            if 'success' in result:
                return channel_instance.send_response()
            else:
                return channel_instance.send_response('fail')
    return channel_instance.send_response('fail')


@route("/sdk/android/sdk/gionee/pay_callback", method=['POST'])
@route('/sdk/gionee/pay_callback', method=['GET', 'POST'])
def sdk_gionee_callback():
    cfg = settings.SDK["gionee"]
    from HJSDK import notify
    from HJSDK.config import set_config
    set_config(cfg)
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    channel_instance = notify.get_channel_instance("Gionee")
    if channel_instance:
        retData = channel_instance.invoke_service(request.forms, request.query)
        if retData and retData['paySuccess'] == 1:
            worldID, entityID = retData['cpPrivateInfo'].split('_')
            result = do_pay(
                int(worldID), int(entityID), retData['myOrderNo'],
                float(retData['money']) / 100,
                rawmsg, sdktype=poem_pb.SDK_GIONEE)
            if 'success' in result:
                return channel_instance.send_response()
            else:
                return channel_instance.send_response('fail')
    return channel_instance.send_response('fail')


@route('/sdk/android/sdk/haima/pay_callback', method=['GET', 'POST'])
@route('/sdk/haima/pay_callback', method=['GET', 'POST'])
def sdk_haima_callback():
    cfg = settings.SDK['haima']
    handler = getattr(pay, 'sdk_hm_callback')
    return handler(cfg, request, sdk_types['haima'], do_pay)


def xx_callback(cfg, request, sdktype, do_pay):
    import md5
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    m = md5.new()
    m.update(params["serialNumber"])
    m.update(params["money"])
    m.update(params["status"])
    m.update(params["t"])
    m.update(cfg["server_secret_key"])
    if params["sign"] != m.hexdigest():
        logger.error(
            '[sdk xx]  sdktype %r verify failed %r' % (sdktype, params))
        return "failure"
    worldID, entityID = params["reserved"].split("_")
    result = do_pay(
        int(worldID), int(entityID), params["serialNumber"],
        float(params['money']),
        rawmsg, sdktype=sdktype)
    if "success" in result:
        return "success"
    logger.error('[sdk xx] sdktype %r pay failed %r' % (sdktype, params))
    return "failure"


@route('/sdk/android/sdk/xx/pay_callback', method=['GET', 'POST'])
@route('/sdk/xx/pay_callback', method=['GET', 'POST'])
def sdk_xx_callback():
    cfg = settings.SDK['xx']
    return xx_callback(cfg, request, sdk_types["xx"], do_pay)


@route('/sdk/xx_ios/pay_callback', method=['GET', 'POST'])
def sdk_xx_ios_callback():
    cfg = settings.SDK['xx_ios']
    return xx_callback(cfg, request, sdk_types["xx_ios"], do_pay)


@route('/sdk/android/sdk/haomeng/pay_callback', method=['GET', 'POST'])
@route('/sdk/haomeng/pay_callback', method=['GET', 'POST'])
def sdk_haomeng_callback():
    from md5 import md5
    cfg = settings.SDK["haomeng"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    sign = md5(''.join([params[f] for f in [
        'uid', 'money', 'time',
        'sid', 'orderid', 'ext',
    ]]) + cfg['pay_key']).hexdigest()
    if sign != params['flag']:
        logger.error('[sdk haomeng]  %r verify failed %r' % params)
        return "3"
    worldID, entityID, orderID = params["ext"].split("_")
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['money']),
        rawmsg, sdktype=poem_pb.SDK_HAOMENG)
    if "success" in result:
        return "1"
    logger.error('[sdk haomeng]  %r pay failed %r' % params)
    return "-1"


@route('/sdk/android/sdk/meizu/pay_callback', method=['GET', 'POST'])
@route('/sdk/meizu/pay_callback', method=['GET', 'POST'])
def sdk_meizu_callback():
    import md5
    cfg = settings.SDK["meizu"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    params.pop("sign_type", "")
    sign = params.pop("sign", "")
    tosign = "&".join("%s=%s" % (f, params[f]) for f in sorted(
        params) if params[f])
    tosign = md5.new(":".join([tosign, cfg["AppSecret"]])).hexdigest()
    if sign != tosign:
        logger.error('[sdk meizu]  %r verify failed %r' % params)
        return {"code": "900000"}
    worldID, entityID = params["user_info"].split("_")
    result = do_pay(
        int(worldID), int(entityID), params["cp_order_id"],
        float(params['total_price']),
        rawmsg, sdktype=poem_pb.SDK_MEIZU)
    if "success" in result:
        return {"code": "200"}
    logger.error('[sdk meizu] %r pay failed %r' % params)
    return {"code": "120014"}


@route('/sdk/android/sdk/kaopu/pay_callback', method=['GET', 'POST'])
@route('/sdk/kaopu/pay_callback', method=['GET', 'POST'])
def sdk_kaopu_callback():
    import md5
    import urllib

    def sign_response(code):
        m = md5.new("|".join([code, cfg["KAOPU_SECRETKEY"]]))
        return {"code": code, "sign": m.hexdigest()}
    cfg = settings.SDK["kaopu"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    sign = params.pop("sign", "")
    params["gamename"] = urllib.unquote(params["gamename"])
    tosign = "|".join(["%s" % params[f] for f in [
        "username", "kpordernum", "ywordernum", "status", "paytype",
        "amount", "gameserver", "errdesc", "paytime", "gamename"
    ]])
    tosign = "|".join([tosign, cfg["KAOPU_SECRETKEY"]])
    tosign = md5.new(tosign).hexdigest()
    if sign != tosign:
        logger.error('[sdk kaopu] verify failed %r' % params)
        return sign_response("1002")
    worldID, entityID, orderID = params["ywordernum"].split("_")
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['amount']) / 100,
        rawmsg, sdktype=poem_pb.SDK_KAOPU)
    if "success" in result:
        return sign_response("1000")
    logger.error('[sdk kaopu] pay failed %r' % params)
    return sign_response("1003")


@route("/sdk/android/sdk/meizu/create_order", method=['GET', 'POST'])
def sdk_meizu_create_order():
    'meizu专用'
    import md5
    cfg = settings.SDK["meizu"]
    params = dict(request.params)
    params.pop("sign_type", "")
    params.pop("sign", "")
    sign = "&".join("%s=%s" % (f, params[f]) for f in sorted(
        params) if params[f])
    sign = md5.new(":".join([sign, cfg["AppSecret"]])).hexdigest()
    return sign


@route('/sdk/android/sdk/m4399/pay_callback', method=['GET', 'POST'])
@route('/sdk/m4399/pay_callback', method=['GET', 'POST'])
def sdk_m4399_callback():
    cfg = settings.SDK["m4399"]
    sdktype = poem_pb.SDK_M4399
    MAX_BODY = 2048
    import urllib
    from yy.sdk.pay import JSONResponse
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST'\
        else request.query_string
    params = dict(request.params)
    values = [params.get(f, "") for f in [
        'orderid', 'uid', 'money', 'gamemoney',
        'serverid', 'mark', 'roleid', 'time']]
    values.insert(5, cfg['appkey'])
    values[6] = urllib.unquote(values[6])
    tosign = ''.join(values)
    if params['sign'] != md5(tosign).hexdigest():
        logger.error('[sdk m4399] verify failed')
        return JSONResponse({
            "status": 1,
            "code": 'sign_error',
        })
    worldID, orderID = params['mark'].split('_')
    # {{
    # 万不得已的做法， FIXME
    # 4399透传参数不能超过32位，所以entityID得不到
    # 只能本地查
    from session.utils import sdk_username
    from sdk.payment import get_payment
    payment = get_payment(sdk_username(sdktype, orderID))
    if not payment:
        return JSONResponse({
            "status": 1,
            "code": 'other_error'})
    entityID = payment["entityID"]
    # }}
    money = float(params['money'])
    result = do_pay(
        int(worldID), int(entityID), orderID,
        money,
        rawmsg, sdktype=sdktype)
    if 'success' in result:
        return JSONResponse({
            "status": 2,
            "code": None,
            "money": money,
            "gamemoney": money * 10,
            "msg": u"充值成功",
        })
    else:
        logger.error('[sdk m4399] pay failed')
        return JSONResponse({
            "status": 1,
            "code": 'other_error'})


@route('/sdk/android/sdk/cc/pay_callback', method=['GET', 'POST'])
@route('/sdk/cc/pay_callback', method=['GET', 'POST'])
def sdk_cc_callback():
    import md5
    cfg = settings.SDK["cc"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    sign = params.pop("sign", "")
    tosign = '&'.join('%s=%s' % (
        f, params[f]) for f in sorted(params) if params[f])
    tosign = "&".join([tosign, cfg["app_key"]])
    tosign = md5.new(tosign).hexdigest()
    if sign != tosign:
        logger.error('[sdk cc] verify failed %r' % params)
        return "0002"
    worldID, entityID, orderID = params["partnerTransactionNo"].split("_")
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['orderPrice']),
        rawmsg, sdktype=poem_pb.SDK_CC)
    if "success" in result:
        return "0000"
    logger.error('[sdk cc] pay failed %r' % params)
    return "0002"


@route('/sdk/android/sdk/yijie/pay_callback', method=['GET', 'POST'])
@route('/sdk/yijie/pay_callback', method=['GET', 'POST'])
def sdk_yijie_callback():
    import md5
    cfg = settings.SDK["yijie"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    sign = params.pop("sign", "")
    tosign = '&'.join('%s=%s' % (
        f, params[f]) for f in sorted(params) if params[f])
    tosign = "".join([tosign, cfg["pay_key"]])
    tosign = md5.new(tosign).hexdigest()
    if sign != tosign:
        logger.error('[sdk yijie] verify failed %r' % params)
        return "FAILED"
    worldID, entityID, orderID = params["cbi"].split("_")
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['fee'])/100.0,
        rawmsg, sdktype=poem_pb.SDK_YIJIE)
    if "success" in result:
        return "SUCCESS"
    logger.error('[sdk yijie] pay failed %r' % params)
    return "FAILED"


@route('/sdk/android/sdk/tiantian/pay_callback', method=['GET', 'POST'])
@route('/sdk/tiantian/pay_callback', method=['GET', 'POST'])
def sdk_tiantian_callback():
    import md5
    import json
    cfg = settings.SDK["tiantian"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)

    sign = params.pop("sign", "")

    sparams = json.dumps(params)
    tosign = md5("/aa/bb" + sparams + cfg["app_key"]).hexdigest()
    if sign != tosign:
        logger.error('[sdk tiantian] verify failed %r' % params)
        raise Exception

    worldID, entityID, orderID = params["cbi"].split("_")
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['fee']),
        rawmsg, sdktype=poem_pb.SDK_TIANTIAN)

    if "success" in result:
        return "SUCCESS"

    logger.error('[sdk tiantian] pay failed %r' % params)
    raise Exception


@route('/sdk/le8/pay_callback', method=['GET', 'POST'])
def sdk_le8_callback():
    import urllib
    import hashlib
    cfg = settings.SDK["le8_ios"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    logger.debug(rawmsg)
    params = dict(request.params)

    sign = params.pop("o_sign", "")

    worldID, entityID = params["u_param"].split("_")
    fields = ['n_time', 'appid', 'o_id', 't_fee', 'g_name', 'g_body', 't_status']
    tosign = '&'.join(['%s=%s' % (k, urllib.quote_plus(params[k])) for k in fields]) + cfg['app_key']
    logger.debug(tosign)
    if hashlib.md5(tosign).hexdigest() != sign:
        logger.error('[sdk le8] verify failed %r' % params)
        raise Exception
    result = do_pay(
        int(worldID), int(entityID), params['o_id'],
        float(params['t_fee']),
        rawmsg, sdktype=poem_pb.SDK_LE8_IOS)

    if "success" in result:
        return "success"

    logger.error('[sdk le8] pay failed %r' % params)
    raise Exception


@route('/sdk/mmy/pay_callback', method=['GET', 'POST'])
def sdk_mmy_callback():
    cfg = settings.SDK["mmy"]
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    sdktype = poem_pb.SDK_MMY

    def check_pay(appkey, data):
        import hashlib
        sign = data.get("tradeSign")
        orderID = data.get("orderID")
        if sign < 14:
            return False
        vstr = sign[0:8]
        dvstr = sign[8:]
        mds = hashlib.md5(dvstr).hexdigest()
        if vstr != mds[0:8]:
            return False
        key_b = dvstr[0:6]
        randkey = "%s%s" % (key_b, appkey)
        randkey = hashlib.md5(randkey).hexdigest()

        def _check_b64(strg):
            import base64
            missing_padding = 4 - len(strg) % 4
            if missing_padding:
                strg += b'=' * missing_padding
            result = base64.b64decode(strg)
            return result
        dv = _check_b64(dvstr[6:])
        dvlen = len(dv)
        st = ""
        for i in range(dvlen):
            st += chr(ord(dv[i]) ^ ord(randkey[i % 32]))
        if st == orderID:
            return True
        return False
    if not check_pay(cfg["appKey"], params):
        logger.error('[sdk mmy] invalid failed %r' % params)
        return 'fail'
    worldID, entityID, orderID = params["productDesc"].split("_")
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['productPrice']),
        rawmsg, sdktype=sdktype)
    if "success" in result:
        return "success"
    logger.error('[sdk mmy] pay failed %r' % params)
    return 'fail'


@route('/sdk/h07073/pay_callback', method=['GET', 'POST'])
def sdk_h07073_callback():
    cfg = settings.SDK["h07073"]
    sdktype = poem_pb.SDK_H07073
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    import json
    params = json.loads(dict(request.params).get("data", ""))
    from md5 import md5
    fields = ['amount', 'gameid', 'orderid', 'serverid', 'time', 'uid']
    sign = "&".join(["%s=%s" % (f, params[f]) for f in fields])
    sign = md5(sign + cfg['secretKey']).hexdigest()
    if params["sign"] != sign:
        logger.error('[sdk h07073] invalid failed %r %r' % (params, sign))
        return 'fail'
    worldID, entityID, orderID = params["extendsInfo"].split("_")
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['amount']),
        rawmsg, sdktype=sdktype)
    if "success" in result:
        return "succ"
    logger.error('[sdk h07073] pay failed %r' % params)
    return 'fail'


@route('/sdk/pyw/pay_callback', method=['GET', 'POST'])
def sdk_pyw_callback():
    cfg = settings.SDK["pyw"]
    sdktype = poem_pb.SDK_PYW
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    import json
    params = json.loads(rawmsg)
    from md5 import md5
    fields = ['cp_orderid', 'ch_orderid', 'amount']
    sign = "".join(["%s" % params[f] for f in fields])
    sign = md5(cfg['apiSecret'] + sign).hexdigest()
    if params["sign"] != sign:
        logger.error('[sdk pyw] validate failed %r %r' % (params, sign))
        return {'ack': 500, 'msg': '验证失败'}
    worldID, entityID = json.loads(params["cp_param"])["area_num"].split("_")
    result = do_pay(
        int(worldID), int(entityID), params["cp_orderid"],
        float(params['amount']),
        rawmsg, sdktype=sdktype)
    if "success" in result:
        return {'ack': 200, 'msg': 'Ok'}
    logger.error('[sdk pyw] pay failed %r' % params)
    return {'ack': 500, 'msg': '发货失败'}


@route('/sdk/liulian/pay_callback', method=['GET', 'POST'])
def sdk_liulian_callback():
    cfg = settings.SDK["liulian"]
    sdktype = poem_pb.SDK_LIULIAN
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    import urlparse
    params = dict([(k, v[0]) for k, v in urlparse.parse_qs(rawmsg).items()])
    params.update(privatekey=cfg['privatekey'])
    from md5 import md5
    fields = ['appid', 'privatekey', 'orderId', 'userId', 'serverId', 'roleId', 'roleName', 'money', 'extInfo', 'status']
    sign = "".join(["%s" % params[f] for f in fields])
    sign = md5(sign).hexdigest()
    if params["sign"] != sign:
        logger.error('[sdk liulian] validate failed %r %r' % (params, sign))
        return "FAILURE"
    worldID, entityID, orderID = params["extInfo"].split("_")
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['money']),
        rawmsg, sdktype=sdktype)
    if "success" in result:
        return "SUCCESS"
    logger.error('[sdk liulian] pay failed %r' % params)
    return "FAILURE"


@route('/sdk/moge/pay_callback', method=['GET', 'POST'])
def sdk_moge_callback():
    cfg = settings.SDK["moge"]
    sdktype = poem_pb.SDK_MOGE
    MAX_BODY = 2048
    rawmsg = request.body.read(MAX_BODY) if request.method == 'POST' \
        else request.query_string
    params = dict(request.params)
    params.update(appkey=cfg['appkey'])
    from md5 import md5
    fields = ['orderid', 'username', 'gameid', 'roleid', 'serverid', 'paytype', 'amount', 'paytime', 'attach', 'appkey']
    sign = md5("&".join(["%s=%s" % (f, params[f]) for f in fields])).hexdigest()
    if params["sign"] != sign:
        logger.error('[sdk moge] validate failed %r %r' % (params, sign))
        return "errorSign"
    worldID, entityID, orderID = params["attach"].split("_")
    result = do_pay(
        int(worldID), int(entityID), orderID,
        float(params['amount']),
        rawmsg, sdktype=sdktype)
    if "success" in result:
        return "success"
    logger.error('[sdk moge] pay failed %r' % params)
    return "error"


if __name__ == "__main__":
    import gevent.monkey
    gevent.monkey.patch_all()
    from gevent.pywsgi import WSGIServer

    logger.info(
        'listening %s:%d',
        settings.SDKAPP['host'],
        settings.SDKAPP['port'])

    # {{{ Sentry
    if hasattr(settings, 'SENTRY_DSN'):
        from raven import Client
        from raven.contrib.bottle import Sentry
        if settings.SENTRY_DSN:
            client = Client(settings.SENTRY_DSN)
            application = Sentry(application, client)
        logger.info('setup sentry with {}'.format(settings.SENTRY_DSN))
    # }}}

    WSGIServer((
        settings.SDKAPP['host'],
        settings.SDKAPP['port']), application).serve_forever()

# vim: set fdm=marker:
