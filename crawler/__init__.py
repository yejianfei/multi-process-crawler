# -*- coding:utf-8 -*-
from pymongo import MongoClient
from config import MONGO
from os import environ


# 检测系统中环境存在mongo docker的连接环境变量时,使用mongo docker的环境变量,而不使用配置文件的连接信息.

MONGO_ADDR = environ.get("MONGO_PORT_27017_TCP_ADDR", None)
if MONGO_ADDR is None:
    MONGO_ADDR = MONGO["HOST"]

MONGO_PORT = environ.get("MONGO_PORT_27017_TCP_PORT", None)
if MONGO_PORT is None:
    MONGO_PORT = MONGO["PORT"]

_client = MongoClient(MONGO_ADDR, int(MONGO_PORT), connect=False)


def insert_collection(name, data):
    """
    根据给定的集合名称,插入数据至该集合中.
    :param name: 集合名称
    :param data: 数据或数据列表
    :return:
    """
    db = _client.get_database(MONGO["DB"])
    collection = db.get_collection(name)

    if isinstance(data, list):
        collection.insert_many(data)
    elif isinstance(data, dict):
        collection.insert(data)



