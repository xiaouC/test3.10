#include <unordered_set>
#include <set>

//std::unordered_set<int> all_win_styles_no_eyes[9];
//std::unordered_set<int> all_win_styles_with_eyes[9];
std::set<int> all_win_styles_no_eyes[9];
std::set<int> all_win_styles_with_eyes[9];

std::set<int> all_check_no_eyes[9];
std::set<int> all_check_with_eyes[9];

void save() {
    for (int i=0; i < 9; ++i) {
        char szFileName_1[64] = { 0 };
        sprintf(szFileName_1, "no_eyes_%d.txt", i);
        FILE* fp_1 = fopen(szFileName_1, "w");
        for (const auto& iter : all_win_styles_no_eyes[i]) {
            fprintf(fp_1, "%d\n", iter);
        }
        fclose(fp_1);

        char szFileName_2[64] = { 0 };
        sprintf(szFileName_2, "with_eyes_%d.txt", i);
        FILE* fp_2 = fopen(szFileName_2, "w");
        for (const auto& iter : all_win_styles_with_eyes[i]) {
            fprintf(fp_2, "%d\n", iter);
        }
        fclose(fp_2);
    }
}

bool add_style(int cards[], int ghost_num, bool has_eyes) {
    bool check_flag = false;
    int style = 0;
    for (int i=0; i < 9; ++i) {
        style = style * 10 + cards[i];

        if (cards[i] > 4) {
            check_flag = true;
        }
    }

    // 能够等于 0，那就是都已经被鬼牌给替换掉了
    // 如果只剩鬼牌的话，那肯定胡了
    if (style == 0) {
        return false;
    }

    // 
    auto& check_styles = has_eyes ? all_check_with_eyes[ghost_num] : all_check_no_eyes[ghost_num];
    if (check_styles.find(style) != check_styles.end()) {
        return false;
    }

    check_styles.insert(style);
    if (check_flag) {
        return true;
    }

    // 缓存起来
    auto& win_styles = has_eyes ? all_win_styles_with_eyes[ghost_num] : all_win_styles_no_eyes[ghost_num];
    if (win_styles.find(style) == win_styles.end()) {
        win_styles.insert(style);
    }

    return true;
}

void ghost_derive_style(int cards[], int ghost_num, bool has_eyes) {
    // 目前来说，最多 8 鬼
    if (ghost_num > 8) {
        return;
    }

    // 减掉一张牌，多带上一张鬼牌，组成新的牌型
    for (int i=0; i < 9; ++i) {
        if (cards[i] == 0) {
            continue;
        }

        --cards[i];

        // 如果这种带鬼的牌型已经存在了
        // 那么由它而衍生出来的带更多鬼的牌型也已经添加过了
        if (!add_style(cards, ghost_num, has_eyes)) {
            ++cards[i];

            continue;
        }

        // 再多带一张鬼牌
        ghost_derive_style(cards, ghost_num + 1, has_eyes);

        // 复原，以便减掉另外一张牌
        ++cards[i];
    }
}

// 根据无鬼的牌型，衍生出带鬼的牌型
void ghost_derive_style(int cards[], bool has_eyes) {
    // 如果这个无鬼的牌型已经添加过了
    // 那么对应这个牌型而衍生出来的带鬼的牌型，也都已经添加过了
    if (!add_style(cards, 0, has_eyes)) {
        return;
    }

    // 从带一张鬼牌开始
    ghost_derive_style(cards, 1, has_eyes);
}

// 把 3 个球丢到 9 个框中，每个框最多只能有 4 个球
void gen_cards(int cards[], int level, bool has_eyes) {
    // 前面 9 次，每次都是把 3 个球丢到同一个框中           => 组成刻子
    // 后面 7 次，每次都把 3 个球按 1，1，1 丢到连续的框中  => 组成顺子
    for (int i=0; i < 16; ++i) {
        if (i <= 8) {
            // 每个框中最多只能有 4 个球，不过。。。
            // 在有鬼的情况下，一个框可以最多有 6 个球(2鬼)
            // 因为如果 7 个球(3鬼)的话，那和 4 个球(0鬼)没有区别了
            // 这 3 鬼可以自个玩去了
            // 8 球(4鬼)和 5 球(1鬼)同理，9 球(5鬼)和 6 球(2鬼)同理，10 球(6鬼)和 7 球(3鬼)也就是 4 球(0鬼)同理
            if (cards[i] > 3)
                continue;

            cards[i] += 3;
        } else {
            int index = i - 9;

            // 每个框中最多只能有 4 个球
            // 在有鬼的情况下，一个框可以最多有 6 个球(2鬼)
            if (cards[index] > 5 || cards[index+1] > 5 || cards[index+2] > 5)
                continue;

            cards[index] += 1;
            cards[index+1] += 1;
            cards[index+2] += 1;
        }

        // 球已丢完，更新牌型去吧
        ghost_derive_style(cards, has_eyes);

        // 开始下一轮丢球
        if (level < 4) {
            gen_cards(cards, level + 1, has_eyes);
        }

        // 还原，这轮的球，我要换个框来放
        if (i <= 8) {
            cards[i] -= 3;
        } else {
            int index = i - 9;
            cards[index] -= 1;
            cards[index+1] -= 1;
            cards[index+2] -= 1;
        }
    }
}

void gen_no_eyes() {
    int cards[9] = { 0 };

    // 丢 4 次球
    gen_cards(cards, 1, false);
}

void gen_with_eyes() {
    int cards[9] = { 0 };

    // 谁做将牌，一人一次呗
    for (int i=0; i < 9; ++i) {
        cards[i] = 2;

        // 单独只有将牌的时候，碰了 4 次的时候，就单吊将牌
        ghost_derive_style(cards, true);

        // 开始 4 次丢球之旅
        gen_cards(cards, 1, true);

        // 换下一个做将
        cards[i] = 0;
    }
}

int main() {
    gen_no_eyes();
    gen_with_eyes();
    save();

    return 0;
}
