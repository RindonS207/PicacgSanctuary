import os.path
import random
import subprocess
import socket
import threading
import time
import requests
import sys

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from colorama import Fore, Style, init
import yaml

UPSTREAM_PROXY = ''
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
init(autoreset=True)


class DownloadInfo(object):

    def __init__(self, url, save_path):
        self.url = url
        self.path = save_path


def download_img(url, path):
    if os.path.exists(path):
        return
    resources = None
    try:
        resources = requests.get(url)
        f = open(path, "wb+")
        f.write(resources.content)
        f.close()
    except requests.HTTPError as e:
        print(f"下载 {url} 失败！可能图床阵亡或是访问过快！\n状态码：{resources.status_code}\n提示信息：" + str(e))


def main():

    driver = None

    try:
        create_new = True
        yml_obj = None
        global BASE_DIR, UPSTREAM_PROXY
        if os.path.exists("cache/config.yaml"):
            try:
                f = open("cache/config.yaml", "r", encoding="utf-8")
                yml_obj = yaml.load(f.read(), Loader=yaml.FullLoader)
                f.close()
                create_new = False
            except FileNotFoundError as e:
                create_new = True

        if create_new:
            print("第一次运行，开始设置配置文件。")
        else:
            print("代理：", "无" if yml_obj["proxy"] == "NONE" else yml_obj["proxy"])
            create_new = True if input("检测到存在的配置文件，是否重新设置？如是输入1") == '1' else False

        if create_new:
            px = input("如果你使用了代理，请输入代理的地址(例如http://localhost:7890)，否则留空：")
            proxy_string = "NONE" if px == '' else px;
            data = {
                "proxy": proxy_string,
            }
            f = open("cache/config.yaml", "w+", encoding="utf-8")
            yaml.dump(data=data, stream=f, allow_unicode=True)
            f.close()
            if yml_obj:
                yml_obj['proxy'] = proxy_string
        UPSTREAM_PROXY = yml_obj['proxy'] if yml_obj else proxy_string

        udp_port = random.randint(10000, 60000)
        # udp_port = 50133
        mitm_port = random.randint(10000, 60000)
        # mitm_port = 10086
        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server.bind(("localhost", udp_port))
        udp_server.settimeout(False)

        f = open("cache/PORT", "w+")
        f.write(str(udp_port))
        f.close()
        ''''''
        cmd = f'"tool/mitmdump.exe" -p {mitm_port} -s addon.py '
        if UPSTREAM_PROXY != "NONE":
            print("开启二级代理模式，地址：", UPSTREAM_PROXY)
            cmd += "--mode upstream:" + UPSTREAM_PROXY
        # print("启动参数：", cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

        p = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': f'127.0.0.1:{mitm_port}',
            'sslProxy': f'127.0.0.1:{mitm_port}'
        })

        opts = FirefoxOptions()
        opts.proxy = p
        opts.add_argument('--ignore-certificate-errors')
        # opts.add_argument('--user-data-dir="cachebrowser"')
        opts.add_argument('--headless')
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        opts.set_preference("browser.cache.disk.parent_directory", current_dir + "\\cache\\broswer")
        driver = webdriver.Firefox(options=opts)
        print("如果是第一次使用可能会缓存很多内容！！请耐心等待或使用高速的网络！！")
        # while True:
        while not process.poll():
            # 程序主循环
            operate = input(Fore.GREEN + Style.BRIGHT + "====================================\n欢迎食用庇护所视频下载，\
made by 凛冻冻 v1.2\n食用方法：首先用此程序抓取M3U8文件，然后用文件夹下的'下载.exe'下载视频哦\
\n此脚本针对庇护所哦！！其它网站下载不了。\n====================================\n\
下载视频输入1 下载漫画输入2 退出输入3 ::")
            if operate == '2':
                # 下载漫画模块
                website = input("欢迎使用漫画下载模块！！此脚本针对庇护所哦！！其他网站下载不了！\n请输入漫画网址：")
                thread_count = int(input("请输入下载线程数："))
                wait_time = float(input("请输入下载间隔(防止拦截,单位秒,可小数)："))
                if wait_time < 0:
                    wait_time = 0
                if thread_count < 1:
                    thread_count = 1
                try:
                    driver.get(website)
                    download_list = []
                    thread_list = []
                    title = driver.find_element(By.XPATH, '//h4[contains(@class,"my-comic-title")]').text
                    base_save_path = 'download/comic/' + title + "/"
                    os.makedirs(base_save_path, exist_ok=True)
                    index = 0
                    for img in driver.find_elements(By.XPATH, '//*[@id="ep-1"]/img'):
                        download_list.append(DownloadInfo(img.get_attribute("data-src"), \
                                                          base_save_path + str(index) + '.jpg'))
                        index += 1
                    # 进入下载
                    while True:
                        for x in range(0, len(download_list), thread_count):
                            print(Fore.YELLOW + "下载中... {:.2f}%".format(x / len(download_list) * 100))
                            for y in range(thread_count):
                                i = x + y
                                if i >= len(download_list):
                                    break
                                thr = threading.Thread(target=download_img, \
                                                       args=(download_list[i].url, download_list[i].path))
                                thr.start()
                                thread_list.append(thr)
                            for thr in thread_list:
                                thr.join()
                            thread_list.clear()
                            time.sleep(wait_time)
                        print(Fore.YELLOW + "下载中... 100%")
                        i = 0
                        # 检查下载成功的内容
                        while i < len(download_list):
                            if os.path.exists(download_list[i].path):
                                del download_list[i]
                                continue
                            i += 1
                        if len(download_list) == 0:
                            break
                        operate = input(Fore.RED + f"检测到有 {len(download_list)} 个图片下载失败！重试吗？如是输入1")
                        if operate != '1':
                            break
                    print(Fore.RED + "下载内容已保存至 download/comic/" + title)
                except Exception as e:
                    print(Fore.RED + "下载失败！链接到页面失败！\n" + str(e))
                driver.get("about:blank")
                continue
            if operate == '3':
                # 程序退出
                break
            # M3U8提取模块
            website = input("请输入要提取视频的网址：")
            err = False
            try:
                driver.get(website)
            except:
                err = True
            if err:
                print(Fore.RED + "访问不到网页，请稍后再试。")
                continue
            t = 0
            while True:
                try:
                    if t == 3:
                        print(Fore.RED + "访问不到网页，请稍后再试。")
                        break
                    # 点击播放按钮
                    driver.find_element(By.XPATH, '//video').click()
                    break
                except:
                    t += 1
                    time.sleep(1)
            if t == 3:
                continue
            data = None
            max_time_out = 30
            time_step = 0
            print("监听数据包中....")
            while True:
                if time_step % 5 == 0:
                    print(Fore.YELLOW + f"监听数据包中... {time_step}")
                if time_step >= max_time_out:
                    operate = input(f"监听时间超过 {max_time_out} 秒了，要继续吗(通常需要刷新一次)？如是输入1 刷新2 取消3 ::")
                    if operate == '2':
                        print("界面刷新中...")
                        driver.refresh()
                        driver.find_element(By.XPATH, '//video').click()
                        time_step = 0
                        print("监听数据包中....")
                        continue
                    if operate == '3':
                        break
                    max_time_out += 30
                try:
                    data = udp_server.recv(2048)
                except BlockingIOError as e:
                    time_step += 1
                    time.sleep(1)
                    continue
                # print(type(data), data)
                data = data.decode('utf-8').split("#")
                if data[0] == 'YES':
                    print(Fore.GREEN + f"抓取成功，索引文件名 {data[1]}，请步移 ‘下载.exe’ 进行视频下载。")
                else:
                    print(Fore.RED + "抓取失败...可能索引文件已走丢，可重试/重启使用代理或更换一个视频。")
                break
            driver.get("about:blank")
        if not process.poll():
            process.terminate()
        print("程序已退出。")

    except Exception as e:

        print("发生错误！程序终止！错误信息：", e,\
              "\n异常文件：", e.__traceback__.tb_frame.f_globals["__file__"],\
              "\n异常行数：", e.__traceback__.tb_lineno,\
              "\n请将以上信息反馈给凛冻冻。")
        input("按回车退出程序 >>>>")

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()

