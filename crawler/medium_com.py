# -*- coding:utf-8 -*-
from requests import get
from requests import codes
from bs4 import BeautifulSoup
from crawler import insert_collection


def fetch(task_id, keyword, start=1, end=5):
    """
    通过https://medium.com/search/posts接口获取medium的关键查询结果,并保存结果至mongodb中
    :param task_id: 本次抓取所属的任务编号
    :param keyword: 搜索关键子
    :param start: 开始页数
    :param end: 结束页数
    :return:
    """
    ignore = list()

    for i in range(1, end + 1):
        resp = get("https://medium.com/search/posts", {"q": keyword, "ignore": ignore})

        if resp.status_code == codes.ok:
            soup = BeautifulSoup(resp.text)

            # 获取当前页的文章ID,用于翻页时使用,medium.com不提供直接翻页的功能,只能逐页跳过.
            items = soup.select("div.blockGroup-list > div.block")
            for post in items:
                ignore.append(post.get("data-post-id"))

            # 根据起始也是忽略结果处理
            if i < start:
                continue

            rows = list()

            # 选择文章详细页面地址,进入详细页码抓取信息.
            items = soup.select(
                "div.blockGroup-list > div.block > div.block-streamText > div.block-content > article > a")
            for post in items:
                data = fetch_post(post.get("href"))
                if data is not None:
                    data["task"] = task_id
                    rows.append(data)

            insert_collection("medium_com", rows)


def fetch_post(url):
    """
    通过详细页面地址获取页面数据并返回结构化数据
    :param url: 页面详细地址
    :return: 结构化数据
    """
    resp = get(url)
    if resp.status_code == codes.ok:
        soup = BeautifulSoup(resp.text)
        content = soup.select_one("div.section-content > div.section-inner.layoutSingleColumn")

        data = {
            "author": soup.select_one("a.link.link.link--darken").text,
            "title": content.select_one(".graf--first").text,
            "content": content.prettify(),
            "recommends": soup.select_one('button[data-action="show-recommends"]').text
        }

        buttons = soup.select('button[data-action="scroll-to-responses"]')
        data["responses"] = buttons[len(buttons) - 1].text

        return data
