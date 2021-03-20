# -*- coding:utf-8 -*-
import requests

__author__ = 'CuiXinyu'

from bs4 import BeautifulSoup
import time

defaultencoding = 'utf-8'


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


# github爬虫类
class GHCrawler:
    # 初始化方法，定义一些变量
    def __init__(self, _topic):
        self.pageIndex = 1
        self.user_agent = 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'
        # 初始化headers
        # self.headers = {'User-Agent': self.user_agent}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/48.0.2564.116 Safari/537.36',
        }

        # 存放段子的变量，每一个元素是每一页的段子们
        self.repo_full_names = []
        # 存放程序是否继续运行的变量
        self.enable = False
        self.topic = topic

    # 传入某一页的索引获得页面代码
    def getPage(self, pageIndex, sort_options):
        # print project_number,sort_options,search_content+"========="
        url = 'https://github.com/search?' + str(sort_options) + '&q=' + str(self.topic) + '&p=' + str(
            pageIndex) + '&l=java'
        print("url is : " + url)

        # 构建请求的request
        # req = request.Request(url, headers=self.headers)
        # # # 利用urlopen获取页面代码
        # response = request.urlopen(req)
        # # 将页面转化为UTF-8编码
        # pageCode = response.read().decode('utf-8')
        retry_count = 50000
        proxy = get_proxy().get("proxy")
        while retry_count > 0:
            try:
                time.sleep(0.5)
                response = requests.get(url, headers=self.headers, proxies={"https": "https://{}".format(proxy)})
                # 使用代理访问
                return response.text
            except Exception as e:
                print("The server couldn't fulfill the request.")

        return None

    # 传入某一页代码，返回本页不带图片的段子列表
    def getPageItems(self, pageIndex, sort_options):
        # print project_number,sort_options,search_content+"===="
        pageCode = self.getPage(pageIndex, sort_options)
        # print pageCode
        if not pageCode:
            print("页面加载失败....")
            return None
        soup = BeautifulSoup(pageCode, "html.parser")
        items = soup.find_all(class_="repo-list-item")
        file_name = self.topic + ".txt"
        f = open(file_name, "a+")
        for item in items:
            tmp = item.contents[3].contents[1].contents[1]['href']
            print(tmp)
            f.writelines(tmp[1:] + "\n")
            # print(item.contents[3].contents[1].contents[1]['href'])
            # self.repo_full_names.append(item.contents[3].contents[1].contents[1]['href'])

    # 加载并提取页面的内容，加入到列表中
    # def loadPage(self, pageIndex, sort_options):
    #     # print project_number,sort_options,search_content
    #     self.getPageItems(self.pageIndex, sort_options)

    # 取规定数量个数内容
    def saveRes2Txt(self):
        file_name = self.topic + ".txt"
        f = open(file_name, "w+")
        for repo_full_name in self.repo_full_names:
            f.writelines(repo_full_name[1:] + "\n")
        f.close()

    # 开始方法
    def start(self, page_number, sort_options):
        print(u"正在读取github页面，搜索内容为：" + self.topic)
        # print project_number,sort_options,search_content
        # 使变量为True，程序可以正常运行
        self.enable = True
        # 先加载一页内容
        while self.pageIndex <= page_number:
            self.getPageItems(self.pageIndex, sort_options)
            time.sleep(0.5)
            self.pageIndex += 1
        # print("saving results to txt...")
        # self.saveRes2Txt()
        # print("finished")


def getSortOptions(argument):
    switcher = {
        0: "o=desc&s=stars",
        1: "o=asc&s=stars",
        2: "o=desc&s=forks",
        3: "o=asc&s=forks",
        4: "o=desc&s=updated",
        5: "o=asc&s=updated",
        6: "o=desc",
    }
    return switcher.get(argument, "nothing")


# 自定义搜索内容
topic = "html"
spider = GHCrawler(topic.replace(" ", "+"))
# 自定义爬取个数
project_number = 50
page_number = project_number / 10
# 自定义/量化（0：最流行，1：不流行，2：复刻/克隆最多，3：克隆最少，4：最近更新，5：近期最少更新）
options = 6
sort_options = getSortOptions(options)
print(sort_options)

spider.start(page_number, sort_options)
