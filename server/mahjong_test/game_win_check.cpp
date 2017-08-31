#include "game_win_check.h"
#include <string>
#include <stdlib.h>

game_win_check::game_win_check() {
    _map_card_id_index[0x01] = 0;
    _map_card_id_index[0x02] = 1;
    _map_card_id_index[0x03] = 2;
    _map_card_id_index[0x04] = 3;
    _map_card_id_index[0x05] = 4;
    _map_card_id_index[0x06] = 5;
    _map_card_id_index[0x07] = 6;
    _map_card_id_index[0x08] = 7;
    _map_card_id_index[0x09] = 8;

    _map_card_id_index[0x11] = 9;
    _map_card_id_index[0x12] = 10;
    _map_card_id_index[0x13] = 11;
    _map_card_id_index[0x14] = 12;
    _map_card_id_index[0x15] = 13;
    _map_card_id_index[0x16] = 14;
    _map_card_id_index[0x17] = 15;
    _map_card_id_index[0x18] = 16;
    _map_card_id_index[0x19] = 17;

    _map_card_id_index[0x21] = 18;
    _map_card_id_index[0x22] = 19;
    _map_card_id_index[0x23] = 20;
    _map_card_id_index[0x24] = 21;
    _map_card_id_index[0x25] = 22;
    _map_card_id_index[0x26] = 23;
    _map_card_id_index[0x27] = 24;
    _map_card_id_index[0x28] = 25;
    _map_card_id_index[0x29] = 26;

    _map_card_id_index[0x31] = 27;
    _map_card_id_index[0x32] = 28;
    _map_card_id_index[0x33] = 29;
    _map_card_id_index[0x34] = 30;
    _map_card_id_index[0x35] = 31;
    _map_card_id_index[0x36] = 32;
    _map_card_id_index[0x37] = 33;
}

game_win_check::~game_win_check() {
}

void game_win_check::load_win_styles() {
    char szBuf[128];

    // wtt.txt
    FILE* fp_1 = fopen("wtt.txt", "r");
    if (!fp_1) {
        printf("load wtt.txt failed!\n");
    } else {
        while (!feof(fp_1)) {
            fgets(szBuf, 1024, fp_1);
            std::string buf = szBuf;
            int pos_1 = buf.find("|");
            int pos_2 = buf.rfind("|");
            std::string str1 = buf.substr(0, pos_1);
            std::string str2 = buf.substr(pos_1 + 1, pos_2 - pos_1 - 1);
            std::string str3 = buf.substr(pos_2 + 1, buf.length() - pos_2 - 2);     // 这里还有一个换行符 \n
            int style = atoi(str1.c_str());
            int ghost_num = atoi(str2.c_str());
            bool has_eyes = (str3.compare("true") == 0);
            // printf("style : %d\n", style);
            // printf("ghost_num : %d\n", ghost_num);
            // printf("has_eyes : %s\n", has_eyes ? "true" : "false");
            // printf("%s\n", str3.c_str());
            // printf("%d\n", str3.compare("true"));

            auto iter = _all_win_styles_1.find(style);
            if (iter == _all_win_styles_1.end()) {
                std::list<std::tuple<int, bool>> listGhostEyes;
                listGhostEyes.push_back(std::make_tuple(ghost_num, has_eyes));

                _all_win_styles_1[style] = listGhostEyes;
            } else {
                bool flag = false;
                for (const auto& iterGE : iter->second) {
                    int num = std::get<0>(iterGE);
                    bool eyes = std::get<1>(iterGE);
                    if (num == ghost_num && eyes == has_eyes) {
                        flag = true;
                        break;
                    }
                }
                if (!flag) {
                    iter->second.push_back(std::make_tuple(ghost_num, has_eyes));
                }
            }
        } 
        fclose(fp_1);

        printf("wtt.txt loaded!%d\n", (int)_all_win_styles_1.size());
    }

    // fan.txt
    FILE* fp_2 = fopen("fan.txt", "r");
    if (!fp_2) {
        printf("load fan.txt failed!\n");
    } else {
        while (!feof(fp_2)) {
            fgets(szBuf, 1024, fp_2);
            std::string buf = szBuf;
            int pos_1 = buf.find("|");
            int pos_2 = buf.rfind("|");
            std::string str1 = buf.substr(0, pos_1);
            std::string str2 = buf.substr(pos_1 + 1, pos_2 - pos_1 - 1);
            std::string str3 = buf.substr(pos_2 + 1, buf.length() - pos_2 - 2);     // 这里还有一个换行符 \n
            int style = atoi(str1.c_str());
            int ghost_num = atoi(str2.c_str());
            bool has_eyes = (str3.compare("true") == 0);
            // printf("style : %d\n", style);
            // printf("ghost_num : %d\n", ghost_num);
            // printf("has_eyes : %s\n", has_eyes ? "true" : "false");
            // printf("%s\n", str3.c_str());
            // printf("%d\n", str3.compare("true"));

            auto iter = _all_win_styles_2.find(style);
            if (iter == _all_win_styles_2.end()) {
                std::list<std::tuple<int, bool>> listGhostEyes;
                listGhostEyes.push_back(std::make_tuple(ghost_num, has_eyes));

                _all_win_styles_2[style] = listGhostEyes;
            } else {
                bool flag = false;
                for (const auto& iterGE : iter->second) {
                    int num = std::get<0>(iterGE);
                    bool eyes = std::get<1>(iterGE);
                    if (num == ghost_num && eyes == has_eyes) {
                        flag = true;
                        break;
                    }
                }
                if (!flag) {
                    iter->second.push_back(std::make_tuple(ghost_num, has_eyes));
                }
            }
        } 
        fclose(fp_2);

        printf("fan.txt loaded!%d\n", (int)_all_win_styles_2.size());
    }
}

void game_win_check::set_ghost_card_id_1(int card_id) {
    _ghost_card_id_1 = card_id;
}

void game_win_check::set_ghost_card_id_2(int card_id) {
    _ghost_card_id_2 = card_id;
}

void game_win_check::convert(int* hand_cards, int hand_card_num, int new_card) {
    memset(_card_id, 0, sizeof(int) * 34);
    _ghost_num = 0;     // 需要剔除鬼牌

    // 手牌
    for (int i=0; i < hand_card_num; ++i) {
        int card_id = hand_cards[i];

        if (card_id != _ghost_card_id_1 && card_id != _ghost_card_id_2) {
            int index = _map_card_id_index[card_id];
            ++_card_id[index];
        } else {
            ++_ghost_num;
        }
    }

    // 新添加进来的牌
    if (new_card != _ghost_card_id_1 && new_card != _ghost_card_id_2) {
        int index = _map_card_id_index[new_card];
        ++_card_id[index];
    } else {
        ++_ghost_num;
    }

    // 
    auto __format__ = [this] (int start_index, int end_index) {
        int value = 0;
        for (int i=start_index; i <= end_index; ++i) {
            value = value * 10 + _card_id[i];
        }
        return value;
    };

    _card_type_value[0] = __format__(0, 8);
    _card_type_value[1] = __format__(9, 17);
    _card_type_value[2] = __format__(18, 26);
    _card_type_value[3] = __format__(27, 33);
}

bool game_win_check::check_is_win(int* hand_cards, int hand_card_num, int new_card) {
    convert(hand_cards, hand_card_num, new_card);

    // printf("_card_type_value[0] : %d\n", _card_type_value[0]);
    // printf("_card_type_value[1] : %d\n", _card_type_value[1]);
    // printf("_card_type_value[2] : %d\n", _card_type_value[2]);
    // printf("_card_type_value[3] : %d\n", _card_type_value[3]);
    // printf("_ghost_num : %d\n", _ghost_num);

    return check_value_2(_ghost_num, true);
}

bool game_win_check::check_value_1(int index, int ghost_num, bool need_eyes) {
    // 能够一直匹配下来，到这里的话，就意味着可胡了
    if (index >= 3) {
        return true;
    }

    // 没有值，就匹配下一个吧
    if (_card_type_value[index] == 0) {
        return check_value_1(index+1, ghost_num, need_eyes);
    }

    // 没有找到对应的牌型，不能胡
    auto iter = _all_win_styles_1.find(_card_type_value[index]);
    if (iter == _all_win_styles_1.end()) {
        return false;
    }

    // 一个牌型下，可能对应的多种类型，如鬼的数量已经是否带眼
    for (auto iter_2 : iter->second) {
        int need_ghost_num = std::get<0>(iter_2);
        bool has_eyes = std::get<1>(iter_2);
        // printf("style $$$$$$$$$$$$$$$$$$$$$$\n");
        // printf("_card_type_value[index] : %d\n", _card_type_value[index]);
        // printf("need_ghost_num : %d\n", need_ghost_num);
        // printf("has_eyes : %s\n", has_eyes ? "true" : "false");
        // printf("-------------------------");
        // printf("ghost_num : %d\n", ghost_num);
        // printf("need_eyes : %s\n", need_eyes ? "true" : "false");

        // 如果不需要眼，但却带眼，这个不能胡
        if (!need_eyes && has_eyes) {
            continue;
        }

        // 没有足够的鬼牌
        if (need_ghost_num > ghost_num) {
            continue;
        }

        // printf("check next =============================================\n");
        // 
        if (check_value_1(index+1, ghost_num - need_ghost_num, has_eyes ? false : need_eyes)) {
            return true;
        }
    }

    // 当前牌型下的所有类型都不匹配，就意味着不能胡
    return false;
}

bool game_win_check::check_value_2(int ghost_num, bool need_eyes) {
    // 没有值，就匹配万条筒去吧
    if (_card_type_value[3] == 0) {
        return check_value_1(0, ghost_num, need_eyes);
    }

    // 没有找到对应的牌型，不能胡
    auto iter = _all_win_styles_2.find(_card_type_value[3]);
    if (iter == _all_win_styles_2.end()) {
        return false;
    }

    // 一个牌型下，可能对应的多种类型，如鬼的数量已经是否带眼
    for (auto iter_2 : iter->second) {
        int need_ghost_num = std::get<0>(iter_2);
        bool has_eyes = std::get<1>(iter_2);

        // 如果不需要眼，但却带眼，这个不能胡
        if (!need_eyes && has_eyes) {
            continue;
        }

        // 没有足够的鬼牌
        if (need_ghost_num > ghost_num) {
            continue;
        }

        // 
        if (!check_value_1(0, ghost_num - need_ghost_num, has_eyes ? false : need_eyes)) {
            continue;
        }
    }

    // 当前牌型下的所有类型都不匹配，就意味着不能胡
    return false;
}

std::list<int> game_win_check::get_ting_list(int* hand_cards, int hand_card_num) {
    std::list<int> win_cards;
    for (const auto& iter : _map_card_id_index) {
        if (check_is_win(hand_cards, hand_card_num, iter.first)) {
            win_cards.push_back(iter.first);
        }
    }

    return win_cards;
}

char* game_win_check::get_win_sequence(int* hand_cards, int hand_card_num, int win_card) {
    return nullptr;
}
