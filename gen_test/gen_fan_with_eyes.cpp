#include "gen_fan_with_eyes.h"
#include <unordered_map>
#include <list>

std::unordered_map<int, std::vector<long long>> all_fan_styles_with_eyes[9];

bool add_fan_style_with_eyes(int cards[], int ghost_num, const long long& sequence) {
    int style = 0;
    for (int i=1; i < 8; ++i) {
        style = style * 10 + cards[i];

        if (cards[i] > 4) {
			return true;
        }
    }

    // 能够等于 0，那就是都已经被鬼牌给替换掉了
    // 如果只剩鬼牌的话，那肯定胡了
    if (style == 0) {
        return false;
    }

    // 
    long long ss = sort_sequence(sequence);

    std::unordered_map<int, std::vector<long long>>& all_fan_styles = all_fan_styles_with_eyes[ghost_num];

    // 
    auto iter = all_fan_styles.find(style);
    if (iter == all_fan_styles.end()) {
        std::vector<long long> sequences;
        sequences.reserve(30);
        sequences.push_back(ss);
        all_fan_styles[style] = sequences;

        return true;
    }

    for (auto& iter1 : iter->second) {
        if (iter1 == ss) {
            return true;
        }
    }

    iter->second.push_back(ss);

    return true;
}

void ghost_derive_fan_style_with_eyes(int cards[], int ghost_num, long long& sequence) {
    // 目前来说，最多 8 鬼
    if (ghost_num > 8) {
        return;
    }

    // 减掉一张牌，多带上一张鬼牌，组成新的牌型
    for (int i=1; i < 8; ++i) {
        if (cards[i] == 0) {
            continue;
        }

        --cards[i];

        // 如果这种带鬼的牌型已经存在了
        // 那么由它而衍生出来的带更多鬼的牌型也已经添加过了
		if (add_fan_style_with_eyes(cards, ghost_num, sequence)) {
            // 再多带一张鬼牌
            ghost_derive_fan_style_with_eyes(cards, ghost_num + 1, sequence);
        }

        // 复原，以便减掉另外一张牌
        ++cards[i];
    }
}

// 根据无鬼的牌型，衍生出带鬼的牌型
void ghost_derive_fan_style_with_eyes(int cards[], long long& sequence) {
    // 如果这个无鬼的牌型已经添加过了
    // 那么对应这个牌型而衍生出来的带鬼的牌型，也都已经添加过了
	add_fan_style_with_eyes(cards, 0, sequence);

    // 从带一张鬼牌开始
	ghost_derive_fan_style_with_eyes(cards, 1, sequence);
}

void gen_fan_cards_with_eyes(int cards[], int level, long long& sequence) {
    // 只组成刻子
    for (int i=1; i < 8; ++i) {
        // 每个框中最多只能有 4 个球，不过。。。
        // 在有鬼的情况下，一个框可以最多有 6 个球(2鬼)
        // 因为如果 7 个球(3鬼)的话，那和 4 个球(0鬼)没有区别了
        // 这 3 鬼可以自个玩去了
        // 8 球(4鬼)和 5 球(1鬼)同理，9 球(5鬼)和 6 球(2鬼)同理，10 球(6鬼)和 7 球(3鬼)也就是 4 球(0鬼)同理
        if (cards[i] > 3)
            continue;

        cards[i] += 3;
        sequence = sequence * 1000 + 100 * i + 10 * i + i;

        // 球已丢完，更新牌型去吧
		ghost_derive_fan_style_with_eyes(cards, sequence);

        // 开始下一轮丢球
        if (level < 4) {
			gen_fan_cards_with_eyes(cards, level + 1, sequence);
        }

        // 还原，这轮的球，我要换个框来放
        cards[i] -= 3;
        //sequence /= 1000;
        sequence *= 0.001;
    }
}

void gen_fan_with_eyes() {
    int cards[8] = { 0 };

    // 谁做将牌，一人一次呗
    long long sequence = 0;
    for (int i=1; i < 8; ++i) {
        cards[i] = 2;
        sequence = sequence * 1000 + 10 * i + i;

        // 单独只有将牌的时候，碰了 4 次的时候，就单吊将牌
		ghost_derive_fan_style_with_eyes(cards, sequence);

        // 开始 4 次丢球之旅
		gen_fan_cards_with_eyes(cards, 1, sequence);

        // 换下一个做将
		cards[i] = 0;
        //sequence /= 1000;
        sequence *= 0.001;
    }

    save_data_text_with_eyes("./data/new_fan_with_eyes.txt", all_fan_styles_with_eyes);
}

