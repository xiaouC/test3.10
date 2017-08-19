#!/usr/bin/python
# coding: utf-8

from app_world import world_service

@world_service.register_msg(1)
def test(a, b):
    print 'test 111111111111111111'
    print a, b


