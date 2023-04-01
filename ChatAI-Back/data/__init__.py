"""
数据模块，主要只能是从数据源获取数据，同时做简单的处理
"""
import json
import logging

from .database import database as db

database = None


def set_database(opts):
    d = db()
    d.call(opts)
    if not d.valid():
        logging.error("数据库连接信息不完整:" + json.dumps(opts))
        exit(0)
    global database
    logging.error("数据库连接信息:" + json.dumps(opts))
    database = d.get_database()


def get_database():
    return database


def change_id_name(itr):
    its = []
    for it in itr:
        it["id"] = it["_id"]
        its.append(it)
    return its
