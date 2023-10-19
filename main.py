import os
import json
import requests


# 直播源的json
def download_json():
    # 读取json文件
    try:
        with open("url.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    finally:
        json_file.close()
    for key, url in data.items():
        try:
            print(url)
            response = requests.get(url)
            print(response)
            if response.status_code == 200:
                with open(f"{key}.txt", "wb") as file:
                    file.write(response.content)
                print(f"已下载文件: {key}.txt")
            else:
                print(f"下载文件 {key} 失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"下载文件 {key} 时发生错误: {str(e)}")


def main():
    print("选择一个操作:")
    print("1. 请求JSON数据并下载文件")
    choice = input("输入数字选择操作: ")

    if choice == "1":
        download_json()
    else:
        print("无效的选择。")


if __name__ == "__main__":
    main()
