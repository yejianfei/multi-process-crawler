# -*- coding:utf-8 -*-
from flask import Flask
from flask import request
from flask import jsonify
from json import dumps
from socket import gethostname
from socket import gethostbyname
from multiprocessing import Process
from requests import post
from requests import put
from requests import codes
from crawler import weibo_cn
from crawler import medium_com
from config import SERVER
from config import NODE

app = Flask(__name__)


def do_task(msg):
    """
    新进程的处理回调函数,用于根据任务类型选择对于的数据抓取实现函数.
    :param msg: 待抓取数据的相关参数
    :return:
    """
    # 处理weibo.cn的抓取任务
    if msg["type"] == "weibo_cn":
        weibo_cn.fetch(msg["task"], msg["keyword"], int(msg["start"]), int(msg["end"]))
    elif msg["type"] == "medium_com":
        medium_com.fetch(msg["task"], msg["keyword"], int(msg["start"]), int(msg["end"]))

    # 通知服务应用服务程序,该抓取任务已完成,请求地址示例:http://127.0.0.1:9000/api/task/<task_id>
    put("%s/api/tasks/%s" % (SERVER["URL"], msg["task"]), json={
        "action": "done"
    })


@app.route("/tasks", methods=["post"])
def task():
    """
    处理开启抓取任务的的请求,接受到请求后,创建新的进程进行异步抓取数据并存储至数据库中.
    :return:
    """
    payload = request.get_json()

    # 开启新进程处理任务并抓取数据.
    proc = Process(target=do_task, args=(payload,))
    proc.start()

    # 直接返回处理结果为成功,达到异步的效果
    return jsonify({
        "success": True
    })


if __name__ == "__main__":
    node = gethostname()

    # 通知应用服务程序该节点已上线
    resp = post("%s/api/nodes" % SERVER["URL"], json={
        "name": node,
        "port": 9001
    })
    if resp.status_code == codes.ok:
        data = resp.json()

        # 应用服务程序接受上线请求才能启动任务节点服务
        if data["success"]:
            app.config["TASK_NODE"] = node
            app.run(port=int(NODE["PORT"]), debug=bool(NODE["DEBUG"]))
        else:
            print "同名节点[%s]已启动,该节点不能启动!" % node

