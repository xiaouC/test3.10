#!/usr/bin/python
# coding: utf-8

import copy

kinds_group = [
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
        ]


def insert_card(cards, card_kind, card_num = 1):
    cards[card_kind] = (card_num if cards.get(card_kind) == None else (cards[card_kind] + card_num))

    if cards[card_kind] < 0 or cards[card_kind] > 4:
        raise Exception("card's number(%d-%d) is wrong!"%(card_kind, cards[card_kind]))

    if cards[card_kind] == 0:
        del cards[card_kind]


def get_cards_sequence(cards):
    pick_pair_cards = []
    for v in kinds_group:
        for i in xrange(v['kind_start'], v['kind_end'] + 1):
            if cards.get(i) != None and cards[i] >= 2:
                pp_cards = copy.deepcopy(cards)
                insert_card(pp_cards, i, -2)
                pick_pair_cards.append({
                    'pair_kind' : i,
                    'all_sequence' : get_cards_sequence_kicked_out_pair(pp_cards),
                    })

    return pick_pair_cards


def get_cards_sequence_kicked_out_pair(pp_cards):
    all_sequence = [{ 'is_valid' : True, 'sequence' : [] }]

    for v in kinds_group:
        check_kind_group(all_sequence, all_sequence[0], pp_cards, v, 0)

    return all_sequence


def check_kind_group(all_sequence, current_sequence, cards, v, offset):
    if len(cards) == 0:
        return

    kind = v['kind_start'] + offset
    if kind > v['kind_end']:
        return

    if cards.get(kind) == None:
        return check_kind_group(all_sequence, current_sequence, cards, v, offset + 1)

    if cards[kind] == 1 or cards[kind] == 2:
        if kind + 2 > v['kind_end'] or cards.get(kind+1) == None or cards.get(kind+2) == None:
            current_sequence['is_valid'] = False
            return

        insert_card(cards, kind, -1)
        insert_card(cards, kind + 1, -1)
        insert_card(cards, kind + 2, -1)
        current_sequence['sequence'].append([kind, kind + 1, kind + 2])
        return check_kind_group(all_sequence, current_sequence, cards, v, offset)

    if cards[kind] == 3:
        if kind + 2 > v['kind_end'] or cards.get(kind + 1) == None or cards.get(kind + 2) == None:    # only 3 together
            insert_card(cards, kind, -3)
            current_sequence['sequence'].append([kind, kind, kind])
            return check_kind_group(all_sequence, current_sequence, cards, v, offset)

        # 2 paths
        new_sequence_cards = copy.deepcopy(cards)
        new_sequence = {
            'is_valid' : True,
            'sequence' : copy.deepcopy(current_sequence['sequence']),
            }
        all_sequence.append(new_sequence)

        # 3 together
        insert_card(cards, kind, -3)
        current_sequence['sequence'].append([kind, kind, kind])
        check_kind_group(all_sequence, current_sequence, cards, v, offset)

        # new path
        insert_card(new_sequence_cards, kind, -1)
        insert_card(new_sequence_cards, kind + 1, -1)
        insert_card(new_sequence_cards, kind + 2, -1)
        new_sequence['sequence'].append([kind, kind + 1, kind + 2])
        return check_kind_group(all_sequence, new_sequence, new_sequence_cards, v, offset)

    # it must be 4
    if kind + 2 > v['kind_end'] or cards.get(kind + 1) == None or cards.get(kind + 2) == None:
        current_sequence['is_valid'] = False
        return

    insert_card(cards, kind, -4)
    insert_card(cards, kind + 1, -1)
    insert_card(cards, kind + 2, -1)
    current_sequence['sequence'].append([kind, kind, kind])
    current_sequence['sequence'].append([kind, kind + 1, kind + 2])

    check_kind_group(all_sequence, current_sequence, cards, v, offset)


def check_is_win(cards, card_kind):
    temp_cards = copy.deepcopy(cards)
    insert_card(temp_cards, card_kind)

    win_sequence = []
    for v in get_cards_sequence(temp_cards):
        for s in v['all_sequence']:
            if s['is_valid']:
                win_sequence.append([[v['pair_kind'], v['pair_kind']]] + s['sequence'])

    return win_sequence
