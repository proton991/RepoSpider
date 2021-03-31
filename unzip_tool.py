import os
import zipfile
import multiprocessing


# def unzip_file(src_dir="D:\\repos\\"):
#
#     src_dir = "D:\\repos\\"
#     zip_files = os.listdir(src_dir)
#     for zip_file in zip_files:
#         fz = zipfile.ZipFile(os.path.join(src_dir, zip_file), 'r')
#         print("begin to extract {}".format(zip_file))
#         try:
#             fz.extractall(src_dir)
#         except FileExistsError as e:
#             print(e)
#         print("finished extracting {}".format(zip_file))
def unzip_file_single(file_path, src_dir):
    fz = zipfile.ZipFile(file_path, 'r')
    print("begin to extract {}".format(fz.filename))
    try:
        fz.extractall(src_dir)
    except FileExistsError as e:
        print(e)
    print("finished extracting {}".format(fz.filename))


def unzip_file_all(src_dir):
    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(cpus if cpus < 4 else 4)
    # src_dir = "D:\\repos\\"
    zip_files = os.listdir(src_dir)
    file_list = []
    for zip_file in zip_files:
        file_path = os.path.join(src_dir, zip_file)
        pool.apply_async(unzip_file_single, args=(file_path, src_dir,))
    pool.close()
    pool.join()

if __name__ == '__main__':
    unzip_file_all("D:\\repos\\")

