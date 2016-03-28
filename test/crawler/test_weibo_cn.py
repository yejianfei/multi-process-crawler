# -*- coding:utf-8 -*-
from crawler import weibo_cn


def test_fetch():
    weibo_cn.fetch("李沁", 3, 6)
