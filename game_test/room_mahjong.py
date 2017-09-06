#!/usr/bin/env python
# coding=utf-8

from game.room_base import RoomBase, RoomRoleSitDownIterator, RoomRoleAllIterator

class RoomMahjong(RoomBase):
    def __init__(self, room_id, entity_id, game_id, game_settings):
        super(RoomMahjong, self).__init__(room_id, entity_id, game_id, game_settings)

        self.all_origin_lei_cards = []
        self.all_lei_cards = []

        if self.game_config['has_wan']:
            self.all_origin_lei_cards.extend([
                0, 0, 0, 0,
                1, 1, 1, 1,
                2, 2, 2, 2,
                3, 3, 3, 3,
                4, 4, 4, 4,
                5, 5, 5, 5,
                6, 6, 6, 6,
                7, 7, 7, 7,
                8, 8, 8, 8,
                ])

        if self.game_config['has_tiao']:
            self.all_origin_lei_cards.extend([
                 9,  9,  9,  9,
                10, 10, 10, 10,
                11, 11, 11, 11,
                12, 12, 12, 12,
                13, 13, 13, 13,
                14, 14, 14, 14,
                15, 15, 15, 15,
                16, 16, 16, 16,
                17, 17, 17, 17,
                ])

        if self.game_config['has_tong']:
            self.all_origin_lei_cards.extend([
                18, 18, 18, 18,
                19, 19, 19, 19,
                20, 20, 20, 20,
                21, 21, 21, 21,
                22, 22, 22, 22,
                23, 23, 23, 23,
                24, 24, 24, 24,
                25, 25, 25, 25,
                26, 26, 26, 26,
                ])

        if self.game_config['has_wind']:
            self.all_origin_lei_cards.extend([
                27, 27, 27, 27,
                28, 28, 28, 28,
                29, 29, 29, 29,
                30, 30, 30, 30,
                31, 31, 31, 31,
                32, 32, 32, 32,
                33, 33, 33, 33,
                ])

        if self.game_config['has_flower']:
            self.all_origin_lei_cards.extend([
                34, 35, 36, 37,
                38, 39, 40, 41,
                ])

    def __del__(self):
        super(RoomMahjong, self).__del__()

    def player_reconn(self, player):
        super(RoomMahjong, self).player_reconn(player)

    def game_start(self):
        if not self.all_user_data:
            self.all_user_data = {}
            for role_info in RoomRoleSitDownIterator(self):
                self.all_user_data[role.entityID] = {
                    'hand_cards': [],           # [1, 2, 3, 4]
                    'out_cards': [],            # [1, 2, 3, 4]
                    'block_cards': [],          # [ {'show_card_ids': [], 'really_card_ids': []}, ]
                    'flower_cards': [],         # [1, 2]
                    'ting_cards': [],           # [ {'card_id': 1, 'remain_count': 1, 'points': 1}, ]
                    'all_ting_list':[],         # c struct
                    'block_op': [],             # [ {'block_type': , 'src_server_index': None, 'src_card_id': None, 'self_card_ids': [1, 2], 'meld_card_ids': [1, 2, 3]}, ]
                    }

            # self.ghost_card_data = {
            #     'flop_card_id': 0,
            #     'ghost_card_ids': [],
            #     'dice_num': [],
            #     }

        # game status
        self.game_status = 'playing'

        # new round
        self.play_count += 1

        # init banker
        self.banker_index = self.init_banker()
        self.user_turn_index = self.banker_index

        # reset card wall
        self.all_lei_cards = copy.deepcopy(self.all_origin_lei_cards)

        # shuffle
        random.shuffle(self.all_lei_cards)

        # dice
        self.dice_num_1 = random.uniform(1, 6)
        self.dice_num_2 = random.uniform(1, 6)

        # ghost card
        self.flop_ghost_card()

        # 
        self.last_card_top_index = -2   # 这个指向最后一墩牌的上面那张牌
        self.last_card_index = -1       # 这个指向最后一张牌
        for role_info in RoomRoleSitDownIterator(self):
            if role_info['server_index'] == self.banker_index:
                self.all_user_data[role_info['entityID']]['hand_cards'] = self.all_lei_cards[:14]
                self.all_lei_cards = self.all_lei_cards[14:]

                self.update_block_op(role_info)
                self.update_ting_cards(role_info)
            else:
                self.all_user_data[role_info['entityID']]['hand_cards'] = self.all_lei_cards[:13]
                self.all_lei_cards = self.all_lei_cards[13:]

        for role_info in RoomRoleSitDownIterator(self):
            rsp = self.pack_game_data(rainbow_pb.GameDataMahjong.Start, role_info['entityID'])
            g_playerManager.sendto(role_info['entityID'], success_msg(msgid.GAME_ROUND_START, rsp))

    def player_out_card(self, player, card_id):
        if self.game_status != 'playing':
            return msgTips.GAME_STATUS_NOT_PLAYING

        role_info = self.get_role_info(player.entityID)
        if role_info['server_index'] != self.user_turn_index:
            return msgTips.OUT_CARD_NOT_YOUR_TURN

        user_data = self.all_user_data[player.entityID]
        if card_id not in user_data['hand_cards']:
            return msgTips.OUT_CARD_CARD_ID_NOT_FOUND

        # remove from hand cards and add to out cards
        user_data['hand_cards'].remove(card_id)
        user_data['out_cards'].append(card_id)

        # response
        rsp = rainbow_pb.UserOutCardResponse()
        rsp.server_index = self.user_turn_index
        rsp.card_id = card_id

        # if no one can block, then next user draw card
        if not self.check_out_card_block_op(player.entityID, card_id, rsp):
            new_card_id = self.player_draw_card(False)
            if new_card_id == -1:
                rsp.is_game_failed = True
                return rsp

            # next user
            self.user_turn_index = self.get_next_user_turn(self.user_turn_index)
            next_role_info = self.get_role_info_by_server_index(self.user_turn_index)
            self.update_block_op(next_role_info)
            self.update_ting_cards(next_role_info)

            rsp.next_user_draw_card.server_index = self.user_turn_index
            rsp.next_user_draw_card.card_id = new_card_id
            self.pack_all_ting_list(rsp)
            rsp.next_user_draw_card.block_list

        return rsp

    def player_do_block(self, player, block_index):
        pass

    def init_banker(self):
        pass

    def flop_ghost_card(self):
        if not self.game_config['has_ghost_card']:
            return

        pass

    def update_ting_cards(self, role):
        pass

    def update_block_op(self, role):
        pass

    def check_out_card_block_op(self, ignore_entity_id, card_id, rsp):
        pass

    def player_draw_card(self, is_kong):
        if len(self.all_lei_cards) == 0:
            return -1

        if not is_kong:
            card_id = self.all_lei_cards[:1]
            self.all_lei_cards = self.all_lei_cards[1:]
        else:
            card_id = self.all_lei_cards[:1]
            self.all_lei_cards = self.all_lei_cards[1:]

        # 摸牌后，判断是否有拦牌

        return card_id


    def pack_game_data(self, game_status, entity_id):
        rsp = rainbow_pb.GameDataMahjong()
        rsp.game_status = game_status
        rsp.play_count = self.play_count
        rsp.total_play_count = self.total_play_count

        # ghost card
        if self.game_config['has_ghost_card']:
            for card_id in self.ghost_card_data['ghost_card_ids']:
                rsp.ghost_data.ghost_card_ids.append(card_id)
            if self.ghost_card_data['flop_card_id']:
                rsp.ghost_data.flop_card_id = self.ghost_card_data['flop_card_id']
            if self.ghost_card_data['dice_num']:
                rsp.ghost_data.dice_data.append(self.ghost_card_data['dice_num'][0])
                rsp.ghost_data.dice_data.append(self.ghost_card_data['dice_num'][1])

        # all user data
        for role_info in RoomRoleSitDownIterator(self):
            rud = self.all_user_data[role_info['entityID']]

            ud = rsp.user_data.add()
            if role_info['entityID'] == entity_id:
                for card_id in rud['hand_cards']:
                    ud.hand_card_ids.append(card_id)

                for v in rud['ting_cards']:
                    ud.ting_list.add(**v)

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

            for card_id in rud['out_cards']:
                ud.out_card_ids.append(card_id)

            for v in rud['block_cards']:
                bc = ud.block_cards.add()
                for card_id in v['show_card_ids']:
                    bc.append(card_id)

            for card_id in rud['flower_cards']:
                ud.flower_card_ids.append(card_id)

        # banker & user turn
        rsp.banker_server_index = self.banker_index
        rsp.user_turn_server_index = self.user_turn_index

        return rsp

    def pack_all_ting_list(self, rsp):
        pass
