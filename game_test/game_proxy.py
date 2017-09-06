#!/usr/bin/env python
# coding=utf-8

import ctypes
import random
import copy
import protocol.rainbow_pb as msgid
from protocol import rainbow_pb
from player.manager import g_playerManager

g_all_lib_game = {}

class GameProxyBase(object):
    def __init__(self, room_obj):
        self.room_obj = room_obj

        global g_all_lib_game
        if not g_all_lib_game[room_obj.game_id]:
            g_all_lib_game[room_obj.game_id] = ctypes.cdll.LoadLibrary('game_proxy/lib_game_%d.so'%room_obj.game_id)
        self.lib_game_handler = g_all_lib_game[room_obj.game_id].new_instance()

    def __del__(self):
        global g_all_lib_game
        g_all_lib_game[room_obj.game_id].destroy_instance(self.lib_game_handler)

    def start(self):
        pass


class GameProxyMahjong(GameProxyBase):
    def __init__(self, room_obj):
        GameProxyBase.__init__(self, room_obj)

        # 牌墙上所有的牌
        self.all_origin_lei_cards = []
        self.all_lei_cards = []

        # 有万字牌
        if room_obj.game_config['has_wan']:
            self.all_origin_lei_cards.extend([
                0, 0, 0, 0,             # 4 张 一万
                1, 1, 1, 1,             # 4 张 二万
                2, 2, 2, 2,             # 4 张 三万
                3, 3, 3, 3,             # 4 张 四万
                4, 4, 4, 4,             # 4 张 五万
                5, 5, 5, 5,             # 4 张 六万
                6, 6, 6, 6,             # 4 张 七万
                7, 7, 7, 7,             # 4 张 八万
                8, 8, 8, 8,             # 4 张 九万
                ])

        # 有索子牌
        if room_obj.game_config['has_tiao']:
            self.all_origin_lei_cards.extend([
                 9,  9,  9,  9,             # 4 张 一索
                10, 10, 10, 10,             # 4 张 二索
                11, 11, 11, 11,             # 4 张 三索
                12, 12, 12, 12,             # 4 张 四索
                13, 13, 13, 13,             # 4 张 五索
                14, 14, 14, 14,             # 4 张 六索
                15, 15, 15, 15,             # 4 张 七索
                16, 16, 16, 16,             # 4 张 八索
                17, 17, 17, 17,             # 4 张 九索
                ])

        # 有筒子牌
        if room_obj.game_config['has_tong']:
            self.all_origin_lei_cards.extend([
                18, 18, 18, 18,              # 4 张 一筒
                19, 19, 19, 19,              # 4 张 二筒
                20, 20, 20, 20,              # 4 张 三筒
                21, 21, 21, 21,              # 4 张 四筒
                22, 22, 22, 22,              # 4 张 五筒
                23, 23, 23, 23,              # 4 张 六筒
                24, 24, 24, 24,              # 4 张 七筒
                25, 25, 25, 25,              # 4 张 八筒
                26, 26, 26, 26,              # 4 张 九筒
                ])

        # 有风牌
        if room_obj.game_config['has_wind']:
            self.all_origin_lei_cards.extend([
                27, 27, 27, 27,              # 4 张 东
                28, 28, 28, 28,              # 4 张 南
                29, 29, 29, 29,              # 4 张 西
                30, 30, 30, 30,              # 4 张 北
                31, 31, 31, 31,              # 4 张 中
                32, 32, 32, 32,              # 4 张 发
                33, 33, 33, 33,              # 4 张 白
                ])

        # 有花牌
        if room_obj.game_config['has_flower']:
            self.all_origin_lei_cards.extend([
                34,      # 春夏秋冬梅兰菊竹
                35,
                36,
                37,
                38,
                39,
                40,
                41,
                ])
        # 

    def __del__(self):
        GameProxyBase.__del__(self)

    def start(self):
        GameProxyBase.start(self)

        # 在开始第一局的时候才初始化玩家数据
        if not self.all_user_data:
            # 玩家的数据
            self.all_user_data = {}
            for role in RoleIterator(self.room_obj):
                self.all_user_data[role.entityID] = {
                    'hand_cards': [],           # 玩家当前手牌              [1, 2, 3, 4]
                    'out_cards': [],            # 玩家当前出牌区的牌        [1, 2, 3, 4]
                    'block_cards': [],          # 玩家碰杠的牌              [ {'show_card_ids': [], 'really_card_ids': []}, ]
                    'flower_cards': [],         # 玩家补花的牌              [1, 2]
                    'ting_cards': [],           # 玩家当前的听牌列表        [ {'card_id': 1, 'remain_count': 1, 'points': 1}, ]
                    'block_op': [],             # 玩家当前可执行的拦牌操作  [ {'block_type': , 'src_server_index': None, 'src_card_id': None, 'self_card_ids': [1, 2], 'meld_card_ids': [1, 2, 3]}, ]
                    }

            # 游戏的数据
            self.play_count = 0                 # 当前局数
            self.total_play_count = 0           # 总的局数
            # self.ghost_card_data = {            # 鬼牌数据
            #     'flop_card_id': 0,                  # 翻出来的牌
            #     'ghost_card_ids': [],               # 真正的鬼牌
            #     'dice_num': [],                     # 一般是两颗骰子
            #     }

            self.banker_index = self.init_banker()              # 庄家
            self.user_turn_index = self.banker_index            # 轮到谁出牌

        # 新的一局，局数加 1
        self.play_count += 1

        # 重置牌墙中的牌的状态
        self.all_lei_cards = copy.deepcopy(self.all_origin_lei_cards)

        # 洗牌
        random.shuffle(self.all_lei_cards)

        # 摇骰子
        self.dice_num_1 = random.uniform(1, 6)
        self.dice_num_2 = random.uniform(1, 6)

        # 确定鬼牌
        self.flop_ghost_card()

        # 发牌，庄家14张，其他玩家13张
        self.last_card_top_index = -2   # 这个指向最后一墩牌的上面那张牌
        self.last_card_index = -1       # 这个指向最后一张牌
        for role in RoleIterator(self.room_obj):
            if role.pos_index == self.banker_index:
                self.all_user_data[role.entityID]['hand_cards'] = self.all_lei_cards[:14]
                self.all_lei_cards = self.all_lei_cards[14:]

                # 这个时候，只有庄家需要
                self.update_block_op()
            else:
                self.all_user_data[role.entityID]['hand_cards'] = self.all_lei_cards[:13]
                self.all_lei_cards = self.all_lei_cards[13:]

            # 更新一下听牌列表
            self.update_ting_cards(role)

        # 下发给玩家
        for role in RoleIterator(self.room_obj):
            rsp = self.pack_game_data(rainbow_pb.GameDataMahjong.Start, role['entityID'])
            g_playerManager.sendto(role['entityID'], success_msg(msgid.GAME_ROUND_START, rsp))

    # 初始化庄家，这个只在第一局开始的时候会被调用
    # 后面庄家，应该是在这一局结束的时候，根据状态来决定下一局的庄家是谁
    def init_banker(self):
        return 0        # 默认就是房主是第一局的庄家

    # 翻鬼牌，有些麻将需要打骰子来确定翻哪张牌
    def flop_ghost_card(self):
        if not self.room_obj.game_config['has_ghost_card']:
            return

        pass

    def update_ting_cards(self, role):
        pass

    def update_block_op(self, role):
        pass

    # 把当前游戏的数据全量打包，这个会在游戏开始的时候，以及玩家断线重连的时候需要用到
    def pack_game_data(self, game_status, entity_id):
        rsp = rainbow_pb.GameDataMahjong()
        rsp.game_status = game_status
        rsp.play_count = self.play_count
        rsp.total_play_count = self.total_play_count

        # 鬼牌数据
        if self.room_obj.game_config['has_ghost_card']:
            for card_id in self.ghost_card_data['ghost_card_ids']:
                rsp.ghost_data.ghost_card_ids.append(card_id)
            if self.ghost_card_data['flop_card_id']:
                rsp.ghost_data.flop_card_id = self.ghost_card_data['flop_card_id']
            if self.ghost_card_data['dice_num']:
                rsp.ghost_data.dice_data.append(self.ghost_card_data['dice_num'][0])
                rsp.ghost_data.dice_data.append(self.ghost_card_data['dice_num'][1])

        # 所有玩家的数据
        for r in RoleIterator(self.room_obj):
            rud = self.all_user_data[entity_id]

            ud = rsp.user_data.add()

            # 手牌，下发真ID
            if r.entityID == entity_id:
                for card_id in rud['hand_cards']:
                    ud.hand_card_ids.append(card_id)

                # 听牌列表
                for v in rud['ting_cards']:
                    tc = ud.ting_list.add(**v)

                # 可拦牌操作
                for v in rud['block_op']:
                    bo = ud.block_list.add()
                    bo.block_type = v['block_type']

                    if v['src_server_index']:
                        bo.src_server_index = v['src_server_index']
                        bo.src_card_id = v['src_card_id']

                    for card_id in v['self_card_ids']:
                        bo.self_card_ids.append(card_id)

                    for card_id in v['meld_card_ids']:
                        bo.meld_card_ids.append(card_id)
            else:
                for card_id in rud['hand_cards']:
                    ud.hand_card_ids.append(0)

            # 出牌区的牌
            for card_id in rud['out_cards']:
                ud.out_card_ids.append(card_id)

            # 碰杠区的牌
            for v in rud['block_cards']:
                bc = ud.block_cards.add()
                for card_id in v['show_card_ids']:
                    bc.append(card_id)

            # 以及补了花的花牌
            for card_id in rud['flower_cards']:
                ud.flower_card_ids.append(card_id)

        # 当前庄家是谁，以及轮到谁出牌
        rsp.banker_server_index = self.banker_index
        rsp.user_turn_server_index = self.user_turn_index

        return rsp

    # 玩家从牌墙摸牌，如果是杠的话，就从牌墙的末尾拿牌
    def user_draw_card(self, is_kong):
        if len(self.all_lei_cards) == 0:
            return -1

        # 杠的话从后面拿牌
        if not is_kong:
            card_id = self.all_lei_cards[:1]
            self.all_lei_cards = self.all_lei_cards[1:]

        # 摸牌后，判断是否有拦牌

        return card_id

    def check_out_card_block_op(self, card_id, rsp):
        pass

    def user_out_card(self, player, req):
        role = self.room_obj.get_role(player.entityID)
        if not role:
            return FAIL_MSG_GAME_PLAYER_NOT_FOUND

        if role.pos_index != self.user_turn_index:
            return FAIL_MSG_GAME_OUT_CARD_TURN_ERROR

        user_data = self.all_user_data[player.entityID]
        if not user_data:
            return FAIL_MSG_GAME_PLAYER_NOT_FOUND

        if req.card_id not in user_data['hand_cards']:
            return FAIL_MSG_GAME_OUT_CARD_NO_CARD

        # 从手牌中移除
        user_data['hand_cards'].remove(req.card_id)

        # response
        rsp = rainbow_pb.UserOutCardResponse()
        rsp.server_index = self.user_turn_index
        rsp.card_id = req.card_id

        # 是否有拦牌，如果没有的话，就下一个摸牌
        if not self.check_out_card_block_op(req.card_id, rsp):
            self.user_draw_card(False)

        return rsp

# 
class GameProxyPoker(GameProxyBase):
    def __init__(self, room_obj):
        GameProxyBase.__init__(self, room_obj)

    def __del__(self):
        GameProxyBase.__del__(self)

    def start(self):
        GameProxyBase.start(self)
