import os
import time

import json5
import requests


def get_url_json():
    # 请求json数据
    url = "https://api.lige.fit/getJson"
    response = requests.get(url)
    if response.status_code == 200:
        with open("url.json", "wb") as file:
            print(response.content)
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

# 生成节目单
def generate_playlist():
    # 循环打开节目生成模板下的所有文件



def main():
    get_iptv_list()
    # print("选择一个操作:")
    # print("1. 请求JSON数据并下载文件")
    # choice = input("输入数字选择操作: ")
    #
    # if choice == "1":
    #     download_json()
    # else:
    #     print("无效的选择。")


if __name__ == "__main__":
    main()
