# -*- coding:utf-8 -*-
from pymongo import MongoClient
from config import MONGO

_client = MongoClient(MONGO["HOST"], int(MONGO["PORT"]), connect=False)


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



