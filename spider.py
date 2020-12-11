import urllib.request
import re
from bs4 import BeautifulSoup


def ask_url(url):
    # 获取一个指定url的网页内容
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/87.0.4280.88 Safari/537.36',
               }
    req = urllib.request.Request(url=url, headers=headers)
    html = ''
    try:
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
        # print(html)
    except Exception as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)

    return html


def parse_data(html):
    # 解析网页内容的数据 获取需要的数据内容
    # 用来匹配的模式 正则表达式
    # 有括号分组时 正则匹配结果只给出括号部分内容 n个括号则结果列表每一项是长度为n的元组形式
    # findall先匹配整个表达式的正则 在匹配结果中的匹配分组中的正则
    pattern_link = re.compile(r'<a href="(.*?)">')
    pattern_img = re.compile(r'<img.*src="(.*?)"', re.S)  # re.S表示忽略换行符 re.I 不分大小写
    pattern_title = re.compile(r'<span class="title">(.*)</span>')
    pattern_rating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
    pattern_people = re.compile(r'<span>(\d*)人评价</span>')
    pattern_quote = re.compile(r'<span class="inq">(.*)</span>')
    pattern_bd = re.compile(r'<p class="">(.*?)</p>', re.S)

    soup = BeautifulSoup(html, 'html.parser')
    data_list = []
    for item in soup.find_all('div', class_='item'):
        item = str(item)
        # print(item)
        one_movie = []
        link = re.findall(pattern_link, item)[0]
        one_movie.append(link)
        img = re.findall(pattern_img, item)[0]
        one_movie.append(img)

        title = re.findall(pattern_title, item)
        one_movie.append(title[0])
        if len(title) == 2:
            one_movie.append(title[1].replace('\xa0', '').replace('/', ''))  # 去掉网页源码中的空格&nbsp;对应的转义字符\xa0
        elif len(title) == 1:
            one_movie.append(' ')

        rating = re.findall(pattern_rating, item)[0]
        one_movie.append(rating)
        people = re.findall(pattern_people, item)[0]
        one_movie.append(people)
        quote = re.findall(pattern_quote, item)
        if quote:
            one_movie.append(quote[0].replace('。', ''))
        else:
            one_movie.append(' ')

        bd = re.findall(pattern_bd, item)[0]
        bd = bd.strip()
        bd = re.sub(r'<br(\s+)?/>(\s+)?', ' ', bd)  # 替换bd中的<br/>
        bd = bd.replace('\xa0', '')
        one_movie.append(bd)

        data_list.append(one_movie)
        # print(data_list)
    return data_list


def get_data(base_url):
    # 获取基于url的所有需要的网页数据
    data_list = []

    for i in range(10):
        url = base_url + str(i * 25)
        html = ask_url(url)
        data = parse_data(html)
        data_list.extend(data)

    print(data_list)
    return data_list


def main():
    base_url = 'https://movie.douban.com/top250?start='
    # html = ask_url(base_url)
    # parse_data(html)
    data_list = get_data(base_url)


if __name__ == '__main__':
    main()
