import time
import requests
import re
import orjson

# 定义一个空列表，用于存放所有的M3U8 URL
result = []


def get_m3u8_url(tv_name, keyword):
    # 设置请求头
    headers = {
        "Host": "tonkiang.us",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://tonkiang.us",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "http://tonkiang.us/",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "arp_scroll_position=0"
    }

    # 设置请求数据
    data = {
        "search": keyword,
        "Submit": "+"
    }
    # 发送HTTP请求
    url = "http://tonkiang.us/"
    response = requests.post(url, headers=headers, data=data, allow_redirects=False)
    # 输出响应内容
    # print(response.text)
    # 使用正则表达式匹配M3U8 URL
    m3u8_urls = re.findall(r'onclick=copyto\("([^"]+)"\)', response.text)

    if m3u8_urls:
        for url in m3u8_urls:
            result.append(tv_name + "," + url)
            print("M3U8 URL:", url)
    else:
        print("未找到M3U8 URL")
    # 使用正则表达式匹配分页页码
    page_pattern = r'href=\'\?page=(\d+)'
    page_numbers = re.findall(page_pattern, response.text)

    if page_numbers:
        # 获取最大页码
        max_page = max(page_numbers)
        # 开始循环
        for page in range(2, int(max_page)):
            url = "http://tonkiang.us/?page=" + str(page) + "&s=" + keyword
            response = requests.get(url, headers=headers, allow_redirects=False)
            # 输出响应内容
            # print(response.text)
            # 使用正则表达式匹配M3U8 URL
            m3u8_urls = re.findall(r'onclick=copyto\("([^"]+)"\)', response.text)
            if m3u8_urls:
                for url in m3u8_urls:
                    result.append(tv_name + "," + url)
                    print("M3U8 URL:", url)
            else:
                print("未找到M3U8 URL")

        print("匹配到的分页页码:", page_numbers)
    else:
        print("未找到匹配的分页页码")


# 打开json文件
with open("节目生成模板/港澳台.json", "r") as f:
    # 用orjson模块读取json文件
    template_data = orjson.loads(f.read())
    # 循环遍历列表中的对象
    for item in template_data:
        # 调用get_m3u8_url函数
        # 循环遍历rule中的关键字
        for keyword in item["rule"]:
            get_m3u8_url(item["name"], keyword)
            # 休眠1秒
            time.sleep(1)
            print("休眠1秒")

# 把列表中的M3U8 URL写入文件
with open("节目列表/spider.txt", "w") as f:
    for m3u8_url in result:
        f.write(m3u8_url + "\n")
