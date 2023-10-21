import os
import time
import json5
import requests
from urllib import request
from urllib.parse import urlparse


def get_url_json():
    # 请求json数据
    url = "https://api.lige.fit/getJson"
    response = requests.get(url)
    if response.status_code == 200:
        with open("url.json", "wb") as file:
            # print(response.content)
            file.write(response.content)
        print("已下载文件: url.json")


# 直播源的json
def get_vbox_config():
    # 读取json文件
    try:
        with open("url.json", "r", encoding="utf-8") as json_file:
            data = json5.load(json_file)
    finally:
        json_file.close()

    # 循环获取json文件
    for i in range(len(data)):
        print("正在下载: " + data[i]["name"])
        # 请求json数据
        url = "https://api.lige.fit/ua"
        res_data = {
            "url": data[i]["url"]
        }

        response = requests.post(url, res_data)
        # print(response.text)
        if response.status_code == 200:
            # print(response.text)
            # 替换文件名中的/字符
            data[i]["name"] = data[i]["name"].replace("/", "")
            with open("vbox配置/" + data[i]["name"] + ".json", "wb") as file:
                # print(response.text)
                content = response.text
                # 去除注释行（以双斜杠 # 开头的行）和其他不必要内容
                lines = content.split('\n')
                cleaned_lines = [line for line in lines if not line.strip().startswith("#")]
                # 去除 // 开头的注释行
                cleaned_lines = [line for line in cleaned_lines if not line.strip().startswith("//")]
                cleaned_content = ''.join(cleaned_lines)

                file.write(cleaned_content.encode("utf-8"))
            print("已下载文件: " + data[i]["name"] + ".json")
        # 休息一秒
        time.sleep(1)


# 下载配置文件中的所有直播源
def get_iptv_list():
    # 获取当前文件夹的路径
    current_directory = os.path.dirname(os.path.realpath(__file__))
    vbox_config_directory = os.path.join(current_directory, "vbox配置")

    # 遍历目录中的文件
    for file_name in os.listdir(vbox_config_directory):
        if file_name.endswith(".json"):  # 仅处理JSON格式的文件
            file_path = os.path.join(vbox_config_directory, file_name)
            # 跳过空文件
            if os.path.getsize(file_path) == 0:
                continue
            # 以 <!DOCTYPE 开头的文件不是JSON文件
            with open(file_path, "r", encoding="utf-8") as file:
                first_line = file.readline()
                if first_line.startswith("<!DOCTYPE"):
                    continue
            # print(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    json_data = json5.loads(content)
                    # 读取lives数组
                    # 判断是否有lives数组
                    if "lives" not in json_data:
                        continue
                    # 判断lives中是否有url数据
                    if "url" not in json_data["lives"][0]:
                        continue

                    iptv_url = json_data["lives"][0]["url"]
                    # 判断iptv_url 开头是否为 http:// 或 https://
                    if not iptv_url.startswith("http://") and not iptv_url.startswith("https://"):
                        # 根据文件名，在url.json中查找对应的url
                        try:
                            with open("url.json", "r", encoding="utf-8") as json_file:
                                data = json5.load(json_file)
                                for i in range(len(data)):
                                    if data[i]["name"] == file_name.replace(".json", ""):
                                        iptv_url = data[i]["url"] + iptv_url
                                        break
                        finally:
                            json_file.close()
                    print(iptv_url)
                    print("正在下载: " + file_name)
                    response = requests.get(iptv_url)
                    if response.status_code == 200:
                        with open("直播源/" + file_name.replace(".json", ".txt"), "wb") as iptv_txt:
                            iptv_txt.write(response.content)
                        print("已下载文件: " + file_name)
                    else:
                        print("下载失败: " + file_name)
            # 报错
            except Exception as e:
                print(f"打开错误： {file_name} : {e}")
            finally:
                file.close()


# 替换字符串string中指定位置p的字符为c
def sub(string, p, c):
    new = []
    for s in string:
        new.append(s)
    new[p] = c
    return ''.join(new)


def readM3U8(url):
    s_url = None
    response = requests.get(url)
    response.encoding = 'utf-8'
    str = response.text
    result = urlparse(url)
    url_tou = result[0] + '://' + result[1]

    # 获取m3u8中的片段ts文件
    # 需要替换 ../
    list = str.split("\n")
    for str in list:

        if str.find(".ts") != -1:
            # 特殊格式==>回退目录
            if (str.find("../../../../..") != -1):
                s_url = str.replace("../../../../..", url_tou)
            # 普通格式，直接替换，如果ts文件的开头是/则表示根目录
            else:
                if str[0:1] == '/':
                    s_url = sub(str, 0, url_tou + "/")
                else:
                    pos = url.rfind("/")
                    s_url = url.replace(url[pos:], "/" + str)

            break

    return check_iptv(s_url)


# 检测直播源是否可用
def check_iptv(url):
    try:
        with request.urlopen(url) as file:
            if file.status != 200:
                return False
            else:
                return True
    except BaseException as err:
        return False


# 生成节目单
def generate_playlist(file_list):
    # 定义文件结果
    result = []
    # 读取黑名单文件
    blacklist = set()
    with open("节目列表/黑名单.txt", "r", encoding="utf-8") as blacklist_file:
        for line in blacklist_file:
            blacklist.add(line.strip())
    # 循环打开 json 文件
    for file_name in file_list:
        with open("节目生成模板/" + file_name + '.json', "r", encoding="utf-8") as json_file:
            template_data = json5.load(json_file)  # 加载 JSON 数据
            # 先往 result 数组中写入标题
            print(file_name)
            result.append(f"{file_name},#genre#\n")
            # 对 JSON 数据进行循环
            for item in template_data:
                name = item.get("name", "")
                rules = item.get("rule", "")
                for rule in rules:
                    # 根据规则查找匹配的行并写入到 index.txt
                    current_directory = os.getcwd() + "/直播源"
                    iptv_files = os.listdir(current_directory)

                    for iptv_file in iptv_files:
                        with open(current_directory + "/" + iptv_file, "r", encoding="utf-8") as source_file:
                            for line in source_file:
                                if line.startswith(f"{rule},"):
                                    # 防止重复写
                                    if line not in result:
                                        # 对line进行处理
                                        line = line.replace(f"{rule},", name + ",")
                                        # 根据逗号拆分，获取url
                                        play_url = line.split(",")[1]
                                        if play_url in blacklist:
                                            print("(直播源在黑名单中)" + name + ":" + play_url)
                                            continue
                                        # 检测直播源是否可用
                                        if check_iptv(play_url):
                                            result.append(line)
                                            print("(直播源可用)" + name + ":" + play_url)
                                        else:
                                            # 添加到黑名单
                                            blacklist.add(play_url)
                                            print("(直播源失效，加入黑名单)" + name + ": " + play_url)

            # 把数据写入到 节目列表文件夹
            with open("节目列表/" + file_name + ".txt", "w", encoding="utf-8") as output_file:
                # 定义一个数组，用于存储已经写入的行
                written_lines = []
                for line in result:
                    # 防止重复写
                    if line in written_lines:
                        continue
                    else:
                        written_lines.append(line)
                    output_file.write(line)
                # 文件写入成功
                print("已写入文件: " + file_name + ".txt")
                # 清空 result 数组
                result.clear()
    # 对黑名单进行去重
    blacklist = set(blacklist)
    # 把黑名单写入到文件
    with open("节目列表/黑名单.txt", "w", encoding="utf-8") as blacklist_file:
        for line in blacklist:
            blacklist_file.write(line + "\n")
    print("已写入文件: 黑名单.txt")


# 读取节目列表所有文件，合并到index.txt
def merge_playlist():
    file_list = ["央视频道", "卫视频道", "广东频道", "港澳台", "少儿频道"]
    # 获取当前目录下的所有文件
    current_directory = os.getcwd() + "/节目列表"
    playlist_files = [f for f in os.listdir(current_directory) if f.endswith(".txt")]

    # 打开或创建 index.txt 文件，以覆盖模式写入
    with open("index.txt", "w", encoding="utf-8") as index_file:
        # 遍历每个文件名，按照指定顺序合并文件
        for file_name in file_list:
            if file_name + ".txt" in playlist_files:
                print("正在合并: " + file_name + ".txt")
                with open("节目列表/" + file_name + ".txt", "r", encoding="utf-8") as source_file:
                    # 读取每个节目列表文件的内容并写入到 index.txt
                    for line in source_file:
                        index_file.write(line)

    # 文件写入成功
    print("已覆盖文件: index.txt")


def main():
    file_list = ["央视频道", "卫视频道", "广东频道", "港澳台", "少儿频道"]
    get_url_json()
    get_vbox_config()
    get_iptv_list()
    generate_playlist(file_list)
    merge_playlist()


if __name__ == "__main__":
    main()
