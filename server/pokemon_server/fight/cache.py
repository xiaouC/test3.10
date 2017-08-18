# coding:utf-8
import logging
logger = logging.getLogger("fight")


def cache_fight_response(p, verify_code, response):
    p.cache_fight_verify_code = verify_code
    p.cache_fight_response = response.SerializeToString()
    p.save()


def get_cached_fight_response(p, verify_code):
    if p.cache_fight_verify_code == verify_code:
        logger.info(
            "player %d, verify_code %s, hit fight cache" % (
                p.entityID, verify_code))
        return str(p.cache_fight_response)
    return None
