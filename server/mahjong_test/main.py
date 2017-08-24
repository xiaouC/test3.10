#!/usr/bin/python
# coding: utf-8

# from ctypes import *
import ctypes
import os, json

libmahjong = ctypes.cdll.LoadLibrary(os.getcwd() + '/libs/libmahjong.so') 
libmahjong.init_rules.argtypes = (ctypes.c_char_p,)
libmahjong.check_is_win_json.restype = ctypes.c_void_p
libmahjong.free_pointer.argtypes = (ctypes.c_void_p,)

from cards.tile_common import insert_card
from cards.tile_common import check_is_win

from cards.tile_ai import TileAI

rules = {
        'kinds_group' : [
            # { 'kind_start' : 0,  'kind_end' : 0 },      #
            # { 'kind_start' : 1,  'kind_end' : 1 },      #
            # { 'kind_start' : 2,  'kind_end' : 2 },      #
            # { 'kind_start' : 3,  'kind_end' : 3 },      #
            # { 'kind_start' : 4,  'kind_end' : 4 },      #
            # { 'kind_start' : 5,  'kind_end' : 5 },      #
            # { 'kind_start' : 6,  'kind_end' : 6 },      #
            # { 'kind_start' : 7,  'kind_end' : 7 },      #
            # { 'kind_start' : 8,  'kind_end' : 8 },      #
            { 'kind_start' : 0,  'kind_end' : 8 },      #
            { 'kind_start' : 9,  'kind_end' : 17 },     #
            { 'kind_start' : 18, 'kind_end' : 26 },     #
            { 'kind_start' : 27, 'kind_end' : 35 },     #
            ],
        }


if __name__ == '__main__':
    json_rules = json.dumps(rules)
    print 'json_rules : [%s]'%json_rules 
    print type(json_rules)

    libmahjong.init_rules(json_rules) 

    ID = libmahjong.new_instance()
    libmahjong.insert_tile(ID, 20, 3);
    libmahjong.insert_tile(ID, 5, 1)
    libmahjong.insert_tile(ID, 6, 1)
    libmahjong.insert_tile(ID, 7, 2)
    libmahjong.insert_tile(ID, 8, 3)
    libmahjong.insert_tile(ID, 9, 3)

    ghost_kind = -1
    join_tile_kind = 5

    from time import clock
    start_time = clock()

    win_sequence_ptr = libmahjong.check_is_win_json(ID, join_tile_kind, ghost_kind)

    finish_time = clock()

    win_sequence_data = json.loads(ctypes.cast(win_sequence_ptr, ctypes.c_char_p).value)
    if win_sequence_data != None:
        for item in win_sequence_data:
            print item['sequence'].split(',')
        print 'total : ', len(win_sequence_data)

    libmahjong.free_pointer(win_sequence_ptr)
    print '======================================='
    print (finish_time - start_time)

    draw_kind = libmahjong.draw_tile(ID, join_tile_kind, ghost_kind)
    print 'draw_kind : ', draw_kind





    # # 
    # my_cards = {}

    # insert_card(my_cards, 0, 3)
    # # insert_card(my_cards, 1, 1)
    # #insert_card(my_cards, 2, 1)
    # #insert_card(my_cards, 3, 1)
    # insert_card(my_cards, 4, 1)
    # insert_card(my_cards, 5, 1)
    # insert_card(my_cards, 6, 1)
    # insert_card(my_cards, 7, 1)
    # insert_card(my_cards, 8, 3)
    # insert_card(my_cards, 9, 3)

    # ghost_kind = 9

    # start_time = clock()
    # win_sequence = check_is_win(my_cards, 3, ghost_kind, rules)
    # finish_time = clock()
    # print 'win_sequence : ====================================================='
    # for v in win_sequence:
    #     print v
    # print '======================================='
    # print (finish_time - start_time)









    # ai_cards = {}

    # insert_card(ai_cards, 0, 1)
    # insert_card(ai_cards, 4, 2)
    # insert_card(ai_cards, 7, 3)
    # insert_card(ai_cards, 9, 2)
    # insert_card(ai_cards, 14, 1)
    # insert_card(ai_cards, 17, 1)
    # insert_card(ai_cards, 18, 1)
    # insert_card(ai_cards, 12, 2)

    # insert_card(ai_cards, 3, 1)

    # tile_ai = TileAI(None, ai_cards, rules)
    # print tile_ai.get_discard_kind([1, 1, 2, 3, 4, 5, 6])
    # print tile_ai.get_discard_kind([1, 2, 3, 4, 5, 6, 6])
    # print 'all_cards : ====================================================='
    # print ai_cards
    # all_segments = tile_ai.split_cards()
    # print 'all_segments : ====================================================='
    # print all_segments


    # # tile_ai.check_is_single_card(14, 9, 17, 1)

    # all_single_cards = tile_ai.get_single_card(1)
    # print 'all_single_cards : ====================================================='
    # print all_single_cards

    # print 'has_only_one_pair : ====================================================='
    # print tile_ai.has_only_one_pair()
