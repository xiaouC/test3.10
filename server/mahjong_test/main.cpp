#include "game_win_check.h"
#include <sys/time.h>

int main() {
    game_win_check obj;
    obj.load_win_styles();

    obj.set_ghost_card_id_1(0x35);

    int hand_cards[13];
    hand_cards[0] = 0x35;
    hand_cards[1] = 0x35;
    hand_cards[2] = 0x14;
    hand_cards[3] = 0x14;
    hand_cards[4] = 0x15;
    hand_cards[5] = 0x16;
    hand_cards[6] = 0x17;
    hand_cards[7] = 0x21;
    hand_cards[8] = 0x22;
    hand_cards[9] = 0x23;
    hand_cards[10] = 0x25;
    hand_cards[11] = 0x27;
    hand_cards[12] = 0x28;

    obj.set_ghost_card_id_1(31);

    hand_cards[0] = 31;
    hand_cards[1] = 31;
    hand_cards[2] = 12;
    hand_cards[3] = 12;
    hand_cards[4] = 13;
    hand_cards[5] = 14;
    hand_cards[6] = 15;
    hand_cards[7] = 18;
    hand_cards[8] = 19;
    hand_cards[9] = 20;
    hand_cards[10] = 22;
    hand_cards[11] = 24;
    hand_cards[12] = 25;

    struct timeval start;
    struct timeval end;
    gettimeofday(&start, NULL);

    bool is_win = false;
    for (int i=0; i < 1000000; ++i) {
        // 0x14, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x35
        is_win = obj.check_is_win(hand_cards, 13, 12);
        // is_win = obj.check_is_win(hand_cards, 13, 0);
    }

    std::list<int> win_cards = obj.get_ting_list(hand_cards, 13);

    gettimeofday(&end, NULL);

    printf("is_win : %s\n", is_win ? "true" : "false");

    printf("ting list : ");
    for (const auto& iter : win_cards) {
        printf("%d, ", iter);
    }
    printf("\n");

    float second = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0f;
    printf("thedifference is %f\n", second);

    return 0;
}
