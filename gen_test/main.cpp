#include "game_win_check.h"
#include "gen_test.h"
#ifdef WIN32
#include <time.h>
#else
#include <sys/time.h>
#endif

void test_win_check() {
	game_win_check obj;
	obj.load_win_styles();

	// 
	char szBuf[1024];
	FILE* fp = fopen("input.txt", "r");

	// ghost card
	fgets(szBuf, 1024, fp);
	std::string buf = szBuf;
	std::vector<std::string> result;
	string_split(buf, ",", result);
	obj.set_ghost_card_id_1(atoi(result[1].c_str()));
	obj.set_ghost_card_id_2(atoi(result[2].c_str()));

	printf("ghost_card_id_1 : %d\n", atoi(result[1].c_str()));
	printf("ghost_card_id_2 : %d\n", atoi(result[2].c_str()));

	// hand card
	int hand_cards[14];
	fgets(szBuf, 1024, fp);
	buf = szBuf;
	string_split(buf, ",", result);
	for (int i = 1; i < (int)result.size(); ++i) {
		hand_cards[i - 1] = atoi(result[i].c_str());
		printf("hand_card : %d\n", atoi(result[i].c_str()));
	}

	// new card
	fgets(szBuf, 1024, fp);
	buf = szBuf;
	string_split(buf, ",", result);
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
	//for (int i=0; i < 10000000; ++i) {
		is_win = obj.check_is_win(hand_cards, 13, new_card);
	//}

	std::list<int> win_cards = obj.get_ting_list(hand_cards, 13);

	hand_cards[13] = new_card;

	std::list<OneSequence*> all_sequences;
	for (int i = 0; i < 100000; ++i) {
		obj.get_all_win_styles(hand_cards, 14, all_sequences);
	}

#ifdef WIN32
	end = clock();
#else
	gettimeofday(&end, NULL);
#endif

	printf("is_win : %s\n", is_win ? "true" : "false");

	printf("ting list : ");
	for (const auto& iter : win_cards) {
		printf("%d, ", iter);
	}
	printf("\n");

	// print
	for (auto iter_1 : all_sequences) {
		if (iter_1->is_valid) {
			printf("sequence : [");
			for (auto iter_2 : iter_1->ssi) {
				if (iter_2.card_style_value_index == 3) {
					const game_win_check::StyleInfo& si = obj._all_win_styles_2.find(iter_2.style_value)->second[iter_2.si_index];
					printf("[%d,%s,%d]", iter_2.style_value, si.has_eyes ? "true" : "false", si.ghost_num);
				}
				else {
					const game_win_check::StyleInfo& si = obj._all_win_styles_1.find(iter_2.style_value)->second[iter_2.si_index];
					printf("[%d,%s,%d]", iter_2.style_value, si.has_eyes ? "true" : "false", si.ghost_num);
				}
			}
			printf("]\n");
		}

		delete iter_1;
	}
	all_sequences.clear();

#ifdef WIN32
	float second = (float)(end - start) / CLOCKS_PER_SEC;
#else
	float second = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0f;
#endif

	printf("duration %f seconds.\n", second);
}

void gen_data() {
	gen_1_no_eyes();
	gen_1_with_eyes();

	gen_2_no_eyes();
	gen_2_with_eyes();

	save_data();
}

int main() {
	//test_win_check();
	gen_data();

	getchar();

    return 0;
}
