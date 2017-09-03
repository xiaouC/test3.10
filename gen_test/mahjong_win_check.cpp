#include "mahjong_win_check.h"
#include <string>
#include <stdlib.h>
#include <functional>
#include "cJSON.h"

std::unordered_map<int, std::vector<StyleInfo>> mahjong_win_check::_all_wtt_styles;
std::unordered_map<int, std::vector<StyleInfo>> mahjong_win_check::_all_fan_styles;
void mahjong_win_check::load_win_styles() {
    load_new_data_binary("./data/data01", _all_wtt_styles);
    load_new_data_binary("./data/data02", _all_fan_styles);
}

int mahjong_win_check::convert(int* hand_cards, int hand_card_num, int ghost_card_id_1, int ghost_card_id_2, int* card_style_value) {
    // 0 - 8    : 万字牌
    // 9 - 17   : 索子牌
    // 18 - 26  : 筒子牌
    // 27 - 33  : 番字牌 东南西北中发白
	int card_num[34] = { 0 };

	// 手牌
	for (int i = 0; i < hand_card_num; ++i) {
		int card_id = hand_cards[i];
		++card_num[card_id];
	}

	// 剔除鬼牌
	int ghost_num = 0;
	if (ghost_card_id_1 != -1) {
		ghost_num += card_num[ghost_card_id_1];
		card_num[ghost_card_id_1] = 0;
	}
	if (ghost_card_id_2 != -1) {
		ghost_num += card_num[ghost_card_id_2];
		card_num[ghost_card_id_2] = 0;
	}

    // 
	auto __format__ = [&card_num](int start_index, int end_index) {
        int value = 0;
        for (int i=start_index; i <= end_index; ++i) {
            value = value * 10 + card_num[i];
        }
        return value;
    };

    card_style_value[0] = __format__(0, 8);
    card_style_value[1] = __format__(9, 17);
    card_style_value[2] = __format__(18, 26);
    card_style_value[3] = __format__(27, 33);

    return ghost_num;
}

int mahjong_win_check::convert_add(int* hand_cards, int hand_card_num, int new_card, int ghost_card_id_1, int ghost_card_id_2, int* card_style_value) {
    // 0 - 8    : 万字牌
    // 9 - 17   : 索子牌
    // 18 - 26  : 筒子牌
    // 27 - 33  : 番字牌 东南西北中发白
	int card_num[34] = { 0 };

	// 手牌
	for (int i = 0; i < hand_card_num; ++i) {
		int card_id = hand_cards[i];
		++card_num[card_id];
	}

	// 新添加进来的牌
    if (new_card != -1) {
        ++card_num[new_card];
    }

	// 剔除鬼牌
	int ghost_num = 0;
	if (ghost_card_id_1 != -1) {
		ghost_num += card_num[ghost_card_id_1];
		card_num[ghost_card_id_1] = 0;
	}
	if (ghost_card_id_2 != -1) {
		ghost_num += card_num[ghost_card_id_2];
		card_num[ghost_card_id_2] = 0;
	}

    // 
	auto __format__ = [&card_num](int start_index, int end_index) {
        int value = 0;
        for (int i=start_index; i <= end_index; ++i) {
            value = value * 10 + card_num[i];
        }
        return value;
    };

    card_style_value[0] = __format__(0, 8);
    card_style_value[1] = __format__(9, 17);
    card_style_value[2] = __format__(18, 26);
    card_style_value[3] = __format__(27, 33);

    return ghost_num;
}

int mahjong_win_check::convert_rm(int* hand_cards, int hand_card_num, int rm_card, int ghost_card_id_1, int ghost_card_id_2, int* card_style_value) {
    // 0 - 8    : 万字牌
    // 9 - 17   : 索子牌
    // 18 - 26  : 筒子牌
    // 27 - 33  : 番字牌 东南西北中发白
	int card_num[34] = { 0 };

	// 手牌
	for (int i = 0; i < hand_card_num; ++i) {
		int card_id = hand_cards[i];
		++card_num[card_id];
	}

	// 需要移除的牌，如果没有这张牌的话，就 return -1
    if (rm_card != -1) {
        if (--card_num[rm_card] < 0) {
            return -1;
        }
    }

	// 剔除鬼牌
	int ghost_num = 0;
	if (ghost_card_id_1 != -1) {
		ghost_num += card_num[ghost_card_id_1];
		card_num[ghost_card_id_1] = 0;
	}
	if (ghost_card_id_2 != -1) {
		ghost_num += card_num[ghost_card_id_2];
		card_num[ghost_card_id_2] = 0;
	}

    // 
	auto __format__ = [&card_num](int start_index, int end_index) {
        int value = 0;
        for (int i=start_index; i <= end_index; ++i) {
            value = value * 10 + card_num[i];
        }
        return value;
    };

    card_style_value[0] = __format__(0, 8);
    card_style_value[1] = __format__(9, 17);
    card_style_value[2] = __format__(18, 26);
    card_style_value[3] = __format__(27, 33);

    return ghost_num;
}

int mahjong_win_check::convert_add_rm(int* hand_cards, int hand_card_num, int add_card, int rm_card, int ghost_card_id_1, int ghost_card_id_2, int* card_style_value) {
    // 0 - 8    : 万字牌
    // 9 - 17   : 索子牌
    // 18 - 26  : 筒子牌
    // 27 - 33  : 番字牌 东南西北中发白
	int card_num[34] = { 0 };

	// 手牌
	for (int i = 0; i < hand_card_num; ++i) {
		int card_id = hand_cards[i];
		++card_num[card_id];
	}

	// 新添加进来的牌
    if (add_card != -1) {
        ++card_num[add_card];
    }

	// 需要移除的牌，如果没有这张牌的话，就 return -1
    if (rm_card != -1) {
        if (--card_num[rm_card] < 0) {
            return -1;
        }
    }

	// 剔除鬼牌
	int ghost_num = 0;
	if (ghost_card_id_1 != -1) {
		ghost_num += card_num[ghost_card_id_1];
		card_num[ghost_card_id_1] = 0;
	}
	if (ghost_card_id_2 != -1) {
		ghost_num += card_num[ghost_card_id_2];
		card_num[ghost_card_id_2] = 0;
	}

    // 
	auto __format__ = [&card_num](int start_index, int end_index) {
        int value = 0;
        for (int i=start_index; i <= end_index; ++i) {
            value = value * 10 + card_num[i];
        }
        return value;
    };

    card_style_value[0] = __format__(0, 8);
    card_style_value[1] = __format__(9, 17);
    card_style_value[2] = __format__(18, 26);
    card_style_value[3] = __format__(27, 33);

    return ghost_num;
}

bool mahjong_win_check::check_is_win(int* hand_cards, int hand_card_num, int new_card, int ghost_card_id_1, int ghost_card_id_2) {
    int card_style_value[4];
    int ghost_num = convert_add(hand_cards, hand_card_num, new_card, ghost_card_id_1, ghost_card_id_2, card_style_value);

    //printf("card_style_value[0] : %d\n", card_style_value[0]);
    //printf("card_style_value[1] : %d\n", card_style_value[1]);
    //printf("card_style_value[2] : %d\n", card_style_value[2]);
    //printf("card_style_value[3] : %d\n", card_style_value[3]);
    //printf("ghost_num : %d\n", ghost_num);

    return check_value_fan(card_style_value, ghost_num, true);
}

bool mahjong_win_check::check_is_win_add_rm(int* hand_cards, int hand_card_num, int add_card, int rm_card, int ghost_card_id_1, int ghost_card_id_2) {
    int card_style_value[4];
    int ghost_num = convert_add_rm(hand_cards, hand_card_num, add_card, rm_card, ghost_card_id_1, ghost_card_id_2, card_style_value);

    // ghost_num 意味着手牌中没有 rm_card 这张牌
    if (ghost_num == -1) {
        return false;
    }

    //printf("card_style_value[0] : %d\n", card_style_value[0]);
    //printf("card_style_value[1] : %d\n", card_style_value[1]);
    //printf("card_style_value[2] : %d\n", card_style_value[2]);
    //printf("card_style_value[3] : %d\n", card_style_value[3]);
    //printf("ghost_num : %d\n", ghost_num);

    return check_value_fan(card_style_value, ghost_num, true);
}

bool mahjong_win_check::check_value_wtt(int* card_style_value, int index, int ghost_num, bool need_eyes) {
    // 能够一直匹配下来，到这里的话，就意味着可胡了
    if (index >= 3) {
        return true;
    }

    // 没有值，就匹配下一个吧
    if (card_style_value[index] == 0) {
        return check_value_wtt(card_style_value, index+1, ghost_num, need_eyes);
    }

    // 没有找到对应的牌型，不能胡
    auto iter = _all_wtt_styles.find(card_style_value[index]);
    if (iter == _all_wtt_styles.end()) {
        return false;
    }

    // 一个牌型下，可能对应的多种类型，如鬼的数量已经是否带眼
    for (auto iter_2 : iter->second) {
		int need_ghost_num = iter_2.ghost_num;
		bool has_eyes = iter_2.has_eyes;

        //printf("style $$$$$$$$$$$$$$$$$$$$$$\n");
        //printf("card_style_value[index] : %d\n", card_style_value[index]);
        //printf("need_ghost_num : %d\n", need_ghost_num);
        //printf("has_eyes : %s\n", has_eyes ? "true" : "false");
        //printf("-------------------------");
        //printf("ghost_num : %d\n", ghost_num);
        //printf("need_eyes : %s\n", need_eyes ? "true" : "false");

        // 没有足够的鬼牌
        if (need_ghost_num > ghost_num) {
            continue;
        }

        // 如果不需要眼，但却带眼，这个不能胡
        if (!need_eyes && has_eyes) {
            continue;
        }

        //printf("check next =============================================\n");
        // 
        if (check_value_wtt(card_style_value, index+1, ghost_num - need_ghost_num, has_eyes ? false : need_eyes)) {
            return true;
        }
    }

    // 当前牌型下的所有类型都不匹配，就意味着不能胡
    return false;
}

bool mahjong_win_check::check_value_fan(int* card_style_value, int ghost_num, bool need_eyes) {
    // 没有值，就匹配万条筒去吧
    if (card_style_value[3] == 0) {
        return check_value_wtt(card_style_value, 0, ghost_num, need_eyes);
    }

    // 没有找到对应的牌型，不能胡
    auto iter = _all_fan_styles.find(card_style_value[3]);
    if (iter == _all_fan_styles.end()) {
        return false;
    }

    // 一个牌型下，可能对应的多种类型，如鬼的数量已经是否带眼
    for (auto iter_2 : iter->second) {
		int need_ghost_num = iter_2.ghost_num;
		bool has_eyes = iter_2.has_eyes;

        // 没有足够的鬼牌
        if (need_ghost_num > ghost_num) {
            continue;
        }

        // 如果不需要眼，但却带眼，这个不能胡
        if (!need_eyes && has_eyes) {
            continue;
        }

        // 
        if (check_value_wtt(card_style_value, 0, ghost_num - need_ghost_num, has_eyes ? false : need_eyes)) {
            return true;
        }
    }

    // 当前牌型下的所有类型都不匹配，就意味着不能胡
    return false;
}

void mahjong_win_check::get_ting_list(std::unordered_map<int, std::list<int>>& all_ting_list, int* hand_cards, int hand_card_num, int ghost_card_id_1, int ghost_card_id_2) {
    all_ting_list.clear();

    for (int rm_card_id=0; rm_card_id < 34; ++rm_card_id) {
        std::list<int> win_cards;
        for (int add_card_id=0; add_card_id < 34; ++add_card_id) {
            if (check_is_win_add_rm(hand_cards, hand_card_num, add_card_id, rm_card_id, ghost_card_id_1, ghost_card_id_2)) {
                win_cards.push_back(add_card_id);
            }
        }

        if (!win_cards.empty()) {
            all_ting_list[rm_card_id] = win_cards;
        }
    }
}

char* mahjong_win_check::get_ting_list_py(int* hand_cards, int hand_card_num, int ghost_card_id_1, int ghost_card_id_2) {
    std::unordered_map<int, std::list<int>> all_ting_list;
    get_ting_list(all_ting_list, hand_cards, hand_card_num, ghost_card_id_1, ghost_card_id_2);

    char szBuf[128];

    cJSON* root = cJSON_CreateObject();
    for (const auto& iter : all_ting_list) {
        cJSON* item = cJSON_CreateObject();
        cJSON_AddItemToObject(root, itoa(iter.first, szBuf), item);
        for (const auto& iter1 : iter.second) {
            cJSON_AddItemToArray(item, cJSON_CreateNumber(iter1));
        }
    }

    char* json_data = cJSON_Print(root);
    int length = strlen(json_data);
    char* ret_data = (char*)malloc(length+1);
    sprintf(ret_data, "%s", json_data);
    ret_data[length] = 0;

    return ret_data;
}

// void mahjong_win_check::get_all_win_styles(int* hand_cards, int hand_card_num, std::list<OneSequence*>& all_sequences) {
//     int card_style_value[4];
//     int ghost_num = convert(hand_cards, hand_card_num, -1, card_style_value);
// 
// 	// 
// 	for (auto iter : all_sequences) {
// 		delete iter;
// 	}
// 	all_sequences.clear();
// 
// 	// 
//     OneSequence* cur_sequence = new OneSequence;
//     all_sequences.push_back(cur_sequence);
// 
//     get_win_style_2(card_style_value, ghost_num, true, all_sequences, cur_sequence);
// }
// 
// void mahjong_win_check::get_win_style_1(int* card_style_value, int index, int ghost_num, bool need_eyes, std::list<OneSequence*>& all_sequences, OneSequence* cur_sequence) {
//     // 能够一直匹配下来，到这里的话，就意味着可胡了
//     if (index >= 3) {
//         return;
//     }
// 
//     // 没有值，就匹配下一个吧
//     if (card_style_value[index] == 0) {
//         get_win_style_1(card_style_value, index+1, ghost_num, need_eyes, all_sequences, cur_sequence);
// 
//         return;
//     }
// 
//     // 没有找到对应的牌型，不能胡
//     auto iter = _all_wtt_styles.find(card_style_value[index]);
//     if (iter == _all_wtt_styles.end()) {
//         cur_sequence->is_valid = false;
// 
//         return;
//     }
// 
//     std::vector<std::function<void(OneSequence*)>> vecValidFuncList;
// 
//     // 一个牌型下，可能对应的多种类型，如鬼的数量已经是否带眼
//     for (int i=0; i < (int)iter->second.size(); ++i) {
// 		int need_ghost_num = iter->second[i].ghost_num;
// 		bool has_eyes = iter->second[i].has_eyes;
// 
//         // 没有足够的鬼牌
//         if (need_ghost_num > ghost_num) {
//             continue;
//         }
// 
//         // 如果不需要眼，但却带眼，这个不能胡
//         if (!need_eyes && has_eyes) {
//             continue;
//         }
// 
//         int remain_ghost_num = ghost_num - need_ghost_num;
//         bool next_need_eyes = has_eyes ? false : need_eyes;
// 		vecValidFuncList.push_back([this, &card_style_value, index, &all_sequences, i, remain_ghost_num, next_need_eyes](OneSequence* os){
// 			os->ssi.push_back(SequenceStyleInfo(index, card_style_value[index], i));
//             get_win_style_1(card_style_value, index+1, remain_ghost_num, next_need_eyes, all_sequences, os);
//         });
//     }
// 
//     if (vecValidFuncList.empty()) {
//         // 当前牌型下的所有类型都不匹配，就意味着不能胡
//         cur_sequence->is_valid = false;
//     } else {
//         for (int i=0; i < (int)vecValidFuncList.size(); ++i) {
//             if (i != vecValidFuncList.size() - 1) {
//                 // new copy
//                 OneSequence* new_sequence = new OneSequence;
//                 new_sequence->ssi = cur_sequence->ssi;
//                 all_sequences.push_back(new_sequence);
// 
//                 vecValidFuncList[i](new_sequence);
//             } else {
//                 vecValidFuncList[i](cur_sequence);
//             }
//         }
//     }
// }
// 
// void mahjong_win_check::get_win_style_2(int* card_style_value, int ghost_num, bool need_eyes, std::list<OneSequence*>& all_sequences, OneSequence* cur_sequence) {
//     // 没有值，就匹配万条筒去吧
//     if (card_style_value[3] == 0) {
//         get_win_style_1(card_style_value, 0, ghost_num, need_eyes, all_sequences, cur_sequence);
// 
//         return;
//     }
// 
//     // 没有找到对应的牌型，不能胡
//     auto iter = _all_fan_styles.find(card_style_value[3]);
//     if (iter == _all_fan_styles.end()) {
//         cur_sequence->is_valid = false;
// 
//         return;
//     }
// 
//     std::vector<std::function<void(OneSequence*)>> vecValidFuncList;
// 
//     // 一个牌型下，可能对应的多种类型，如鬼的数量已经是否带眼
//     for (int i=0; i < (int)iter->second.size(); ++i) {
// 		int need_ghost_num = iter->second[i].ghost_num;
// 		bool has_eyes = iter->second[i].has_eyes;
// 
//         // 没有足够的鬼牌
//         if (need_ghost_num > ghost_num) {
//             continue;
//         }
// 
//         // 如果不需要眼，但却带眼，这个不能胡
//         if (!need_eyes && has_eyes) {
//             continue;
//         }
// 
//         int remain_ghost_num = ghost_num - need_ghost_num;
// 		bool next_need_eyes = has_eyes ? false : need_eyes;
// 		vecValidFuncList.push_back([this, &card_style_value, &all_sequences, i, remain_ghost_num, next_need_eyes](OneSequence* os){
//             os->ssi.push_back(SequenceStyleInfo(3, card_style_value[3], i));
//             get_win_style_1(card_style_value, 0, remain_ghost_num, next_need_eyes, all_sequences, os);
//         });
//     }
// 
//     if (vecValidFuncList.empty()) {
//         // 当前牌型下的所有类型都不匹配，就意味着不能胡
//         cur_sequence->is_valid = false;
//     } else {
//         for (int i=0; i < (int)vecValidFuncList.size(); ++i) {
//             if (i != vecValidFuncList.size() - 1) {
//                 // new copy
//                 OneSequence* new_sequence = new OneSequence;
//                 new_sequence->ssi = cur_sequence->ssi;
//                 all_sequences.push_back(new_sequence);
// 
//                 vecValidFuncList[i](new_sequence);
//             } else {
//                 vecValidFuncList[i](cur_sequence);
//             }
//         }
//     }
// }

//
//char* mahjong_win_check::get_win_sequence(int* hand_cards, int hand_card_num, int win_card) {
//    return nullptr;
//}
