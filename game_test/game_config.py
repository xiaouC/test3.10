#!/usr/bin/env python
# coding=utf-8

all_game_config = {
    '100001': {
        'expire': 3 * 60 * 60,              # 3 hours
        'min_player_count': 2,              # 最少开始游戏人数
        'max_player_count': 4,              # 最多游戏人数
        'has_ghost_card': True,             # 是否有鬼牌
        'has_wan': False,                   # 是否有万字牌
        'has_tiao': True,                   # 是否有条
        'has_tong': True,                   # 是否有筒子
        'has_wind': True,                   # 是否有风牌
        'has_arrow': True,                  # 是否有箭牌
        'has_flower': False,                # 是否有花牌
        'allow_sequence': False,            # 是否有顺子[万，条，筒]
        'allow_wind_sequence': False,       # 是否有风牌顺子
        'allow_arrow_sequence': False,      # 是否有箭牌顺子
        'allow_triplet': True,              # 是否有刻子
        'allow_kong': True,                 # 是否有杠
        }
}
