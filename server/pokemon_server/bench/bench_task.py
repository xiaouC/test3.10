import settings
settings.watch()

from common import ConfigFiles
from config.configs import get_registereds
from yy.config.fields import ValidationError
config_files = ConfigFiles(settings.REGION['ID'])
try:
    config_files.load_configs(
        get_registereds(),
        settings.CONFIG_FILE_PATH)
except ValidationError as e:
    print e.message.encode("utf-8")
    raise e

from player.model import Player
p = Player.load(11)
print p.name

from task.manager import on_end_fb_count, on_levelup
import timeit
import cProfile

timeit.main(['-s', 'from __main__ import on_levelup, p',
            '-n', '1', 'on_levelup(p)'])

cProfile.run('for i in xrange(1):on_levelup(p)',
             sort='time')

#timeit.main(['-s', 'from __main__ import on_end_fb_count, p',
#            '-n', '1000', 'on_end_fb_count(p, 100111)'])
#
#cProfile.run('for i in xrange(1000):on_end_fb_count(p, 100111)',
#             sort='time')

