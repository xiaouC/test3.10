#include <iostream>  
#include <fstream>  
#include <string>  
#include <unistd.h>  
#include <ctime>  
#include <cstdlib>  
#include <thread> 
#include <string.h>
#include <map>
#include <list>
#include <sstream>
#include <time.h>
#include <stdlib.h>
#include <limits.h>
#include <cmath>

#include "mahjong.h"

std::string intcat_1(const std::list<int>& listInt) {
    std::stringstream stream;

    for (const auto& v : listInt) {
        stream << v;
    }

    return stream.str();
}

/*
std::string intcat_2(const std::list<int>& listInt) {
    char szBuf[1024] = { 0 };

    for (const auto& v : listInt) {
        sprintf(szBuf, "%s%d", szBuf, v);
    }

    return std::string(szBuf);
}
*/

std::string intcat_3(const std::list<int>& listInt) {
    std::stringstream stream;

    unsigned long long tt = 0;
    int index = 0;
    for (const auto& v : listInt) {
        tt = tt * 10 + v;
        if (++index >= 19) {
            stream << tt;
            tt = 0;
            index = 0;
        }
    }

    if (tt != 0) {
        stream << tt;
    }

    return stream.str();
}

std::string intcat_4(const std::list<int>& listInt) {
    char szBuf[listInt.size()+1];
    int pos = 0;
    szBuf[listInt.size()] = 0;
    for (auto& v : listInt) {
        szBuf[pos++] = '0' + v;
    }

    return szBuf;
}

int main(int argc, char* argv[])
{
    /*
    const char* json_rules = "{\"kinds_group\": [{\"kind_end\": 8, \"kind_start\": 0}, {\"kind_end\": 17, \"kind_start\": 9}, {\"kind_end\": 26, \"kind_start\": 18}, {\"kind_end\": 35, \"kind_start\": 27}]}";

    init_rules(json_rules);

    int ID = new_instance();
    insert_tile(ID, 0, 3);
    insert_tile(ID, 4, 1);
    insert_tile(ID, 5, 1);
    insert_tile(ID, 6, 1);
    insert_tile(ID, 7, 1);
    insert_tile(ID, 8, 3);
    insert_tile(ID, 9, 3);

    int ghost_kind = 9;
    std::string win_sequence = check_is_win_json(ID, 3, ghost_kind);
    std::cout << win_sequence << std::endl;

    std::map<int, int> mapInt;
    std::cout << "mapInt[0] : " << mapInt[0] << std::endl;
    */

    std::list<int> li;
    for (int i=0; i < 9; ++i) {
        li.push_back(0);
        li.push_back(1);
        li.push_back(2);
        li.push_back(3);
    }

    int count = 1000000;

    clock_t start_1 = clock();
    for (int i=0; i < count; ++i) {
        intcat_1(li);
    }
    clock_t end_1 = clock();

    double duration_1 = (double)(end_1 - start_1) / CLOCKS_PER_SEC;
    printf("%s", intcat_1(li).c_str());
    printf("duration 1 : %f\n",duration_1);

    /*
    /////////////////////////////////////////////////////////////////////////
    clock_t start_2 = clock();
    for (int i=0; i < count; ++i) {
        intcat_2(li);
    }
    clock_t end_2 = clock();

    double duration_2 = (double)(end_2 - start_2) / CLOCKS_PER_SEC;
    printf("%s", intcat_2(li).c_str());
    printf("duration 2 : %f\n",duration_2);
    */

    //////////////////////////////////////////////////////////////////////
    clock_t start_3 = clock();
    for (int i=0; i < count; ++i) {
        intcat_3(li);
    }
    clock_t end_3 = clock();

    double duration_3 = (double)(end_3 - start_3) / CLOCKS_PER_SEC;
    printf("%s", intcat_3(li).c_str());
    printf("duration 3 : %f\n",duration_3);

    //////////////////////////////////////////////////////////////////////
    clock_t start_4 = clock();
    for (int i=0; i < count; ++i) {
        intcat_4(li);
    }
    clock_t end_4 = clock();

    double duration_4 = (double)(end_4 - start_4) / CLOCKS_PER_SEC;
    printf("%s", intcat_4(li).c_str());
    printf("duration 4 : %f\n",duration_4);

    //////////////////////////////////////////////////////////////////////
    return 0;
}

