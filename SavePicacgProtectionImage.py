from selenium import webdriver
from selenium.webdriver.common.by import By
from colorama import init,Fore,Back,Style
import time
import os
import re
import sys
import warnings
import requests

warnings.filterwarnings("ignore")

init(autoreset=True)

print(Fore.YELLOW + "请选择要使用的浏览器驱动(需要安装相应浏览器)1火狐2 EDGE" + Fore.RESET)
driver = None;
if(input() == "1"):
    print(Fore.GREEN + "正在加载驱动。。。请稍后" + Fore.RESET)
    from selenium.webdriver.firefox.options import Options
    more_options = Options()
    more_options.add_argument("--headless")
    driver = webdriver.Firefox("firefoxdriver",options=more_options)
else:
    print(Fore.GREEN + "正在加载驱动。。。请稍后" + Fore.RESET)
    from selenium.webdriver.edge.options import Options
    more_options = Options()
    more_options.add_argument("--headless")
    driver = webdriver.Edge("edgedriver",options=more_options)

driver.get("https://www.baidu.com")
print(Fore.YELLOW + "驱动启动完毕！" + Fore.RESET)
print(Fore.YELLOW + "获取庇护所新域名中。。。" + Fore.RESET)

resources = requests.get("https://soapi.01linkjump.top/?chhost=ios&tqwtqt")
resources.encoding = "utf-8"
domain = re.search(r"(https://[^#|$]*?\")",resources.text).group().replace("\"","/")
resources.close()
print(Fore.GREEN + "域名获取成功!" + Fore.RESET)

mainwindow = driver.window_handles[0]

class pathInfo():
    def __init__(self,path:str,loaded:bool):
        self.path = path
        self.loaded = bool
    def isLoaded(self):
        return self.loaded

def openNewWindow(url):
    global driver
    driver.get(url)

def changeThisWindow(url):
    js = "window.open('" + url + "','_self');"
    global driver
    driver.execute_script(js)

def getCurrentPageImage(count,image_timer,error_information,page_count):
    global driver
    img_path_list = []
    for x in driver.find_elements(By.CSS_SELECTOR,".view-header"):
        for i in x.find_elements(By.CSS_SELECTOR,"p > img"):
            path = i.get_attribute("data-src")
            loaded = False
            if("loaded" in i.get_attribute("class")):
                loaded = True
            element = pathInfo(path,loaded)
            img_path_list.append(element)
    now_count = 1;
    for path in img_path_list:
        print("正在请求第" + str(count) + "张图片....")
        if(path.isLoaded()):
            resources = requests.get(path.path)
            #driver.get(path.path)
            if(resources.status_code == 429):
                print(Fore.RED + "啊偶！访问过快被拦截了！稍后重新请求！" + Fore.RESET)
                error_information.append(page_count + "," + str(now_count))
            else:
                #driver.get_full_page_screenshot_as_file("image/" + str(count) + ".png")
                resources.encoding = "utf-8"
                if("We cannot" in resources.text):
                    print(Fore.RED + "第" + str(count) + "张图片的图床君已阵亡.....\n出错地址：" + path.path)
                else:
                    file = open("image/" + str(count) + ".jpg","wb")
                    file.write(resources.content)
                    file.close()
                    print(Fore.GREEN + "第" + str(count) + "张图片保存成功。" + Fore.RESET)
            resources.close()
        else:
            print(Fore.RED + "第" + str(count) + "张图片的图床君已阵亡.....\n出错地址：" + path.path)
            
        time.sleep(image_timer)
        count += 1;
        now_count += 1;
    return count

def currentPageHasNext():
    global driver
    flag = False
    try:
        driver.find_element(By.CSS_SELECTOR,".next-coll")
        flag = True
    except:
        flag = False
    return flag

def ToanimationPage(anim_id:str,page_id:str,pline_id:str):
    global driver
    global domain
    print("正在请求" + anim_id + "的第" + page_id + "页，若请求时间过长可尝试挂代理或换线路...")
    openNewWindow(domain + anim_id + "/"+ page_id + "/?pline=" + pline_id)


while(True):
    print(Fore.CYAN + "请输入要获取的本子id和线路（不输入默认1），用空格隔开。\n"+ Fore.RESET+ Fore.RED+"退出程序输入quit，非正常退出会残留程序！"+Fore.RESET)
    value = input().split(" ")
    if(value[0] == "quit"):
        print(Fore.YELLOW + "程序正在退出。" + Fore.RESET)
        driver.quit()
        sys.exit()
        break
    animation_id = 0;
    pline_id = "1";
    if(len(value) > 1):
        pline_id = value[1]
    animation_id = value[0]
    print(Fore.YELLOW + "请输入图片获取间隔(建议1.0，如果经常提示访问过快可以调慢点！)\n和翻页间隔(建议1.0)用空格隔开，防止爬崩网页"+Fore.RESET)
    value = input().split(" ")
    image_timer = float(value[0])
    page_timer = float(value[1])
    page_count = 1;
    error = list()
    ToanimationPage(animation_id,str(page_count),pline_id)
    count = 1;
    while(True):
        hasnext = currentPageHasNext()
        count = getCurrentPageImage(count,image_timer,error,str(page_count))
        if(hasnext):
            page_count += 1;
            time.sleep(page_timer)
            ToanimationPage(animation_id,str(page_count),pline_id)
        else:
            if(len(error) != 0):
                print(Fore.RED + "检测到有部分图片未请求成功，输入1重新请求，输入2取消请求。" + Fore.RESET)
                value = input()
                if(value == "1"):
                    while(True):
                        error_info_dict = dict()
                        for info in error:
                            sp = info.split(",")
                            if(error_info_dict.get(sp[0],"null") == "null"):
                                error_info_dict[sp[0]] = sp[1]
                            else:
                                error_info_dict[sp[0]] += ("," + sp[1])
                        for info in error_info_dict.keys():
                            print(Fore.RED + "正在重新请求第" + info + "页。" + Fore.RESET)
                            while(True):
                                driver.get(domain + animation_id + "/" + info + "/?pline=" + pline_id)
                                elements = driver.find_elements(By.CSS_SELECTOR,".view-header > p > img")
                                img_id_list = error_info_dict[info].split(",")
                                links = list()
                                for x in img_id_list:
                                    links.append(elements[int(x)])
                                error_again = False
                                now_count = 0;
                                for x in links:
                                    resources = requests.get(x)
                                    #driver.get(x)
                                    if(resources.status_code == 429):
                                        print(Fore.RED + "啊奥！还是访问过快了！" + Fore.RESET)
                                        error_again = True
                                        continue
                                    else:
                                        #driver.get_full_page_screenshot_as_file("image/" + str(img_resident_id) + ".png")
                                        file = open("image/" + str(img_resident_id) + ".png","wb")
                                        file.write(resources.content)
                                        file.close()
                                        del img_id_list[now_count]
                                        now_count += 1;
                                        print(Fore.GREEN + "第" + info + "页的第" + str(now_count) + "张图片抢救成功。" + Fore.RESET)
                                        #print(Fore.GREEN + "第" + info + "页的第" + str(now_count) "张出错图片保存成功。" + Fore.RESET)
                                        
                                    resources.close()
                                if(error_again):
                                    print(Fore.RED + "检测到本页仍然保存失败，输入1继续请求，输入2跳过本页。" + Fore.RESET)
                                    value = input()
                                    if(value == "1"):
                                        error_info_dict[info] = ",".join(img_id_list)
                                    else:
                                        break
                            
            print(Fore.GREEN+"\n全部图片已保存至运行目录image/下！每次使用请清理。"+Fore.RESET + Fore.YELLOW+"\n\n1.如提示“图床君阵亡”则表示图床服务器挂了。(服务器问题)\n2.如图片显示“xx因存在错误而无法显示”则表示服务器挂了\n3.访问速度太慢尝试挂代理或换线路\n\n"+Fore.RESET)
            break

