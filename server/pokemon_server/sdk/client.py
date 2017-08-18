# coding: utf-8
import logging
logger = logging.getLogger('sdk')

from protocol import poem_pb
import settings

from yy.sdk.login import check_login_hm as check_login_haima  # android IOS 共用

from urllib3 import PoolManager
sdk_poolmanager = PoolManager(num_pools=10)


def check_login_huawei(request, cfg, sid, uin):
    import time
    import json
    # from urllib3 import PoolManager
    # sdk_poolmanager = PoolManager(num_pools=10)
    access_token = unicode(sid).encode("utf-8")
    args = {
        "nsp_svc": "OpenUP.User.getInfo",
        "nsp_ts": int(time.time()),
        "access_token": access_token,
    }
    rsp = sdk_poolmanager.request('GET', cfg['LOGIN_URL'], fields=args)
    if rsp.status == 200:
        try:
            data = json.loads(rsp.data)
        except ValueError:
            logger.error(
                '[sdk huawei]decode check login response failed %s', rsp.data)
            return False
        if data.get('error'):
            logger.error('[sdk huawei]check login status failed %s',
                         data.get('error'))
            return False
    else:
        logger.error(
            '[sdk huawei]check login status %d', rsp.status)
        return False
    return data["userID"]


def check_login_wl(request, cfg, sid, uin, tag="wl"):
    import md5
    import json
    # from urllib3 import PoolManager
    # sdk_poolmanager = PoolManager(num_pools=10)

    def sendwl(uri, params, pool):
        sign = "&".join("%s=%s" % (f, params[f]) for f in sorted(params))
        sign = "&".join(["__e__=1", sign, "appKey=%s" % cfg["appKey"]])
        sign = list(md5.new(sign).hexdigest())
        sign[1], sign[13] = sign[13], sign[1]
        sign[5], sign[17] = sign[17], sign[5]
        sign[7], sign[23] = sign[23], sign[7]
        params["sign"] = "".join(sign)
        params["__e__"] = "1"
        rsp = sdk_poolmanager.request("POST", uri, fields=params)
        if rsp.status == 200:
            try:
                data = json.loads(rsp.data)
            except ValueError:
                logger.error("params %r", params)
                logger.error(
                    "[sdk %s] %s req %r failed %s", tag, uri, sid, rsp.data)
                return False
            if data.get('codes'):
                logger.error("params %r", params)
                logger.error("[sdk %s] %s req %r failed %r",
                             tag, uri, sid, data)
                return False
        else:
            logger.error("params %r", params)
            logger.error(
                "[sdk %s] %s status %d", tag, uri, rsp.status)
            return False
        return data

    uri = "%s/%s" % (cfg["login_url"], "getToken.lg")
    token = sendwl(uri, {
        'redirect_uri': '1',
        'grant_type': 'authorization_code',
        'code': sid,
        'productId': cfg['productId'],
        'client_id': cfg['client_id'],
        'client_secret': cfg['client_secret'],
    }, sdk_poolmanager)
    if not token:
        return False
    uri = "%s/%s" % (cfg["login_url"], "getUserInfo.lg")
    data = sendwl(uri, {
        'productId': cfg['productId'],
        'access_token': token["access_token"],
    }, sdk_poolmanager)
    if not data:
        return False
    return data["userID"]


def check_login_lx(request, cfg, sid, uin):
    from xml.dom.minidom import parseString
    # from urllib3 import PoolManager
    # sdk_poolmanager = PoolManager(num_pools=10)
    args = {
        "realm": cfg["OPEN_APP_ID"],
        "lpsust": sid,
    }
    rsp = sdk_poolmanager.request('GET', cfg['login_url'], fields=args)
    if rsp.status == 200:
        try:
            dom = parseString(rsp.data)
        except ValueError:
            logger.error(
                '[sdk lx] decode check login response failed %s', rsp.data)
            return False
    else:
        logger.error(
            '[sdk lx] check login status %d', rsp.status)
        return False
    return dom.getElementsByTagName("AccountID")[0].childNodes[0].data


def check_login_gionee(request, cfg, sid, uin):
    import json
    from HJSDK import auth
    from HJSDK.config import set_config
    set_config(cfg)
    proxy_obj = {
        "channel": "Gionee",
        "auth_code": "",
        "access_token": sid,
        "token_secret": "",
    }
    channel_instance = auth.get_channel_instance(json.dumps(proxy_obj))
    if channel_instance:
        retData = channel_instance.invoke_service()
        if 'errMsg' in retData:
            logger.error('[sdk gionee] response invalid %s', retData)
            return False
        return retData['open_id'], json.dumps(retData)


def check_login_coolpad(request, cfg, sid, uin):
    import json
    from HJSDK import auth
    from HJSDK.config import set_config
    set_config(cfg)
    proxy_obj = {
        "channel": "Coolpad",
        "auth_code": sid,
        "access_token": "",
        "token_secret": "",
    }
    channel_instance = auth.get_channel_instance(json.dumps(proxy_obj))
    if channel_instance:
        retData = channel_instance.invoke_service()
        if 'errMsg' in retData:
            logger.error('[sdk coolpad] response invalid %s', retData)
            return False
        return retData['open_id'], json.dumps(retData)


def check_login_vivo(request, cfg, sid, uin):
    import json
    from HJSDK import auth
    from HJSDK.config import set_config
    set_config(cfg)
    proxy_obj = {
        "channel": "Vivo",
        "auth_code": "",
        "access_token": sid,
        "token_secret": "",
    }
    channel_instance = auth.get_channel_instance(json.dumps(proxy_obj))
    if channel_instance:
        retData = channel_instance.invoke_service()
        if 'errMsg' in retData:
            logger.error('[sdk vivo] response invalid %s', retData)
            return False
        return retData['open_id'], json.dumps(retData)


def check_login_xx(request, cfg, sid, uin):
    import md5
    import time
    # from urllib3 import PoolManager
    # sdk_poolmanager = PoolManager(num_pools=10)
    url = "http://guopan.cn/gamesdk/verify/"
    params = {
        "game_uin": uin,
        "token": sid,
        "t": str(int(time.time())),
        "appid": cfg["APP_ID"],
    }
    m = md5.new()
    m.update(params["game_uin"] + params["appid"])
    m.update(params["t"] + cfg["server_secret_key"])
    params["sign"] = m.hexdigest()
    rsp = sdk_poolmanager.request('GET', url, fields=params)
    if rsp.status == 200:
        if "true" not in rsp.data:
            logger.error("[sdk xx] check login failed %r", rsp.data)
            return False
    else:
        logger.error('[sdk lx] check login status %d', rsp.status)
        return False
    return uin


def check_login_meizu(request, cfg, sid, uin):
    import md5
    import json
    import time
    # from urllib3 import PoolManager
    # sdk_poolmanager = PoolManager(num_pools=10)
    url = "https://api.game.meizu.com/game/security/checksession"
    params = {
        'app_id': cfg["AppID"],
        "session_id": sid,
        "uid": uin,
        "ts": int(time.time() * 1000),
    }
    sign = "&".join("%s=%s" % (f, params[f]) for f in sorted(params))
    sign = md5.new(":".join([sign, cfg["AppSecret"]])).hexdigest()
    params["sign_type"] = "md5"
    params["sign"] = sign
    rsp = sdk_poolmanager.request('POST', url, fields=params)
    if rsp.status == 200:
        try:
            data = json.loads(rsp.data)
        except ValueError:
            logger.error("params %r", params)
            logger.error("[sdk meizu] req %r failed %s", sid, rsp.data)
            return False
        if data.get('code', 0) == 200:
            logger.error("params %r", params)
            logger.error("[sdk meizu] req %s failed %s", sid, data)
            return False
    else:
        logger.error("params %r", params)
        logger.error("[sdk meizu] %s status %d", url, rsp.status)
        return False
    return uin


def check_login_kaopu(request, cfg, sid, uin):
    import md5
    import json
    # from urllib3 import PoolManager
    # sdk_poolmanager = PoolManager(num_pools=10)
    SECRETS = [
        "18257284-7F5D-348D-AB09-299E5B7DD997",
        "655A957D-157D-7C21-E3A7-9CAAFA835318",
        "F467CA93-D550-346D-6BCB-173995F7C83A",
        "BD32817A-99F9-2E26-5B33-15208F7B360A"]

    def request_url(url, params):
        to_sign = "".join("%s" % params[f] for f in sorted(params))
        params["sign"] = md5.new(
            to_sign + SECRETS[int(params["r"])]).hexdigest()
        rsp = sdk_poolmanager.request('GET', url, fields=params)
        if rsp.status == 200:
            try:
                data = json.loads(rsp.data)
            except ValueError:
                logger.error("params %r", params)
                logger.error("[sdk kaopu] %s req failed %s", url, rsp.data)
                return False
            if int(data.get('code', 0)) != 1:
                logger.error("params %r", params)
                logger.error("[sdk kaopu] %s req failed %s", url, data)
                return False
        else:
            logger.error("params %r", params)
            logger.error("[sdk kaopu] %s status %d", url, rsp.status)
            return False
        return data
    url = "http://sdk.geturl.kpzs.com/api/UserAuthUrl"
    params = {
        "tag": cfg["KAOPU_APPKEY"],
        "tagid": cfg["KAOPU_SECRETKEY"],
        "appid": cfg["KAOPU_APPID"],
        "version": cfg["KAOPU_APPVERSION"],
        "r": "1",
        "imei": request.deviceInfo.IMEI,
        "channelkey": "kaopu",
    }
    data = request_url(url, params)
    if not data:
        return False
    auth_url = data["data"]["url"]
    params = {
        "devicetype": "android",
        "imei": request.deviceInfo.IMEI,
        "r": "1",
        "tagid": cfg["KAOPU_SECRETKEY"],
        "tag": cfg["KAOPU_APPKEY"],
        "appid": cfg["KAOPU_APPID"],
        "channelkey": "kaopu",
        "openid": uin,
        "token": sid,
    }
    data = request_url(auth_url, params)
    if not data:
        return False
    return uin


def check_login_pp(request, cfg, sid, uin):
    import md5
    import json
    import time
    # from urllib3 import PoolManager
    # sdk_poolmanager = PoolManager(num_pools=10)
    url = "http://passport_i.25pp.com:8080/account?tunnel-command=2852126760"
    params = {
        "id": int(time.time()),
        "service": "account.verifySession",
        "data": {"sid": sid},
        "game": {"gameId": cfg["AppId"]},
        "encrypt": "MD5",
    }
    sign = md5.new("sid=%s%s" % (sid, cfg["AppKey"])).hexdigest()
    params["sign"] = sign
    rsp = sdk_poolmanager.urlopen(
        'POST', url, headers={"Content-Type": "application/json"},
        body=json.dumps(params))
    if rsp.status == 200:
        try:
            data = json.loads(rsp.data)
        except ValueError:
            logger.error("params %r", params)
            logger.error("[sdk pp] req %r failed %s", sid, rsp.data)
            return False
        if int(data.get('state', {}).get("code", 0)) != 1:
            logger.error("params %r", params)
            logger.error("[sdk pp] req %s failed %s", sid, data)
            return False
    else:
        logger.error("params %r", params)
        logger.error("[sdk pp] %s status %d", url, rsp.status)
        return False
    return data["data"]["accountId"]


def check_login_baidu2(request, cfg, sid, uin):
    from md5 import md5
    import json
    import urllib
    # from urllib3 import PoolManager
    # sdk_poolmanager = PoolManager(num_pools=10)
    sign = md5(cfg['appid'] + sid + cfg['secretkey']).hexdigest()
    fields = {'AppID': cfg['appid'], 'AccessToken': sid, 'Sign': sign}
    rsp = sdk_poolmanager.request('GET', cfg['loginurl'], fields)
    if rsp.status != 200:
        logger.error('[sdk baidu2]response status error %d', rsp.status)
        return False
    msg = json.loads(rsp.data)
    content = urllib.unquote(msg['Content'])
    rsp_sign = md5(cfg['appid'] + str(msg['ResultCode']) + content + cfg['secretkey']).hexdigest()
    if msg['Sign'] != rsp_sign:
        logger.error('[sdk baidu2]response sign mismatch %s %s', msg['Sign'], rsp_sign)
        return False
    return str(json.loads(content.decode('base64'))['UID'])


def check_login_haomeng(request, cfg, sid, uin):
    import json
    from md5 import md5
    # from urllib3 import PoolManager
    # sdk_poolmanager = PoolManager(num_pools=10)
    flag = md5(cfg['appid'] + uin + sid + cfg['login_key']).hexdigest()
    params = {'appid': cfg['appid'], 'uid': uin, 'state': sid, 'flag': flag}
    rsp = sdk_poolmanager.request('GET', cfg['loginurl'], params)
    if rsp.status == 200:
        try:
            data = json.loads(rsp.data)
        except ValueError:
            logger.error("params %r", params)
            logger.error("[sdk haomeng] req %r failed %s", sid, rsp.data)
            return False
        if data.get('ret', 0) != 100:
            logger.error("params %r", params)
            logger.error("[sdk haomeng] req %s failed %s", sid, data)
            return False
    else:
        logger.error("params %r", params)
        logger.error("[sdk haomeng] %s status %d", cfg['loginurl'], rsp.status)
        return False
    return data["uid"]


def check_login_cc(request, cfg, sid, uin):
    params = {"token": sid}
    rsp = sdk_poolmanager.request("GET", cfg["login_url"], params)
    if rsp.status == 200:
        if "success" not in rsp.data:
            logger.error("params %r", params)
            logger.error("[sdk cc] req %s failed %s", sid, rsp.data)
            return False
    else:
        logger.error("params %r", params)
        logger.error("[sdk cc] %s status %d", cfg['loginurl'], rsp.status)
        return False
    return uin


def check_login_yijie(request, cfg, sid, uin):
    import urllib
    params = {
        "app": cfg["app_key"],
        "sdk": request.channel,
        "uin": uin,
        "sess": sid,
    }
    uri = "?".join([cfg["login_url"], urllib.urlencode(params)])
    rsp = sdk_poolmanager.urlopen("GET", uri)
    if rsp.status == 200:
        if rsp.data != '0':
            logger.error("params %r", params)
            logger.error("[sdk yijie] req %s failed %s", sid, rsp.data)
            return False
    else:
        logger.error("params %r", params)
        logger.error("[sdk yijie] %s status %d", cfg['loginurl'], rsp.status)
        return False
    return request.channel + uin


def check_login_tiantian(request, cfg, sid, uin):
    import json
    from md5 import md5
    params = {
        "cpId": cfg["app_id"],
        "token": sid,
    }
    sparams = json.dumps(params)
    sign = md5("/user/info" + sparams + cfg["app_key"]).hexdigest()
    info = {
        "data": sparams,
        "sign": sign,
    }
    rsp = sdk_poolmanager.request("GET", cfg["login_url"], info)
    if rsp.status == 200:
        rsp_json_data = json.loads(rsp.data)
        if rsp_json_data["status"] != 1:
            logger.error("params %r", params)
            logger.error("[sdk tiantian] req %s failed %s", sid, rsp.data)
            return False
    else:
        logger.error("params %r", params)
        logger.error(
            "[sdk tiantian] %s status %d", cfg['loginurl'], rsp.status)
        return False
    return rsp_json_data["data"]["id"]


def check_login_oppo(request, cfg, sid, uin):
    import sys
    import random
    import time
    import hmac
    import json
    from hashlib import sha1
    import urllib
    fields = {
        'fileId': uin,
        'token': sid,
    }
    args = [
        ('oauthConsumerKey', cfg['appkey']),
        ('oauthToken', sid),
        ('oauthSignatureMethod', 'HMAC-SHA1'),
        ('oauthTimestamp', int(time.time())),
        ('oauthNonce', random.randint(0, sys.maxint)),
        ('oauthVersion', '1.0'),
    ]
    tosign = urllib.urlencode(args) + '&'
    key = cfg['secretkey'] + '&'
    sign = urllib.quote_plus(
        hmac.new(key, tosign, digestmod=sha1).digest().encode('base64'))
    headers = {
        'param': tosign,
        'oauthSignature': sign,
    }
    rsp = sdk_poolmanager.request(
        'GET', cfg['loginurl'], fields=fields, headers=headers)
    if rsp.status != 200:
        logger.error('[sdk oppo]response status error %d', rsp.status)
        return False

    if 'errorCode' in rsp.data:
        logger.error('[sdk oppo]response invalid %s', rsp.data)
        return False

    data = json.loads(rsp.data)
    try:
        return data['ssoid']
    except KeyError:
        logger.error('[sdk oppo]response error %s', rsp.data)
        return False


def check_login_le8(request, cfg, sid, uin):
    params = {
        'appid': cfg["app_id"],
        "t": sid,
        "uid": uin,
    }
    rsp = sdk_poolmanager.request('POST', cfg['login_url'], fields=params)
    if rsp.status == 200:
        return uin if 'success' in rsp.data else False
    else:
        logger.error("[sdk le8] %s status %d", cfg['login_url'], rsp.status)
        return False
    return uin


def check_login_mmy(request, cfg, sid, uin):
    params = {
        'token': sid,
        'uid': uin,
    }
    rsp = sdk_poolmanager.request('POST', cfg['login_url'], fields=params)
    if rsp.status == 200:
        return uin if 'success' in rsp.data else False
    else:
        logger.error("[sdk mmy] %s status %d", cfg['login_url'], rsp.status)
        return False
    return uin


def check_login_h07073(request, cfg, sid, uin):
    from md5 import md5
    import json
    params = {
        'username': uin,
        'token': sid,
        'pid': cfg['pid'],
    }
    to_sign = "&".join("%s=%s" % (f, params[f]) for f in sorted(params))
    to_sign = '%s%s' % (to_sign, cfg['secretKey'])
    params['sign'] = md5(to_sign).hexdigest()
    rsp = sdk_poolmanager.request('POST', cfg['login_url'], fields=params)
    if rsp.status == 200:
        try:
            data = json.loads(rsp.data)
        except ValueError:
            logger.error("params %r", params)
            logger.error("[sdk h07073] req %r failed %s", sid, rsp.data)
            return False
        if data.get('state', 0) != 1:
            logger.error("params %r", params)
            logger.error("[sdk h07073] req %s failed %s", sid, data)
            return False
    else:
        logger.error("params %r", params)
        logger.error("[sdk h07073] %s status %d", cfg['loginurl'], rsp.status)
        return False
    return data["data"]["uid"]


def check_login_pyw(request, cfg, sid, uin):
    import json
    import time
    from md5 import md5
    tid = ''.join(
        list(md5(str(time.time())).hexdigest())[8:-8])
    params = {
        'uid': uin,
        'token': sid,
        'tid': tid,
    }
    rsp = sdk_poolmanager.urlopen(
        'POST', cfg["login_url"],
        headers={"Content-Type": "application/json"},
        body=json.dumps(params))
    if rsp.status == 200:
        try:
            data = json.loads(rsp.data)
        except ValueError:
            logger.error("params %r", params)
            logger.error("[sdk pyw] req %r failed %s", sid, rsp.data)
            return False
        if data.get('ack', 0) != 200:
            logger.error("params %r", params)
            logger.error("[sdk pyw] %s", data['msg'])
            return False
    else:
        logger.error("params %r", params)
        logger.error("[sdk pyw] %s status %d", cfg['loginurl'], rsp.status)
        return False
    return uin


def check_login_liulian(request, cfg, sid, uin):
    from md5 import md5
    import json
    params = {
        'appid': cfg['appid'],
        'appkey': cfg['appkey'],
        'sid': sid,
        'sign': md5(cfg['appid'] + cfg['appkey'] + cfg['privatekey'] + sid).hexdigest(),
    }
    rsp = sdk_poolmanager.request('POST', cfg['login_url'], fields=params)
    if rsp.status == 200:
        try:
            data = json.loads(rsp.data)
            print data
        except ValueError:
            logger.error("params %r", params)
            logger.error("[sdk pyw] req %r failed %s", sid, rsp.data)
            return False

        if data['status'] != 1:
            logger.error("params %r", params)
            logger.error("[sdk liulian] %s status %d", cfg['login_url'], data['status'])
            return False

        return data['userid']

    logger.error("params %r", params)
    logger.error("[sdk liulian] %s status %d", cfg['login_url'], rsp.status)
    return False


def check_login_moge(request, cfg, sid, uin):
    from md5 import md5
    sid, logintime = sid.split("_")
    sign = "username=" + uin + "&appkey=" + cfg['appkey'] + "&logintime=" + logintime
    sign = md5(sign).hexdigest()
    if sign != sid:
        return False

    return uin


def check_login(request, sdkType, req):
    from yy.sdk import login
    sdk_labels = {
        poem_pb.SDK_ITOOLS_IOS:     'itools',
        poem_pb.SDK_PP_IOS:         'pp',
        poem_pb.SDK_UC:             'uc',
        poem_pb.SDK_XY_IOS:         'xy',
        poem_pb.SDK_TB_IOS:         'tb',
        poem_pb.SDK_KY_IOS:         'ky',
        poem_pb.SDK_AS_IOS:         'as',
        poem_pb.SDK_IIAPPLE_IOS:    'iiapple',
        poem_pb.SDK_HM_IOS:         'hm',
        poem_pb.SDK_XIAOMI:         'xiaomi',
        poem_pb.SDK_C360:           'c360',
        poem_pb.SDK_OPPO:           'oppo',
        poem_pb.SDK_ANZHI:          'anzhi',
        poem_pb.SDK_WDJ:            'wdj',
        poem_pb.SDK_BAIDU:          'baidu',
        poem_pb.SDK_WANKA:          'wanka',
        poem_pb.SDK_YYB:            'yyb',
        poem_pb.SDK_GFAN:           'gfan',
        poem_pb.SDK_HWD:            'hwd',
        poem_pb.SDK_MM:             'mm',
        poem_pb.SDK_M4399:          'm4399',
        poem_pb.SDK_PAOJIAO:        'paojiao',
        poem_pb.SDK_PIPAW:          'pipaw',
        poem_pb.SDK_YOUKU:          'youku',
        poem_pb.SDK_YYH:            'yyh',
        poem_pb.SDK_ZY:             'zy',
        poem_pb.SDK_KUGOU:          'kugou',
        poem_pb.SDK_EGAME:          'egame',
        poem_pb.SDK_DOWNJOY:        'downjoy',
        poem_pb.SDK_PPS:            'pps',
        poem_pb.SDK_PPTV:           'pptv',
        poem_pb.SDK_MZW:            'mzw',
        poem_pb.SDK_VIVO:           'vivo',
        poem_pb.SDK_HUAWEI:         'huawei',
        poem_pb.SDK_WL:             'wl',
        poem_pb.SDK_LX:             'lx',
        poem_pb.SDK_GIONEE:         'gionee',
        poem_pb.SDK_HAIMA:          'haima',
        poem_pb.SDK_COOLPAD:        "coolpad",
        poem_pb.SDK_XX:             "xx",
        poem_pb.SDK_XX_IOS:         "xx_ios",
        poem_pb.SDK_MEIZU:          "meizu",
        poem_pb.SDK_KAOPU:          "kaopu",
        poem_pb.SDK_BAIDU2:         "baidu2",
        poem_pb.SDK_WL2:            "wl2",
        poem_pb.SDK_HAOMENG:        "haomeng",
        poem_pb.SDK_CC:             "cc",
        poem_pb.SDK_YIJIE:          "yijie",
        poem_pb.SDK_LE8_IOS:        "le8_ios",
        poem_pb.SDK_TIANTIAN:       'tiantian',
        poem_pb.SDK_MMY:            "mmy",
        poem_pb.SDK_H07073:         'h07073',
        poem_pb.SDK_PYW:            'pyw',
        poem_pb.SDK_LIULIAN:        'liulian',
        poem_pb.SDK_MOGE:           'moge',
    }

    if sdkType == poem_pb.SDK_LJ:
        return login.check_login_lj(request, settings.SDK['lj'], req.ljsdkInfo)
    elif sdkType == poem_pb.SDK_HUAWEI:
        label = sdk_labels[sdkType]
        return check_login_huawei(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_WL:
        label = sdk_labels[sdkType]
        return check_login_wl(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_WL2:
        label = sdk_labels[sdkType]
        return check_login_wl(
            request, settings.SDK.get(label),
            req.sessionId, req.uin, tag="wl2")
    elif sdkType == poem_pb.SDK_LX:
        label = sdk_labels[sdkType]
        return check_login_lx(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_GIONEE:
        label = sdk_labels[sdkType]
        return check_login_gionee(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_COOLPAD:
        label = sdk_labels[sdkType]
        return check_login_coolpad(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_HAIMA:
        label = sdk_labels[sdkType]
        return check_login_haima(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_XX:
        label = sdk_labels[sdkType]
        return check_login_xx(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_XX_IOS:
        label = sdk_labels[sdkType]
        return check_login_xx(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_MEIZU:
        label = sdk_labels[sdkType]
        return check_login_meizu(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_KAOPU:
        label = sdk_labels[sdkType]
        return check_login_kaopu(
            req, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_PP_IOS:
        label = sdk_labels[sdkType]
        return check_login_pp(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_BAIDU2:
        label = sdk_labels[sdkType]
        return check_login_baidu2(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_HAOMENG:
        label = sdk_labels[sdkType]
        return check_login_haomeng(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_CC:
        label = sdk_labels[sdkType]
        return check_login_cc(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_YIJIE:
        label = sdk_labels[sdkType]
        return check_login_yijie(
            req, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_TIANTIAN:
        label = sdk_labels[sdkType]
        return check_login_tiantian(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_OPPO:
        label = sdk_labels[sdkType]
        return check_login_oppo(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_LE8_IOS:
        label = sdk_labels[sdkType]
        return check_login_le8(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_MMY:
        label = sdk_labels[sdkType]
        return check_login_mmy(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_H07073:
        label = sdk_labels[sdkType]
        return check_login_h07073(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_PYW:
        label = sdk_labels[sdkType]
        return check_login_pyw(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_LIULIAN:
        label = sdk_labels[sdkType]
        return check_login_liulian(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    elif sdkType == poem_pb.SDK_MOGE:
        label = sdk_labels[sdkType]
        return check_login_moge(
            request, settings.SDK.get(label), req.sessionId, req.uin)
    else:
        label = sdk_labels[sdkType]
        handler = getattr(login, 'check_login_'+label)
        return handler(
            request, settings.SDK.get(label), req.sessionId, req.uin)
