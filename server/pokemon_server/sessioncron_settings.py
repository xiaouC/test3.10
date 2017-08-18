# coding: utf-8
from yy.cron import reset_jobs, Job
from gm import *
from yy.utils import mysql_ping

reset_jobs([
    #Job(lambda:mysql_ping("user"), minute='*/30'),
])
