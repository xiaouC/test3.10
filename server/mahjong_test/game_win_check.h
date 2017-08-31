#pragma once
#include <unordered_map>

class game_win_check {
public:
    game_win_check();
    ~game_win_check();

    void load_win_styles();

public:
    void set_ghost_card_id_1(int card_id);
    void set_ghost_card_id_2(int card_id);

    bool check_is_win(int* hand_cards, int hand_card_num, int new_card);
	int* get_ting_list(int* hand_cards, int hand_card_num);
    char* get_win_sequence(int* hand_cards, int hand_card_num, int win_card);

protected:
    void convert(int* hand_cards, int hand_card_num, int new_card);

    bool check_value(int index, int ghost_num, bool need_eyes);

protected:
    // first: 牌型组成的 int
    // second: 鬼牌个数，是否带眼
    std::unordered_map<int, std::tuple<int, bool>> _all_win_styles;

    // card id => index
    std::unordered_map<int, int> _map_card_id_index;

    // 最多双鬼
    int _ghost_card_id_1 = 0;
    int _ghost_card_id_2 = 0;

    // 0 - 8    : 万字牌
    // 9 - 17   : 索子牌
    // 18 - 26  : 筒子牌
    // 27 - 33  : 番字牌
    int _card_id[34];

    // 万字牌值，索子牌值，筒子牌值，番牌值
    int _card_type_value[4];
    int _ghost_num = 0;
};
