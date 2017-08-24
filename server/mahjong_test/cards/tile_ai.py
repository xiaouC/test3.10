#!/usr/bin/python
# coding: utf-8

# 出牌策略是重点，决定了AI的难度。我把它分成了8步。
# 
# a、检查听牌
# 
# b、去除间隔2个空位的不连续单牌，从两头向中间排查
# 
# c、去除间隔1个空位的不连续单牌，从两头向中间排查
# 
# d、去除连续牌数为4、7、10、13中的一张牌，让牌型成为无将胡牌型。如2344条，去除4条。
# 
# e、去除连续牌数为3、6、9、12中的一张牌，有将则打一吃二成为无将听牌型（如233条，去除3条）；无将则打一成将成为有将胡牌型（如233条，去除2条）。
# 
# f、去除连续牌数位2、5、8、11中的一张牌，让牌型成为有将听牌型。如23445条，去除5条。
# 
# g、从将牌中打出一张牌。
# 
# 这8步是标准胡牌AI的基础，其中对于七对等特殊胡牌型没有涉及，可以把电脑设定为超过4或5对时转为特殊胡牌AI。AI难度2级时加入海牌的策略，即考虑桌面上已出的牌，AI难度3级时加入记牌分析模块，即记录玩家的出牌过程并进行分析。

class TileAI:
    def __init__(self, user, cards, rules):
        self.user = user
        self.cards = cards
        self.rules = rules
        self.all_segments = []

    def __del__(self):
        pass

    def split_cards(self):
        if len(self.all_segments) == 0:
            cur_segment = []
            for v in self.rules['kinds_group']:
                if len(cur_segment) > 0:
                    self.all_segments.append(cur_segment)
                    cur_segment = []

                for i in xrange(v['kind_start'], v['kind_end'] + 1):
                    if self.cards.get(i) == None:
                        if len(cur_segment) > 0:
                            self.all_segments.append(cur_segment)
                            cur_segment = []
                    else:
                        for c in xrange(0, self.cards[i]):
                            cur_segment.append(i)

        return self.all_segments

    def check_is_none_card(self, card_kind, kind_start, kind_end):
        if card_kind >= kind_start and card_kind <= kind_end:
            return self.cards.get(card_kind) == None

        return True

    def check_is_single_card(self, card_kind, kind_start, kind_end, space):
        if self.cards.get(card_kind) == None:
            return False

        if self.cards.get(card_kind) != 1:
            return False

        for s in xrange(1, space + 1):
            if not self.check_is_none_card(card_kind-s, kind_start, kind_end):
                return False

            if not self.check_is_none_card(card_kind+s, kind_start, kind_end):
                return False

        return True

    def get_single_card(self, space):
        single_segment = []

        tmp_kg = []
        for v in self.rules['kinds_group']:
            ks = v['kind_start']
            ke = v['kind_end']
            if ks == ke:
                if self.cards.get(ks) != None and self.cards.get(ks) == 1:
                    single_segment.append(ks)
            else:
                tmp_kg.append({
                    'ks' : ks,
                    'ke' : ke,
                    })

        for i in xrange(0, 4):
            for kg in tmp_kg:
                kind_1 = i + kg['ks']
                if self.check_is_single_card(kind_1, kg['ks'], kg['ke'], space):
                    single_segment.append(kind_1)

                kind_2 = kg['ke'] - i
                if self.check_is_single_card(kind_2, kg['ks'], kg['ke'], space):
                    single_segment.append(kind_2)

        for kg in tmp_kg:
            kind = 4 + kg['ks']
            if self.check_is_single_card(kind, kg['ks'], kg['ke'], space):
                single_segment.append(kind)

        return single_segment

    def has_only_one_pair(self):
        all_segments = self.split_cards()
        for seg in all_segments:
            if len(seg) == 2 and self.cards.get(seg[0]) == self.cards.get(seg[1]):
                return seg

        return []

    def get_discard_kind(self, card_segment):
        num = len(card_segment)
        if num == 4:
            # AABC => return A
            if card_segment[0] == card_segment[1] and card_segment[2] == card_segment[1] + 1 and card_segment[3] == card_segment[2] + 1:
                return card_segment[0]

            # ABBC => return B
            if card_segment[1] == card_segment[0] + 1 and card_segment[2] == card_segment[1] and card_segment[3] == card_segment[2] + 1:
                return card_segment[1]

            # ABCC => return C
            if card_segment[1] == card_segment[0] + 1 and card_segment[2] == card_segment[1] + 1 and card_segment[3] == card_segment[2]:
                return card_segment[2]

            return -1

        if num == 7:
            # AABCDEF => return A
            if (card_segment[0] == card_segment[1] and
                card_segment[2] == card_segment[1] + 1 and
                card_segment[3] == card_segment[2] + 1 and
                card_segment[4] == card_segment[3] + 1 and
                card_segment[5] == card_segment[4] + 1 and
                card_segment[6] == card_segment[5] + 1):
                    return card_segment[0]

            # ABBCDEF => return B
            if (card_segment[1] == card_segment[0] + 1 and
                card_segment[2] == card_segment[1] and
                card_segment[3] == card_segment[2] + 1 and
                card_segment[4] == card_segment[3] + 1 and
                card_segment[5] == card_segment[4] + 1 and
                card_segment[6] == card_segment[5] + 1):
                    return card_segment[1]

            # ABCCDEF => return C
            if (card_segment[1] == card_segment[0] + 1 and
                card_segment[2] == card_segment[1] + 1 and
                card_segment[3] == card_segment[2] and
                card_segment[4] == card_segment[3] + 1 and
                card_segment[5] == card_segment[4] + 1 and
                card_segment[6] == card_segment[5] + 1):
                    return card_segment[2]

            # ABCDDEF => return D
            if (card_segment[1] == card_segment[0] + 1 and
                card_segment[2] == card_segment[1] + 1 and
                card_segment[3] == card_segment[2] + 1 and
                card_segment[4] == card_segment[3] and
                card_segment[5] == card_segment[4] + 1 and
                card_segment[6] == card_segment[5] + 1):
                    return card_segment[3]

            # ABCDEEF => return E
            if (card_segment[1] == card_segment[0] + 1 and
                card_segment[2] == card_segment[1] + 1 and
                card_segment[3] == card_segment[2] + 1 and
                card_segment[4] == card_segment[3] + 1 and
                card_segment[5] == card_segment[4] and
                card_segment[6] == card_segment[5] + 1):
                    return card_segment[4]

            # ABCDEFF => return F
            if (card_segment[1] == card_segment[0] + 1 and
                card_segment[2] == card_segment[1] + 1 and
                card_segment[3] == card_segment[2] + 1 and
                card_segment[4] == card_segment[3] + 1 and
                card_segment[5] == card_segment[4] + 1 and
                card_segment[6] == card_segment[5]):
                    return card_segment[5]

            # AABCCDE => return A
            if (card_segment[1] == card_segment[0] and
                card_segment[2] == card_segment[1] + 1 and
                card_segment[3] == card_segment[2] + 1 and
                card_segment[4] == card_segment[3] and
                card_segment[5] == card_segment[4] + 1 and
                card_segment[6] == card_segment[5] + 1):
                    return card_segment[0]

            # ABCCDEE => return E
            if (card_segment[1] == card_segment[0] + 1 and
                card_segment[2] == card_segment[1] + 1 and
                card_segment[3] == card_segment[2] and
                card_segment[4] == card_segment[3] + 1 and
                card_segment[5] == card_segment[4] + 1 and
                card_segment[6] == card_segment[5]):
                    return card_segment[6]

        if num == 10:
            pair_kinds = self.get_pair_from_cards(card_segment)
            if len(pair_kinds) == 1:
                return pair_kinds[0]

        return -1

    def get_pair_from_cards(self, card_segment):
        length = len(card_segment)
        index = 1
        cur_kind = card_segment[0]
        num = 1
        pair_kinds = []
        while length > index:
            if cur_kind == card_segment[index]:
                num += 1
            else:
                if num == 2:
                    pair_kinds.append(cur_kind)

                cur_kind = card_segment[index]
                num = 1

            index += 1

        return pair_kinds
