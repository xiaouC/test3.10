#!/usr/bin/env python
# coding=utf8


from mall.service import *  # NOQA
from world.service import *  # NOQA


@rpcmethod(msgid.MALL_BUY_PRODUCT)
def mall_buy_product(self, msgtype, body):
    p = self.player
    req = poem_pb.MallBuyProduct()
    req.ParseFromString(body)
    logger.debug(req)
    config = get_config(MallConfig)[req.ID]
    if not check_open(p, config.type):
        return fail_msg(msgtype, reason="商店未开启")
    # 限制
    count = p.mall_limits.get(req.ID, 0)
    if config.limit > 0 and count >= config.limit:
        return fail_msg(msgtype, reason="超过购买次数")
    now = int(time.time())
    last = p.mall_times.get(req.ID, 0)
    if last and now < last + config.cd:
        return fail_msg(msgtype, reason="购买冷却中")
    reward = parse_reward([{
        'type': config.product_type,
        'arg': config.productID,
        'count': config.product_amount}])
    cost = parse_reward([{
        'type': config.item_type,
        'count': config.price,
    }])
    try:
        apply_reward(
            p, reward, cost,
            type=RewardType.MallBuy)
    except AttrNotEnoughError:
        return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)

    from campaign.manager import g_campaignManager
    if g_campaignManager.exchange_campaign.is_open():
        start_time, end_time = g_campaignManager.exchange_campaign.get_current_time()
        if p.exchange_campaign_last_time < start_time or p.exchange_campaign_last_time > end_time:
            p.exchange_campaign_counter = 0
        p.exchange_campaign_counter = p.exchange_campaign_counter + 1
        p.exchange_campaign_last_time = now

        current = g_campaignManager.exchange_campaign.get_current()
        from config.configs import ExchangeCampaignByGroupConfig
        group = get_config(ExchangeCampaignByGroupConfig).get(current.group)

        ex_rsp = poem_pb.ExchangeCampaignItemResponse()

        rewards = {}
        for i in range(0, len(group.consumes)):
            tmp_count = group.refresh_counts[i]
            if not tmp_count or tmp_count <= 0:
                continue

            if p.exchange_campaign_counter % tmp_count == 0:
                tmp_config = group.consumes[i]
                print tmp_config
                r = parse_reward([{
                    "arg": tmp_config["arg"],
                    "type": tmp_config["type"],
                    "count": 1,
                }])
                combine_reward(r, {}, rewards)

                info = {}
                info["arg"] = tmp_config["arg"]
                info["type"] = tmp_config["type"]
                info["count"] = 1
                ex_rsp.items.add(**info)

        if len(rewards) > 0:
            apply_reward(p, rewards, type=RewardType.RefreshMall)

            from player.manager import g_playerManager
            ex_msg = success_msg(msgid.EXCHANGE_CAMPAIGN_ITEM_RESULT, ex_rsp)
            g_playerManager.sendto(p.entityID, ex_msg)

    p.mall_limits[req.ID] = count + 1
    p.mall_times[req.ID] = now
    from task.manager import on_shopping
    on_shopping(p)
    p.save()
    p.sync()
    return success_msg(msgtype, '')

WorldService._method_map[msgid.MALL_BUY_PRODUCT] = mall_buy_product
