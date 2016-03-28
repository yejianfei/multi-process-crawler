# -*- coding:utf-8 -*-
from flask import Flask
from flask import request
from flask import jsonify
from flask import abort
from requests import post
from requests import codes
from pymongo import MongoClient
from config import MONGO

client = MongoClient(MONGO["HOST"], int(MONGO["PORT"]))
db = client.get_database(MONGO["DB"])
app = Flask(__name__)


@app.route("/nodes", methods=["post"])
def reg_node():
    payload = dict(request.get_json().items() + {
        "status": 1
    }.items())

    # 之前未注册过的新节点,才用新增操作
    if db.nodes.count({"name": payload["name"]}) == 0:
        db.nodes.insert(payload)
    else:
        db.nodes.find_and_modify({"name": payload["name"]}, payload)

    return jsonify({"success": True})


@app.route("/tasks", methods=["post"])
def create_task():
    """
    处理创建根据相关抓取参数及抓取节点服务的名称,启动数据抓取.
    :return:
    """
    payload = request.get_json()

    # 查找抓取节点信息
    node = db.nodes.find_one({"name": payload["node"]})

    # 未找到抓取节点返回404
    if node is None:
        return abort(404)

    # 保存任务信息至数据库中
    task = db.tasks.insert({
        ""
    })

    # 请求节点的抓取任务接口,启动抓取任务
    resp = post("http://%s:%d/tasks" % (node["addr"], node["port"]), json={
        "task": task["_id"],
        "type": payload["type"],
        "keyword": payload["keyword"],
        "start": payload["start"],
        "end": payload["end"]
    })

    # 如果抓取节点请求成功,直接返回请求节点的处理结果,反之返回请求节点http状态
    if resp.status_code == codes.ok:
        return jsonify(resp.json())
    else:
        abort(resp.status_code)


if __name__ == "__main__":
    app.run(port=9000, debug=True)
