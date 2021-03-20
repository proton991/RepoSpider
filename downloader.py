import os
import multiprocessing
from github import Github
import wget


def wget_download(url, path):
    wget.download(url, out=path)


class MPDownloader:
    def __init__(self, file_type_set, max_pool_size=4):
        cpus = multiprocessing.cpu_count()
        self.pool = multiprocessing.Pool(cpus if cpus < max_pool_size else max_pool_size)
        self.out_dir = os.path.dirname(os.path.abspath(__file__))
        self.access_token = 'f25528303e7da1048f0deb70e14bbcae563e339e'
        self.g = Github(self.access_token)
        self.file_type_set = file_type_set

    def is_target_file(self, fileName):
        return os.path.splitext(fileName)[-1] in self.file_type_set

    def run(self, repo_full_name):
        download_list = []
        repo = self.g.get_repo(repo_full_name)
        self.out_dir = os.path.join(self.out_dir, str.replace(repo_full_name, '/', '-'))
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)
        # print(self.out_dir)
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            elif self.is_target_file(file_content.name):
                print(os.path.join(self.out_dir, file_content.path.replace("/", "\\")))
                download_list.append([file_content.download_url, os.path.join(self.out_dir, file_content.path)])
        print(download_list)
        # for url, path in download_list:
        #     print('Beginning file download with wget module {n}'.format(n=url))
        #     self.pool.apply_async(wget_download, args=(url, path,))
        # self.pool.close()
        # self.pool.join()
        # print("finished downloading " + repo_full_name)
