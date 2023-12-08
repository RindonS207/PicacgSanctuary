import mitmproxy.http
from mitmproxy import ctx, http
import datetime
import socket
import re
import requests


class Listener(object):

    def __init__(self):
        f = open("cache/PORT", "r")
        p = f.read()
        f.close()
        self.SAVE_PATH = ""
        self.SERVER_ADDRESS = ("localhost", int(p))
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def response(self, stream: mitmproxy.http.HTTPFlow):
        if stream.response.headers.get("Content-type", None) == 'application/vnd.apple.mpegurl':
            data = stream.response.content[:300]
            if self.is_index_file(data):
                string = self.save_index_file(stream)
                self.SOCKET.sendto(("YES#index_" + string).encode("utf-8"), self.SERVER_ADDRESS)

    def is_index_file(self, data: bytes):
        data = data.decode('utf-8')
        return "EXTINF" in data

    def save_index_file(self, stream: mitmproxy.http.HTTPFlow) -> str:
        data = stream.response.content.decode('utf-8')
        data = self.clearAD(data.split("\n"))
        regex = r"^https?://.+"
        req_url = "https://" + stream.request.host + ":" + str(stream.request.port) + \
                  stream.request.path[:stream.request.path.rfind('/')]
        for index in range(len(data)):
            d = data[index]
            if not d:
                continue
            if d[0] == '#':
                continue
            if not re.match(regex, d):
                if d[0] == '/':
                    data[index] = req_url + d
                else:
                    data[index] = req_url + "/" + d
        key = "NONE"
        encrypt_method = "NONE"
        for line in data[:20]:
            if "#EXT-X-KEY:" in line:
                line = line[11:]
                line = line.split(",")
                encrypt_method = line[0].split("=")[1]
                key = line[1].split("=")[1].replace('"',"")
                key_url = ""
                if re.match(regex, key):
                    key_url = key
                else:
                    if key[0] == '/':
                        key_url = req_url + key
                    else:
                        key_url = req_url + "/" + key
                key_res = requests.get(key_url)
                key_res.encoding = "utf-8"
                key = key_res.text
        data = "\n".join(data)
        f_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + ".m3u8"
        f = open("cache/content/index_" + f_name, "w+", encoding="utf-8")
        f.write(data)
        f.close()
        f = open("cache/info/index_" + f_name + ".config", "w+", encoding='utf-8')
        f.write("METHOD:" + encrypt_method + "\nKEY:" + key)
        f.close()
        return f_name

    def find_element(self, l, e, i=0):
        index = i
        for x in range(index, len(l)):
            element = l[x]
            if element == e:
                return x
        return -1

    def clearAD(self, m3u8):
        while True:
            index = self.find_element(m3u8, "#EXT-X-DISCONTINUITY")
            if index == -1:
                break
            sub_index = self.find_element(m3u8, "#EXT-X-DISCONTINUITY", index + 1)
            if sub_index != -1:
                del m3u8[index:sub_index + 1]
                while "EXTINF" not in m3u8[index]:
                    del m3u8[index]
            else:
                sub_index = self.find_element(m3u8, "#EXT-X-ENDLIST", index)
                del m3u8[index:sub_index]
        return m3u8

    def save_package(self, stream: mitmproxy.http.HTTPFlow, is_request: bool = True,
                      message_path: str = "", body_path: str = ""):
        if message_path:
            if '\\' in message_path and message_path[-1] != '\\':
                message_path += '\\'
            if '/' in message_path and message_path[-1] != '/':
                message_path += '/'
            if '\\' not in message_path and '/' not in message_path:
                message_path += '/'
        if body_path:
            if '\\' in body_path and body_path[-1] != '\\':
                body_path += '\\'
            if '/' in body_path and body_path[-1] != '/':
                body_path += '/'
            if '\\' not in body_path and '/' not in body_path:
                body_path += "/"
        f_name = str(("REQ_" if is_request else "RES_") + stream.request.host + \
                     datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f"))
        f = open(message_path + f_name + '.txt', "w+")
        if is_request:
            f.write(stream.request.method + " " + stream.request.scheme + " " + stream.request.host + ":" + \
                str(stream.request.port) + "\n" + str(stream.request.headers))
        else:
            f.write(str(stream.response.status_code) + " " + stream.response.reason + " " + stream.response.http_version + \
                    "来自:" + stream.request.host + ":" + str(stream.request.port) + "\n" + str(stream.response.headers))
        f.close()
        if (stream.request and stream.request.content) or (stream.response and stream.response.content):
            f = open(body_path + f_name + ".bin", "wb+")
            if is_request:
                f.write(stream.request.content)
            else:
                f.write(stream.response.content)
            f.close()



