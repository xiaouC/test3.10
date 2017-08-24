#!/usr/bin/python
# coding: utf-8

import copy

all_kinds = 34
kind_group = [
        { 'kind_start' : 0,  'kind_end' : 8 },
        { 'kind_start' : 9,  'kind_end' : 17 },
        { 'kind_start' : 18, 'kind_end' : 26 },
        { 'kind_start' : 27, 'kind_end' : 33 },
        ]

def insert_card(cards, card_kind, card_num = 1):
    if cards.get(card_kind) == None:
        cards[card_kind] = card_num
    else:
        cards[card_kind] += card_num

    if cards[card_kind] == 0:
        del cards[card_kind]


def get_cards_sequence(pp_cards):
    all_sequence = [
            { 'is_valid' : True, 'sequence' : [] }
            ]

    for v in kind_group:
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
        if kind + 2 > v['kind_end'] or cards.get(kind+1) == None or cards.get(kind+2) == None:    # only 3 together
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
    if kind + 2 > v['kind_end'] or cards.get(kind+1) == None or cards.get(kind+2) == None:
        current_sequence['is_valid'] = False
        return

    insert_card(cards, kind, -4)
    insert_card(cards, kind + 1, -1)
    insert_card(cards, kind + 2, -1)
    current_sequence['sequence'].append([kind, kind, kind])
    current_sequence['sequence'].append([kind, kind + 1, kind + 2])

    check_kind_group(all_sequence, current_sequence, cards, v, offset)

class User:
    def __init__(self):
        self.reset_round()

    def __del__(self):
        pass

    def reset_round(self):
        self.cards = {}

    def check_hu(self, card_kind):
        temp_cards = copy.deepcopy(self.cards)
        insert_card(temp_cards, card_kind)
        print temp_cards

        pick_pair_cards = []
        for i in xrange(0, all_kinds):
            if temp_cards.get(i) != None and temp_cards[i] >= 2:
                pp_cards = copy.deepcopy(temp_cards)
                insert_card(pp_cards, i, -2)
                pick_pair_cards.append({
                    'pair_kind' : i,
                    'all_sequence' : get_cards_sequence(pp_cards),
                    })

        for v in pick_pair_cards:
            print v


if __name__ == '__main__':
    u = User()

    # insert_card(u.cards, 0, 3)
    # insert_card(u.cards, 1)
    # insert_card(u.cards, 2)
    # insert_card(u.cards, 3)
    # insert_card(u.cards, 4)
    # insert_card(u.cards, 5)
    # insert_card(u.cards, 6)
    # insert_card(u.cards, 7)
    # insert_card(u.cards, 8, 3)

    insert_card(u.cards, 0, 4)
    insert_card(u.cards, 1, 4)
    insert_card(u.cards, 2, 4)
    insert_card(u.cards, 3, 1)

    u.check_hu(3)
