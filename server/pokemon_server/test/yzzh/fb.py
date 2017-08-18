# coding:utf-8
from test.utils import *  # NOQA
from gevent import getcurrent
from protocol import poem_pb
from .pet import auto_breed, auto_sale
from .mall import buy_sp, expand_pet_box
from .rank import main as rank_main


def enter_fb(fbID, allow_error=False):
    print 'enter', fbID
    sock = get_peer(getcurrent())
    sock.sendall(
        request_msg(msgid.ENTER_FB, poem_pb.EnterFbRequest(fbID=fbID)))
    return expect(
        msgid.ENTER_FB, poem_pb.EnterFbResponse, allow_error=allow_error)


def group_rewards(rsp):
    result = []
    rewards = rsp.rewards
    result += rewards
    for d in rsp.drops:
        result += d.must
        result += d.maybe
    return result


def end_fb(fbID, rewards, verify_code, allow_error=False):
    sock = get_peer(getcurrent())
    # player = get_player(getcurrent())
    req = poem_pb.EndFbRequest(
        fbID=fbID,
        rewards=rewards,
    )
    req.verify_code = verify_code
    sock.sendall(request_msg(msgid.END_FB, req))
    return expect(msgid.END_FB, poem_pb.EndFbResponse, allow_error=allow_error)


def main(sock):
    player = get_player(getcurrent())
    fbID = sorted(player.fbs.keys())[0]
    try:
        while True:
            count = player.get_fb_count(fbID)
            if not count:
                fbID = player.get_fblinked().get(fbID, 0)
                if not fbID:
                    break
                else:
                    continue
            try:
                rsp = enter_fb(fbID)
            except ExpectException as e:
                if e.body == '用户携带怪物数量已到上限':
                    try:
                        auto_breed()
                    except ExpectException as e:
                        if e.code == 582:  # 钱币不足
                            try:
                                auto_sale()
                            except ExpectException as ee:
                                if ee.body == '没有可以出售的将':
                                    expand_pet_box()
                                else:
                                    raise ee
                        elif e.body == '没有可以吞噬的将':
                            expand_pet_box()
                        else:
                            raise e
                elif e.body == '能量不足':
                    buy_sp()
                else:
                    raise e
            else:
                print 'fighting'
                rewards = group_rewards(rsp)
                verify_code = rsp.verify_code
                rand_sleep(50, 30)
                rsp = end_fb(fbID, rewards, verify_code)
                player.update_fb(fbID, count - 1)
                for fb in rsp.newFbInfos:
                    player.update_fb(fb.fbID, fb.count)
                fbID = player.get_fblinked().get(fbID, 0)
                if not fbID:
                    print 'not fb break'
                    break
    except ExpectException as e:
        rank_main(sock)
