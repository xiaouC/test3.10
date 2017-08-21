# coding: utf-8
# import time

from yy.cron import reset_jobs, Job
from gm.app import *  # NOQA
from entity.manager import check_over_day, reset_on_zero

reset_jobs([
    Job(reset_on_zero,                  minute='0', second='0', hour='0'),
    Job(check_over_day,                 minute='0', second='0', hour='0'),
])
