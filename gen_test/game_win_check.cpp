#include "game_win_check.h"
#include <string>
#include <stdlib.h>
#include <functional>



game_win_check::game_win_check() {
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
            fgets(szBuf, 128, fp_1);
            std::string buf = szBuf;
			std::vector<std::string> result;
			string_split(buf, "|", result);
			int style = atoi(result[0].c_str());
			bool has_eyes = (result[1].compare("true") == 0);
			int ghost_num = atoi(result[2].c_str());
            //printf("style : %d\n", style);
            //printf("ghost_num : %d\n", ghost_num);
            //printf("has_eyes : %s\n", has_eyes ? "true" : "false");
            //printf("%s\n", str3.c_str());
            //printf("%d\n", str3.compare("true"));

            auto iter = _all_win_styles_1.find(style);
            if (iter == _all_win_styles_1.end()) {
				std::vector<StyleInfo> vecGhostEyes;
				vecGhostEyes.push_back(StyleInfo(ghost_num, has_eyes));

                _all_win_styles_1[style] = vecGhostEyes;
            } else {
                bool flag = false;
                for (const auto& iterGE : iter->second) {
					int num = iterGE.ghost_num;
					bool eyes = iterGE.has_eyes;
                    if (num == ghost_num && eyes == has_eyes) {
                        flag = true;
                        break;
                    }
                }
                if (!flag) {
					iter->second.push_back(StyleInfo(ghost_num, has_eyes));
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
            fgets(szBuf, 128, fp_2);
            std::string buf = szBuf;
			std::vector<std::string> result;
			string_split(buf, "|", result);
			int style = atoi(result[0].c_str());
			bool has_eyes = (result[1].compare("true") == 0);
			int ghost_num = atoi(result[2].c_str());
            //printf("style : %d\n", style);
            //printf("ghost_num : %d\n", ghost_num);
            //printf("has_eyes : %s\n", has_eyes ? "true" : "false");
            //printf("%s\n", str3.c_str());
            //printf("%d\n", str3.compare("true"));

            auto iter = _all_win_styles_2.find(style);
            if (iter == _all_win_styles_2.end()) {
				std::vector<StyleInfo> vecGhostEyes;
				vecGhostEyes.push_back(StyleInfo(ghost_num, has_eyes));

                _all_win_styles_2[style] = vecGhostEyes;
            } else {
                bool flag = false;
                for (const auto& iterGE : iter->second) {
					int num = iterGE.ghost_num;
					bool eyes = iterGE.has_eyes;
                    if (num == ghost_num && eyes == has_eyes) {
                        flag = true;
                        break;
                    }
                }
                if (!flag) {
					iter->second.push_back(StyleInfo(ghost_num, has_eyes));
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

int game_win_check::convert(int* hand_cards, int hand_card_num, int new_card, int* card_style_value) {
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
	if (_ghost_card_id_1 != -1) {
		ghost_num += card_num[_ghost_card_id_1];
		card_num[_ghost_card_id_1] = 0;
	}
	if (_ghost_card_id_2 != -1) {
		ghost_num += card_num[_ghost_card_id_2];
		card_num[_ghost_card_id_2] = 0;
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

bool game_win_check::check_is_win(int* hand_cards, int hand_card_num, int new_card) {
    int card_style_value[4];
    int ghost_num = convert(hand_cards, hand_card_num, new_card, card_style_value);

    //printf("card_style_value[0] : %d\n", card_style_value[0]);
    //printf("card_style_value[1] : %d\n", card_style_value[1]);
    //printf("card_style_value[2] : %d\n", card_style_value[2]);
    //printf("card_style_value[3] : %d\n", card_style_value[3]);
    //printf("ghost_num : %d\n", ghost_num);

    return check_value_2(card_style_value, ghost_num, true);
}

bool game_win_check::check_value_1(int* card_style_value, int index, int ghost_num, bool need_eyes) {
    // 能够一直匹配下来，到这里的话，就意味着可胡了
    if (index >= 3) {
        return true;
    }

    // 没有值，就匹配下一个吧
    if (card_style_value[index] == 0) {
        return check_value_1(card_style_value, index+1, ghost_num, need_eyes);
    }

    // 没有找到对应的牌型，不能胡
    auto iter = _all_win_styles_1.find(card_style_value[index]);
    if (iter == _all_win_styles_1.end()) {
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
        if (check_value_1(card_style_value, index+1, ghost_num - need_ghost_num, has_eyes ? false : need_eyes)) {
            return true;
        }
    }

    // 当前牌型下的所有类型都不匹配，就意味着不能胡
    return false;
}

bool game_win_check::check_value_2(int* card_style_value, int ghost_num, bool need_eyes) {
    // 没有值，就匹配万条筒去吧
    if (card_style_value[3] == 0) {
        return check_value_1(card_style_value, 0, ghost_num, need_eyes);
    }

    // 没有找到对应的牌型，不能胡
    auto iter = _all_win_styles_2.find(card_style_value[3]);
    if (iter == _all_win_styles_2.end()) {
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
        if (check_value_1(card_style_value, 0, ghost_num - need_ghost_num, has_eyes ? false : need_eyes)) {
            return true;
        }
    }

    // 当前牌型下的所有类型都不匹配，就意味着不能胡
    return false;
}

std::list<int> game_win_check::get_ting_list(int* hand_cards, int hand_card_num) {
    std::list<int> win_cards;
    for (int card_id=0; card_id < 34; ++card_id) {
        if (check_is_win(hand_cards, hand_card_num, card_id)) {
            win_cards.push_back(card_id);
        }
    }

    return win_cards;
}

void game_win_check::get_all_win_styles(int* hand_cards, int hand_card_num, std::list<OneSequence*>& all_sequences) {
    int card_style_value[4];
    int ghost_num = convert(hand_cards, hand_card_num, -1, card_style_value);

	// 
	for (auto iter : all_sequences) {
		delete iter;
	}
	all_sequences.clear();

	// 
    OneSequence* cur_sequence = new OneSequence;
    all_sequences.push_back(cur_sequence);

    get_win_style_2(card_style_value, ghost_num, true, all_sequences, cur_sequence);
}

void game_win_check::get_win_style_1(int* card_style_value, int index, int ghost_num, bool need_eyes, std::list<OneSequence*>& all_sequences, OneSequence* cur_sequence) {
    // 能够一直匹配下来，到这里的话，就意味着可胡了
    if (index >= 3) {
        return;
    }

    // 没有值，就匹配下一个吧
    if (card_style_value[index] == 0) {
        get_win_style_1(card_style_value, index+1, ghost_num, need_eyes, all_sequences, cur_sequence);

        return;
    }

    // 没有找到对应的牌型，不能胡
    auto iter = _all_win_styles_1.find(card_style_value[index]);
    if (iter == _all_win_styles_1.end()) {
        cur_sequence->is_valid = false;

        return;
    }

    std::vector<std::function<void(OneSequence*)>> vecValidFuncList;

    // 一个牌型下，可能对应的多种类型，如鬼的数量已经是否带眼
    for (int i=0; i < (int)iter->second.size(); ++i) {
		int need_ghost_num = iter->second[i].ghost_num;
		bool has_eyes = iter->second[i].has_eyes;

        // 没有足够的鬼牌
        if (need_ghost_num > ghost_num) {
            continue;
        }

        // 如果不需要眼，但却带眼，这个不能胡
        if (!need_eyes && has_eyes) {
            continue;
        }

        int remain_ghost_num = ghost_num - need_ghost_num;
        bool next_need_eyes = has_eyes ? false : need_eyes;
		vecValidFuncList.push_back([this, &card_style_value, index, &all_sequences, i, remain_ghost_num, next_need_eyes](OneSequence* os){
			os->ssi.push_back(SequenceStyleInfo(index, card_style_value[index], i));
            get_win_style_1(card_style_value, index+1, remain_ghost_num, next_need_eyes, all_sequences, os);
        });
    }

    if (vecValidFuncList.empty()) {
        // 当前牌型下的所有类型都不匹配，就意味着不能胡
        cur_sequence->is_valid = false;
    } else {
        for (int i=0; i < (int)vecValidFuncList.size(); ++i) {
            if (i != vecValidFuncList.size() - 1) {
                // new copy
                OneSequence* new_sequence = new OneSequence;
                new_sequence->ssi = cur_sequence->ssi;
                all_sequences.push_back(new_sequence);

                vecValidFuncList[i](new_sequence);
            } else {
                vecValidFuncList[i](cur_sequence);
            }
        }
    }
}

void game_win_check::get_win_style_2(int* card_style_value, int ghost_num, bool need_eyes, std::list<OneSequence*>& all_sequences, OneSequence* cur_sequence) {
    // 没有值，就匹配万条筒去吧
    if (card_style_value[3] == 0) {
        get_win_style_1(card_style_value, 0, ghost_num, need_eyes, all_sequences, cur_sequence);

        return;
    }

    // 没有找到对应的牌型，不能胡
    auto iter = _all_win_styles_2.find(card_style_value[3]);
    if (iter == _all_win_styles_2.end()) {
        cur_sequence->is_valid = false;

        return;
    }

    std::vector<std::function<void(OneSequence*)>> vecValidFuncList;

    // 一个牌型下，可能对应的多种类型，如鬼的数量已经是否带眼
    for (int i=0; i < (int)iter->second.size(); ++i) {
		int need_ghost_num = iter->second[i].ghost_num;
		bool has_eyes = iter->second[i].has_eyes;

        // 没有足够的鬼牌
        if (need_ghost_num > ghost_num) {
            continue;
        }

        // 如果不需要眼，但却带眼，这个不能胡
        if (!need_eyes && has_eyes) {
            continue;
        }

        int remain_ghost_num = ghost_num - need_ghost_num;
		bool next_need_eyes = has_eyes ? false : need_eyes;
		vecValidFuncList.push_back([this, &card_style_value, &all_sequences, i, remain_ghost_num, next_need_eyes](OneSequence* os){
            os->ssi.push_back(SequenceStyleInfo(3, card_style_value[3], i));
            get_win_style_1(card_style_value, 0, remain_ghost_num, next_need_eyes, all_sequences, os);
        });
    }

    if (vecValidFuncList.empty()) {
        // 当前牌型下的所有类型都不匹配，就意味着不能胡
        cur_sequence->is_valid = false;
    } else {
        for (int i=0; i < (int)vecValidFuncList.size(); ++i) {
            if (i != vecValidFuncList.size() - 1) {
                // new copy
                OneSequence* new_sequence = new OneSequence;
                new_sequence->ssi = cur_sequence->ssi;
                all_sequences.push_back(new_sequence);

                vecValidFuncList[i](new_sequence);
            } else {
                vecValidFuncList[i](cur_sequence);
            }
        }
    }
}

//
//char* game_win_check::get_win_sequence(int* hand_cards, int hand_card_num, int win_card) {
//    return nullptr;
//}
