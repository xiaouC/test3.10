# coding:utf-8
from config.configs import get_config
from config.configs import AmbitionConfig
from config.configs import VipAmbitionConfig


def reload_ambition(p):
    configs = get_config(AmbitionConfig)
    current = len(p.ambition or '')
    while True:
        config = configs.get(current + 1)
        if not config:
            break
        if config.level > p.level:
            break
        p.ambition = (p.ambition or '') + '1'
        current += 1
    p.save()
    p.sync()


def reload_vip_ambition(p):
    configs = get_config(VipAmbitionConfig)
    current = len(p.vip_ambition or '')
    while True:
        config = configs.get(current + 1)
        if not config:
            break
        if config.level > p.vip:
            break
        p.vip_ambition = (p.vip_ambition or '') + '1'
        current += 1
    p.save()
    p.sync()
