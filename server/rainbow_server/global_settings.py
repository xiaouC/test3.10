# coding: utf-8
import os
import __main__

PROJECT = 'xydld'

LOG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
        'gmflow': {
            'format': '[%(asctime)s] %(message)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'paylog': {
            'format': '[%(asctime)s] [%(funcName)s] %(message)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'launch': {
            'format': '<<%(logto)s>> %(asctime)s|%(featureCode)s|%(sessionID)s'
                      '|%(worldVersion)s|%(os)s|%(osVersion)s|%(resolution)s'
                      '|%(IMEI)s|%(UDID)s|%(MAC)s|%(UA)s|%(clientVersion)s'
                      '|%(clientIP)s||%(idfa)s|%(deviceUniqueID)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'account-register': {
            'format': '<<%(logto)s>> %(asctime)s|%(featureCode)s|%(sessionID)s'
                      '||%(os)s|%(osVersion)s|%(resolution)s|%(IMEI)s|%(UDID)s'
                      '|%(MAC)s|%(UA)s|%(clientVersion)s|%(clientIP)s'
                      '|%(username)s|%(sdkType)s|%(userID)s||'
                      '|%(idfa)s|%(deviceUniqueID)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'account-login': {
            'format': '<<%(logto)s>> %(asctime)s|%(featureCode)s|%(sessionID)s'
                      '||%(os)s|%(osVersion)s|%(resolution)s|%(IMEI)s|%(UDID)s'
                      '|%(MAC)s|%(UA)s|%(clientVersion)s|%(clientIP)s'
                      '|%(username)s|%(sdkType)s|%(userID)s'
                      '|%(idfa)s|%(deviceUniqueID)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'role-credit': {
            'format': '%(asctime)s|%(_featureCode)s|%(sessionID)s'
                      '|%(sessionID)s|%(worldVersion)s'
                      '|%(_clientVersion)s|%(_clientIP)s'
                      '|%(_username)s|%(sdkType)s|%(_userID)s|%(_entityID)s'
                      '|%(_level)s||||%(amount)s|2|%(gold)s|%(billingType)s|'
                      '|%(orderNO)s||%(result)s|||',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'role-debit': {
            'format': '%(asctime)s|%(_featureCode)s|%(sessionID)s'
                      '|%(sessionID)s|%(worldVersion)s'
                      '|%(_clientVersion)s|%(_clientIP)s'
                      '|%(_username)s|%(sdkType)s|%(_userID)s'
                      '|%(_entityID)s|%(_level)s||%(debitType)s|%(itemType)s'
                      '|%(argID)s|%(argAmount)s||%(currency)s'
                      '|%(amount)s|%(balance)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'role-register': {
            'format': '%(asctime)s|%(_featureCode)s|%(sessionID)s'
                      '|%(sessionID)s|%(worldVersion)s'
                      '|%(_clientVersion)s|%(_clientIP)s'
                      '|%(_username)s|%(sdkType)s|%(_userID)s'
                      '|%(_entityID)s|%(_level)s|'
                      '|1|%(_exp)s|2|%(_gold)s|4|%(_slate)s|5'
                      '|%(_gp)s|6|%(_bp)s|7|%(_vs)s|8|%(_money)s|9'
                      '|%(_spprop)s|10|%(_petmax)s|11|%(_sp)s|99|%(_name)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'role-login': {
            'format': '%(asctime)s|%(_featureCode)s|%(sessionID)s'
                      '|%(sessionID)s|%(worldVersion)s'
                      '|%(_clientVersion)s|%(_clientIP)s'
                      '|%(_username)s|%(sdkType)s|%(_userID)s'
                      '|%(_entityID)s|%(_level)s|'
                      '|1|%(_exp)s|2|%(_gold)s|4|%(_slate)s|5'
                      '|%(_gp)s|6|%(_bp)s|7|%(_vs)s|8|%(_money)s|9'
                      '|%(_spprop)s|10|%(_petmax)s|11|%(_sp)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'role-heartbeat': {
            'format': '%(asctime)s|%(_featureCode)s|%(sessionID)s'
                      '|%(sessionID)s|%(worldVersion)s'
                      '|%(_clientVersion)s|%(_clientIP)s'
                      '|%(_username)s|%(sdkType)s|%(_userID)s'
                      '|%(_entityID)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        },
        'role-custom': {
            'format': '%(asctime)s|%(_featureCode)s|%(sessionID)s'
                      '|%(sessionID)s|%(worldVersion)s'
                      '|%(_clientVersion)s|%(_clientIP)s'
                      '|%(_username)s|%(sdkType)s|%(_userID)s'
                      '|%(_entityID)s|%(_level)s||%(type)s|%(arg1)s',
            'datefmt': '%Y-%m-%d %X,000 +0800'
        }
    },
    'handlers': {
        'property': {
            'class': 'common.log.WatchedFileHandler',
            'formatter': 'gmflow',
            'filename': 'log/property.{real_worldID}'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'dump': {
            'class': 'common.log.TimedRotatingFileHandler',
            'formatter': 'gmflow',
            'filename': 'log/world_gmflow.{real_worldID}',
            'when': 'M',
            'interval': 5,  # how long to backup.
            # 'backupCount':7,#max backups.
        },
        'paylog': {
            'class': 'common.log.WatchedFileHandler',
            'formatter': 'paylog',
            'filename': 'log/paylog',
            # 'when':'MIDNIGHT',
            # 'interval':1,#how long to backup.
            # 'backupCount':7,#max backups.
        },

        'cronlog': {
            'class': 'common.log.WatchedFileHandler',
            'formatter': 'simple',
            'filename': 'log/cronlog.{real_worldID}',
        },
        'launch': {
            'class': 'logging.StreamHandler',
            # 'class':'common.log.WatchedFileHandler',
            'formatter': 'launch',
            # 'filename':'log/s{sessionID}.{project}.yunyue.hgame.lauch'
        },
        'account-register': {
            'class': 'logging.StreamHandler',
            # 'class':'common.log.WatchedFileHandler',
            'formatter': 'account-register',
            # 'filename':'log/s{sessionID}.{project}.yunyue.hgame.account-register'
        },
        'account-login': {
            'class': 'logging.StreamHandler',
            # 'class':'common.log.WatchedFileHandler',
            'formatter': 'account-login',
            # 'filename':'log/s{sessionID}.{project}.yunyue.hgame.account-login'
        },
        'role-credit': {
            # 'class':'logging.StreamHandler',
            'class': 'common.log.WatchedFileHandler',
            'formatter': 'role-credit',
            'filename': 'log/R{worldID}.{project}.yunyue.hgame.'
                        'role-credit.{real_worldID}'
        },
        'role-debit': {
            # 'class':'logging.StreamHandler',
            'class': 'common.log.WatchedFileHandler',
            'formatter': 'role-debit',
            'filename': 'log/R{worldID}.{project}.yunyue.hgame.'
                        'role-debit.{real_worldID}'
        },
        'role-register': {
            # 'class':'logging.StreamHandler',
            'class': 'common.log.WatchedFileHandler',
            'formatter': 'role-register',
            'filename': 'log/R{worldID}.{project}.yunyue.hgame.'
                        'role-register.{real_worldID}'
        },
        'role-login': {
            # 'class':'logging.StreamHandler',
            'class': 'common.log.WatchedFileHandler',
            'formatter': 'role-login',
            'filename': 'log/R{worldID}.{project}.yunyue.hgame.'
                        'role-login.{real_worldID}'
        },
        'role-heartbeat': {
            # 'class':'logging.StreamHandler',
            'class': 'common.log.WatchedFileHandler',
            'formatter': 'role-heartbeat',
            'filename': 'log/R{worldID}.{project}.yunyue.hgame.'
                        'role-heartbeat.{real_worldID}'
        },
        'role-custom': {
            # 'class':'logging.StreamHandler',
            'class': 'common.log.WatchedFileHandler',
            'formatter': 'role-custom',
            'filename': 'log/R{worldID}.{project}.yunyue.hgame.'
                        'role-custom.{real_worldID}'
        },
        'launch-uwsgi-pipe': {
            'class': 'logging.StreamHandler',
            'formatter': 'launch',
        },
        'account-register-uwsgi-pipe': {
            'class': 'logging.StreamHandler',
            'formatter': 'account-register',
        },
        'account-login-uwsgi-pipe': {
            'class': 'logging.StreamHandler',
            'formatter': 'account-login',
        },
        # 'rq': {
        #     'class': 'common.log.RQHandler',
        #     'redis_url': 'redis://192.168.100.104:6379/1',
        #     'name': 'adclick',
        #     'handler': 'ttxm.tasks.adclick_dispatch',
        #     'include': ['pay', 'sessionaccess'],
        # },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'gmflow': {
            'handlers': ['dump'],
            'level': 'INFO',
            'propagate': False,
        },

        'paylog': {
            'handlers': ['paylog'],
            'filename': 'log/paylog',
            'propagate': False,
        },
        'cron': {
            'handlers': ['cronlog'],
            'propagate': False,
        },
        'launch': {
            'handlers': ['launch-uwsgi-pipe'],
            'level': 'INFO',
            'propagate': False,
        },
        'account-register': {
            'handlers': ['account-register-uwsgi-pipe'],
            'level': 'INFO',
            'propagate': False,
        },
        'account-login': {
            'handlers': ['account-login-uwsgi-pipe'],
            'level': 'INFO',
            'propagate': False,
        },
        'role-credit': {
            'handlers': ['role-credit'],
            'level': 'INFO',
            'propagate': False,
        },
        'role-debit': {
            'handlers': ['role-debit'],
            'level': 'INFO',
            'propagate': False,
        },
        'role-register': {
            'handlers': ['role-register'],
            'level': 'INFO',
            'propagate': False,
        },
        'role-login': {
            'handlers': ['role-login'],
            'level': 'INFO',
            'propagate': False,
        },
        'role-heartbeat': {
            'handlers': ['role-heartbeat'],
            'level': 'INFO',
            'propagate': False,
        },
        'role-custom': {
            'handlers': ['role-custom'],
            'level': 'INFO',
            'propagate': False,
        },
        'urllib3': {
            'handlers': ['console'],
            'level': 'CRITICAL'
        },
    },
}
main_package = __main__.__package__
if main_package is None:
    # try uwsgi
    try:
        import uwsgi
        main_package = uwsgi.opt.get('main-package')
    except ImportError:
        pass

if main_package in ('world', 'region'):
    del LOG['handlers']['account-register']
    del LOG['handlers']['account-login']
    del LOG['handlers']['launch']
    del LOG['loggers']['account-register']
    del LOG['loggers']['account-login']
    del LOG['loggers']['launch']
elif main_package == 'session':
    del LOG['handlers']['role-heartbeat']
    del LOG['handlers']['role-register']
    del LOG['handlers']['role-login']
    del LOG['handlers']['role-credit']
    del LOG['handlers']['role-debit']
    del LOG['handlers']['role-custom']
    del LOG['loggers']['role-heartbeat']
    del LOG['loggers']['role-register']
    del LOG['loggers']['role-login']
    del LOG['loggers']['role-credit']
    del LOG['loggers']['role-debit']
    del LOG['loggers']['role-custom']
    LOG['formatters']['gmflow-pipe'] = {
        'format': '<<session_gmflow>> [%(asctime)s] %(message)s',
        'datefmt': '%Y-%m-%d %X,000 +0800'
    }
    del LOG['handlers']['dump']
    LOG['handlers']['dump-pipe'] = {
        'class': 'logging.StreamHandler',
        'formatter': 'gmflow-pipe'
    }
    LOG['loggers']['gmflow'] = {
        'handlers': ['dump-pipe'],
        'level': 'INFO',
        'propagate': False,
    }
else:
    del LOG['handlers']['role-heartbeat']
    del LOG['handlers']['role-register']
    del LOG['handlers']['role-login']
    del LOG['handlers']['role-credit']
    del LOG['handlers']['role-debit']
    del LOG['loggers']['role-heartbeat']
    del LOG['loggers']['role-register']
    del LOG['loggers']['role-login']
    del LOG['loggers']['role-credit']
    del LOG['loggers']['role-debit']
    del LOG['handlers']['role-custom']
    del LOG['handlers']['account-register']
    del LOG['handlers']['account-login']
    del LOG['handlers']['launch']
    del LOG['loggers']['account-register']
    del LOG['loggers']['account-login']
    del LOG['loggers']['launch']
    del LOG['loggers']['role-custom']

ROOT = os.path.dirname(__file__)

WORLD = {
    'ID': 0,
    'ip': '127.0.0.1',  # session服务器发送给客户端连接用
    'port': 11000,
    'mode': '',
    'managehost': '127.0.0.1',
    'manageport': 11001,        # 用于内部管理任务，比如监控，定时任务
    'backdoorport': 11002,        # python shell
}

PROXY = {
    'host': '10.116.118.193',
    'port': 22001
}


SESSION = {
    'ID': 200,
    'host': '0.0.0.0',
    'port': 29000,
}

SDK = {
    'uc': {
        'loginurl': 'http://sdk.g.uc.cn/cp/account.verifySession',
        # 'loginurl': 'http://sdk.test4.g.uc.cn/cp/account.verifySession',
        'AppKey': 'a895fb0cdf715863b02ae35f9cde646b',
        'game': {
            'cpId': 49025,
            'gameId': 579041,
            'channelId': 2,
            'serverId': 0,
        },
    },
    'c360': {
        'loginurl': 'https://openapi.360.cn/user/me',
        'appsecret': '7136b2a534558eab686b0e37e1d6cb43',
    },
    'baidu': {
        'loginurl': 'http://querysdkapi.91.com/CpLoginStateQuery.ashx',
        'appid': '7187701',
        'secretkey': 'tcPufD3XaZlpt0reQBaRbA5BUgjNPpvx',
    },
    'baidu2': {
        'loginurl': 'http://querysdkapi.91.com/CpLoginStateQuery.ashx',
        'appid': '7398765',
        'secretkey': '16UNvoAfxSQgD4qGCvge3aE5hTcGplxh',
    },
    'xiaomi': {
        'loginurl': 'http://mis.migc.xiaomi.com/api/biz/service/verifySession.do',
        'appId': '2882303761517427343',
        'appKey': '5881742752343',
        'appSecret': 'uM1e9cad86xztvZJC5+23w==',
    },
    'wdj': {
        'loginurl': 'https://pay.wandoujia.com/api/uid/check',
        'appkey': '100034487',
        'rsa_public_key': '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCd95FnJFhPinpNiE/h4VA6bU1rzRa5+a25Bxsn
FX8TzquWxqDCoe4xG6QKXMXuKvV57tTRpzRo2jeto40eHKClzEgjx9lTYVb2RFHHFWio/YGTfnqI
PTVpi7d7uHY+0FZ0lYL5LlW4E2+CQMxFOPRwfqGzMjs1SDlH7lVrLEVy6QIDAQAB
-----END PUBLIC KEY-----''',
    },
    'anzhi': {
        'loginurl': 'http://user.anzhi.com/web/api/sdk/third/1/queryislogin',
        'appkey': '14482459076Q40C2DSvGMJ2Y69551d',
        'appsecret': 'F4TWgtKHesIKN5v3eEsSQM42',
    },
    'oppo': {
        'loginurl': 'http://i.open.game.oppomobile.com/gameopen/user/fileIdInfo',
        'appkey': 'bjiQLpsqyu8Gg4kgK8goCKko4',
        'secretkey': '8d68A258e9D93812b86B532567635352',
        'rsa_public_key': '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCmreYIkPwVovKR8rLHWlFVw7YD
fm9uQOJKL89Smt6ypXGVdrAKKl0wNYc3/jecAoPi2ylChfa2iRu5gunJyNmpWZzl
CNRIau55fxGW0XEu553IiprOZcaw5OuYGlf60ga8QT6qToP0/dpiL/ZbmNUO9kUh
osIjEu22uFgR+5cYyQIDAQAB
-----END PUBLIC KEY-----''',
    },
    'yyh': {
        'loginurl': 'http://api.appchina.com/appchina-usersdk/user/get.json',
        'appid': '10932',
        'appkey': 'xBtsAo9c4F1CNnW0',
        'payid': '5000372262',
        'paykey': 'NTI0QzA3RURDNzVGM0JGOThGNUU5N0ZDNzQ1RDdDQzM5MEI5OTVBOU1USXlOek15TkRreE16WTNOakUxTmpRd01qTXJNak15TXpNeE5EYzJPVFEyTXpBNE5qUXpNalkyT1RjM05Ua3dOREE0TmpJek1USTVOek01',
    },
    'gfan': {
        'appid': '28090372',
        'loginurl': 'http://api.gfan.com/uc1/common/verify_token',
    },
    'wanka': {
            # 金立
            'GIONEE_API_KEY': 'CF0DCD6F233A41328FDF18024B6D00BB',
            'GIONEE_SECRET_KEY': '75CB7F6ED315425E87FC53EE5F847B20',
            'GIONEE_NOTIFY_URL': 'http://sdk.fengshen.yunyuegame.com/sdk/android/sdk/wanka/gionee/pay_callback',
            'GIONEE_PRIVATE_KEY': 'MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAKj4dWmnfkBvPp4zagfutc+j1dchNUeO4Vb1R9zJxr551mSTQlXsMLOpitineExkxw+lUx92B211X9WHuLDSIyPDzRtL4bnGEZw2zc+Yp4VnlaP8zfSsZYfXdAEjp8rmMWNHYn1ZMgexPdWbwVJaQOXOVi2ZJEU5apboEcYGgpgBAgMBAAECgYBkaOlU9LyYy8K5PjJXLmqKToDHy6ser/CGvVGMCbf5/usBb2TvLGEwkqK45qQdOZH1YThJLNlzGVnuyS1enjFUmnf1fjKKN7iBrYLGnOzLiJck8yiHHmY02kr+NNl0M6GUUOPQ1UJbA0TabPvdHpgEPbCc0nBA6b9qazqmPRRR1QJBAOJKYJ2fJYu+x1HFspmLi/4W4e9hnSop9rQW23+U9gc9PriFFOYIxiquFmX/H8ag8MqrBrxOuQ7IX9qCgNcBw8MCQQC/J46KGzcFsu6Eff4koJ2G5mPoFwLUvVEtCnbANAiGH2BQQltrwh/hBnAPoz/bwpfgzeo+Hp1lNPHdLd6YwkzrAkBJnJZXT/j/v5zJLf2OU0XD7x+qJl/g4mu9Y54dn5B1BGhN0ATfW8VTBvSEU3y7uYj69K2pPhaXB3me9EsDJjDPAkAULZLIVVMbkOXIqpwXNbUrNkq5hyRPXKSjAoXCiDuWHN3H2xlXaKiA0nMl02+8PPBXVKUzZXvr4Qje9iaXLXt9AkBX4I2oITufMUaoxN/xv0EMmxd7XTohGQWnHVuY7sLjeUBvB70vzrD7F0U/KfcpuMIFy5/wki8226e1BnVasGU9',
            'GIONEE_PUBLIC_KEY': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDAdKB4eM1gL3n0p0R9CxYoWYaSknd4E4X3thOtNC/vzt/IeeKW+wlYXpQnpP83qzR4v8ETysxOWCiePeEs/s4HraAutCOYZOAEuOAjljdIuP36NasNHSsCche7FjNsSqzAvFHxVknXEtXZGxl0jl3QqUg/yZ1F6+jP+GP7ZB4lewIDAQAB',

            # 联想
            'LENOVO_KEY': 'MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBALr+6ls/ELiUoXpKwniM/Eq4uMkk0kmITC1bK4bzvZb18u3bPrSjOEYU4RImGPYUS3hJaiqN6fTg4DteWvBXE53ubDMLP60Bm44RILgtcgzJDn29ULePcUqmIEVkepJ/LnFcwFxGYo0LVbZYiSD9GIUx6ZcMjW3bpjt7Ly5m6MXVAgMBAAECgYAqRXv2+o+uGjNSsNm7ZKuXvKBRIBjFdKE705NIY4slOB4ddOV88jTDau7iKmiUIExbOcVdL02HBNrLsO2/zP9q3jmSpjdemRWVUtEgB6vmXK8q9AfojzLifzUdX5DIptHSl55tt5ilCLDQQNy3Hfi/PZ5oqjuQOpIf0J0NxDzcIQJBAOSoBMSxN+I6ljOt8GcjO//5KSO5N01OwrudP2uZO8+3owD4MTdYZrttOZJNKsgbX2x3tiD1A/G8v+R1zS6OUCkCQQDRW4Tv95dG4JKHivUaYA9qI5expcxokyGZ0mn1YxJMgwh2epN/UUMp4MOpYKWnb2pDEy4zoX6y8F7oqsn/7I3NAkEA3Vt/Cj+aHyuifzNTeTVV/49hcVD8JZ4qzOAFJpA4o/VeGzEqzC6LfcTWqDiGQySks2gM7EjmYZ7dkjkswnZJSQJBAJ/XxT7GBZ0a1yVfpdV2ZC6AcFA1K0TomO3tpfKxqoX6QVrcKYM6kxIFRr4qSS/2M+Z0XYEUGz0Zowz3YPTiMj0CQF7qlOHnUke5hRyXMoKq+Yso+9LFUEsOK88EbpG9Tefj4D1Pq1itIJiogu9u0eu7o0mJNq0vQTOGH69lYf0Kk1w=',
            'OPEN_APP_ID': '1507070405463.app.ln',

            # VIVO
            'VIVO_CP_KEY': 'b3898db483efcdec40eea325aaec8c85',
            'VIVO_CP_ID': '20150407175155578850',
            'VIVO_APP_ID': 'a639b48b57908dfc423d89b2271217b4',
            'VIVO_NOTIFY_URL': 'http://sdk.fengshen.yunyuegame.com/sdk/android/sdk/wanka/vivo/pay_callback',

            # HUAWEI
            'HUAWEI_PUBLIC_KEY': 'MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAL9YQhS2L67dHYyQqEoJM+6Hasy6XkVGFIn6B3aHQyfivAgHaDlEYXxvv9HeKpW5HHGI6fuPspVfzxWBR5OSl9kCAwEAAQ==',

            # COOLPAD
            'COOLPAD_APP_ID': '5000001475',
            'COOLPAD_APP_KEY': '4bcd7fccf85b4adeb438a3e9f97e9f82',
            'COOLPAD_PUBLIC_KEY': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCVKQVCzLNsK0DbY60/5+NFVgTMvouVbuaVrRsRb3kvTUGtXp/8XYK465MZwI4HZmrBGJcSpNX9vaCBMO47YwhkPVGn/0CDhdjd+uRzGoBnfFWxVoR2eTZBCjoXXsPLOP+kCxWa5/e58O+/7NrfNT4QhZslO/WznUskQYQs/IH6YwIDAQAB',

    },
    'downjoy': {
        'loginurl': 'http://ngsdk.d.cn/api/cp/checkToken',
        'appid': '3749',
        'appkey': 'dNQsiZIW',
        'paykey': 'S4CKTxVq8p4m',
    },
    'huawei': {
        "APP_ID": "10430315",
        "PAY_ID": "900086000022190346",
        "PAY_RSA_PUBLIC": """-----BEGIN PUBLIC KEY-----
MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAKQM73iEYW/f6JtRgOuwsyvvk1hfKNUn
C3F0arwr8+YqrIOrPZMA+5fzV6hMH4Pqeinp7QtRrWwKycH96dWPt08CAwEAAQ==
-----END PUBLIC KEY-----""",
        "BUO_SECRET": "MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAJTBPBA7v+KxhJ1nUq+bx9Ivh30g5F4bGFskGP4vrh6ELZJ4CS7S3JwpMsuvx76NafinQjEXEiOHci66d/bH62+WHyCKLbv7jLrbMxmpEbIFuXOJa9Sm/d7MxraDBqk6M3WtJeRWdFYx/jF6f1UnmF3QlUIOznHNMHxXMkKjhmYxAgMBAAECgYAKQmmKFRTe5a9ny8CALBZUAMMvdh1KAERlxM+UeGVh5WvfNjgr6o8clhrSwYTdN5OfeqmuCRFPMgBGCMZNVux94mvTmh+uqspTsPcI55Z5jtA+E768+yzxEqgyY44G0TzO2SNvWpeufOzh/p5aPvAGcdPmQ9JGHTnFKMLfzwCYIQJBAOYd/SVYhcsCrcf+pUun1lQwBId9D+YL1v6eC+KnmG3zaI3TlHZlIidimtJqtJRJcxPLiycVAJyGjl482Hy+TsMCQQClfH4hIqWC8ll2R2D1sHn6YjC1FiWbrrtBLHVmzfCra/8xUOzCNafF/8jAhzZAQ0jgcyrp9ZgvT6DNdZviy0/7AkEAuUHhX+SBaeuRLlZCisLnGMXDj7ROTVywzDE+zk0wuSvhu3RfrGVE9sI6dDX1hQAQxhnywBb3dAwbp6CChQLM8wJAQ/pMsX3S8WRuHWkayjHxGUpGacysLDRtlUsW+uDz0ObvECoG54w029/DblrcjS9We2SzpyGMnzqdemiqXVJZCwJAGE+ty0/JgSMrkrq1Y6VNwh047xo9/0cUy/guPTKl9nofIwJFkYF3tnZuaSHdP6SkCjHX1TcirDsksJJb+yC0Yg==",
        "PAY_RSA_PRIVATE": "MIIBVgIBADANBgkqhkiG9w0BAQEFAASCAUAwggE8AgEAAkEApAzveIRhb9/om1GA67CzK++TWF8o1ScLcXRqvCvz5iqsg6s9kwD7l/NXqEwfg+p6KentC1GtbArJwf3p1Y+3TwIDAQABAkEAn19Btd9FmZ35KAsCJ/a92c0hZBTuYkVQRKRInQ5GIC978KDw1BJh4JohtRq+lzarr03WA+TqE6N/7bTA3mHb4QIhAObTvWllvimgELm9a5PgG1XAEBJ41Q7g0fxN3sSK+NFbAiEAtfDrK1ARmNgSeMzMnovOvp0N9XTuBAMRvNWmG4QgAB0CIGsQf2SpuoCYK+nbQFDAvC0T/uByh3B1OzDp9Y/4XdzNAiEAi2E65315XZv52q0Z/EOiaIgsj2O6izxGtGD/1YiMc0kCIQDmmTSwhndR56Y/lea/RpwYi1X/19vSwGiQ2LzIKrNdpA==",
        "LOGIN_URL": "https://api.vmall.com/rest.php",
    },
    'pps': {
        'loginkey': '74974bf301ff7e270d0e1e6860735f38',
        'paykey': 'FSXXR9476E385FA7210F3817AF39B3289E8A33639',
    },
    'mzw': {
        'loginurl': 'http://sdk.muzhiwan.com/oauth2/getuser.php',
        'appkey': 'f3244edd2c89a457b9708eb4e503b37d',
        'secret': '55828a700882c',
    },
    'pptv': {
        'loginurl': 'http://api.user.vas.pptv.com/c/v2/cksession.php',
        'paykey': '5002e7b2109c3bd9e27880299d3167b2',
    },
    'pipaw': {
        'loginurl': 'http://sdk.pipaw.com/appuser/Checksid',
        'privatekey': 'f57d74d191b5fe31143ff28254d47941',
        'appid': '12381435890541',
        'merchant_id': '1238',
        'merchant_app_id': '1301',
    },
    'egame': {
        'loginurl': 'https://open.play.cn/oauth/token',
        'appkey': 'ac1dd0b898e076b2ed49624c16253924',
        'client_id': '16578107',
        'client_secret': '562b4a48f9584bc69c4a3291dfda1d93',
    },
    'itools': {
        'loginurl': 'https://pay.itools.cn/?r=auth/verify',
        'appId': '1880',
        'appKey': 'C36C7CC46723AAEECC4A92B993D2588D',
        'rsa_public_key': """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC2kcrRvxURhFijDoPpqZ/IgPlA
gppkKrek6wSrua1zBiGTwHI2f+YCa5vC1JEiIi9uw4srS0OSCB6kY3bP2DGJagBo
Egj/rYAGjtYJxJrEiTxVs5/GfPuQBYmU0XAtPXFzciZy446VPJLHMPnmTALmIOR5
Dddd1Zklod9IQBMjjwIDAQAB
-----END PUBLIC KEY-----""",
    },
    'as': {
        'loginurl': 'https://pay.i4.cn/member_third.action',
        'AppKey': '6b76cf555d2046328a7947d844357b19',
        'rsa_public_key': """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl5t26zmMswxxZL4pp6kkRAH/j1aYdRI5rLOsQ
UNSYYqzioKptTeousEHeqev85A+eI6ZUd0qRYAFTAO8c3Rumd2c43T/hLAr8g8q0UgIxsBFAvssj
SLzJ2K0KW1rn8uj49rJYJK0rrJsWhgXo3Bmh6Ob9/xez70jhsfhD7TakyQIDAQAB
-----END PUBLIC KEY-----""",
    },
    'xy': {
        "loginurl": "http://passport.xyzs.com/checkLogin.php",
        "appid": "100026172",
        "appkey": "StJ6GSl8G2KPBswAofXc0zP7SWLu6bCw",
    },
    'pp': {
        'addr': ('passport_i.25pp.com', 8080),
        "AppId": 7017,
        "AppKey": "8c8306744dd417b7ee5662272e5b2a61",
        'rsa_public_key': """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0BmOR2Wz7YUplIuN5dWB
nM/LsdyG0ZBNuXhcLxdkz72KVWMGw/cB/DrM0YJ+IHlrGpqpJffl6fxAQ9D8S64q
BDpeiZjkl3Iyu/WFLz63oQ2y1sJafE3QRAGZcVyLRLFZdJIfTDY9tUC6TNloJQ61
XesGEmL0oJNTKdQMGZVjqpEtX1DwOW6XYm99FO0gsoeJ37YxEZzZd8Ul0BzWSuUf
lgMqQp94IMKWsv/R0HtvYapXd8cPLmKdZV+kEXZq1DZ43MUrL55nLKwiL5XIdB/S
F/GK9xMQ3BZ53kw8++dhiBv/VDBqZHIU5EVhe70obMVU41tg+r7WSc1clET+3yQ6
xQIDAQAB
-----END PUBLIC KEY-----""",
    },
    'tb': {
        'loginurl': 'http://tgi.tongbu.com/checkv2.aspx',
        'appid': '151163',
        'appkey': '4Olyn@VhXu8RGeqB4NaxnUKhWE7Rd2q4',
    },
    'ky': {
        'loginurl': 'http://f_signin.bppstore.com/loginCheck.php',
        'AppKey': '10d5ac0c126eb7566a7746747d3caa97',
        'rsa_public_key': """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCjkhNHDfjwQhokLk+fk+uD1iWy
ft1pmunJuZzfSB2+Cfpxhc3tWrD2IqgN1iwdApoUJeHn6C101f6Gjngo+ndbS2VX
P7+/zUvYUsbiOcQM0cPh7qF0Y1oaRiq8rrFWEkkLuU81Huo48XIpeKulqIee9Im0
61n0O4CnhHoa+5oVuQIDAQAB
-----END PUBLIC KEY-----""",
    },
    'hm': {
        'loginurl': 'http://api.haimawan.com/index.php?m=api&a=validate_token',
        'appid': '6298a2133f7d4858e5699972fceb6e6c',
        'appkey': '1354c9582f197b63feafd6629115f60f',
    },
    'iiapple': {
        'loginurl': 'http://ucenter.iiapple.com/foreign/oauth/verification.php',
        'gameKey': 'f248471aec4c243ef0546b4fe9895461',
        'secretKey': 'abb07c387781b350e5ee095e39f5ca78',
    },
    'paojiao': {
        'loginurl': 'http://ng.sdk.paojiao.cn/api/user/token.do',
        'appid': '1274',
        'appkey': 'LJICymT8uw5gvZBOTw2IPN6V4Ii8QXUe',
    },
    'vivo': {
        'loginurl': 'https://usrsys.inner.bbk.com/auth/user/info',
        'VIVO_CP_KEY': '59bfe89ef9ca4cc1586b81d072dba5cd',
        'VIVO_CP_ID': '20141231144202034104',
        'VIVO_APP_ID': '829b98597d987dd831b7f36d92d8fd04',
        'VIVO_NOTIFY_URL': 'http://pokemonpro.sdk.dnastdio.com:8888/sdk/vivo/pay_callback',
    },
    'zcgame': {
        'rsa_public_key': """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbrhU8uPZ7+KMnoEn4YfAr1o6T
FP2tpv1U4mLDkMaPO7snzO3xiI3C1Uz+yi41wcm/8vz8HYHNgH+UwkDIvdnglpuM
MgN354yE/MsUFx5xMZWZ8r8tAby1BdFWmuDbqrunmoGdx+YjMToGKIIa/2/Wm4y7
6vcmUroQCan98YYPHwIDAQAB
-----END PUBLIC KEY-----""",
    },
    "wl": {
        'login_url': "http://srv.weilanhd.com/sdksrv/auth",
        'client_id': 'P10116A',
        "projectID": "P10116A",
        'client_secret': 'psyvmyra6f7of4sacvpu',
        "appsecret": "psyvmyra6f7of4sacvpu",
        "severID": "M1028A",
        "productId": "D10053A",
        "appKey": "5i29qfd23a4bghaswx9w",
        "synKey": "a53qgua6milqmexhep1p"
    },
    "wl2": {
        'login_url': "http://srv.weilanhd.com/sdksrv/auth",
        'client_id': 'P10117A',
        "projectID": "P10117A",
        'client_secret': 'psyvmyra6f7of4sacvpu',
        "appsecret": "rv29y983xdmkzywi3op8",
        "severID": "M1029A",
        "productId": "D10054A",
        "appKey": "attgos3er5dk2ekrifa7",
        "synKey": "p7wr5uwq1nhe7s7nnsn2"
    },
    "lx": {
        "login_url": "http://passport.lenovo.com/interserver/authen/1.2/getaccountid",
        'LENOVO_KEY': 'MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBALr+6ls/ELiUoXpKwniM/Eq4uMkk0kmITC1bK4bzvZb18u3bPrSjOEYU4RImGPYUS3hJaiqN6fTg4DteWvBXE53ubDMLP60Bm44RILgtcgzJDn29ULePcUqmIEVkepJ/LnFcwFxGYo0LVbZYiSD9GIUx6ZcMjW3bpjt7Ly5m6MXVAgMBAAECgYAqRXv2+o+uGjNSsNm7ZKuXvKBRIBjFdKE705NIY4slOB4ddOV88jTDau7iKmiUIExbOcVdL02HBNrLsO2/zP9q3jmSpjdemRWVUtEgB6vmXK8q9AfojzLifzUdX5DIptHSl55tt5ilCLDQQNy3Hfi/PZ5oqjuQOpIf0J0NxDzcIQJBAOSoBMSxN+I6ljOt8GcjO//5KSO5N01OwrudP2uZO8+3owD4MTdYZrttOZJNKsgbX2x3tiD1A/G8v+R1zS6OUCkCQQDRW4Tv95dG4JKHivUaYA9qI5expcxokyGZ0mn1YxJMgwh2epN/UUMp4MOpYKWnb2pDEy4zoX6y8F7oqsn/7I3NAkEA3Vt/Cj+aHyuifzNTeTVV/49hcVD8JZ4qzOAFJpA4o/VeGzEqzC6LfcTWqDiGQySks2gM7EjmYZ7dkjkswnZJSQJBAJ/XxT7GBZ0a1yVfpdV2ZC6AcFA1K0TomO3tpfKxqoX6QVrcKYM6kxIFRr4qSS/2M+Z0XYEUGz0Zowz3YPTiMj0CQF7qlOHnUke5hRyXMoKq+Yso+9LFUEsOK88EbpG9Tefj4D1Pq1itIJiogu9u0eu7o0mJNq0vQTOGH69lYf0Kk1w=',
        'OPEN_APP_ID': '1511180153656.app.ln',
    },
    'gionee': {
        'GIONEE_API_KEY': '11B5BA6537274E798CEED85864AC63CF',
        'GIONEE_SECRET_KEY': '58C3AFE7BF634066AE652CBA98405704',
        'GIONEE_NOTIFY_URL': 'http://pokemonpro.sdk.dnastdio.com:8888/sdk/android/sdk/gionee/pay_callback',
        'GIONEE_PRIVATE_KEY': 'MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBANnsRJw2XZwlu4o86jq41zhimyxkjIQKiucPqb/KxvuzDh9KliAnR38TUbaBaQCMdlEpuZIwvapwKeWDdVIuXvPeEFPesltMwYTuefY36Boy4LfCg7F7lrkYN2PR2CrUypib7qdYDdZEpHoiJi83c9/yus0WKLEWkspLw+bsn66pAgMBAAECgYAuUQoQDXn92wMuEV5TFsAfas3CNKis07TMAUc5zTZXfqnsuqSHtvF6L7f5Sy3vAOuQuoaHbLaTB/3Pmw4PZm2lkM+rdqhN6Gt4e5C+LjvsDGELKy7GAJ9ZOgzCiqClNb0LIGwWr+Iu3iDMjs1zFDajkxu8ECIkDO1oEJKhMrzxZQJBAO6zrnREpOqD8H4gSUOLDA3ybFfdG25ethubdl42A0p86ZSgWWXwK4Enx8SbW6PZlkuM1Q0olxqNJFQ7Nz4mk0MCQQDptxonEvcej/luLWyABeWvzN8kaFVVCYQJRbzn5SFW6Uzugj3F1+xxtP9FJ0BsOMqarRxyO/66LiyJq5xEQjmjAkA21JNIJdR0Aial8iiiGTiFo5/7dtCsQ5k1Mjq4XVPYMmU9PLAMWGTF4CtlIAKm2n5JkGoIAcDj2nPz3T5NSnMdAkEArX1vW3wXl0dW6DOt7Cb0hpi1OCh+1541tlBfV2Dea87Jfe+OfXO4n/u01pe5mdxagZFpoV7pyzkFdLjASmdCswJBAMmCE/jkOundunGtyG/yVzgwSG+cn1SgX1vJJZ1TOfHny6ukHxMQDbAaVMOStWB7HrifOXObyHH4X4Qu6ogfkZw=',
        'GIONEE_PUBLIC_KEY': 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbhvB2Ob1GQSWLMPk9E5J234SvoK7zOHIcd63r+mByy0JxDRlGDMUxHBF+/HKBeOda5NcaujHWxIIQX2kLp44sjJmk0PbIrdPNacpys8kAgtrdJmDdQQNrRg4RPwB+Q+cjp5/hCbkjs9OgkhE3Wvfi207M/tNY3wrSOgHKbEZO0QIDAQAB',
    },
    'youku': {
        'appid': 2512,
        'appkey': 'f8096fefaa88dbad',
        'paykey': '444cb0068d22d798116516df15925cd2',
        'loginurl': 'http://sdk.api.gamex.mobile.youku.com/game/user/infomation',
        'callbackurl': 'http://pokemonpro.sdk.dnastdio.com:8888/sdk/android/sdk/youku/pay_callback',
    },
    'haima': {
        'loginurl': 'http://api.haimawan.com/index.php?m=api&a=validate_token',
        'appid': '07958c0f992df0d72e71dfdeaf06d72f',
        'appkey': '57093e2be9da90b6f7c158a239aa9ad8',
    },
    'sina': {
        "app_key": "475230145",
        "app_secret": "36806cb1b76c27c95abf53487d5dc799",
        "redirectURL": "http://m.game.weibo.cn/oauth2/default",
        "signature_key": "178ae5aeb7ed0654668712ec4bafc652",
    },
    'kaopu': {
        "KAOPU_APPKEY": "10216",
        "KAOPU_SECRETKEY": "B7FA47A6-3765-4DE8-8DC5-7C8355D7C7C5",
        "KAOPU_APPID": "10216001",
        "KAOPU_APPVERSION": "1.0",
    },
    'coolpad': {
        'COOLPAD_APP_ID': '5000002454',
        'COOLPAD_APP_KEY': '4bcd7fccf85b4adeb438a3e9f97e9f82',
        'COOLPAD_PUBLIC_KEY': "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCVKQVCzLNsK0DbY60/5+NFVgTMvouVbuaVrRsRb3kvTUGtXp/8XYK465MZwI4HZmrBGJcSpNX9vaCBMO47YwhkPVGn/0CDhdjd+uRzGoBnfFWxVoR2eTZBCjoXXsPLOP+kCxWa5/e58O+/7NrfNT4QhZslO/WznUskQYQs/IH6YwIDAQAB",
    },
    'xx_ios': {
        "APP_ID": "102119",
        "server_secret_key": "2UJ7AU5ZDJGLZ40UHD3D908XC1QUDAMWCF3ADR8XWVP8IIC2M6BAIU88UOB2DRYO",
    },
    'xx': {
        "APP_ID": "102121",
        "server_secret_key": "WV1B12NQLIHTFR4ISVR69T428LKH8HAAHMSRIWX2AJZNYVOQ4CEDC0XJ6W07YJT9",
    },
    'meizu': {
        "AppID": "2820741",
        "AppKey": "e158c5bd9d2c49a29c890e5a588d9952",
        "AppSecret": "5Yw8PU48YF8dW2gZdHCHctTNwbYcfpIo",
    },
    'kaopu': {
        "KAOPU_APPKEY": "10216",
        "KAOPU_SECRETKEY": "B7FA47A6-3765-4DE8-8DC5-7C8355D7C7C5",
        "KAOPU_APPID": "10216001",
        "KAOPU_APPVERSION": "1.0",
    },
    'm4399': {
        "loginurl": "http://m.4399api.com/openapi/oauth-check.html",
        "appkey": "a91f175f827b4d0391cbfd3853b3d3b3",
    },
    'haomeng': {
        "appid": "516",
        "loginurl": "http://www.91wan.com/api/mobile/sdk_oauth.php",
        "login_key": "3CenL3VuMEunxzsDthNrSbvFa5$00516",
        "pay_key": "b251bc4ed8f58c95389a772702966416",
    },
    'yyb': {
        # 'qq_loginurl': 'http://msdktest.qq.com/auth/verify_login',
        # 'weixin_loginurl': 'http://msdktest.qq.com/auth/check_token',
        'qq_loginurl': 'http://msdk.qq.com/auth/verify_login',
        'weixin_loginurl': 'http://msdk.qq.com/auth/check_token',
        # 'qq_loginurl': 'http://msdk.tencent-cloud.net/auth/verify_login',
        # 'weixin_loginurl': 'http://msdk.tencent-cloud.net/auth/check_token',

        "weixin_appid": "wx84325ed5efe57c0d",
        "weixin_appkey": "323d6a6b28bb319056b5052b1ca38e5d",
        "qq_appid": "1104928607",
        # "qq_appkey": "ihNyP0xCjLGuLx0kog3SnU72H4Ccjtx1",
        "qq_appkey": "moGFruUJK4I6Re5C",
        "qq_paykey": "ihNyP0xCjLGuLx0kog3SnU72H4Ccjtx1",

        # 'domain': 'msdktest.qq.com',
        'domain': 'msdk.qq.com',
        # 'domain': 'msdk.tencent-cloud.net',
        'zones': {
            299: 1,
        }
    },
    'cc': {
        'login_url': 'http://android-api.ccplay.com.cn/api/v2/payment/checkUser',
        'app_key': '9c73cfb7562d4fcba71e40738e1acfd4',
    },
    'yijie': {
        'login_url': 'http://sync.1sdk.cn/login/check.html',
        'app_key': '{D848E772-DB4FAEFE}',
        'pay_key': 'RAH7Z26UII6BX7Y4FLG9R8EXSJFM2HVM',
    },
    'tiantian': {
        'login_url': 'http://sdk.ttigame.com/user/info',
        'app_id': 'LT20160107-118',
        'app_key': '0feda7238dff69be78ca38ef418459af',
    },
    'le8_ios': {
        'login_url': 'http://api.le890.com/index.php?m=api&a=validate_token',
        'app_id': '56e5c7a38d8e7f751927d3dd332e7a2c',
        'app_key': 'abc4919f1cb863402e71d9d075cc6c60',
    },
    'mmy': {
        'login_url': 'http://pay.mumayi.com/user/index/validation',
        'appKey': 'a192bfc26e8139fedUp2QhpSDo7KPdHZUXWQgKmFLNhaypH8PWwqzZdLfTAeYVLzuQZl'
    },
    'h07073': {
        'login_url': 'http://sdk.07073sy.com/index.php/User/v4',
        'pid': '399',
        'secretKey': '7F19DDC066A00268E229B3CED475C1'
    },
    'pyw': {
        # 'login_url': 'http://xp.yyft.com:8081/Cpapi/check',
        'login_url': 'http://pywsdk.pengyouwan.com/Cpapi/check',
        'apiSecret': '2a610833165198d5',
    },
    'liulian': {
        'login_url': 'http://user.6lyx.com/sdk/game/verifylogin',
        'appid': '69f0456c269a8dff6cfae986679b55ae',
        'appkey': 'acab48e810a53c0182e49762d39c9efc',
        'privatekey': '545908c7a34c01112cbd36cb78dd9e01',
    },
    'moge': {
        'appkey': '54c04b15356925679e31926498bd212f',
    },
}


# 支付宝参数
ALIPAY_PARAMS = {
    'partner': u'2088011077894531',
    'seller': u'limchen@yunyuegame.com',
}
# 是否使用关闭注册时间
ISUSECLOSESERVERTIME = 0
# 关闭注册时间
CLOSEREGTIME = '2013-11-19 18:00:00'

# session服务器最大在线人数
MAX_ONLINES = 5000

# 测试充值
TEST_PAY = False
# 开启充值
PAY = True

# 可以登录的客户端版本
CLIENTVERSIONLOGIN = 0

# 是否appsandbox支付
APPSANDBOX = False

# 注册限制3个
REGISTERLIMIT = True

DELAY_SAVE = False  # 延时存储玩家数据

CONFIG_FILE_PATH = os.path.join(
    os.path.split(os.path.abspath(__file__))[0], 'data')

# 关闭服务器添加超时处理
TIMEOUTCLOSESERVER = False

# session服务器白名单
LOGINLIMITMSG = u'服务器维护中，请耐心等待。'

REDISES = {
    # 用户数据
    'user': 'redis://10.170.155.65:19100',
    # 角色，游戏数据
    'entity': 'redis://10.170.155.65:19102',
    'friendfb': 'redis://10.170.155.65:19102',
    # 登录验证
    'session': 'redis://10.170.155.65:9000',
    # 服务器配置
    'settings': 'redis://10.170.155.65:9001',
    # cdkey
    'giftkey': 'redis://10.170.155.65:9002',
    'payment': 'redis://10.170.155.65:9003',
    # ID生成器
    'identity': 'redis://10.170.155.65:9004',
    # 各种索引，公会等级排行，玩家等级排行，玩家竞技场排行，用户名索引，角色名索引，公会名索引
    'index': 'redis://10.170.155.65:9004',
}


LONGLOG = False  # 是否开启longlog日志

FIGHT_VERIFY_SKIP = 1           # 每N个战斗校验一次
FIGHT_VERIFY_WORKERS = 4        # 起N个线程专门发送战斗校验请求
FIGHT_VERIFY_SKIP_FB = set([100111, 100112, 100113, 100114, 100115, 100116, 100120])  # 这些副本假战斗，不用校验
DIRECT_FIGHT_VERIFY = True  # 服务器端战斗校验
# FIGHT_VERIFY_URL = "http://10.170.127.71:21003"


#  {{ enter scene 同步 给客户端的字段
ENABLE_GIFTKEY = True
#  }}

SKIP_GUIDE = False  # 用来给客户端同步是否跳过指引

# SENTRY_DSN = 'gevent+http://8e061988c3e5421094d3969f8ce893bc:28697211dc7f41f5870aec9ae83ab42f@sentry.yunyuegame.com/9'

SDKAPP = {
    'host': '192.168.0.39',
    'port': 20002,
}

CLIENTOLDVERSION_NOTICE = ''

# 屏蔽sdk，能看到服务器列表，但登录服务器，显示维护公告，实例：{regionID: [sdkType, sdkType]}
DISALLOW_SDKS = {}
SENTRY_DSN = "sync+http://2a2ba8db864f43f98f46c35f6a8d6ed6:a416a95657e84bae981da98dc1cb622c@sentry.dnastdio.com:8888/5"
SERVER_DSN = "http://5fefd62e7e794752a852d443759282ef:5f52ab2254b349a5ad484109dabbb1af@sentry.dnastdio.com:8888/4"
TRIGGER_PACKS_FLAG = False
KICK_ACCLERATE = True

try:
    import git
    from datetime import datetime
    REV = datetime.fromtimestamp(
        git.Repo(os.path.dirname(
            os.path.abspath(__file__)
        )).commit().committed_date
    ).strftime("%Y-%m-%d %H:%M:%S")
    del git
except Exception as e:
    import sys
    print >> sys.stderr, "Read git rev:", e
    REV = ''
