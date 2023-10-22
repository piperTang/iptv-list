import os
import threading
import orjson
import requests
from multiprocessing import Manager
import m3u8


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
            json_data = json_file.read()
            data = orjson.loads(json_data)
    finally:
        json_file.close()

    # 创建线程列表
    threads = []

    # 循环获取json文件
    for i in range(len(data)):
        # 创建线程并启动它，down_vbox_json()函数传递给线程
        thread = threading.Thread(target=down_vbox_json, args=(data[i],))
        threads.append(thread)

    # 批量开启线程
    for thread in threads:
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()


# 下载json文件
def down_vbox_json(data):
    print("正在下载: " + data["name"])
    # 请求json数据
    url = "https://api.lige.fit/ua"
    res_data = {
        "url": data["url"]
    }

    response = requests.post(url, res_data)
    # print(response.text)
    if response.status_code == 200:
        # print(response.text)
        # 替换文件名中的/字符
        data["name"] = data["name"].replace("/", "")
        with open("vbox配置/" + data["name"] + ".json", "wb") as file:
            # print(response.text)
            content = response.text
            # 去除注释行（以双斜杠 # 开头的行）和其他不必要内容
            lines = content.split('\n')
            cleaned_lines = [line for line in lines if not line.strip().startswith("#")]
            # 去除 // 开头的注释行
            cleaned_lines = [line for line in cleaned_lines if not line.strip().startswith("//")]
            cleaned_content = ''.join(cleaned_lines)

            file.write(cleaned_content.encode("utf-8"))
        print("已下载文件: " + data["name"] + ".json")


# 下载配置文件中的所有直播源
def get_iptv_list():
    # 获取当前文件夹的路径
    current_directory = os.path.dirname(os.path.realpath(__file__))
    vbox_config_directory = os.path.join(current_directory, "vbox配置")

    # 创建线程列表
    threads = []

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
                    json_data = orjson.loads(content)
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
                                url_json_data = json_file.read()
                                data = orjson.loads(url_json_data)
                                for i in range(len(data)):
                                    if data[i]["name"] == file_name.replace(".json", ""):
                                        iptv_url = data[i]["url"] + iptv_url
                                        break
                        finally:
                            json_file.close()
                    # 创建线程并启动它，down_iptv_list()函数传递给线程
                    thread = threading.Thread(target=down_iptv_list, args=(iptv_url, file_name))
                    threads.append(thread)
                    thread.start()

            # 报错
            except Exception as e:
                print(f"打开错误： {file_name} : {e}")

    # 等待所有线程完成
    for thread in threads:
        thread.join()


def down_iptv_list(iptv_url, file_name):
    print(iptv_url)
    print("正在下载: " + file_name)
    response = requests.get(iptv_url)
    if response.status_code == 200:
        with open("直播源/" + file_name.replace(".json", ".txt"), "wb") as iptv_txt:
            iptv_txt.write(response.content)
        print("已下载文件: " + file_name)
    else:
        print("下载失败: " + file_name)


# 修改check_iptv_thread()函数，以将结果存储在共享数据结构中
def check_iptv_thread(url, result_dict):
    try:
        # 发出HTTP请求获取M3U8文件内容
        response = requests.get(url)
        response.raise_for_status()

        # 解析M3U8文件
        m3u8_obj = m3u8.loads(response.text)

        # 检查是否有有效的视频流
        if m3u8_obj.data.get('segments'):
            print("M3U8链接可正常播放:"+url)
            result_dict[url] = True
        else:
            print("M3U8链接没有有效的视频流:"+url)
            result_dict[url] = False
            # print("M3U8链接没有有效的视频流")

    except requests.exceptions.RequestException as e:
        print("无法访问M3U8链接:", e)
        result_dict[url] = False
    except Exception as e:
        result_dict[url] = False
        print("无法解析M3U8文件:", e)


# 生成节目单
def generate_playlist(file_list):
    # 定义文件结果
    result = []
    # 循环打开 json 文件
    for file_name in file_list:
        with open("节目生成模板/" + file_name + '.json', "r", encoding="utf-8") as json_file:
            json_data = json_file.read()
            template_data = orjson.loads(json_data)
            # 先往 result 数组中写入标题
            print("--------------------------------------------------")
            print(file_name)
            result.append(f"{file_name},#genre#\n")

            # 创建线程列表
            threads = []

            # 创建一个共享的字典
            manager = Manager()
            result_dict = manager.dict()

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
                                        # 检测直播源是否可用
                                        # 创建线程并启动它，check_iptv_thread()函数传递给线程
                                        thread = threading.Thread(target=check_iptv_thread,
                                                                  args=(play_url, result_dict))
                                        threads.append(thread)
            # 打印当前线程数
            print("当前线程数: " + str(len(threads)) + ",正在检测直播源是否可用")
            # 批量开启线程
            for thread in threads:
                thread.start()

            # 等待所有线程完成
            for thread in threads:
                thread.join()

            # 对 JSON 数据进行循环
            for item in template_data:
                name = item.get("name", "")
                rules = item.get("rule", "")
                for rule in rules:
                    # 根据规则查找匹配的行并写入到 index.txt
                    current_directory = os.getcwd() + "/直播源"
                    iptv_files = os.listdir(current_directory)
                    # 迭代检查结果，根据结果来生成节目列表
                    for iptv_file in iptv_files:
                        with open(current_directory + "/" + iptv_file, "r", encoding="utf-8") as source_file:
                            for line in source_file:
                                if line.startswith(f"{rule},"):
                                    # 防止重复写
                                    if line not in result:
                                        # 对line进行处理
                                        line = line.replace(f"{rule},", name + ",")
                                        for key, value in result_dict.items():
                                            if value:
                                                result.append(line)
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
                print("--------------------------------------------------")
                # 清空 result 数组
                result.clear()


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
