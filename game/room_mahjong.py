#!/usr/bin/env python
# coding=utf-8

from game.struct import *
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
        # 如果这是第一局的话，那么就清理掉房间中的无关的玩家
        if self.play_count == 0:
            # 当前的所有玩家的拦牌操作:
            # [
            #     {
            #         'block_priority': rainbow_pb.Block_Priority_Unknown,    # 拦牌的优先级
            #         'block_type': rainbow_pb.Pong,                          # 拦牌的类型
            #         'src_server_index': None,                               # 出牌的玩家
            #         'src_card_id': None,                                    # 出牌的 ID
            #         'dest_server_index': 1,                                 # 拦牌的玩家
            #         'dest_card_ids': [1, 2],                                # 如果拦牌成功，需要从拦牌玩家手牌中移除的 ID
            #         'show_card_ids': [1, 2, 3],                             # 最终显示的牌
            #         'block_status': rainbow_pb.Block_Status_Unknown,        # 拦牌的状态
            #     },
            # ]
            self.all_block_op = []
            self.cur_block_priority = rainbow_pb.Block_Priority_Unknown         # 当前的玩家选择的最大优先级
            self.top_block_priority = rainbow_pb.Block_Priority_Unknown         # 在所有的拦牌操作里面，最大的优先级
            self.top_block_priority_wait_num = 0                                # 需要等待的最大优先级的个数

            # 初始化玩家的一些数据
            for role_info in RoomRoleIterator(self):
                role_info['hand_cards'] = []                # [1, 2, 3, 4]
                role_info['out_cards'] = []                 # [1, 2, 3, 4]
                role_info['flower_cards'] = []              # [1, 2]
                role_info['block_cards'] = []               # [ {'block_type': 'kong', 'show_card_ids': [], 'really_card_ids': [], 'src_server_index': 0, 'src_card_id':1, 'self_card_list':[]}, ]
                role_info['all_ting_list'] = TingList()     # c struct

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
        for role_info in RoomRoleIterator(self):
            if role_info['server_index'] == self.banker_index:
                role_info['hand_cards'] = self.all_lei_cards[:14]
                self.all_lei_cards = self.all_lei_cards[14:]

                self.update_block_op()
                self.update_ting_cards(role_info)
            else:
                role_info['hand_cards'] = self.all_lei_cards[:13]
                self.all_lei_cards = self.all_lei_cards[13:]

        for role_info in RoomRoleIterator(self):
            rsp = self.pack_game_data(rainbow_pb.GameDataMahjong.Start, role_info['entityID'])
            g_playerManager.sendto(role_info['entityID'], success_msg(msgid.GAME_ROUND_START, rsp))

    def player_out_card(self, player, card_id):
        role_info = self.get_role_info_by_server_index(self.user_turn_index)

        # remove from hand cards and add to out cards
        role_info['hand_cards'].remove(card_id)
        role_info['out_cards'].append(card_id)

        # response
        rsp = rainbow_pb.UserOutCardResponse()
        rsp.server_index = self.user_turn_index
        rsp.card_id = card_id

        # if no one can block, then next user draw card
        self.update_block_op(role_info['server_index'], card_id)
        need_block_op = True if self.all_block_op else False
        new_card_id = -1
        if not need_block_op:
            # next turn user
            self.user_turn_index = self.get_next_user_turn(self.user_turn_index)
            next_role_info = self.get_role_info_by_server_index(self.user_turn_index)

            new_card_id = self.player_draw_card(next_role_info, False)
            if new_card_id == -1:
                rsp.game_faile = True
            else:
                self.pack_user_draw_card(role_info, rsp.user_draw_card, new_card_id)

        # send msg
        for other_role_info in RoomRoleIterator(self):
            # 出牌的玩家的 msg 在 rsp
            if other_role_info['entityID'] == player.entityID:
                continue

            rsp_other = rainbow_pb.UserOutCardResponse()
            rsp_other.server_index = rsp.server_index
            rsp_other.card_id = rsp.card_id

            # 如果有拦牌操作的话，就打包拦牌数据进去
            # 否则，就到下一个玩家摸牌
            if need_block_op:
                self.pack_block_op_list(other_role_info, rsp_other.block_list)
            else:
                # 如果没有摸到牌，就是流局了
                if new_card_id != -1:
                    self.pack_user_draw_card(other_role_info, rsp_other.user_draw_card, new_card_id)
                else:
                    rsp_other.game_faile = True

            g_playerManager.sendto(other_role_info['entityID'], success_msg(msgid.MAHJONG_OUT_CARD, rsp_other))

        return rsp

    def player_do_block(self, player, block_index):
        role_info = self.get_role_info(player.entityID)

        # block_index == -1 的话，就是取消
        block_op_data = self.all_block_op[block_index] if block_index != -1 else None
        need_wait_others = False

        # 更新拦牌列表的状态
        # 如果是取消的话，那么就把这个玩家的所有拦牌操作全部无效
        for index, v in enumerate(self.all_block_op):
            if v['block_status'] = rainbow_pb.Block_Status_Invalid:
                continue

            if index == block_index:
                v['block_status'] = rainbow_pb.Block_Status_Finish
                continue

            # 如果是同一个玩家的，那么这个玩家所对应的其他拦牌操作全部无效
            if v['dest_server_index'] == role_info['server_index']:
                v['block_status'] = rainbow_pb.Block_Status_Invalid
                continue

            # 如果是取消的话，只要还有等待玩家操作的，那么就需要等待
            if block_index == -1:
                if v['block_status'] == rainbow_pb.Block_Status_Waiting_Player:
                    need_wait_others = True
                    break
            else:
                # 如果还有相同优先级或者更高优先级的玩家未操作的话，需要等待
                # 相同优先级，应该就只有一炮多响了
                if v['block_priority'] >= block_op_data['block_priority'] and v['block_status'] == rainbow_pb.Block_Status_Waiting_Player:
                    need_wait_others = True
                    break

        # 需要等待
        rsp = rainbow_pb.BlockResponse()
        if need_wait_others:
            rsp.waiting_others = True
            return rsp

        # 不需要等待其他玩家的操作，就找出真出起作用的操作
        effect_priority = rainbow_pb.Block_Status_Unknown
        effect_indices = []
        for index, v in enumerate(self.all_block_op):
            if v['block_status'] != rainbow_pb.Block_Status_Finish:
                continue

            if v['block_priority'] == effect_priority:
                effect_indices.append(index)
                continue

            if v['block_priority'] > effect_priority:
                effect_priority = v['block_priority']
                effect_indices = [ index ]

        # 大家都取消了，那就到下一个玩家摸牌了
        if len(effect_indices) == 0:
            self.user_turn_index = self.get_next_user_turn(self.user_turn_index)
            next_role_info = self.get_role_info_by_server_index(self.user_turn_index)
            new_card_id = self.player_draw_card(next_role_info, False)
            if new_card_id == -1:
                rsp.game_faile = True
            else:
                self.pack_user_draw_card(role_info, rsp.user_draw_card, new_card_id)

            # 发送给其他玩家的拦牌结果
            for other_role_info in RoomRoleIterator(self):
                if other_role_info['entityID'] == player.entityID:
                    continue

                rsp_other = rainbow_pb.BlockResponse()

                # 如果没有摸到牌，就是流局了
                if new_card_id != -1:
                    self.pack_user_draw_card(other_role_info, rsp_other.user_draw_card, new_card_id)
                else:
                    rsp_other.game_faile = True

                g_playerManager.sendto(other_role_info['entityID'], success_msg(msgid.MAHJONG_BLOCK_CARD, rsp_other))

            return rsp

        # 遍历所有起作用的操作
        kong_card_id = None       # 有可能是杠，这个时候需要从牌墙末尾拿一张牌
        for index in effect_indices:
            block_result = rsp.block_results.add()
            bo_data = self.all_block_op[index]

            # 如果是杠的话，从牌墙未摸一张牌
            if bo_data['block_type'] == rainbow_pb.Kong:
                # 到杠牌的玩家出牌
                self.user_turn_index = bo_data['server_index']
                kong_role_info = self.get_role_info_by_server_index(self.user_turn_index)
                kong_card_id = self.player_draw_card(kong_role_info, True)

                # 流局
                if kong_card_id == -1:
                    rsp.game_faile = True

            self.pack_block_result(role_info, block_result, index, kong_card_id, False)

        # 发送给其他玩家的拦牌结果
        for other_role_info in RoomRoleIterator(self):
            if other_role_info['entityID'] == player.entityID:
                continue

            rsp_other = rainbow_pb.BlockResponse()
            for index in effect_indices:
                block_result = rsp.block_results.add()
                bo_data = self.all_block_op[index]

                self.pack_block_result(other_role_info, block_result, index, kong_card_id, True)

                if kong_card_id == -1:
                    rsp_other.game_faile = True

            g_playerManager.sendto(other_role_info['entityID'], success_msg(msgid.MAHJONG_BLOCK_CARD, rsp_other))

        return rsp
        
    def init_banker(self):
        pass

    def flop_ghost_card(self):
        if not self.game_config['has_ghost_card']:
            return

        pass

    def update_ting_cards(self, role):
        pass

    def check_is_win(self, role_info, card_id=None):
        input_data = InputData()
        pass

    def check_kong(self, role_info, card_id=None):
        card_num = {}
        for id in role_info['hand_cards']:
            if id in card_num:
                ++card_num[id]
            else:
                card_num[id] = 0

        if card_id:
            if card_id in card_num:
                ++card_num[card_id]
            else:
                card_num[card_id] = 0

        kong_card_ids = []
        for id, num in card_num.items():
            if num == 4:
                kong_card_ids.append(id)

        return kong_card_ids

    def check_pong(self, role_info, card_id=None):
        card_num = {}
        for id in role_info['hand_cards']:
            if id in card_num:
                ++card_num[id]
            else:
                card_num[id] = 0

        if card_id:
            if card_id in card_num:
                ++card_num[card_id]
            else:
                card_num[card_id] = 0

        pong_card_ids = []
        for id, num in card_num.items():
            if num == 3:
                pong_card_ids.append(id)

        return pong_card_ids

    def check_chow(self, role_info, card_id=None):
        chow_card_ids = []

        # 3万 - 7万，3条 - 7条，3筒 - 7筒
        if (card_id >= 2 and card_id <= 6) or (card_id >= 11 and card_id <= 15) or (card_id >= 20 and card_id <= 24):
            if card_id - 1 in role_info['hand_cards']:
                if card_id - 2 in role_info['hand_cards']:
                    chow_card_ids.append([card_id - 2, card_id - 1, card_id])

                if card_id + 1 in role_info['hand_cards']:
                    chow_card_ids.append([card_id - 1, card_id, card_id + 1])

            if card_id + 1 in role_info['hand_cards'] and card_id + 2 in role_info['hand_cards']:
                chow_card_ids.append([card_id, card_id + 1, card_id + 2])

        # 2万，8万，2条，8条，2筒，8筒
        if card_id == 1 or card_id == 7 or card_id == 10 or card_id == 16 or card_id == 19 or card_id == 25:
            if card_id - 1 in role_info['hand_cards'] and card_id + 1 in role_info['hand_cards']:
                chow_card_ids.append([card_id - 1, card_id, card_id + 1])

        # 1万，1条，1筒
        if card_id == 0 or card_id == 9 or card_id == 18:
            if card_id + 1 in role_info['hand_cards'] and card_id + 2 in role_info['hand_cards']:
                chow_card_ids.append([card_id, card_id + 1, card_id + 2])

        # 9万，9条，9筒
        if card_id == 8 or card_id == 17 or card_id == 26:
            if card_id - 2 in role_info['hand_cards'] and card_id - 1 in role_info['hand_cards']:
                chow_card_ids.append([card_id - 2, card_id - 1, card_id])

        return chow_card_ids

    def update_block_op(self, out_server_index, out_card_id):
        # 当前的所有玩家的拦牌操作:
        self.all_block_op = []

        # 如果是摸牌的话，那就只更新 self.user_turn_index
        # 如果是出牌的话，那就更新除了 out_server_index 以外的所有其他玩家
        if not out_server_index:
            role_info = self.get_role_info_by_server_index(self.user_turn_index)

            # win
            if self.check_is_win(role_info):
                self.all_block_op.append({
                    'block_priority': rainbow_pb.Block_Priority_Win,
                    'block_type': rainbow_pb.Win,
                    'dest_server_index': self.user_turn_index,
                    'dest_card_ids': [],
                    'show_card_ids': [],
                    'block_status': rainbow_pb.Block_Status_Waiting_Player,
                })

            # kong    
            kong_card_ids = self.check_kong(role_info)
            for card_id in kong_card_ids:
                self.all_block_op.append({
                    'block_priority': rainbow_pb.Block_Priority_Kong,
                    'block_type': rainbow_pb.Kong,
                    'dest_server_index': self.user_turn_index,
                    'dest_card_ids': [card_id, card_id, card_id, card_id],
                    'show_card_ids': [card_id, card_id, card_id, card_id],
                    'block_status': rainbow_pb.Block_Status_Waiting_Player,
                })
        else:
            for role_info in RoomRoleIterator(self):
                if role_info['server_index'] == out_server_index:
                    continue

            # win
            if self.check_is_win(role_info, out_card_id):
                self.all_block_op.append({
                    'block_priority': rainbow_pb.Block_Priority_Win,
                    'block_type': rainbow_pb.Win,
                    'src_server_index': out_server_index,
                    'src_card_id': out_card_id,
                    'dest_server_index': role_info['server_index'],
                    'dest_card_ids': [],
                    'show_card_ids': [],
                    'block_status': rainbow_pb.Block_Status_Waiting_Player,
                })

            # kong    
            kong_card_ids = self.check_kong(role_info, out_card_id)
            for card_id in kong_card_ids:
                self.all_block_op.append({
                    'block_priority': rainbow_pb.Block_Priority_Kong,
                    'block_type': rainbow_pb.Kong,
                    'src_server_index': out_server_index,
                    'src_card_id': out_card_id,
                    'dest_server_index': role_info['server_index'],
                    'dest_card_ids': [card_id, card_id, card_id],
                    'show_card_ids': [card_id, card_id, card_id, card_id],
                    'block_status': rainbow_pb.Block_Status_Waiting_Player,
                })

            # pong
            pong_card_ids = self.check_pong(role_info, out_card_id)
            for card_id in pong_card_ids:
                self.all_block_op.append({
                    'block_priority': rainbow_pb.Block_Priority_Pong,
                    'block_type': rainbow_pb.Pong,
                    'src_server_index': out_server_index,
                    'src_card_id': out_card_id,
                    'dest_server_index': role_info['server_index'],
                    'dest_card_ids': [card_id, card_id],
                    'show_card_ids': [card_id, card_id, card_id],
                    'block_status': rainbow_pb.Block_Status_Waiting_Player,
                })

            # chow
            if out_server_index + 1 == role_info['server_index'] or out_server_index - 3 == role_info['server_index']:
                chow_card_ids = self.check_chow(role_info, out_card_id)
                for card_ids in chow_card_ids:
                    dest_card_ids = []
                    for card_id in card_ids:
                        if card_id != out_card_id:
                            dest_card_ids.append(card_id)

                    self.all_block_op.append({
                        'block_priority': rainbow_pb.Block_Priority_Chow,
                        'block_type': rainbow_pb.Chow,
                        'src_server_index': out_server_index,
                        'src_card_id': out_card_id,
                        'dest_server_index': role_info['server_index'],
                        'dest_card_ids': dest_card_ids,
                        'show_card_ids': card_ids,
                        'block_status': rainbow_pb.Block_Status_Waiting_Player,
                    })

    def player_draw_card(self, draw_role_info, is_kong):
        if len(self.all_lei_cards) == 0:
            return -1

        new_card_id = -1
        if not is_kong:
            new_card_id = self.all_lei_cards[:1]
            self.all_lei_cards = self.all_lei_cards[1:]
        else:
            new_card_id = self.all_lei_cards[:1]
            self.all_lei_cards = self.all_lei_cards[1:]

        # append to hand cards
        draw_role_info['hand_cards'].append(new_card_id)

        # update block op & ting list
        self.update_block_op()
        self.update_ting_cards(draw_role_info)

        return card_id

    # 把游戏数据打包进：
    # rainbow_pb.GameDataMahjong
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

    # 把拦牌的操作列表打包进：
    # repeated    BlockOperationData  block_list;
    def pack_block_op_list(self, role_info, block_list):
        for index, v in enumerate(role_info['block_op']):
            bo = block_list.add()
            bo.block_type = v['block_type']
            bo.src_server_index = v['src_server_index']
            bo.src_card_id = v['src_card_id']
            bo.self_card_ids = v['self_card_ids']
            bo.show_card_ids = v['show_card_ids']
            bo.block_index = index

    # 把听牌列表打包进:
    # repeated    TingItem      ting_list;
    def pack_all_ting_list(self, role_info, ting_list):
        for i in range(0, role_info['all_ting_list'].count):
            c_item = role_info['all_ting_list'].items[i]

            item = ting_list.add()
            item.out_card_id = c_item.card_id

            for j in range(0, c_item.valid_count):
                item.ting_ids.append(c_item.valid_ids[j])

    # pack_role_info 这个摸牌数据，是打包给谁的
    # user_draw_card : rainbow_pb.UserDrawCard
    def pack_user_draw_card(self, pack_role_info, user_draw_card, new_card_id):
        user_draw_card.server_index = self.user_turn_index
        if pack_role_info['server_index'] == self.user_turn_index:
            user_draw_card.card_id = new_card_id
            self.pack_all_ting_list(pack_role_info, user_draw_card.ting_list)
            self.pack_block_op_list(pack_role_info, user_draw_card.block_list)
        else:
            user_draw_card.card_id = 0

    # pack_role_info 这是将一个拦牌的结果数据，打包给谁
    # block_result : rainbow_pb.BlockResult
    def pack_block_result(self, pack_role_info, block_result, block_index, kong_card_id, only_pack_data):
        bo_data = self.all_block_op[block_index]

        block_result.block_type = bo_data['block_type']

        for id in bo_data['show_card_list']:
            block_result.show_card_list.append(id)

        block_result.dest_server_index = bo_data['dest_server_index']
        dest_role_info = self.get_role_info_by_server_index(bo_data['dest_server_index']) if not only_pack_data else None

        for id in bo_data['dest_card_ids']:
            block_result.dest_card_ids.append(id)

            if not dest_role_info:
                dest_role_info['hand_cards'].remove(id)      # 从手牌移除

        # 如果是吃或者碰或者杠别人的牌的话，就要把对方出的牌从 out_cards 里面拿走
        if bo_data['src_server_index']:
            block_result.src_server_index = bo_data['src_server_index']
            block_result.src_card_id = bo_data['src_card_id']

            src_role_info = self.get_role_info_by_server_index(bo_data['src_server_index']) if not only_pack_data else None
            if not src_role_info:
                src_role_info['out_cards'].pop()    # 这个肯定是最后一个

        # 如果是杠的话，需要从牌墙未摸一张牌
        if not kong_card_id and kong_card_id != -1:
            self.pack_user_draw_card(pack_role_info, block_result.user_draw_card, kong_card_id)

        pass
