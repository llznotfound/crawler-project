import sqlite3
import urllib.request
import re
import xlwt
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

    # 除了使用上述正则表示式进行页面的所有内容匹配之外，也可以利用BeautifulSoup提供的的select方法进行 标签tap、类class、id的选择匹配
    # bs.select('div > .class > #id') >表示在当前层级下面找

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

    # print(data_list)
    return data_list


def save_data(save_file, data_list):
    print('saving data to fie: ' + save_file)
    work_book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = work_book.add_sheet('top250', cell_overwrite_ok=True)
    header = ('电影序号', '电影详情页链接', '封面图片链接', '电影中文名', '电影英文名', '电影评分', '评分人数', '电影简评', '影片信息')
    for i in range(len(header)):
        sheet.write(0, i, header[i])

    for i in range(len(data_list)):
        print('第%d部电影写入' % (i+1))
        one_movie = data_list[i]
        sheet.write(i+1, 0, i+1)
        for j in range(len(one_movie)):
            sheet.write(i+1, j+1, one_movie[j])

    work_book.save(save_file)
    print('data save success.')


def save2db(dbname, data_list):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    for i in range(len(data_list)):
        movie = data_list[i]
        sql = 'insert into top250 (id, link, img, cname, fname, rating, people, quote, bdinfo) values('
        sql += str(i+1)
        for item in movie:
            sql += ',' + '"' + item + '"'
        sql += ')'
        # print(sql)
        # 也可以在sql中用占位符的方法
        # sql = 'insert into top250 (id, link, img, cname, fname, rating, people, quote, bdinfo) values(%s)'%
        # 后面加上数据拼接而成的字符串内容
        cursor.execute(sql)

    conn.commit()
    cursor.close()
    conn.close()
    print('data save to db success.')


def main():
    base_url = 'https://movie.douban.com/top250?start='
    save_file = 'top250.xls'
    dbname = 'spider.db'
    # html = ask_url(base_url)
    # parse_data(html)
    data_list = get_data(base_url)
    # save_data(save_file, data_list)
    save2db(dbname, data_list)


if __name__ == '__main__':
    main()
