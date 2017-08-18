#coding:utf-8
from test.utils import *
from protocol import poem_pb
import protocol.poem_pb as msgid

def auto_breed():
    print 'auto breed'
    player = get_player(getcurrent())
    valuables = player.get_valuable_pets()
    for petID in valuables:
        petIDs = list(set(player.get_feeding_pets()).difference(player.get_lineuped_pets()))[:10]
        if not petIDs:
            petIDs = list(set(player.get_futile_pets()).difference(player.get_lineuped_pets()))[:10]
        breed(petID, petIDs)

def auto_sale():
    print 'auto sale'
    player = get_player(getcurrent())
    petIDs = list(set(player.get_futile_pets()).difference(player.get_lineuped_pets()))[:10]
    return sale(petIDs)

def breed(t_petID, petIDs):
    req = poem_pb.RequestHeroBreed(
        targetHeroID=t_petID,
        materialHeroIDs=petIDs,
    )
    sock = get_peer(getcurrent())
    sock.sendall(request_msg(msgid.HERO_BREED, req))
    rsp = expect(msgid.HERO_BREED, poem_pb.ResponseHeroBreed)
    player = get_player(getcurrent())
    for petID in petIDs:
        player.del_pet(petID)
    return rsp

def sale(petIDs):
    req = poem_pb.RequestHeroSale(
        heroIDs=petIDs
    )
    sock = get_peer(getcurrent())
    sock.sendall(request_msg(msgid.HERO_SALE, req))
    rsp = expect(msgid.HERO_SALE, poem_pb.ResponseHeroSale)
    player = get_player(getcurrent())
    for petID in petIDs:
        player.del_pet(petID)
    return rsp
