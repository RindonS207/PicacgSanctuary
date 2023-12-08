# PicacgSanctuary
本程序通过selenium访问网页，然后xpath定位元素来查找图片下载地址。而视频下载则是通过mitmproxy监听数据包，然后抓取m3u8文件，最后解析下载m3u8文件使用ffmpeg合并！！

## 使用者 > 
使用此脚本需要安装火狐浏览器、ffmpeg！！先把这两个添加到全局变量！

## 开发者 > 
本脚本使用到selenium等模块，没安装的要使用pip安装哟。因为开发的时候没用虚拟环境emmmm要是缺包了就自己找把。
可以在release下载到原项目包和可执行包。

```
pip install selenium
pip install yaml
pip install mitmproxy
pip install m3u8
pip install cryptography
```

## 更新记录 >

### v1.2
暂时移除了对Edge的支持，火狐好用的一批！
添加了下载视频功能
添加了多线程下载功能

### v1.1
添加了Edge驱动的支持，优化了下载图片的方式，添加了请求失败重新请求的功能

### v1.0
脚本完成，支持火狐浏览器驱动

## 更新预告 >

暂时没有什么想法了，再更新应该是支持其他驱动，或者是换一个使用的自动化框架。
