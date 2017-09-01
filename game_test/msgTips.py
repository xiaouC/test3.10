# coding:utf-8
# Purpose: 消息提示CODE常量集合
# Created: 2012-12-7

SUCCESS_MSG                                 = 0

FAIL_MSG_LOGIN_WRONG_ACCOUNT = 1
FAIL_MSG_LOGIN_PLAYERNAME_EXIST = 2
FAIL_MSG_LOGIN_PLAYERNAME_ISEMPTY = 3
FAIL_MSG_LOGIN_LINE_TIME_OUT = 4
FAIL_MSG_ALREADY_LOGIN = 6

FAIL_MSG_ROOM_NOT_EXIST                     = 100               # 房间不存在
FAIL_MSG_ROOM_LIMIT_EXCEED                  = 101               # 超过人数限制
FAIL_MSG_ROOM_PLAYER_NOT_EXIST              = 102               # 玩家不存在
FAIL_MSG_ROOM_DISMISSED                     = 103               # 已经解散了
FAIL_MSG_ROOM_KICK_OUT_PERMISSION_DENY      = 104
FAIL_MSG_ROOM_CREATE_HAS_ROOM               = 105               # 已经在房间里，不能创建
FAIL_MSG_ROOM_DISMISS_CANCEL                = 106               # 解散
FAIL_MSG_NOT_ALL_USER_READY                 = 107               # 有玩家还没准备就绪

FAIL_MSG_GAME_PLAYER_NOT_FOUND              = 108               # 在房间中没有找到玩家
FAIL_MSG_GAME_OUT_CARD_TURN_ERROR           = 109               # 不是轮到你出牌
FAIL_MSG_GAME_OUT_CARD_NO_CARD              = 110               # 手牌中没有这张牌
