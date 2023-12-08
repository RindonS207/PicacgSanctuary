import os
import sys
import threading
import requests

from m3u8 import M3U8
from Crypto.Cipher import AES
from colorama import Fore, Style, init

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
init(autoreset=True)


class FragInfo(object):

    def __init__(self, index, url):
        self.index = index
        self.url = url


def download_frag(path_to_save: str, download_url: str):
    try:
        resources = requests.get(download_url)
        f = open(path_to_save, "wb+")
        f.write(resources.content)
        f.close()
    except Exception as e:
        print(f"{download_url} 分段下载失败惹！！！\n报错信息：{str(e)}")


def parse_download_list(path_to_m3u8: str) -> list:
    f = open(path_to_m3u8, "r")
    content = M3U8(f.read())
    f.close()
    lis = []
    for x in range(len(content.segments)):
        lis.append(FragInfo(x, content.segments[x].uri))
    return lis


def scan_m3u8() -> (list, str):
    global BASE_DIR
    path = BASE_DIR + "\\cache\\content\\"
    if not os.path.exists(path):
        print("找不到索引文件夹了！！你对文件夹结构做了什么！！")
        return []
    ret = []
    for file_name in os.listdir(path):
        ret.append(file_name)
    return ret, path


def decode_m3u8(path_root: str, encrypt_method: str, key: bytes):
    global BASE_DIR
    if encrypt_method == "AES-128":
        cipher = AES.new(key, AES.MODE_CBC)
        cipher_list = []
        for f in os.listdir(path_root):
            cipher_list.append(os.path.join(path_root, f))
        print("检测到文件加密，开始解密。")
        total = len(cipher_list)
        for x in range(len(cipher_list)):
            print("解密中... {:.2f}%".format(x / total * 100))
            f = open(cipher_list[x], "rb")
            out_f = open(BASE_DIR + f'\\cache\\download\\decode\\{str(x)}.ts', "wb+")
            extent_text = cipher.decrypt(f.read())
            out_f.write(extent_text[:-extent_text[-1]])
            out_f.close()
            f.close()


def read_m3u8_info(index: str) -> (bool, str, str):
    global BASE_DIR
    f = open(BASE_DIR + '\\cache\\info\\' + index + ".config", "r")
    file_ = f.read()
    f.close()
    file_ = file_.split('\n')
    method = file_[0].split(':')[1]
    encrypt = method != 'NONE'
    key = file_[1].split(':')[1]
    return encrypt, method, key


def integrate_m3u8_frag(frag_path: str, out_put_path: str):
    global BASE_DIR
    print("开始合并分段")
    path_root = frag_path
    def sortF(x: str):
        return int(x.split(".")[0])
    f_list = list()
    for f in os.listdir(frag_path):
        if os.path.isfile(os.path.join(path_root, f)):
            f_list.append(f)
    f_list = list(sorted(f_list, key=sortF))
    index_path = BASE_DIR + "\\cache\\INDEX"
    f = open(index_path, "w+")
    for file_name in f_list:
        f.write(f"file {os.path.join(path_root, file_name)}\n".replace('\\', '/'))
    f.close()
    os.system(f'ffmpeg -f concat -safe 0 -i {index_path} -c copy ' + out_put_path)
    print("合并完毕！！")


def clear_folder(folder_path: str, remove_self: bool):
    for file_name in os.listdir(folder_path):
        path = os.path.join(folder_path, file_name)
        if os.path.isfile(path):
            os.remove(path)
        else:
            os.rmdir(path)
    if remove_self:
        os.rmdir(folder_path)


def main():
    global BASE_DIR
    try:
        while True:
            operate = input(Fore.GREEN + Style.BRIGHT + "====================================\n欢迎使用m3u8解析程序，\
made by 凛冻冻\n食用之前请先使用 'main.exe' 拦截数据包哦！！\n\
====================================\n解析视频输入1 退出程序2 :: ")
            if operate == '2':
                break
            m3u8_list, base_path = scan_m3u8()
            if not m3u8_list:
                print(Fore.RED + "未扫描到索引文件，请先使用 'main.exe' 拦截数据包哦！！！\n")
                continue
            for x in range(len(m3u8_list)):
                print(f"序号 {x}  ::  {m3u8_list[x]}")
            index = int(input("扫描到以上索引文件，请选择要下载的视频，并在这里输入回车 :: "))
            if index < 0 or index >= len(m3u8_list):
                print(Fore.RED + '请输入一个有效值[○･｀Д´･ ○]')
                continue
            index_name = m3u8_list[index]
            file_name = input("请为你的视频指定一个保存名称记得带后缀！！(xxx.mp4)  ::  ")
            thread_count = int(input("请设定下载线程数 ::  "))
            if thread_count < 1:
                thread_count = 1
            CACHE_DIR = BASE_DIR + "\\cache\\download\\" + index_name
            m3u8_list = parse_download_list(base_path + index_name)
            thread_list = []
            if os.path.exists(CACHE_DIR):
                print("检测到缓存文件夹，即将继续下载")
                index = 0
                while index < len(m3u8_list):
                    if os.path.exists(CACHE_DIR + f"\\{str(m3u8_list[index].index)}.ts"):
                        del m3u8_list[index]
                        continue
                    index += 1
            else:
                os.makedirs(CACHE_DIR, exist_ok=True)
            while True:
                for x in range(0, len(m3u8_list), thread_count):
                    print(Fore.YELLOW + "下载中... {:.2f}%".format(x / len(m3u8_list) * 100))
                    for y in range(thread_count):
                        index = x + y
                        if index >= len(m3u8_list):
                            break
                        f_path = CACHE_DIR + f"\\{str(m3u8_list[index].index)}.ts"
                        thr = threading.Thread(target=download_frag, args=(f_path, m3u8_list[index].url))
                        thr.start()
                        thread_list.append(thr)
                    for thr in thread_list:
                        thr.join()
                    thread_list.clear()
                index = 0
                while index < len(m3u8_list):
                    if os.path.exists(CACHE_DIR + f"\\{str(m3u8_list[index].index)}.ts"):
                        del m3u8_list[index]
                        continue
                    index += 1
                if not m3u8_list:
                    break
                operate = input(Fore.RED + "检测到有下载失败的分段！是否重新下载！如是输入1 ::  ")
                if operate != '1':
                    break
            if m3u8_list:
                continue
            print(Fore.GREEN + "下载完成！")
            encrypt, method, key = read_m3u8_info(index_name)
            if encrypt:
                decode_m3u8(CACHE_DIR, method, key.encode())
            integrate_m3u8_frag(BASE_DIR + '\\cache\\download\\decode' if encrypt else CACHE_DIR, \
                                BASE_DIR + '\\download\\video\\' + file_name)
            operate = input(Fore.GREEN + f"视频下载完成啦！！保存到路径：download/video/{file_name}\n是否删除索引和缓存信息？如是输入1  ::  ")
            if operate == '1':
                clear_folder(CACHE_DIR, True)
                if encrypt:
                    clear_folder(BASE_DIR + '\\cache\\download\\decode', False)
                os.remove(base_path + index_name)
                os.remove(BASE_DIR + '\\cache\\info\\' + index_name + ".config")
    except Exception as e:

        print("发生错误！程序终止！错误信息：", e, \
                  "\n异常文件：", e.__traceback__.tb_frame.f_globals["__file__"], \
                  "\n异常行数：", e.__traceback__.tb_lineno, \
                  "\n请将以上信息反馈给凛冻冻。")
        input("按回车退出程序 >>>>")


if __name__ == "__main__":
    main()
