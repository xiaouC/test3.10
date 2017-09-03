#include "common.h"
#include <stdlib.h>

void string_split(const std::string& src, const std::string& s, std::vector<std::string>& result) {
    result.clear();

    std::string::size_type pos1 = 0;
    std::string::size_type pos2 = src.find(s);

    while (pos2 != std::string::npos) {
		result.push_back(src.substr(pos1, pos2 - pos1));

        pos1 = pos2 + s.size();
        pos2 = src.find(s, pos1);
    }

    if (pos1 != src.length()) {
        result.push_back(src.substr(pos1));
    }
}

int cmp(const void * a, const void * b) {
    return (*(int*)b - *(int*)a);   // b > a 返回正值  
} 

long long sort_sequence(long long sequence) {
    int num[5] = {0};

    int index = 0;
    while (sequence > 0) {
        num[index++] = sequence % 1000;
        // sequence /= 1000;
        sequence *= 0.001;
    }

    qsort(num, 5, sizeof(int), &cmp);

    long long new_sequence = num[4] * 1000000000000LL + num[3] * 1000000000LL + num[2] * 1000000LL + num[1] * 1000LL + num[0];
    //long long new_sequence = 0;
    //for (int i=4; i >= 0; --i) {
    //    if (num[i] > 0) {
    //        new_sequence = new_sequence * 1000 + num[i];
    //    }
    //}

    return new_sequence;
}

std::vector<int> split_sequence(long long sequence) {
    int num[5] = {0};

    int index = 0;
    while (sequence > 0) {
        num[index++] = sequence % 1000;
        //sequence /= 1000;
        sequence *= 0.001;
    }

    std::vector<int> ret;
    for (int i=0; i < 5; ++i) {
        if (num[i] > 0) {
            ret.push_back(num[i]);
        }
    }

    return ret;
}

/* itoa:  convert n to characters in s */
char* itoa(int n, char s[]) {
    int i, sign;

    if ((sign = n) < 0)  /* record sign */
        n = -n;          /* make n positive */
    i = 0;
    do {       /* generate digits in reverse order */
        s[i++] = n % 10 + '0';   /* get next digit */
    } while ((n /= 10) > 0);     /* delete it */
    if (sign < 0)
        s[i++] = '-';
    s[i] = '\0';
    reverse(s);

    return s;
} 

/* reverse:  reverse string s in place */
void reverse(char s[]) {
    int i, j;
    char c;

    for (i = 0, j = strlen(s)-1; i<j; i++, j--) {
        c = s[i];
        s[i] = s[j];
        s[j] = c;
    }
} 

bool is_the_same_sequence(const std::list<int>& s1, const std::list<int>& s2) {
    if (s1.size() != s2.size()) {
        return false;
    }

    std::list<int>::const_iterator iter1 = s1.begin();
    std::list<int>::const_iterator iter2 = s2.begin();
    for (; iter1 != s1.end(); ++iter1, ++iter2) {
        if ((*iter1) != (*iter2)) {
            return false;
        }
    }

    return true;
}

/*
void save_new_data_binary(const char* filename, const std::unordered_map< int, std::list<GenStyleInfo> >& all_styles) {
    FILE* fp = fopen(filename, "wb");

    // 
    int all_styles_length = (int)all_styles.size();
    fwrite(&all_styles_length, sizeof(int), 1, fp);

    for (const auto& iter_1 : all_styles) {
        fwrite(&iter_1.first, sizeof(int), 1, fp);        // win style

        int si_length = (int)iter_1.second.size();
        fwrite(&si_length, sizeof(int), 1, fp);

        for (const auto& iter_2 : iter_1.second) {
            int ghost_num = iter_2.ghost_num;
            bool has_eyes = iter_2.has_eyes;
            std::list<long long> card_styles = iter_2.card_styles;

            fwrite(&ghost_num, sizeof(int), 1, fp);
            fwrite(&has_eyes, sizeof(bool), 1, fp);

            int all_sequence_length = (int)iter_2.card_styles.size();   // 鬼牌+是否带眼下，所有的胡牌序列
            fwrite(&all_sequence_length, sizeof(int), 1, fp);

            for (const auto& iter_3 : card_styles) {
                std::vector<int> one_sequence = split_sequence(iter_3);

                int all_meld_length = (int)one_sequence.size();           // 一个序列有多个 顺子、刻子 组成
                fwrite(&all_meld_length, sizeof(int), 1, fp);

                for (const auto& iter_4 : one_sequence) {
                    int id_1 = iter_4 % 10;
                    int id_3 = iter_4 / 100;
                    int id_2 = (iter_4 - id_3 * 100) / 10;

                    // 一个刻子/顺子/眼
                    if (id_3 == 0) {   // 这代表只有两个 id 是有效的
                        int count = 2;
                        fwrite(&count, sizeof(int), 1, fp);
                        fwrite(&id_2, sizeof(int), 1, fp);
                        fwrite(&id_1, sizeof(int), 1, fp);
                    } else {
                        int count = 3;
                        fwrite(&count, sizeof(int), 1, fp);
                        fwrite(&id_3, sizeof(int), 1, fp);
                        fwrite(&id_2, sizeof(int), 1, fp);
                        fwrite(&id_1, sizeof(int), 1, fp);
                    }
                }
            }
        }
    }
    fclose(fp);

    printf("saved!");
}

void load_new_data_binary(const char* filename, std::unordered_map<int, std::vector<StyleInfo>>& all_styles) {
    FILE* fp = fopen(filename, "rb");

    int all_styles_length = 0;
    fread(&all_styles_length, sizeof(int), 1, fp);

    for (int i=0; i < all_styles_length; ++i) {
        int win_style = 0;
        fread(&win_style, sizeof(int), 1, fp);

        int si_length = 0;
        fread(&si_length, sizeof(int), 1, fp);

        std::vector<StyleInfo> style_infos;
        style_infos.resize(si_length);

        for (int j=0; j < si_length; ++j) {
            fread(&style_infos[j].ghost_num, sizeof(int), 1, fp);
            fread(&style_infos[j].has_eyes, sizeof(bool), 1, fp);

            int all_sequence_length = 0;
            fread(&all_styles_length, sizeof(int), 1, fp);
            style_infos[j].sequences.resize(all_sequence_length);

            for (int k=0; k < all_sequence_length; ++k) {
                // 一个序列有多个顺子
                int all_meld_length = 0;
                fread(&all_meld_length, sizeof(int), 1, fp);
                style_infos[j].sequences[k].resize(all_meld_length);

                for (int m=0; m < all_meld_length; ++m) {
                    // 一个顺子有多张牌
                    int count = 0;
                    fread(&count, sizeof(int), 1, fp);
                    style_infos[j].sequences[k][m].resize(count);

                    // 不是 2，就是 3
                    fread(&style_infos[j].sequences[k][m][0], sizeof(int), 1, fp);
                    fread(&style_infos[j].sequences[k][m][1], sizeof(int), 1, fp);
                    if (count == 3) {
                        fread(&style_infos[j].sequences[k][m][2], sizeof(int), 1, fp);
                    }
                }
            }
        }

        // 
        all_styles[win_style] = style_infos;
    }
}
*/

void save_data_text_no_eyes(const char* filename, const std::unordered_map<int, std::vector<long long>> all_styles[]) {
    FILE* fp = fopen(filename, "w");
    for (int i=0; i < 9; ++i) {
        for (const auto& iter_1 : all_styles[i]) {
            for (const auto& iter_2 : iter_1.second) {
                fprintf(fp, "%d|false|%d|%lld\n", iter_1.first, i, iter_2);
            }
        }
    }
    fclose(fp);

    printf("saved!\n");
}

void save_data_text_with_eyes(const char* filename, const std::unordered_map<int, std::vector<long long>> all_styles[]) {
    FILE* fp = fopen(filename, "w");
    for (int i=0; i < 9; ++i) {
        for (const auto& iter_1 : all_styles[i]) {
            for (const auto& iter_2 : iter_1.second) {
                fprintf(fp, "%d|true|%d|%lld\n", iter_1.first, i, iter_2);
            }
        }
    }
    fclose(fp);

    printf("saved!\n");
}

void save_data_text_wtt_no_eyes(const char* filename, const std::unordered_map<int, std::unordered_set<long long>> all_styles[]) {
    FILE* fp = fopen(filename, "w");
    for (int i=0; i < 9; ++i) {
        for (const auto& iter_1 : all_styles[i]) {
            for (const auto& iter_2 : iter_1.second) {
                fprintf(fp, "%d|false|%d|%lld\n", iter_1.first, i, iter_2);
            }
        }
    }
    fclose(fp);

    printf("saved!\n");
}

void save_data_text_wtt_with_eyes(const char* filename, const std::unordered_map<int, std::unordered_set<long long>> all_styles[]) {
    FILE* fp = fopen(filename, "w");
    for (int i=0; i < 9; ++i) {
        for (const auto& iter_1 : all_styles[i]) {
            for (const auto& iter_2 : iter_1.second) {
                fprintf(fp, "%d|true|%d|%lld\n", iter_1.first, i, iter_2);
            }
        }
    }
    fclose(fp);

    printf("saved!\n");
}

/*
void load_new_data_text(const char* filename, std::unordered_map<int, std::list<GenStyleInfo>>& all_styles) {
    char szBuf[1024];

    FILE* fp = fopen(filename, "r");
    while (!feof(fp)) {
        fgets(szBuf, 1024, fp);
        std::vector<std::string> result;
        string_split(szBuf, "|", result);
        int style = atoi(result[0].c_str());
        bool has_eyes = (result[1].compare("true") == 0);
        int ghost_num = atoi(result[2].c_str());
        long long sequence = std::stoll(result[3]);

        // 
        auto iter = all_styles.find(style);
        if (iter == all_styles.end()) {
            std::list<GenStyleInfo> style_infos;
            style_infos.push_back(GenStyleInfo(ghost_num, has_eyes, sequence));

            all_styles[style] = style_infos;
        } else {
            bool flag = false;
            for (auto& iter_1 : iter->second) {
                int num = iter_1.ghost_num;
                bool eyes = iter_1.has_eyes;
                if (num == ghost_num && eyes == has_eyes) {
                    iter_1.card_styles.push_back(sequence);

                    flag = true;
                    break;
                }
            }
            if (!flag) {
                iter->second.push_back(GenStyleInfo(ghost_num, has_eyes, sequence));
            }
        }
    } 
    fclose(fp);
}
*/

void binary_to_text(const char* src_file, const char* dest_file) {
    //std::unordered_map<int, std::vector<StyleInfo>> all_styles;
    //load_new_data_binary(src_file, all_styles);
}

void text_to_binary(const char* src_file, const char* dest_file) {
    //std::unordered_map<int, std::list<GenStyleInfo>> all_styles;
    //load_new_data_text(src_file, all_styles);
    //save_new_data_binary(dest_file, all_styles);
}
