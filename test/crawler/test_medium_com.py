# -*- coding:utf-8 -*-
from crawler import medium_com


def test_fetch():
    medium_com.fetch("test_task", "java", 1, 6)
