#pragma once
#include <string>
#include <map>

// int_10 = c_int * 10
// myarr = int_10()
// myarr[2] = c_int(24)


class game_impl_base {
public:
    game_impl_base();
    virtual ~game_impl_base();

    void update_or_add_one_rule(const char* key, int value);
    void set_ghost_card_id_1(int card_id);
    void set_ghost_card_id_2(int card_id);
    void update_rules();

    virtual bool check_is_win(int* hand_cards, int hand_card_num, int new_card);
    virtual char* get_win_sequence(int* hand_cards, int hand_card_num, int new_card);

protected:
    std::map<int, int> convert(int* hand_cards, int hand_card_num);
    int get_ghost_card_num(const std::map<int, int>& card_list);
    int get_card_num(const std::map<int, int>& card_list, int card_id);

    virtual bool check_is_win_no_ghost(const std::map<int, int>& card_list);
    virtual bool check_is_win_no_eyes(const std::map<int, int>& card_list);

protected:
    // 一个顺子、刻子或杠子 
    struct meld_info {
        int x, y, z;
        meld_info(int x1 = -1, int y1 = -1, int z1 = -1) : x(x1), y(y1), z(z1) { }
        meld_info& operator=(const meld_info& rhs) {
            this->x = rhs.x;
            this->y = rhs.y;
            this->z = rhs.z;

            return *this;
        }
    };

    // 一个胡牌序列，就是一个 meld 列表，最终会拼合成字符串返回给 python
    struct sequence_info {
        bool is_valid = true;               // 这个序列最终是否能够组合成有效的胡牌序列
        std::list<meld_info> sequences;     // meld 列表

        sequence_info() { }
    };

protected:
    std::list<std::tuple<int, int>> _card_id_groups;          // 
    int _total_kinds = 0;

    std::map<std::string, int> _game_rules;     // 规则，使用 key : value 的形式存储
    int _ghost_card_id_1 = 0;                   // 鬼牌(万能牌)的ID，没有的话，就是 0
    int _ghost_card_id_2 = 0;                   // 鬼牌(万能牌)的ID，没有的话，就是 0
};
