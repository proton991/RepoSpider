import os
from github import Github, GithubException
import multiprocessing
import requests
from unzip_tool import unzip_file_all


def download(_url, out_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/48.0.2564.116 Safari/537.36',
    }
    try:
        r = requests.get(_url, headers=headers, stream=True)
        zip_file = open(out_path, 'wb')
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                zip_file.write(chunk)
        zip_file.flush()
        zip_file.close()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = "D:\\"
    base_dir = os.path.join(base_dir, "spring_repos")
    # base_dir = "/mnt/clonedata/CodeClone/datasetDir"
    # base_dir = os.path.join(base_dir, "spring_repos")
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    access_token = 'your github access token here'
    g = Github(access_token)
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    files = os.listdir(data_dir)
    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(cpus if cpus < 4 else 4)
    download_list = []

    for file in files:  # 遍历文件夹
        if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
            f = open(os.path.join(data_dir, file))  # 打开文件
            iter_f = iter(f)  # 创建迭代器
            for repo_full_name in iter_f:  # 遍历文件，一行行遍历，读取文本
                repo_full_name = repo_full_name.strip("\n")
                repo = None
                try:
                    repo = g.get_repo(repo_full_name)
                except GithubException as e:
                    print(e.data)
                if not repo:
                    continue
                download_url = repo.get_archive_link(archive_format="zipball")
                out_dir = os.path.join(base_dir, repo_full_name.replace('/', '+') + ".zip")
                print('Beginning file download with requests module {n}'.format(n=download_url))
                pool.apply_async(download, args=(download_url, out_dir,))
    pool.close()
    pool.join()
    print("finished!")
    unzip_file_all(base_dir)
