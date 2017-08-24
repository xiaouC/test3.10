#pragma once
#include <string>

extern "C" {
    void init_rules(const char* rules);
    int new_instance();
    bool insert_tile(int ID, int tile_kind, int num = 1);
    char* check_is_win_json(int ID, int join_tile_kind, int ghost_kind);
    void free_pointer(char* p);

    int draw_tile(int ID, int join_tile_kind, int ghost_kind);
}
