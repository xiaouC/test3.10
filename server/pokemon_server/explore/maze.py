# coding:utf-8
import time
from config.configs import get_config
from config.configs import MazeConfig
from config.configs import MazeCaseConfig
from config.configs import MazeBossConfig
from config.configs import get_cons_value
from yy.utils import weighted_random2
from .constants import MazeEventType
from mall.constants import MallType


def step_mazes(p, attr, incr, count):
    mazes = get_config(MazeConfig)
    maze_step_count = p.maze_step_count
    results = []
    while count > 0:
        remain = time.time() + 3600
        data = {}
        config = mazes[maze_step_count % len(mazes)]
        append = False  # 是否加入事件组
        attr["money_rest_pool"] = min(
            attr.get("money_rest_pool", p.money_rest_pool) + get_cons_value(
                "MazeMustDropMoney"), p.money_most_pool)
        attr["maze_rest_count"] = attr.get(
            "maze_rest_count", p.maze_rest_count)
        data["attr"] = attr
        data["incr"] = incr
        if config.type == MazeEventType.DoubleMoney:
            v = int(attr.get(
                "money_rest_pool", p.money_rest_pool) * config.argv)
            v = max(min(v, p.money_most_pool), 0)
            attr["money_rest_pool"] = v
        elif config.type == MazeEventType.AddMoney:
            v = int(attr.get(
                "money_rest_pool", p.money_rest_pool) + config.argv)
            v = max(min(v, p.money_most_pool), 0)
            attr["money_rest_pool"] = v
        elif config.type == MazeEventType.DoubleCount:
            origin = attr.get("maze_rest_count", p.maze_rest_count)
            v = int(origin * config.argv)
            v = max(v, 0)
            if v > origin:
                attr["maze_rest_count"] = origin
                incr["maze_rest_count"] = incr.get(
                    "maze_rest_count", 0) + v - origin
            else:
                attr["maze_rest_count"] = v
        elif config.type == MazeEventType.AddCount:
            origin = attr.get("maze_rest_count", p.maze_rest_count)
            v = int(origin + config.argv)
            v = max(v, 0)
            if v > origin:
                attr["maze_rest_count"] = origin
                incr["maze_rest_count"] = incr.get(
                    "maze_rest_count", 0) + v - origin
            else:
                attr["maze_rest_count"] = v
        elif config.type == MazeEventType.Drop:
            data.update({"drop": int(config.argv)})
        elif config.type == MazeEventType.Shop:
            if config.argv == MallType.Silver:
                attr["mall_silver_open_remain"] = remain
            elif config.argv == MallType.Golden:
                attr["mall_golden_open_remain"] = remain
            data.update({"argv": int(config.argv)})
            append = True
        elif config.type == MazeEventType.Case:
            weights = []
            for each in get_config(MazeCaseConfig):
                if p.level >= each.level:
                    weights.append([each.drop, each.prob])
                else:
                    break
            drop = weighted_random2(weights)
            data.update({"argv": int(drop)})
            append = True
        elif config.type == MazeEventType.Boss:
            weights = []
            for each in get_config(MazeBossConfig):
                if p.level >= each.level:
                    weights.append([each.boss, each.prob])
                else:
                    break
            boss = weighted_random2(weights)
            data.update({"argv": int(boss)})
            append = True
        elif config.type == MazeEventType.Noop:
            pass
        else:
            break
        result = {
            "type": config.type,
            "time": remain,
            "append": append,
        }
        result.update(**data)
        result.setdefault("argv", config.argv)
        results.append(result)
        attr["maze_rest_count"] = max(attr["maze_rest_count"] - 1, 0)
        maze_step_count += 1
        if "maze_rest_count" in attr and attr["maze_rest_count"] == 0:
            break
        if attr["money_rest_pool"] >= p.money_most_pool:
            break
        count -= 1
    return results
