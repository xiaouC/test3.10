#include "mahjong.h"
#include <map>
#include <list>
#include <set>
#include <string>
#include <sstream>
#include <iostream>
#include <functional>
#include <json/json.h>

struct MJData {
    std::map<int, int> tiles;
};

int g_nNextIndex = 0;
std::map<int, MJData*> g_mapData;

struct KindGroup {
    int kind_start;
    int kind_end;
};
int g_nTotalKind = 0;
std::list<KindGroup> g_vecKindGroups;

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

struct sequence_info {
    bool is_valid;
    std::list<meld_info> sequences;

    sequence_info() { is_valid = true; }
};

bool insert_tile_need_check(std::map<int, int>& tiles, int tile_kind, int num);
void get_win_sequences_kicked_out_pair(std::map<int,int>& pp_tiles, std::list<sequence_info*>& win_sequences);
void check_kind_group(std::list<sequence_info*>& all_sequence, sequence_info* current_sequence, std::map<int,int>& pp_tiles, const KindGroup& kg, int offset);
void check_is_win_no_ghost(std::map<int, int>& tiles, std::list<std::list<meld_info>>& win_sequences);
void check_is_win_ghost(std::set<std::string>& tiles_checked, std::map<int, int>& tiles, int ghost_tile_index, int ghost_tile_num, std::list<std::list<meld_info>>& win_sequences);
std::string tiles_format(const std::map<int, int>& tiles);
void split_tile_segment(const std::map<int, int>& tiles, std::list<std::vector<int>>& tile_segments);
bool is_single_tile(const std::map<int, int>& tiles, int kind, int kind_start, int kind_end, int space);
void get_all_single_tile(const std::map<int, int>& tiles, std::list<int>& single_tiles, int space);
void get_pair_kinds(const std::vector<int>& tile_segment, std::vector<int>& pair_kinds);
bool has_single_pair();
void get_kind_start_end(int kind, int& kind_start, int& kind_end);

// A => 1
//  2 chengpai paixing : AA => 2
//  3 chengpai paixing : AAA, ABC => 3
//  5 chengpai paixing : AAABB, AABBB, AAABC, AABCD, ABCCC, ABCDD => [23] or [32]
//  5 chengpai paixing : ABBBC
//  6 chengpai paixing : AAABBB, ABCCDE, ABCDEF
//  6 chengpai paixing : AAAABC => [33]
//  6 chengpai paixing : ABBCCD, AABBCC, ABBBBC
//  8 chengpai paixing : [26], [62], [35], [53], [233], [323], [332]
//  9 chengpai paicing : [36], [63], [333]
// 11 chengpai paixing : [29], [92], [38], [83]
bool is_style_2(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds);
bool is_style_3(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds);
bool is_style_5(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds);
bool is_style_6(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds);
bool is_style_8(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds);
bool is_style_9(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds);
bool is_style_11(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds);
bool is_style_12(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds);

int get_discard_4(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);
int get_discard_7(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);
int get_discard_10(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);
int get_discard_13(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);

int get_discard_3(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);
int get_discard_6(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);
int get_discard_9(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);
int get_discard_12(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);

int get_discard_2(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);
int get_discard_5(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);
int get_discard_8(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);
int get_discard_11(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds);

struct discard_info {
    int segment_length;
    std::function<int(const std::vector<int>&, std::list<int>&)> discard_func;

    discard_info(int length, std::function<int(const std::vector<int>&, std::list<int>&)> func) : segment_length(length), discard_func(func) { }
};
std::list<discard_info> g_listDiscardFuncs1;
std::list<discard_info> g_listDiscardFuncs2;
std::list<discard_info> g_listDiscardFuncs3;

void init_rules(const char* rules) {
    Json::Reader reader;
    Json::Value root;

    //std::cout << "init rules begin ======================================" << std::endl;
    //std::cout << "rules : " << rules << std::endl;
    if (reader.parse(rules, root)) {
        g_nTotalKind = 0;
        g_vecKindGroups.clear();

        Json::Value kind_groups = root["kinds_group"];
        for (int i = 0; i < (int)kind_groups.size(); ++i) {
            Json::Value item_data = kind_groups[i];

            KindGroup kg;
            kg.kind_start = item_data["kind_start"].asInt();
            kg.kind_end = item_data["kind_end"].asInt();
            g_vecKindGroups.push_back(kg);

            g_nTotalKind += (kg.kind_end - kg.kind_start + 1);

            //std::cout << "kind_start : " << kg.kind_start << ", kind_end : " << kg.kind_end << std::endl;
        }
    }
    else {
        std::cout << "parse rules failed!";
    }
    //std::cout << "init rules end ======================================" << std::endl;

    g_listDiscardFuncs1.clear();
    g_listDiscardFuncs1.push_back(discard_info(4, get_discard_4));
    g_listDiscardFuncs1.push_back(discard_info(7, get_discard_7));
    g_listDiscardFuncs1.push_back(discard_info(10, get_discard_10));
    g_listDiscardFuncs1.push_back(discard_info(13, get_discard_13));

    g_listDiscardFuncs2.clear();
    g_listDiscardFuncs2.push_back(discard_info(3, get_discard_3));
    g_listDiscardFuncs2.push_back(discard_info(6, get_discard_6));
    g_listDiscardFuncs2.push_back(discard_info(9, get_discard_9));
    g_listDiscardFuncs2.push_back(discard_info(12, get_discard_12));

    g_listDiscardFuncs3.clear();
    g_listDiscardFuncs3.push_back(discard_info(2, get_discard_2));
    g_listDiscardFuncs3.push_back(discard_info(5, get_discard_5));
    g_listDiscardFuncs3.push_back(discard_info(8, get_discard_8));
    g_listDiscardFuncs3.push_back(discard_info(11, get_discard_11));
}

int new_instance() {
    int ID = g_nNextIndex++;

    MJData* data = new MJData;
    g_mapData[ID] = data;

    return ID;
}

MJData* get_data_by_id(int ID) {
    std::map<int, MJData*>::iterator iter = g_mapData.find(ID);
    if (iter == g_mapData.end())
        return nullptr;

    return iter->second;
}

int get_tile_num(MJData* data, int kind) {
    std::map<int, int>::iterator iter = data->tiles.find(kind);
    if (iter == data->tiles.end())
        return 0;

    return iter->second;
}

int get_tile_num(const std::map<int, int>& pp_tiles) {
    int ret_num = 0;

    for (const auto& v : pp_tiles) {
        ret_num += v.second;
    }

    return ret_num;
}

int get_tile_num(const std::map<int, int>& pp_tiles, int kind) {
    auto iter = pp_tiles.find(kind);
    if (iter == pp_tiles.end())
        return 0;

    return iter->second;
}

bool insert_tile(int ID, int tile_kind, int num) {
    std::map<int, MJData*>::iterator iter = g_mapData.find(ID);
    if (iter == g_mapData.end())
        return false;

    return insert_tile_need_check(iter->second->tiles, tile_kind, num);
}

void insert_tile(std::map<int, int>& tiles, int tile_kind, int num) {
    std::map<int, int>::iterator iter = tiles.find(tile_kind);
    if (iter != tiles.end()) {
        iter->second += num;
    }
    else {
        tiles[tile_kind] = num;
    }
}

bool insert_tile_need_check(std::map<int, int>& tiles, int tile_kind, int num) {
    std::map<int, int>::iterator iter = tiles.find(tile_kind);
    if (iter != tiles.end()) {
        if (iter->second + num < 0 || iter->second + num > 4)
            return false;

        iter->second += num;
    }
    else {
        if (num < 0 || num > 4)
            return false;

        tiles[tile_kind] = num;
    }

    return true;
}

void check_is_win_no_ghost(std::map<int, int>& tiles, std::list<std::list<meld_info>>& win_sequences) {
    for (auto& kg : g_vecKindGroups) {
        for (int i=kg.kind_start; i <= kg.kind_end; ++i) {
            if (get_tile_num(tiles, i) >= 2) {
                // a new copy
                std::map<int, int> pp_tiles = tiles;
                insert_tile(pp_tiles, i, -2);

                std::list<sequence_info*> sequence;
                get_win_sequences_kicked_out_pair(pp_tiles, sequence);

                for (auto& s : sequence) {
                    if (s->is_valid) {
                        s->sequences.insert(s->sequences.begin(), meld_info(i, i));
                        win_sequences.push_back(s->sequences);
                    }

                    delete s;
                }
            }
        }
    }
}

void get_win_sequences_kicked_out_pair(std::map<int,int>& pp_tiles, std::list<sequence_info*>& win_sequences) {
    sequence_info* si = new sequence_info();
    win_sequences.push_back(si);

    for (auto& kg : g_vecKindGroups) {
        check_kind_group(win_sequences, si, pp_tiles, kg, 0);
    }
}

void check_kind_group(std::list<sequence_info*>& all_sequence, sequence_info* current_sequence, std::map<int,int>& pp_tiles, const KindGroup& kg, int offset) {
    if (get_tile_num(pp_tiles) == 0) {
        return;
    }

    int kind = kg.kind_start + offset;
    if (kind > kg.kind_end) {
        return;
    }

    int tile_num = get_tile_num(pp_tiles, kind);
    if (tile_num == 0) {
        check_kind_group(all_sequence, current_sequence, pp_tiles, kg, offset + 1);

        return;
    }

    if (tile_num == 1 || tile_num == 2) {
        if (kind + 2 > kg.kind_end || get_tile_num(pp_tiles, kind + 1) == 0 || get_tile_num(pp_tiles, kind + 2) == 0) {
            current_sequence->is_valid = false;

            return;
        }

        insert_tile(pp_tiles, kind, -1);
        insert_tile(pp_tiles, kind + 1, -1);
        insert_tile(pp_tiles, kind + 2, -1);

        current_sequence->sequences.push_back(meld_info(kind, kind + 1, kind + 2));

        check_kind_group(all_sequence, current_sequence, pp_tiles, kg, offset);

        return;
    }

    if (tile_num == 3) {
        if (kind + 2 > kg.kind_end || get_tile_num(pp_tiles, kind + 1) == 0 || get_tile_num(pp_tiles, kind + 2) == 0) {
            insert_tile(pp_tiles, kind, -3);

            current_sequence->sequences.push_back(meld_info(kind, kind, kind));

            check_kind_group(all_sequence, current_sequence, pp_tiles, kg, offset);

            return;
        }

        std::map<int, int> new_pp_tiles = pp_tiles;
        sequence_info* new_si = new sequence_info();
        new_si->sequences = current_sequence->sequences;

        // 3 together
        insert_tile(pp_tiles, kind, -3);

        current_sequence->sequences.push_back(meld_info(kind, kind, kind));

        check_kind_group(all_sequence, current_sequence, pp_tiles, kg, offset);

        // new path
        insert_tile(new_pp_tiles, kind, -1);
        insert_tile(new_pp_tiles, kind + 1, -1);
        insert_tile(new_pp_tiles, kind + 2, -1);

        new_si->sequences.push_back(meld_info(kind, kind + 1, kind + 2));

        all_sequence.push_back(new_si);

        check_kind_group(all_sequence, new_si, new_pp_tiles, kg, offset);

        return;
    }

    // it must be 4
    if (kind + 2 > kg.kind_end || get_tile_num(pp_tiles, kind + 1) == 0 || get_tile_num(pp_tiles, kind + 2) == 0) {
        current_sequence->is_valid = false;

        return;
    }

    insert_tile(pp_tiles, kind, -1);
    insert_tile(pp_tiles, kind + 1, -1);
    insert_tile(pp_tiles, kind + 2, -1);

    current_sequence->sequences.push_back(meld_info(kind, kind + 1, kind + 2));

    check_kind_group(all_sequence, current_sequence, pp_tiles, kg, offset);
}

void check_is_win(const std::map<int, int>& tiles, int join_tile_kind, int ghost_kind, std::list<std::list<meld_info>>& win_sequences) {
    if (get_tile_num(tiles) % 3 != 1) {
        return;
    }

    std::map<int, int> temp_tiles = tiles;
    insert_tile(temp_tiles, join_tile_kind, 1);

    int ghost_tile_num = get_tile_num(temp_tiles, ghost_kind);
    if (ghost_tile_num == 0) {
        check_is_win_no_ghost(temp_tiles, win_sequences);

        return;
    }

    insert_tile(temp_tiles, ghost_kind, -ghost_tile_num);

    std::set<std::string> tiles_checked;
    check_is_win_ghost(tiles_checked, temp_tiles, 0, ghost_tile_num, win_sequences);
}

void check_is_win_ghost(std::set<std::string>& tiles_checked, std::map<int, int>& tiles, int ghost_tile_index, int ghost_tile_num, std::list<std::list<meld_info>>& win_sequences) {
    if (ghost_tile_index >= ghost_tile_num) {
        std::string tf = tiles_format(tiles);
        if (tiles_checked.find(tf) == tiles_checked.end()) {
            tiles_checked.insert(tf);

            check_is_win_no_ghost(tiles, win_sequences);
        }

        return;
    }

    for (auto& kg : g_vecKindGroups) {
        for (int i=kg.kind_start; i <= kg.kind_end; ++i) {
            std::map<int, int> temp_tiles = tiles;
            if (insert_tile_need_check(temp_tiles, i, 1)) {
                check_is_win_ghost(tiles_checked, temp_tiles, ghost_tile_index + 1, ghost_tile_num, win_sequences);
            }
        }
    }
}

std::string tiles_format(const std::map<int, int>& tiles) {
    char szBuf[g_nTotalKind+1];

    int index = 0;
    for (auto& kg : g_vecKindGroups) {
        for (int i=kg.kind_start; i <= kg.kind_end; ++i) {
            szBuf[index++] = '0' + get_tile_num(tiles, i);
        }
    }
    szBuf[index] = 0;

    return szBuf;
}

char* check_is_win_json(int ID, int join_tile_kind, int ghost_kind) {
    MJData* data = get_data_by_id(ID);

    std::list<std::list<meld_info>> win_sequences;
    check_is_win(data->tiles, join_tile_kind, ghost_kind, win_sequences);

    Json::Value root;
    for (auto& v : win_sequences) {
        std::stringstream stream;
        for (auto& s : v) {
            stream << s.x << "," << s.y << ",";
            if (s.z != -1) {
                stream << s.z << ",";
            }
        }

        std::string item_data = stream.str();
        item_data.erase(item_data.begin() + item_data.length() - 1);

        Json::Value item;
        item["sequence"] = item_data;

        root.append(item);
    }

    std::string json_data = root.toStyledString();
    char* ret_data = (char*)malloc(json_data.length()+1);
    sprintf(ret_data, "%s", json_data.c_str());
    ret_data[json_data.length()] = 0;

    return ret_data;
}

void free_pointer(char* p) {
    // std::cout << "free_pointer : " << p << std::endl;
    free(p);
}

int draw_tile(int ID, int join_tile_kind, int ghost_kind) {
    MJData* data = get_data_by_id(ID);
    if (data == nullptr) {
        return -1;
    }

    std::list<std::list<meld_info>> win_sequences;
    check_is_win(data->tiles, join_tile_kind, ghost_kind, win_sequences);

    if (win_sequences.empty()) {
        insert_tile(ID, join_tile_kind, 1);

        std::list<int> all_single_tiles;

        // 去除间隔2个空位的不连续单牌，从两头向中间排查
        get_all_single_tile(data->tiles, all_single_tiles, 2);
        if (!all_single_tiles.empty()) {
            return *(all_single_tiles.begin());
        }

        // 去除间隔1个空位的不连续单牌，从两头向中间排查
        get_all_single_tile(data->tiles, all_single_tiles, 1);
        if (!all_single_tiles.empty()) {
            return *(all_single_tiles.begin());
        }

        std::list<std::vector<int>> tile_segments;
        split_tile_segment(data->tiles, tile_segments);

        std::list<int> all_pair_kinds;
        for (auto& v : tile_segments) {
            std::cout << "length : " << v.size() << std::endl;
            if (v.size() == 2 && v[0] == v[1]) {
                all_pair_kinds.push_back(v[0]);
            }
        }

        // 去除连续牌数为4、7、10、13中的一张牌，让牌型成为无将胡牌型。如2344条，去除4条
        for (auto& discard_info : g_listDiscardFuncs1) {
            for (auto& v : tile_segments) {
                if ((int)v.size() == discard_info.segment_length) {
                    int kind = discard_info.discard_func(v, all_pair_kinds);
                    if (kind != -1) {
                        return kind;
                    }
                }
            }
        }

        // 去除连续牌数为3、6、9、12中的一张牌，有将则打一吃二成为无将听牌型（如233条，去除3条）；无将则打一成将成为有将胡牌型（如233条，去除2条）
        for (auto& discard_info : g_listDiscardFuncs2) {
            for (auto& v : tile_segments) {
                if ((int)v.size() == discard_info.segment_length) {
                    int kind = discard_info.discard_func(v, all_pair_kinds);
                    if (kind != -1) {
                        return kind;
                    }
                }
            }
        }

        // 去除连续牌数位2、5、8、11中的一张牌，让牌型成为有将听牌型。如23445条，去除5条。
        for (auto& discard_info : g_listDiscardFuncs3) {
            for (auto& v : tile_segments) {
                if ((int)v.size() == discard_info.segment_length) {
                    int kind = discard_info.discard_func(v, all_pair_kinds);
                    if (kind != -1) {
                        return kind;
                    }
                }
            }
        }

        // 从将牌中打出一张牌。
        return *all_pair_kinds.begin();
    }

    return -1;
}

void split_tile_segment(const std::map<int, int>& tiles, std::list<std::vector<int>>& tile_segments) {
    for (auto& v : tiles) {
        std::cout << "kind " << v.first << " : " << v.second << std::endl;
    }

    std::vector<int> cur_segment;
    for (auto& kg : g_vecKindGroups) {
        if (!cur_segment.empty()) {
            tile_segments.push_back(cur_segment);
            cur_segment.clear();
        }

        for (int i=kg.kind_start; i <= kg.kind_end; ++i) {
            int num = get_tile_num(tiles, i);
            if (num == 0 && !cur_segment.empty()) {
                tile_segments.push_back(cur_segment);
                cur_segment.clear();
            }

            cur_segment.insert(cur_segment.begin() + cur_segment.size(), num, i);
        }
    }

    if (!cur_segment.empty()) {
        tile_segments.push_back(cur_segment);
    }
}

bool is_single_tile(const std::map<int, int>& tiles, int kind, int kind_start, int kind_end, int space) {
    if (get_tile_num(tiles, kind) != 1) {
        return false;
    }

    auto is_kind_none = [&] (int ck) {
        if (ck >= kind_start && ck <= kind_end) {
            return (get_tile_num(tiles, ck) == 0);
        }

        return true;
    };

    for (int i=1; i <= space; ++i) {
        if (!is_kind_none(kind - i)) {
            return false;
        }

        if (!is_kind_none(kind + i)) {
            return false;
        }
    }

    return true;
}

void get_all_single_tile(const std::map<int, int>& tiles, std::list<int>& single_tiles, int space) {
    std::list<std::tuple<int, int>> temp_kg;
    for (auto& kg : g_vecKindGroups) {
        if (kg.kind_start == kg.kind_end) {
            if (get_tile_num(tiles, kg.kind_start) == 1) {
                single_tiles.push_back(kg.kind_start);
            }
        }
        else {
            temp_kg.push_back(std::make_tuple(kg.kind_start, kg.kind_end));
        }
    }

    for (int i=0; i < 4; ++i) {
        for (auto& kg : temp_kg) {
            int kind_start = std::get<0>(kg);
            int kind_end = std::get<1>(kg);

            int kind_1 = kind_start + i;
            int kind_2 = kind_end - i;

            if (is_single_tile(tiles, kind_1, kind_start, kind_end, space)) {
                single_tiles.push_back(kind_1);
            }

            if (is_single_tile(tiles, kind_2, kind_start, kind_end, space)) {
                single_tiles.push_back(kind_2);
            }
        }
    }

    for (auto& kg : temp_kg) {
        int kind_start = std::get<0>(kg);
        int kind_end = std::get<1>(kg);

        int kind = kind_start + 4;

        if (is_single_tile(tiles, kind, kind_start, kind_end, space)) {
            single_tiles.push_back(kind);
        }
    }
}

int get_discard_4(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    // AABC => return A
    if (tile_segment[0] == tile_segment[1] &&
        tile_segment[2] == tile_segment[1] + 1 &&
        tile_segment[3] == tile_segment[2] + 1) {
        return tile_segment[0];
    }

    // ABBC => return B
    if (tile_segment[1] == tile_segment[0] + 1 &&
        tile_segment[2] == tile_segment[1] &&
        tile_segment[3] == tile_segment[2] + 1) {
        return tile_segment[1];
    }

    // ABCC => return C
    if (tile_segment[1] == tile_segment[0] + 1 &&
        tile_segment[2] == tile_segment[1] + 1 &&
        tile_segment[3] == tile_segment[2]) {
        return tile_segment[2];
    }

    // pair
    if (tile_segment[1] == tile_segment[0]) {
        all_pair_kinds.push_back(tile_segment[0]);
    }

    if (tile_segment[3] == tile_segment[2]) {
        all_pair_kinds.push_back(tile_segment[3]);
    }

    if (tile_segment[1] == tile_segment[2]) {
        if (tile_segment[0] == tile_segment[1] || tile_segment[3] == tile_segment[2]) {
            all_pair_kinds.push_back(tile_segment[0]);
        }
    }

    return -1;
}

int get_discard_7(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    for (int i=0; i < 7; ++i) {
        std::vector<int> temp_segment = tile_segment;

        int kind = temp_segment[i];
        temp_segment.erase(temp_segment.begin() + i);
        if (is_style_6(temp_segment, 0, &all_pair_kinds))
            return kind;
    }

    return -1;
}

int get_discard_10(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    for (int i=0; i < 10; ++i) {
        std::vector<int> temp_segment = tile_segment;

        int kind = temp_segment[i];
        temp_segment.erase(temp_segment.begin() + i);
        if (is_style_9(temp_segment, 0, &all_pair_kinds))
            return kind;
    }

    return -1;
}

int get_discard_13(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    for (int i=0; i < 13; ++i) {
        std::vector<int> temp_segment = tile_segment;

        int kind = temp_segment[i];
        temp_segment.erase(temp_segment.begin() + i);
        if (is_style_12(temp_segment, 0, &all_pair_kinds))
            return kind;
    }

    return -1;
}

int get_discard_3(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    if (is_style_3(tile_segment, 0, &all_pair_kinds))
        return -1;

    if (!all_pair_kinds.empty()) {
        return tile_segment[1];
    }

    all_pair_kinds.push_back(tile_segment[1]);
    return tile_segment[0] == tile_segment[1] ? tile_segment[2] : tile_segment[0];
}

int get_discard_6(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    if (is_style_6(tile_segment, 0, &all_pair_kinds))
        return -1;

    for (int i=0; i < 6; ++i) {
        std::vector<int> temp_segment = tile_segment;

        int kind = temp_segment[i];
        temp_segment.erase(temp_segment.begin() + i);
        if (is_style_5(temp_segment, 0, &all_pair_kinds))
            return kind;
    }

    return -1;
}

int get_discard_9(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    if (is_style_9(tile_segment, 0, &all_pair_kinds))
        return -1;

    for (int i=0; i < 9; ++i) {
        std::vector<int> temp_segment = tile_segment;

        int kind = temp_segment[i];
        temp_segment.erase(temp_segment.begin() + i);
        if (is_style_8(temp_segment, 0, &all_pair_kinds))
            return kind;
    }

    return -1;
}

int get_discard_12(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    if (is_style_12(tile_segment, 0, &all_pair_kinds))
        return -1;

    for (int i=0; i < 12; ++i) {
        std::vector<int> temp_segment = tile_segment;

        int kind = temp_segment[i];
        temp_segment.erase(temp_segment.begin() + i);
        if (is_style_11(temp_segment, 0, &all_pair_kinds))
            return kind;
    }

    return -1;
}

int get_discard_2(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    if (tile_segment[0] == tile_segment[1]) {
        all_pair_kinds.push_back(tile_segment[0]);

        return -1;
    }

    int kind_start = -1;
    int kind_end = -1;
    get_kind_start_end(tile_segment[0], kind_start, kind_end);

    return (tile_segment[0] - kind_start) > (kind_end - tile_segment[1]) ? tile_segment[1] : tile_segment[0];
}

int get_discard_5(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    if (is_style_5(tile_segment, 0, &all_pair_kinds))
        return -1;

    // ABBCD => return A
    if (tile_segment[1] == tile_segment[0] + 1 &&
        tile_segment[2] == tile_segment[1] &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] + 1)
    {
        all_pair_kinds.push_back(tile_segment[1]);

        return tile_segment[0];
    }

    // ABCCD => return D
    if (tile_segment[1] == tile_segment[0] + 1 &&
        tile_segment[2] == tile_segment[1] + 1 &&
        tile_segment[3] == tile_segment[2] &&
        tile_segment[4] == tile_segment[3] + 1)
    {
        all_pair_kinds.push_back(tile_segment[2]);

        return tile_segment[4];
    }

    return -1;
}

int get_discard_8(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    if (is_style_8(tile_segment, 0, &all_pair_kinds))
        return -1;

    // ABBCDEFG => return A
    if (tile_segment[1] == tile_segment[0] + 1 &&
        tile_segment[2] == tile_segment[1] &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] + 1 &&
        tile_segment[5] == tile_segment[4] + 1 &&
        tile_segment[6] == tile_segment[5] + 1 &&
        tile_segment[7] == tile_segment[6] + 1)
    {
        all_pair_kinds.push_back(tile_segment[1]);

        return tile_segment[0];
    }

    // ABCDEFFG => return G
    if (tile_segment[1] == tile_segment[0] + 1 &&
        tile_segment[2] == tile_segment[1] + 1 &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] + 1 &&
        tile_segment[5] == tile_segment[4] + 1 &&
        tile_segment[6] == tile_segment[5] &&
        tile_segment[7] == tile_segment[6] + 1)
    {
        all_pair_kinds.push_back(tile_segment[5]);

        return tile_segment[7];
    }

    // AABCDEEF => return E
    if (tile_segment[1] == tile_segment[0] &&
        tile_segment[2] == tile_segment[1] + 1 &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] + 1 &&
        tile_segment[5] == tile_segment[4] + 1 &&
        tile_segment[6] == tile_segment[5] &&
        tile_segment[7] == tile_segment[6] + 1)
    {
        all_pair_kinds.push_back(tile_segment[0]);

        return tile_segment[6];
    }

    // ABBCDEFF => return B
    if (tile_segment[1] == tile_segment[0] + 1 &&
        tile_segment[2] == tile_segment[1] &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] + 1 &&
        tile_segment[5] == tile_segment[4] + 1 &&
        tile_segment[6] == tile_segment[5] + 1 &&
        tile_segment[7] == tile_segment[6])
    {
        all_pair_kinds.push_back(tile_segment[7]);

        return tile_segment[1];
    }

    // ABBCDEEF => A,F
    if (tile_segment[1] == tile_segment[0] + 1 &&
        tile_segment[2] == tile_segment[1] &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] + 1 &&
        tile_segment[5] == tile_segment[4] + 1 &&
        tile_segment[6] == tile_segment[5] &&
        tile_segment[7] == tile_segment[6] + 1)
    {
        // TODO:
        if (rand() % 2 == 0) {
            all_pair_kinds.push_back(tile_segment[1]);

            return tile_segment[0];
        }
        else {
            all_pair_kinds.push_back(tile_segment[6]);

            return tile_segment[7];
        }
    }

    // ABBCDEEE => A
    if (tile_segment[1] == tile_segment[0] + 1 &&
        tile_segment[2] == tile_segment[1] &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] + 1 &&
        tile_segment[5] == tile_segment[4] + 1 &&
        tile_segment[6] == tile_segment[5] &&
        tile_segment[7] == tile_segment[6])
    {
        all_pair_kinds.push_back(tile_segment[7]);

        return tile_segment[0];
    }

    // AAABCDDE => E
    if (tile_segment[1] == tile_segment[0] &&
        tile_segment[2] == tile_segment[1] &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] + 1 &&
        tile_segment[5] == tile_segment[4] + 1 &&
        tile_segment[6] == tile_segment[5] &&
        tile_segment[7] == tile_segment[6] + 1)
    {
        all_pair_kinds.push_back(tile_segment[0]);

        return tile_segment[7];
    }

    // AABCCDDD => A
    if (tile_segment[1] == tile_segment[0] &&
        tile_segment[2] == tile_segment[1] + 1 &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] &&
        tile_segment[5] == tile_segment[4] + 1 &&
        tile_segment[6] == tile_segment[5] &&
        tile_segment[7] == tile_segment[6])
    {
        return tile_segment[0];
    }

    // AAABBCDD => D
    if (tile_segment[1] == tile_segment[0] &&
        tile_segment[2] == tile_segment[1] &&
        tile_segment[3] == tile_segment[2] + 1 &&
        tile_segment[4] == tile_segment[3] &&
        tile_segment[5] == tile_segment[4] + 1 &&
        tile_segment[6] == tile_segment[5] + 1 &&
        tile_segment[7] == tile_segment[6])
    {
        return tile_segment[7];
    }

    return -1;
}

int get_discard_11(const std::vector<int>& tile_segment, std::list<int>& all_pair_kinds) {
    if (is_style_11(tile_segment, 0, &all_pair_kinds))
        return -1;

    if (is_style_8(tile_segment, 0, &all_pair_kinds)) {
        return tile_segment[9];
    }

    if (is_style_8(tile_segment, 1, &all_pair_kinds)) {
        return tile_segment[0];
    }

    if (is_style_8(tile_segment, 2, &all_pair_kinds)) {
        return tile_segment[10];
    }

    if (is_style_8(tile_segment, 3, &all_pair_kinds)) {
        return tile_segment[1];
    }

    return -1;
}

void get_pair_kinds(const std::vector<int>& tile_segment, std::vector<int>& pair_kinds) {
    int index = 1;
    int cur_kind = tile_segment[0];
    int num = 1;

    while (index < (int)tile_segment.size()) {
        if (cur_kind == tile_segment[index]) {
            ++num;
        }
        else {
            if (num == 2) {
                pair_kinds.push_back(cur_kind);
            }

            cur_kind = tile_segment[index];
            num = 1;
        }

        ++index;
    }
}

// 2 chengpai paixing : AA => 2
bool is_style_2(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds) {
    if (tile_segment[pos_start] == tile_segment[pos_start+1]) {
        if (all_pair_kinds != nullptr) {
            all_pair_kinds->push_back(tile_segment[pos_start]);
        }

        return true;
    }

    return false;
}

// 3 chengpai paixing : AAA, ABC => 3
bool is_style_3(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds) {
    if (tile_segment[pos_start] == tile_segment[pos_start+1] && tile_segment[pos_start] == tile_segment[pos_start+2])
        return true;

    if (tile_segment[pos_start] + 1 == tile_segment[pos_start+1] && tile_segment[pos_start+1] + 1 == tile_segment[pos_start+2])
        return true;

    return false;
}

// 5 chengpai paixing : AAABB, AABBB, AAABC, AABCD, ABCCC, ABCDD => [23] or [32]
// 5 chengpai paixing : ABBBC
bool is_style_5(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds) {
    // [23]
    if (is_style_2(tile_segment, pos_start, nullptr) && is_style_3(tile_segment, pos_start + 2, nullptr)) {
        if (all_pair_kinds != nullptr) {
            all_pair_kinds->push_back(tile_segment[0]);
        }

        return true;
    }

    // [32]
    if (is_style_3(tile_segment, pos_start, nullptr) && is_style_2(tile_segment, pos_start + 3, nullptr)) {
        if (all_pair_kinds != nullptr) {
            all_pair_kinds->push_back(tile_segment[4]);
        }

        return true;
    }

    // ABBBC
    if (tile_segment[pos_start+1] == tile_segment[pos_start+0] + 1 &&
        tile_segment[pos_start+1] == tile_segment[pos_start+2] &&
        tile_segment[pos_start+2] == tile_segment[pos_start+3] &&
        tile_segment[pos_start+4] == tile_segment[pos_start+3] + 1) {
        if (all_pair_kinds != nullptr) {
            all_pair_kinds->push_back(tile_segment[1]);
        }

        return true;
    }

    return false;
}

// 6 chengpai paixing : ABBCCD, AABBCC, ABBBBC
bool is_style_6(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds) {
    // [33]
    if (is_style_3(tile_segment, pos_start, nullptr) && is_style_3(tile_segment, pos_start + 3, nullptr))
        return true;

    // ABBCCD
    if (tile_segment[pos_start+1] == tile_segment[pos_start+0] + 1 &&
        tile_segment[pos_start+2] == tile_segment[pos_start+1] &&
        tile_segment[pos_start+3] == tile_segment[pos_start+2] + 1 &&
        tile_segment[pos_start+4] == tile_segment[pos_start+3] &&
        tile_segment[pos_start+5] == tile_segment[pos_start+4] + 1)
        return true;

    // AABBCC
    if (tile_segment[pos_start+1] == tile_segment[pos_start+0] &&
        tile_segment[pos_start+2] == tile_segment[pos_start+1] + 1 &&
        tile_segment[pos_start+3] == tile_segment[pos_start+2] &&
        tile_segment[pos_start+4] == tile_segment[pos_start+3] + 1 &&
        tile_segment[pos_start+5] == tile_segment[pos_start+4])
        return true;

    // ABBBBC
    if (tile_segment[pos_start+1] == tile_segment[pos_start+0] + 1 &&
        tile_segment[pos_start+2] == tile_segment[pos_start+1] &&
        tile_segment[pos_start+3] == tile_segment[pos_start+2] &&
        tile_segment[pos_start+4] == tile_segment[pos_start+3] &&
        tile_segment[pos_start+5] == tile_segment[pos_start+4] + 1)
        return true;

    return false;
}

// 8 chengpai paixing : [26], [62], [35], [53]
bool is_style_8(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds) {
    // [26]
    if (is_style_2(tile_segment, pos_start, nullptr) && is_style_6(tile_segment, pos_start + 2, nullptr)) {
        if (all_pair_kinds != nullptr) {
            all_pair_kinds->push_back(tile_segment[0]);
        }

        return true;
    }

    // [62]
    if (is_style_6(tile_segment, pos_start, nullptr) && is_style_2(tile_segment, pos_start + 6, nullptr)) {
        if (all_pair_kinds != nullptr) {
            all_pair_kinds->push_back(tile_segment[7]);
        }

        return true;
    }

    // [35]
    if (is_style_3(tile_segment, pos_start, nullptr) && is_style_5(tile_segment, pos_start + 3, all_pair_kinds)) {
        return true;
    }

    // [53]
    if (is_style_5(tile_segment, pos_start, all_pair_kinds) && is_style_3(tile_segment, pos_start + 5, nullptr)) {
        return true;
    }

    return false;
}

//  9 chengpai paicing : [36], [63]
bool is_style_9(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds) {
    // [36]
    if (is_style_3(tile_segment, pos_start, nullptr) && is_style_6(tile_segment, pos_start + 3, nullptr)) {
        return true;
    }

    // [63]
    if (is_style_6(tile_segment, pos_start, nullptr) && is_style_3(tile_segment, pos_start + 6, nullptr))
        return true;

    return false;
}

// 11 chengpai paixing : [29], [92], [38], [83]
bool is_style_11(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds) {
    // [29]
    if (is_style_2(tile_segment, pos_start, nullptr) && is_style_9(tile_segment, pos_start + 2, nullptr)) {
        if (all_pair_kinds != nullptr) {
            all_pair_kinds->push_back(tile_segment[0]);
        }

        return true;
    }

    // [92]
    if (is_style_9(tile_segment, pos_start, nullptr) && is_style_2(tile_segment, pos_start + 9, nullptr)) {
        if (all_pair_kinds != nullptr) {
            all_pair_kinds->push_back(tile_segment[10]);
        }

        return true;
    }

    // [38]
    if (is_style_3(tile_segment, pos_start, nullptr) && is_style_8(tile_segment, pos_start + 3, all_pair_kinds)) {
        return true;
    }

    // [83]
    if (is_style_8(tile_segment, pos_start, all_pair_kinds) && is_style_3(tile_segment, pos_start + 8, nullptr)) {
        return true;
    }

    return false;
}

// [39], [93], [66], [255], [525], [552]
bool is_style_12(const std::vector<int>& tile_segment, int pos_start, std::list<int>* all_pair_kinds) {
    // [39]
    if (is_style_3(tile_segment, pos_start, nullptr) && is_style_9(tile_segment, pos_start + 3, nullptr))
        return true;

    // [93]
    if (is_style_9(tile_segment, pos_start, nullptr) && is_style_3(tile_segment, pos_start + 9, nullptr))
        return true;

    // [66]
    if (is_style_6(tile_segment, pos_start, nullptr) && is_style_6(tile_segment, pos_start + 6, nullptr))
        return true;

    // [255]
    if (is_style_2(tile_segment, pos_start, all_pair_kinds) && is_style_5(tile_segment, pos_start + 2, all_pair_kinds) && is_style_5(tile_segment, pos_start + 7, all_pair_kinds)) {
        return true;
    }

    if (is_style_5(tile_segment, pos_start, all_pair_kinds)) {
        // [525]
        if (is_style_2(tile_segment, pos_start + 5, all_pair_kinds) && is_style_5(tile_segment, pos_start + 7, all_pair_kinds)) {
            return true;
        }

        // [552]
        if (is_style_5(tile_segment, pos_start + 5, all_pair_kinds) && is_style_2(tile_segment, pos_start + 10, all_pair_kinds)) {
            return true;
        }
    }

    return false;
}

void get_kind_start_end(int kind, int& kind_start, int& kind_end) {
    for (auto& kg : g_vecKindGroups) {
        if (kind >= kg.kind_start && kind <= kg.kind_end) {
            kind_start = kg.kind_start;
            kind_end = kg.kind_end;

            return;
        }
    }
}
