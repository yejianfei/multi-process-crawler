# -*- coding:utf-8 -*-
from flask import Flask
from flask import request
from flask import jsonify
from flask import abort
from flask import render_template
from requests import post
from requests import codes
from requests.exceptions import ConnectionError
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import MONGO
from config import SERVER
from time import strftime
from time import localtime

client = MongoClient(MONGO["HOST"], int(MONGO["PORT"]))
db = client.get_database(MONGO["DB"])
app = Flask(__name__)


@app.route("/api/nodes", methods=["post"])
def reg_node():
    """
    处理抓取节点上线或注册新抓取节点的氢气.
    :return:
    """
    payload = dict(request.get_json().items() + {
        "status": 1,
        "addr": request.remote_addr
    }.items())

    # 之前未注册过的新节点,才用新增操作
    if db.nodes.count({"name": payload["name"]}) == 0:
        db.nodes.insert(payload)
    else:
        db.nodes.find_and_modify({"name": payload["name"]}, payload)

    return jsonify({"success": True})


@app.route("/api/tasks", methods=["post"])
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
    payload["task"] = "%s@%s" % (payload["node"], strftime("%Y%m%d%H%M%S", localtime()))
    payload["status"] = 0
    payload["done"] = 0
    db.tasks.insert(payload)

    # 请求节点的抓取任务接口,启动抓取任务

    try:
        resp = post("http://%s:%d/tasks" % (node["addr"], node["port"]), json={
            "task": str(payload["_id"]),
            "type": payload["type"],
            "keyword": payload["keyword"],
            "start": payload["start"],
            "end": payload["end"]
        })

        # 如果抓取节点请求成功,直接返回请求节点的处理结果,反之返回请求节点http状态
        if resp.status_code == codes.ok:
            payload["status"] = 1
            db.tasks.save(payload)
            return jsonify(resp.json())
        else:
            abort(resp.status_code)
    except ConnectionError:
        # 网络原因无法通知节点服务启动任务时,删除本次建立的任务信息.
        db.tasks.delete_one({"_id": payload["_id"]})
        return jsonify({"success": False, "code": -1})


@app.route("/api/tasks/<task_id>", methods=["put"])
def update_task(task_id):
    """
    处理更新抓取任务信息的请求
    :param task_id: 待更新的任务主键
    :return:
    """
    payload = request.get_json()

    # 如果操作未任务完成,更新任务状态
    if payload["action"] == "done":
        db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": 2}})

    return jsonify({"success": True})


@app.route("/api/tasks/<task_type>/<task_id>", methods=["delete"])
def delete_task(task_type, task_id):
    """
    处理删除任务信息的请求
    :param task_type:
    :param task_id:
    :return:
    """
    cc = db.get_collection(task_type)

    # 同时删除任务采集的数据
    if cc is not None:
        cc.delete_many({"task": task_id})

    db.tasks.delete_one({"_id": ObjectId(task_id)})
    return jsonify({"success": True})


@app.route("/tasks")
@app.route("/tasks/<page>")
def list_task(page=1):
    """
    处理任务列表页面的请求
    :param page:
    :return:
    """
    tasks = db.tasks.find()
    return render_template("list.html", tasks=tasks)


@app.route("/tasks/form", methods=["get"])
def form_task():
    """
    处理获取创建任务表单页码的请求
    :return:
    """
    nodes = db.nodes.find()
    return render_template("form.html", nodes=nodes)


def view_task():
    pass


if __name__ == "__main__":
    app.run(port=int(SERVER["PORT"]), debug=bool(SERVER["DEBUG"]))
