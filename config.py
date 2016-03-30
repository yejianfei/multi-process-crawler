# -*- coding:utf-8 -*-

SERVER = {
    # 任务管理主服务的请求地址，用于采集节点服务使用
    "URL": "http://127.0.0.1:9000",
    # 任务管理主服务的运行端口
    "PORT": 9000,
    # 开启flask调试状态
    "DEBUG": True
}

NODE = {
    # 采集节点的运行端口
    "PORT": 9001,
    # 开启flask调试状态
    "DEBUG": True
}

MONGO = {
    # 数据库主机地址
    "HOST": "localhost",
    # 数据库端口
    "PORT": "27017",
    # 数据库名称
    "DB": "crawler_db"
}