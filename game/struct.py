#!/usr/bin/python
# coding: utf-8

from ctypes import *

class TingItem(Structure):
    _fields_ = [
            ('card_id', c_int),
            ('valid_count', c_int),
            ('valid_ids', c_int * 34),
            ]

class TingList(Structure):
    _fields_ = [
            ('count', c_int),
            ('items', TingItem * 14),
            ]

class InputData(Structure):
    _fields_ = [
            ('hand_cards_num', c_int),
            ('hand_cards', c_int * 14),
            ('ghost_card_id_1', c_int),
            ('ghost_card_id_2', c_int),
            ]
