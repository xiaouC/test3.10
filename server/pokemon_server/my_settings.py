# coding: utf-8
from global_settings import *

LOG['formatters']["gmflow"] = {
	"format":"%(message)s",
	"datefmt":"",
}

LOG["handlers"]["dump"] = {
	'class': 'logging.handlers.TimedRotatingFileHandler',
	'formatter':'gmflow',
	'filename': 'log/gmflow',
	'when':'M',
	'interval':5,#how long to backup.
	#'backupCount':7,#max backups.
}

LOG["loggers"]["gmflow"] = {
	'handlers':['dump'],
	'level': 'ERROR',
	'propagate': False,
}

LOG['loggers']['db'] = {
    'handlers':['console'],
    'level': 'DEBUG',
    'propagate': False,
}

LOG['loggers']['property'] = {
    'handlers':['console'],
    'level': 'INFO',
    'propagate': False,
}

LOG['loggers']['rpc'] = {
    'handlers':['console'],
    'level': 'DEBUG',
    'propagate': False,
}

LOG['loggers']['world'] = {
    'handlers':['console'],
    'level': 'DEBUG',
    'propagate': False,
}

LOG['loggers']['taskReward'] = {
    'handlers':['console'],
    'level': 'DEBUG',
    'propagate': False,
}

LOG['loggers']['campaign'] = {
    'handlers':['console'],
    'level': 'DEBUG',
    'propagate': False,
}

LOG['loggers']['role'] = {
    'handlers':['console'],
    'level': 'DEBUG',
    'propagate': False,
}

LOG['loggers']['lineup'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

LOG['loggers']['pvp'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

LOG['handlers']['console'] = {
    'level': 'DEBUG',
    'class': 'logging.StreamHandler',
    'formatter': 'simple'
}

LOG['handlers']['credis'] = {
    'level': 'INFO',
    'class': 'logging.StreamHandler',
    'formatter': 'simple'
}

LOG['root'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
}

LOG['handlers']['dump'] = {
    'class': 'logging.handlers.WatchedFileHandler',
    'formatter':'gmflow',
    'filename': 'log/gmflow',
    #'backupCount':7,#max backups.
}

SESSION['CHANNEL'] = 'ANDROID'
SESSION['CHANNEL_IOS_ADDR'] = 'localhost:30051'

import socket

world_host = socket.gethostbyname(socket.gethostname())
WORLD = {
    'ID': 100,
    'ip': world_host,  # session服务器发送给客户端连接用
    'port': 11000,
    'mode': 'NORMAL',  # NORMAL 或者 DEBUG
    'managehost': '0.0.0.0',
    'manageport': 11001,     # 用于内部管理任务，比如监控，定时任务
    'backdoorport': 11002,     # python shell
}

import socket
regionID = int(socket.gethostbyname(socket.gethostname()).split(".")[-1])

REGION = {
    'ID':regionID,
}

PROXY = {
    'host':'192.168.0.249',
    'port':20001
}

ENABLE_FIGHT_CD = False
TEST_PAY = True

LOG['formatters']['gmflow']['datefmt'] = '%s'
LOG['handlers']['dump']['filename'] = 'log/%s_gmflow'%main_package
CHECKRECEIPT = False
CLIENTVERSIONLOGIN = 0

REGISTERLIMIT = False
DESIGNDATA = 'data'
DELAY_SAVE = False

TESTPAY = True

REDISES  = {
    #登录验证
    'session': 'redis://192.168.0.249:10000/3',
    #ID生成器
    'identity': 'redis://192.168.0.249:10000/1',
    #用户数据
    'user':'redis://192.168.0.249:10000/1',
    #角色，游戏数据
    'entity':'redis://192.168.0.249:10000',
    #服务器配置
    'settings':'redis://192.168.0.249:10000/2',
    #各种索引，公会等级排行，玩家等级排行，玩家竞技场排行，用户名索引，角色名索引，公会名索引
    'index':'redis://192.168.0.249:10000/1',
    #cdkey
    'giftkey': 'redis://192.168.0.249:10000/2',
    'friendfb':'redis://192.168.0.249:10000',
}
