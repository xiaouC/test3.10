#!/usr/bin/python
# coding: utf-8

from db.storage import DBStorage

def test():
    db = DBStorage('127.0.0.1', 8888)

    db.set('test', '123')
    print db.get('test')
