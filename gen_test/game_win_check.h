#pragma once
#include <unordered_map>
#include <list>
#include <tuple>
#include <unordered_set>
#include <vector>

void string_split(const std::string& src, const std::string& s, std::vector<std::string>& result);

struct SequenceStyleInfo {
	SequenceStyleInfo(int v1, int v2, int v3) :
		card_style_value_index(v1),
		style_value(v2),
		si_index(v3) {}
	int card_style_value_index;     // 万条筒番
	int style_value;                // 牌型值, 就是 _all_win_styles_1 或者 _all_win_styles_2 中的 first
	int si_index;                   // _all_win_styles_1 或者 _all_win_styles_2 中的 second 的 index
};

struct OneSequence {
	bool    is_valid = true;
	std::list<SequenceStyleInfo> ssi;
};

class game_win_check {
public:
    game_win_check();
    ~game_win_check();

    void load_win_styles();

public:
    void set_ghost_card_id_1(int card_id);
    void set_ghost_card_id_2(int card_id);

    bool check_is_win(int* hand_cards, int hand_card_num, int new_card);
	std::list<int> get_ting_list(int* hand_cards, int hand_card_num);

protected:
    // card_style_value: int card_style_value[4];
    // 0: 万字牌，1: 索子牌，2: 筒子牌，3: 番牌
    // return: ghost_num
    int convert(int* hand_cards, int hand_card_num, int new_card, int* card_style_value);

    bool check_value_1(int* card_style_value, int index, int ghost_num, bool need_eyes);       // 判断万条筒
    bool check_value_2(int* card_style_value, int ghost_num, bool need_eyes);       // 判断番牌

public:
	struct StyleInfo {
		StyleInfo(int num, bool eyes) : ghost_num(num), has_eyes(eyes) {}
		int		ghost_num;
		bool	has_eyes;
	};
    // first: 牌型组成的 int
    // second: 鬼牌个数，是否带眼
	std::unordered_map<int, std::vector<StyleInfo>> _all_win_styles_1;   // 万条筒
	std::unordered_map<int, std::vector<StyleInfo>> _all_win_styles_2;   // 番

    // 最多双鬼
    int _ghost_card_id_1 = -1;      // 0 是 1 万，所以鬼牌 ID 不能初始化为 0
    int _ghost_card_id_2 = -1;

public:
	void get_all_win_styles(int* hand_cards, int hand_card_num, std::list<OneSequence*>& all_sequences);

protected:
	void get_win_style_1(int* card_style_value, int index, int ghost_num, bool need_eyes, std::list<OneSequence*>& all_sequences, OneSequence* cur_sequence);       // 判断万条筒
	void get_win_style_2(int* card_style_value, int ghost_num, bool need_eyes, std::list<OneSequence*>& all_sequences, OneSequence* cur_sequence);       // 判断番牌

//	/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//public:
//	char* get_win_sequence(int* hand_cards, int hand_card_num, int win_card);
//
//protected:
//	// 一个顺子、刻子或杠子 
//	struct meld_info {
//		int x, y, z;
//		meld_info(int x1 = -1, int y1 = -1, int z1 = -1) : x(x1), y(y1), z(z1) { }
//		meld_info& operator=(const meld_info& rhs) {
//			this->x = rhs.x;
//			this->y = rhs.y;
//			this->z = rhs.z;
//
//			return *this;
//		}
//	};
//
//	// 一个胡牌序列，就是一个 meld 列表，最终会拼合成字符串返回给 python
//	struct sequence_info {
//		bool is_valid = true;               // 这个序列最终是否能够组合成有效的胡牌序列
//		std::list<meld_info> sequences;     // meld 列表
//
//		sequence_info() { }
//	};
//
//	virtual void get_win_sequences_ghost(std::unordered_set<std::string>& checked_list, std::unordered_map<int, int>& no_ghost_card_list, int ghost_index, int ghost_num);
//	virtual void get_win_sequences_no_ghost(const std::unordered_map<int, int>& card_list);
//	virtual void get_win_sequences_no_eyes(std::unordered_map<int, int>& card_list, sequence_info* si);
//	virtual bool get_win_sequences_kind_group(std::list<std::tuple<int, int>>::iterator iter, int start_id, int end_id, int offset, sequence_info* si, std::unordered_map<int, int>& card_list);
//
//	std::list<sequence_info*> _win_sequences;               // 胡牌序列，这个一般只在胡牌后，结算用到
};
