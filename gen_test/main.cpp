#include "mahjong_win_check.h"
#include <string>
#include <stdlib.h>
#ifdef WIN32
#include <time.h>
#else
#include <sys/time.h>
#endif

void test_win_check() {
    mahjong_win_check::load_win_styles();

	// 
	char szBuf[1024];
	FILE* fp = fopen("input.txt", "r");

	// ghost card
	fgets(szBuf, 1024, fp);
	std::vector<std::string> result;
	string_split(szBuf, ",", result);
    int ghost_card_id_1 = atoi(result[1].c_str());
    int ghost_card_id_2 = atoi(result[2].c_str());

	printf("ghost_card_id_1 : %d\n", ghost_card_id_1);
	printf("ghost_card_id_2 : %d\n", ghost_card_id_2);

	// hand card
	int hand_cards[14];
	fgets(szBuf, 1024, fp);
	string_split(szBuf, ",", result);
	for (int i = 1; i < (int)result.size(); ++i) {
		hand_cards[i - 1] = atoi(result[i].c_str());
		printf("hand_card : %d\n", atoi(result[i].c_str()));
	}

	// new card
	fgets(szBuf, 1024, fp);
	string_split(szBuf, ",", result);
	int new_card = atoi(result[1].c_str());
	printf("new_card : %d\n", atoi(result[1].c_str()));

	fclose(fp);

	printf("start test ...\n");

#ifdef WIN32
	clock_t start, end;
	start = clock();
#else
	struct timeval start;
	struct timeval end;
	gettimeofday(&start, NULL);
#endif

	bool is_win = false;
	for (int i=0; i < 10000000; ++i) {
		is_win = mahjong_win_check::check_is_win(hand_cards, 13, new_card, ghost_card_id_1, ghost_card_id_2);
	}

    // 
    hand_cards[13] = new_card;
    std::unordered_map<int, std::list<int>> all_ting_list;
	mahjong_win_check::get_ting_list(all_ting_list, hand_cards, 14, ghost_card_id_1, ghost_card_id_2);

    // 
    char* json_data = mahjong_win_check::get_ting_list_py(hand_cards, 14, ghost_card_id_1, ghost_card_id_2);

    // 胡牌的番型
	// hand_cards[13] = new_card;

	// std::list<OneSequence*> all_sequences;
	// for (int i = 0; i < 100000; ++i) {
	// 	obj.get_all_win_styles(hand_cards, 14, all_sequences);
	// }

#ifdef WIN32
	end = clock();
#else
	gettimeofday(&end, NULL);
#endif

    // is win
	printf("is_win : %s\n", is_win ? "true" : "false");

    // 听牌列表
	printf("ting list : \n");
    for (const auto& iter : all_ting_list) {
        printf("[%d]:[", iter.first);
        for (const auto& iter1 : iter.second) {
            printf("%d, ", iter1);
        }
        printf("]\n");
    }

    // python json data
    printf("%s\n", json_data);
    free(json_data);

    // 胡牌的番型
	// // print
	// for (auto iter_1 : all_sequences) {
	// 	if (iter_1->is_valid) {
	// 		printf("sequence : [");
	// 		for (auto iter_2 : iter_1->ssi) {
	// 			if (iter_2.card_style_value_index == 3) {
	// 				const game_win_check::StyleInfo& si = obj._all_win_styles_2.find(iter_2.style_value)->second[iter_2.si_index];
	// 				printf("[%d,%s,%d]", iter_2.style_value, si.has_eyes ? "true" : "false", si.ghost_num);
	// 			}
	// 			else {
	// 				const game_win_check::StyleInfo& si = obj._all_win_styles_1.find(iter_2.style_value)->second[iter_2.si_index];
	// 				printf("[%d,%s,%d]", iter_2.style_value, si.has_eyes ? "true" : "false", si.ghost_num);
	// 			}
	// 		}
	// 		printf("]\n");
	// 	}

	// 	delete iter_1;
	// }
	// all_sequences.clear();

#ifdef WIN32
	float second = (float)(end - start) / CLOCKS_PER_SEC;
#else
	float second = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0f;
#endif

	printf("duration %f seconds.\n", second);
}


int main() {
	//test_win_check();
    int num[18];
    for (int i=0; i < 18; ++i) {
        num[i] = 4;
    }

    long ll_num = 0;
    for (int i=0; i < 18; ++i) {
        ll_num = ll_num * 10 + num[i];
    }
    printf("%ld\n", ll_num);

    // 
    long long sequence = 111222333444055LL;
    printf("%lld\n", sequence);

    sequence /= 1000;
    printf("%lld\n", sequence);

    sequence = sequence * 1000 + 6 * 100 + 6 * 10 + 6;
    printf("%lld\n", sequence);

    long long ss = 111555033222666LL;
    printf("ss : %lld\n", ss);
    printf("new : %lld\n", sort_sequence(ss));

#ifdef WIN32
	getchar();
#endif

    return 0;
}
