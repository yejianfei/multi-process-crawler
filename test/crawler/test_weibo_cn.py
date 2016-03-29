# -*- coding:utf-8 -*-
from crawler import weibo_cn


def test_fetch():
    weibo_cn.fetch("test_task", "李沁", 3, 6)
