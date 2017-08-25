#include "game_impl_base.h"

game_impl_base::game_impl_base() {
    // init default rules, [ 1: true, 0: false ]
    // 当然，这个不可能除了 true 就是 false 的
    // 花牌在手牌都会被补花，不算到胡牌里面，所以这里不管
    _game_rules["has_wan"] = 1;                         // 是否有万牌 [ 1 - 9 万 ]
    _game_rules["has_tiao"] = 1;                        // 是否有条牌 [ 1 - 9 条 ]
    _game_rules["has_tong"] = 1;                        // 是否有筒牌 [ 1 - 9 筒 ]
    _game_rules["has_wind"] = 1;                        // 是否有风牌 [ 东南西北 ]
    _game_rules["has_dragon"] = 1;                      // 是否有箭牌 [ 中发白 ]
    _game_rules["allow_sequence"] = 1;                  // 允许万条筒顺子
    _game_rules["allow_wind_sequence"] = 0;             // 允许风牌顺子
    _game_rules["allow_dragon_sequence"] = 0;           // 允许箭牌顺子
    _game_rules["allow_triplet"] = 1;                   // 允许有刻子
    _game_rules["can_win_qd"] = 1;                      // 可胡七对
    _game_rules["can_win_ssy"] = 1;                     // 可胡十三幺
}

game_impl_base::~game_impl_base() {
}

void game_impl_base::update_or_add_one_rule(const char* key, int value) {
    _game_rules[key] = value;
}

void game_impl_base::set_ghost_card_id_1(int card_id) {
    _ghost_card_id_1 = card_id;
}

void game_impl_base::set_ghost_card_id_2(int card_id) {
    _ghost_card_id_2 = card_id;
}

void game_impl_base::update_rules() {
    /*
       0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09,						// 1 - 9 万
       0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19,						// 1 - 9 条
       0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29,						// 1 - 9 筒
       0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,									// 东、南、西、北、中、发、白
       0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E,									// 梅、兰、竹、菊、春、夏、秋、冬
    */
    _card_id_groups.clear();
    _total_kinds = 0;

    // 是否有万牌
    if (_game_rules["has_wan"] == 1) {
        if (_game_rules["allow_sequence"]) {
            _card_id_groups.push_back(std::make_tuple(0x01, 0x09));
        } else {
            _card_id_groups.push_back(std::make_tuple(0x01, 0x01));
            _card_id_groups.push_back(std::make_tuple(0x02, 0x02));
            _card_id_groups.push_back(std::make_tuple(0x03, 0x03));
            _card_id_groups.push_back(std::make_tuple(0x04, 0x04));
            _card_id_groups.push_back(std::make_tuple(0x05, 0x05));
            _card_id_groups.push_back(std::make_tuple(0x06, 0x06));
            _card_id_groups.push_back(std::make_tuple(0x07, 0x07));
            _card_id_groups.push_back(std::make_tuple(0x08, 0x08));
            _card_id_groups.push_back(std::make_tuple(0x09, 0x09));
        }

        _total_kinds += 9;
    }

    // 是否有条牌
    if (_game_rules["has_tiao"] == 1) {
        if (_game_rules["allow_sequence"]) {
            _card_id_groups.push_back(std::make_tuple(0x11, 0x19));
        } else {
            _card_id_groups.push_back(std::make_tuple(0x11, 0x11));
            _card_id_groups.push_back(std::make_tuple(0x12, 0x12));
            _card_id_groups.push_back(std::make_tuple(0x13, 0x13));
            _card_id_groups.push_back(std::make_tuple(0x14, 0x14));
            _card_id_groups.push_back(std::make_tuple(0x15, 0x15));
            _card_id_groups.push_back(std::make_tuple(0x16, 0x16));
            _card_id_groups.push_back(std::make_tuple(0x17, 0x17));
            _card_id_groups.push_back(std::make_tuple(0x18, 0x18));
            _card_id_groups.push_back(std::make_tuple(0x19, 0x19));
        }

        _total_kinds += 9;
    }

    // 是否有筒牌
    if (_game_rules["has_tong"] == 1) {
        if (_game_rules["allow_sequence"]) {
            _card_id_groups.push_back(std::make_tuple(0x21, 0x29));
        } else {
            _card_id_groups.push_back(std::make_tuple(0x21, 0x21));
            _card_id_groups.push_back(std::make_tuple(0x22, 0x22));
            _card_id_groups.push_back(std::make_tuple(0x23, 0x23));
            _card_id_groups.push_back(std::make_tuple(0x24, 0x24));
            _card_id_groups.push_back(std::make_tuple(0x25, 0x25));
            _card_id_groups.push_back(std::make_tuple(0x26, 0x26));
            _card_id_groups.push_back(std::make_tuple(0x27, 0x27));
            _card_id_groups.push_back(std::make_tuple(0x28, 0x28));
            _card_id_groups.push_back(std::make_tuple(0x29, 0x29));
        }

        _total_kinds += 9;
    }

    // 是否有风牌
    if (_game_rules["has_wind"] == 1) {
        if (_game_rules["allow_wind_sequence"]) {
            _card_id_groups.push_back(std::make_tuple(0x31, 0x34));
        } else {
            _card_id_groups.push_back(std::make_tuple(0x31, 0x31));
            _card_id_groups.push_back(std::make_tuple(0x32, 0x32));
            _card_id_groups.push_back(std::make_tuple(0x33, 0x33));
            _card_id_groups.push_back(std::make_tuple(0x34, 0x34));
        }

        _total_kinds += 4;
    }

    // 是否有箭牌
    if (_game_rules["has_dragon"] == 1) {
        if (_game_rules["allow_dragon_sequence"]) {
            _card_id_groups.push_back(std::make_tuple(0x35, 0x37));
        } else {
            _card_id_groups.push_back(std::make_tuple(0x35, 0x35));
            _card_id_groups.push_back(std::make_tuple(0x36, 0x36));
            _card_id_groups.push_back(std::make_tuple(0x37, 0x37));
        }

        _total_kinds += 3;
    }
}

std::map<int, int> game_impl_base::convert(int* hand_cards, int hand_card_num) {
    std::map<int, int> new_hand_cards;
    for (int i=0; i < hand_card_num; ++i) {
        int card_id = hand_cards[i];
        ++new_hand_cards[card_id];
    }
    return new_hand_cards;
}

int game_impl_base::get_ghost_card_num(const std::map<int, int>& card_list) {
    int num = 0;
    for (const auto& iter : card_list) {
        if (iter.first == _ghost_card_id_1 || iter.first == _ghost_card_id_2) {
            num += iter.second;
        }
    }
    return num;
}

int game_impl_base::get_card_num(const std::map<int, int>& card_list, int card_id) {
    int num = 0;
    for (const auto& iter : card_list) {
        if (iter.first == card_id) {
            num += iter.second;
        }
    }
    return num;
}

bool game_impl_base::check_is_win(int* hand_cards, int hand_card_num, int new_card) {
    // 先把手牌整理成 id : num 的形式
    std::map<int, int> new_hand_cards = std::move(convert(hand_cards, hand_card_num));

    // 新加入的牌添加进去
    ++new_hand_cards[new_card];

    // 如果没有鬼牌的话
    if (get_ghost_card_num(new_hand_cards) == 0) {
        return check_is_win_no_ghost(new_hand_cards);
    }
}

bool game_impl_base::check_is_win_no_ghost(const std::map<int, int>& card_list) {
    for (const auto& iter : _card_id_groups) {
        int card_id_start = std::get<0>(iter);
        int card_id_end = std::get<1>(iter);
        for (int card_id=card_id_start; card_id <= card_id_end; ++card_id) {
            // 用这个 id 做眼 (做将)
            if (get_card_num(card_list, card_id) >= 2) {
                // a new copy
                std::map<int, int> new_card_list = card_list;
                new_card_list[card_id] -= 2;

                if (check_is_win_no_eyes(new_card_list)) {
                    return true;
                }
            }
        }
    }

    return false;
}

bool game_impl_base::check_is_win_no_eyes(const std::map<int, int>& card_list) {
    for (const auto& iter : _card_id_groups) {
    }

    for (auto& kg : g_vecKindGroups) {
        check_kind_group(win_sequences, si, pp_tiles, kg, 0);
    }
}

char* game_impl_base::get_win_sequence(int* hand_cards, int hand_card_num, int new_card) {
}

