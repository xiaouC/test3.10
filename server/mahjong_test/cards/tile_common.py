#!/usr/bin/python
# coding: utf-8

import copy

def insert_card(cards, card_kind, card_num = 1):
    cards[card_kind] = (card_num if cards.get(card_kind) == None else (cards[card_kind] + card_num))

    if cards[card_kind] < 0 or cards[card_kind] > 4:
        return False

    if cards[card_kind] == 0:
        del cards[card_kind]

    return True


def get_cards_sequence(cards, rules):
    pick_pair_cards = []
    for v in rules['kinds_group']:
        for i in xrange(v['kind_start'], v['kind_end'] + 1):
            if cards.get(i) != None and cards[i] >= 2:
                pp_cards = copy.deepcopy(cards)
                insert_card(pp_cards, i, -2)
                pick_pair_cards.append({
                    'pair_kind' : i,
                    'all_sequence' : get_cards_sequence_kicked_out_pair(pp_cards, rules),
                    })

    return pick_pair_cards


def get_cards_sequence_kicked_out_pair(pp_cards, rules):
    all_sequence = [{ 'is_valid' : True, 'sequence' : [] }]

    for v in rules['kinds_group']:
        check_kind_group(all_sequence, all_sequence[0], pp_cards, v, 0, rules)

    return all_sequence


def check_kind_group(all_sequence, current_sequence, cards, v, offset, rules):
    if len(cards) == 0:
        return

    kind = v['kind_start'] + offset
    if kind > v['kind_end']:
        return

    if cards.get(kind) == None:
        return check_kind_group(all_sequence, current_sequence, cards, v, offset + 1, rules)

    if cards[kind] == 1 or cards[kind] == 2:
        if kind + 2 > v['kind_end'] or cards.get(kind+1) == None or cards.get(kind+2) == None:
            current_sequence['is_valid'] = False
            return

        insert_card(cards, kind, -1)
        insert_card(cards, kind + 1, -1)
        insert_card(cards, kind + 2, -1)
        current_sequence['sequence'].append([kind, kind + 1, kind + 2])
        return check_kind_group(all_sequence, current_sequence, cards, v, offset, rules)

    if cards[kind] == 3:
        if kind + 2 > v['kind_end'] or cards.get(kind + 1) == None or cards.get(kind + 2) == None:    # only 3 together
            insert_card(cards, kind, -3)
            current_sequence['sequence'].append([kind, kind, kind])
            return check_kind_group(all_sequence, current_sequence, cards, v, offset, rules)

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
        check_kind_group(all_sequence, current_sequence, cards, v, offset, rules)

        # new path
        insert_card(new_sequence_cards, kind, -1)
        insert_card(new_sequence_cards, kind + 1, -1)
        insert_card(new_sequence_cards, kind + 2, -1)
        new_sequence['sequence'].append([kind, kind + 1, kind + 2])
        return check_kind_group(all_sequence, new_sequence, new_sequence_cards, v, offset, rules)

    # it must be 4
    if kind + 2 > v['kind_end'] or cards.get(kind + 1) == None or cards.get(kind + 2) == None:
        current_sequence['is_valid'] = False
        return

    insert_card(cards, kind, -4)
    insert_card(cards, kind + 1, -1)
    insert_card(cards, kind + 2, -1)
    current_sequence['sequence'].append([kind, kind, kind])
    current_sequence['sequence'].append([kind, kind + 1, kind + 2])

    check_kind_group(all_sequence, current_sequence, cards, v, offset, rules)


def get_cards_num(cards):
    num = 0
    for v in cards.values():
        num += v
    return num

def check_is_win(cards, card_kind, ghost_kind, rules):
    if get_cards_num(cards) % 3 != 1:       # 3n + 1
        return []

    temp_cards = copy.deepcopy(cards)
    insert_card(temp_cards, card_kind)

    if ghost_kind == None or temp_cards.get(ghost_kind) == None:
        return check_is_win_no_ghost(temp_cards, rules)

    win_sequence = []

    ghost_card_num = temp_cards[ghost_kind]
    insert_card(temp_cards, ghost_kind, -ghost_card_num)

    cards_checked = set()
    return check_is_win_ghost(cards_checked, temp_cards, 0, ghost_card_num, rules)


def check_is_win_no_ghost(cards, rules):
    win_sequence = []
    for v in get_cards_sequence(cards, rules):
        for s in v['all_sequence']:
            if s['is_valid']:
                win_sequence.append([[v['pair_kind'], v['pair_kind']]] + s['sequence'])

    return win_sequence


def check_is_win_ghost(cards_checked, cards, ghost_card_index, ghost_card_num, rules):
    if ghost_card_index >= ghost_card_num:
        cf = cards_format(cards, rules)
        if cf not in cards_checked:
            cards_checked.add(cf)
            return check_is_win_no_ghost(cards, rules)
        else:
            return []

    win_sequence = []

    for v in rules['kinds_group']:
        for i in xrange(v['kind_start'], v['kind_end'] + 1):
            temp_cards = copy.deepcopy(cards)
            if insert_card(temp_cards, i, 1):
                    tmp_sequence = check_is_win_ghost(cards_checked, temp_cards, ghost_card_index + 1, ghost_card_num, rules)
                    if len(tmp_sequence) > 0:
                        # print "ghost : ", i
                        # print tmp_sequence
                        win_sequence.extend(tmp_sequence)

    return win_sequence


def cards_format(cards, rules):
    nums = []
    for v in rules['kinds_group']:
        for i in xrange(v['kind_start'], v['kind_end'] + 1):
            nums.append('0' if cards.get(i) == None else str(cards[i]))

    return ''.join(nums)

