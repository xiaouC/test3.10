# coding:utf-8
from test.utils import *
from protocol import poem_pb
import protocol.poem_pb as msgid


def get_opponents_thumb():
    sock = get_peer(getcurrent())
    sock.sendall(request_msg(msgid.PVP_OPPONENT_LIST))
    return expect(msgid.PVP_OPPONENT_LIST, poem_pb.PvpOpponentList)


def fight():
    sock = get_peer(getcurrent())
    sock.sendall(request_msg(msgid.PVP_START_FIGHT))
    try:
        start_rsp = expect(msgid.PVP_START_FIGHT, poem_pb.TargetDetailResponse)
    except ExpectException as e:
        if e.body == '挑战CD中':
            sock.sendall(request_msg(msgid.PVP_CLEAN_CD))
        else:
            raise e
    else:
        req = poem_pb.PvpEndFightRequest(
            fight={"fightResult": True},
            verify_code=start_rsp.verify_code
        )
        sock.sendall(request_msg(msgid.PVP_FINAL_FIGHT, req))
        end_rsp = expect(msgid.PVP_FINAL_FIGHT, poem_pb.PvpEndFightResponse)


def main(sock):
    player = get_player(getcurrent())
    while player.rank_free_vs or player.vs or player.gold > 20:
        fight()
        sleep(1)
