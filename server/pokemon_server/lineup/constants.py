# coding:utf-8
from protocol import poem_pb

LINEUP_LENGTH_LIMIT = 4


class LineupType:
    DEF = poem_pb.LineupTypeDEF
    ATK = poem_pb.LineupTypeATK
    Mine1 = poem_pb.LineupTypeMine1
    Mine2 = poem_pb.LineupTypeMine2
    Daily = poem_pb.LineupTypeDaily
    City = poem_pb.LineupTypeCity
    Accredit = poem_pb.LineupTypeAccredit
