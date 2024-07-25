'''
练习写一个爬虫代码
'''

import requests
import re
import base64
import os
import urllib.parse


# 起始爬取的网页带有页码头
start_url = 'https://hifini.com/index-'
# 网站首页
base_url = "https://hifini.com/"
# referer参数
referer_url = "https://hifini.com/"
# 伪装
headers1 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Cookie': 'bbs_sid=vv2trfih02c6nsmtnjg8ajksh2'
}
headers2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Cookie': 'bbs_sid=vv2trfih02c6nsmtnjg8ajksh2',
    'Referer': referer_url
}


# 获得列表页数据
def get_data(url, headers):
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.text

        # print("请求成功")
        # print(data)
        return data
    else:
        print("请求失败!")


# 获取详情页数据
def get_song_data(song_url, headers):
    return get_data(song_url, headers)


# 解析数据
def parse_data(data):
    # 解析歌曲名字和链接
    z1 = '<li\sclass="media\sthread\stap.*?\s\s".*?<div\sclass="subject\sbreak-all">.*?<a\shref="(.*?)">(.*?)</a>'
    result = re.findall(z1, data, re.S)
    # print(result)
    songs_dict = {}
    # 解析列表有多少页
    parse_page = '<a\s+href="index-.*?>\.\.\.(\d+)</a>'
    # 获取到了所有页码
    page = re.search(parse_page, data, re.S)
    # print(page.group(1))
    # x = 0
    # # 获取多少个歌曲
    # max_song = 15
    # print("result为：", result)
    if result:
        for i in result:
            # print(i)
            # if x >= max_song:
            #     break
            song_url = base_url + i[0]
            name = i[1]
            # print(song_url, name)
            html = requests.get(song_url).text
            if "generate" in html:
                # 调用函数 获得详情页信息
                song_data = get_song_data(song_url, headers1)
                if "music: [" not in song_data:
                    print(300 * "*")
                    print("歌曲详情页没有音乐资源！！！！")
                    print("链接为：", song_url)
                    print(300 * "*")
                else:
                    if song_data:
                        # print(song_data)
                        print("歌曲详情页捕获成功")
                        z2 = "music:\s\[.*?url:\s'(.*?)'\s*\+\s*generateParam\('(.*?)'"
                        song_result = re.findall(z2, song_data, re.S)
                        # [0]

                        # x += 1
                        if song_result:
                            print('歌曲链接捕获成功')
                            for j in song_result:
                                song_first_link = j[0]
                                p = generate_param(j[1])
                                song_all_link = base_url + song_first_link + p
                                print(f"歌曲名称为：{name}")
                                print("链接全称为", song_all_link)
                                song = requests.get(song_all_link, headers=headers1)
                                print("去往歌曲链接的请求状态:", song.status_code)
                                song_data_bytes = song.content
                                # print(song_data_bytes)
                                songs_dict[name] = song_data_bytes
                        else:
                            print(300 * "=")
                            print("Error：歌曲链接捕获失败！")
                            print(f"详情页链接为：{song_url}")
                            print(300 * "=")
            else:
                song_data = get_song_data(song_url, headers1)
                if "music: [" not in song_data:
                    print(300 * "*")
                    print("歌曲详情页没有音乐资源！！！！")
                    print("链接为：", song_url)
                    print(300 * "*")
                else:
                    if song_data:
                        # print(song_data)
                        print("歌曲详情页捕获成功")
                        z2 = "music:\s\[.*?url:\s'(.*?)',"
                        song_result = re.findall(z2, song_data, re.S)
                        # [0]
                        print(song_result)
                        # x += 1
                        if song_result:
                            print('歌曲链接捕获成功')
                            # for j in song_result:
                            song_all_link = song_result[0]
                            print(f"歌曲名称为：{name}")
                            print("链接全称为", song_all_link)
                            song = requests.get(song_all_link, headers=headers2)
                            print("去往歌曲链接的请求状态:", song.status_code)
                            song_data_bytes = song.content
                            # print(song_data_bytes)
                            songs_dict[name] = song_data_bytes
                        else:
                            print(300 * "=")
                            print("Error：歌曲链接捕获失败！")
                            print(f"详情页链接为：{song_url}")
                            print(300 * "=")


    else:
        print("解析数据失败 ")

    return songs_dict


# 保存数据
def save_data(songs_dict, dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    for name, song_data_bytes in songs_dict.items():
        print(f"存储歌曲名称: {name}")  # 键名
        # print(f"歌曲数据: {song_data_bytes}")  # 键值
        # print(type(name))
        song_name = re.sub('[\/:*?<>|]', "-", name)
        with open(dir_name + '\{}.m4a'.format(song_name), 'wb') as f:
            f.write(song_data_bytes)
        print("存储成功")


def get_page_data(url, start_page, end_page, dir_name):
    if 'search' not in url:
        for i in range(start_page, end_page+1):
            all_url = url + str(i) + ".htm"
            # print(all_url)
            print("抓取的页码为：", i)
            data = get_data(all_url, headers1)
            songs_dict = parse_data(data)
            all_keys = songs_dict.keys()
            # 调用储存函数
            save_data(songs_dict, dir_name)
            print("所有歌曲名称:", list(all_keys))

    else:
        for i in range(start_page, end_page+1):
            # 列表页网址
            all_url = url + "1-" + str(i) + ".htm"
            # print(all_url)
            print(300 * "=")
            print("抓取的页码为：", i)
            data = get_data(all_url, headers1)
            songs_dict = parse_data(data)
            all_keys = songs_dict.keys()
            # 调用储存函数
            save_data(songs_dict, dir_name)
            print("所有歌曲名称:", list(all_keys))


def get_search_data(content):
    url_part1 = escape_chinese(content)
    # print(url_part1)
    # 拼接网址
    url = base_url + "search-" + url_part1 + "-"
    # print(url)
    return url




'''
下面的函数：
    1.对网站加密的处理
    2.对字符转义的处理
'''


# 1.解密处理
def xor_encrypt(data, key):
    out_text = ''
    j = 0
    for i in range(len(data)):
        if j == len(key):
            j = 0
        out_text += chr(ord(data[i]) ^ ord(key[j]))
        j += 1
    return out_text


def base32_encode(data):
    return base64.b32encode(data.encode()).decode()


def generate_param(data):
    key = '95wwwHiFiNicom27'
    out_text = xor_encrypt(data, key)
    return base32_encode(out_text)


# 对搜索内容的处理
def escape_chinese(text):
    result = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 检查是否是汉字
            # 将汉字字符转换为 URL 编码形式
            result.append(urllib.parse.quote(char.encode('utf-8')))
        else:
            # 英文字符直接添加
            result.append(char)

    result = ''.join(result)
    result = re.sub('%', '_', result)
    return result


if __name__ == '__main__':
    dir_name = "童话镇"
    get_page_data(start_url, 1, 2, dir_name)
#     content1 = "周杰伦"
#     content2 = "star"
#     result1 = escape_chinese(content1)
#     print(result1)
#     search_content = "睡觉"
#     url = get_search_data(search_content)

#     get_page_data(url, 1, 2, dir_name)
