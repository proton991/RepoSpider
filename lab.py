import requests
from bs4 import BeautifulSoup
import time
import multiprocessing

# -*- coding:utf-8 -*-
__author__ = 'Cui Xin yu'
default_encoding = 'utf-8'


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


# github爬虫类
class GHCrawler:
    # 初始化方法，定义一些变量
    def __init__(self, _topic, project_number=500, sort_options="o=desc"):
        self.pageIndex = 1
        self.page_number = project_number / 10
        self.user_agent = 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'
        # 初始化headers
        # self.headers = {'User-Agent': self.user_agent}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/48.0.2564.116 Safari/537.36',
        }

        # 存放段子的变量，每一个元素是每一页的段子们
        self.repo_full_names = set()
        # 存放程序是否继续运行的变量
        self.enable = False
        self.topic = topic
        self.file_name = self.topic + ".txt"

        self.sort_options = sort_options

    # 传入某一页的索引获得页面代码
    def getPage(self, url):
        # print project_number,sort_options,search_content+"========="
        # url = 'http://github.com/search?' + str(self.sort_options) + '&q=' + str(self.topic) + '&p=' + str(
        #     page_index) + '&l=java'
        print("url is : " + url)
        retry_count = 10
        while retry_count > 0:
            try:
                # time.sleep(0.5)
                # 使用代理访问
                proxy = get_proxy().get("proxy")
                proxies = {
                    "http": "http://{}".format(proxy),
                    "https": "https://{}".format(proxy),
                }
                response = requests.get(url, headers=self.headers, proxies=proxies, timeout=10, verify=False)
                return response.text
            except requests.exceptions.RequestException:
                retry_count = retry_count - 1
                print("The server couldn't fulfill the request, switch proxy...")

        return None

    def extract_info(self, url):
        pageCode = self.getPage(url)
        while not pageCode:
            print("页面加载失败, 重新加载中")
            pageCode = self.getPage(url)
        soup = BeautifulSoup(pageCode, "html.parser")
        items = soup.find_all(class_="repo-list-item")
        if len(items) != 10:
            print("项目列表未完全加载, 重新加载中...")
            return self.extract_info(url)
        return items

    def getPageItems(self, url):
        items = self.extract_info(url)
        repo_set = set()
        for item in items:
            tmp = item.contents[3].contents[1].contents[1]['href']
            print(tmp)
            repo_set.add(tmp)
        return repo_set

    # 取规定数量个数内容
    def saveRes2Txt(self, repo_set):
        f = open(self.file_name, "a+")
        for repo_full_name in repo_set:
            f.writelines(repo_full_name[1:] + "\n")
        f.close()

    # 开始方法
    def start(self):
        print(u"正在读取github页面，搜索内容为：" + self.topic)
        # 使变量为True，程序可以正常运行
        self.enable = True
        # 先加载一页内容
        cpus = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(cpus if cpus < 4 else 4)
        page_index = 1
        url_list = []
        while page_index <= self.page_number:
            url = 'http://github.com/search?' + str(self.sort_options) + '&q=' + str(self.topic) + '&p=' + str(
                page_index) + '&l=java'
            url_list.append(url)
            page_index += 1
        # print(url_list)
        for url in url_list:
            pool.apply_async(self.getPageItems, args=(url,), callback=self.saveRes2Txt)
        # pool.apply_async(self.getPageItems, args=(page_index,), callback=self.saveRes2Txt)
        # time.sleep(0.5)
        #
        # # print("saving results to txt...")
        # # self.saveRes2Txt()
        # # print("finished")
        pool.close()
        pool.join()


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


if __name__ == '__main__':
    # 自定义搜索内容
    topic = "spring"
    spider = GHCrawler(topic.replace(" ", "+"), 500, getSortOptions(6))
    # 自定义/量化（0：最流行，1：不流行，2：复刻/克隆最多，3：克隆最少，4：最近更新，5：近期最少更新）
    spider.start()
