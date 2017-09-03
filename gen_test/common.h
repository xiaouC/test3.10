#pragma once
#include <list>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <string>

// 生成数据用到
struct GenStyleInfo {
    GenStyleInfo() {}
    GenStyleInfo(int num, long long sequence) :
        ghost_num(num)
    {
        card_styles.push_back(sequence);
    }
    int ghost_num;
    std::list<long long> card_styles;
};

// 游戏判断用到
struct StyleInfo {
    StyleInfo() {}
    StyleInfo(int num, bool eyes) : ghost_num(num), has_eyes(eyes) {}
    int		ghost_num = 0;
    bool	has_eyes = false;
    // 最外层是多个序列，一个序列多个刻子/顺子，一个顺子多张牌
    std::vector<std::vector<std::vector<int>>> sequences;
};

void string_split(const std::string& src, const std::string& s, std::vector<std::string>& result);
long long sort_sequence(long long sequence);
std::vector<int> split_sequence(long long sequence);

/* itoa:  convert n to characters in s */
char* itoa(int n, char s[]);
void reverse(char s[]);

bool is_the_same_sequence(const std::list<int>& s1, const std::list<int>& s2);

//void save_new_data_binary(const char* filename, const std::unordered_map<int, std::list<GenStyleInfo>>& all_styles);
//void load_new_data_binary(const char* filename, std::unordered_map<int, std::vector<StyleInfo>>& all_styles);

void save_data_text_no_eyes(const char* filename, const std::unordered_map<int, std::vector<long long>> all_styles[]);
void save_data_text_with_eyes(const char* filename, const std::unordered_map<int, std::vector<long long>> all_styles[]);

void save_data_text_wtt_no_eyes(const char* filename, const std::unordered_map<int, std::unordered_set<long long>> all_styles[]);
void save_data_text_wtt_with_eyes(const char* filename, const std::unordered_map<int, std::unordered_set<long long>> all_styles[]);
//void load_new_dat_wtta_text(const char* filename, std::unordered_map<int, std::list<GenStyleInfo>>& all_styles);

void binary_to_text(const char* src_file, const char* dest_file);
void text_to_binary(const char* src_file, const char* dest_file);
