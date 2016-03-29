# -*- coding:utf-8 -*-
from requests import get
from requests import codes
from time import strftime
from time import sleep
from time import localtime
from crawler import insert_collection


def fetch(task_id, keyword, start=1, end=5):
    """
    通过http://m.weibo.cn/page/pageJson接口获取微博的关键查询结果,并保存结果至mongodb中
    :param task_id: 本次抓取所属的任务编号
    :param keyword: 搜索关键子
    :param start: 开始页数
    :param end: 结束页数
    :return:
    """

    for i in range(start, end + 1):

        keyword = "100103type=&q=%s" % keyword

        # 请求m版的ajax接口获取微博关键子查询列表及内容数据.
        resp = get("http://m.weibo.cn/page/pageJson", {
            "containerid": keyword,
            "v_p": 11,
            "ext": "",
            "fid": keyword,
            "uicode": 10000011,
            "next_cursor": "",
            "page": i
        })

        if resp.status_code == codes.ok:
            rows = list()
            data = resp.json()

            for item in data["cards"]:
                # hotmblog与mblog节点是需要获取的微博内容数据,hotmblog只会在第一页时出现
                if item["itemid"] in ("hotmblog", "mblog"):
                    for row in item["card_group"]:
                        blog = row["mblog"]

                        rows.append({
                            "task": task_id,
                            "text": blog["text"],
                            "source": blog["source"],
                            "reposts_count": blog["reposts_count"],
                            "comments_count": blog["comments_count"],
                            "attitudes_count": blog["attitudes_count"],
                            "created_at": blog["created_at"],
                            "fetch_time": strftime("%Y-%m-%d %H:%M:%S", localtime())
                        })
            # 插入数据库
            insert_collection("weibo_cn", rows)
            # 发送进度信息至应用服务程序

        # 线程休息一秒,防止服务器误认为是攻击
        sleep(1)
