'''
@Author: Mario
@Date: 2020-07-09 16:54:57
@LastEditTime: 2020-07-11 10:25:41
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: \douban\spider.py
'''

import sys
from bs4 import BeautifulSoup       #网页解析，获取数据
import re                           #正则表达式
import urllib.request, urllib.error #指定URL获取网页数据
import xlwt                         #进行excel操作
import sqlite3                      #进行数据库操作


def main():
    baseurl = 'https://movie.douban.com/top250?start='
    #1.爬取网页
    datalist = getData(baseurl)
    #2.逐一解析数据

    #3.保存数据
    savepath = ".\\豆瓣电影Top250.xls"  # 当前文件夹里 
    saveData(datalist,savepath)
    dbpath = "movie.db"
    saveData2DB(datalist,dbpath)

# 影片详情连接的规则
findlink = re.compile(r'<a href="(.*?)">') # 生成正则表达式对象，表示规则（字符串模式）
# 找影片图片链接
findImage = re.compile(r'<img.*src="(.*?)"',re.S) # re.S ： 忽视换行符
# 影片片名
findtitle = re.compile(r'<span class="title">(.*)</span>')
# 评分
findstar = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 评价人数
findpeople = re.compile(r'<span>(\d*)人评价</span>')
# 找到概况
findinq = re.compile(r'<span class="inq">(.*)</span>')
# 找影片的相关内容
findbd = re.compile(r'<p class="">(.*?)</p>',re.S)



# 爬取网页（得到数据）
def getData(baseurl):
    datalist = []
    # 左闭右开
    for i in range(0,10): # 调用获取页面信息的函数，10次
        url = baseurl + str(i*25)
        html = askURL(url) # 保存获取到的网页源码
            
            # 2.逐一解析数据
        soup = BeautifulSoup(html,"html.parser") # 解析器
        for item in soup.find_all('div',class_ = "item"): # 查找符合要求的字符串，形成列表。找到class是item的且是div的
            data = [] # 保存一部电影的所有信息
            item = str(item)

            # 用re库查找指定字符串，给规则
            link = re.findall(findlink, item)[0] # 获取影片详情的链接
            data.append(link)

            img = re.findall(findImage,item)[0]
            data.append(img)

            titles = re.findall(findtitle,item) # 片名可能有多个名字（中外）
            if(len(titles)==2):
                ctitle = titles[0]
                data.append(ctitle) # 添加中文名
                otitle = titles[1].replace("/","") # 去掉无关符号
                data.append(otitle) # 添加外国名
            else:
                data.append(titles[0])
                data.append('null')    # 外国名留空

            rating = re.findall(findstar,item)[0]
            data.append(rating)         # 评分

            judgeNum = re.findall(findpeople,item)[0]
            data.append(judgeNum)       # 人数

            inq = re.findall(findinq,item)
            if len(inq)!=0:
                inq = inq[0].replace("。","") # 去掉句号
                data.append(inq)              # 概述
            else:
                data.append(" ")        # 留空
            
            bd  =re.findall(findbd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd) # 去掉br
            bd = re.sub('/'," ",bd)                 # 用空格替换/
            data.append(bd.strip())                 # 去掉空格

            datalist.append(data)                   # 把处理好的一部电影信息放进datalist里
    #print(datalist)
    return datalist



# 得到指定一个URL的网页内容
def askURL(url):
    # 用户代理表示告诉豆瓣服务器我们是什么类型的机器，浏览器。本质上是告诉浏览器我们可以接受什么水平的文件内容。
    # 模拟浏览器头部信息，像豆瓣服务器发送消息（伪装）
    head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}

    request = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)

    return html


# 保存数据
def saveData(datalist,savepath):
    book = xlwt.Workbook(encoding='utf-8',style_compression=0)
    sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=True)    # 创建一个sheet表
    col = ('电影链接','图片链接','影片中文名','影片外国名','评分','评价人数','概况','相关信息')
    for i in range(0,8):
        sheet.write(0,i,col[i]) # 列名

    for i in range(0,250):
        data=datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])

    book.save(savepath) # 保存


def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index == 5:
                continue
            data[index] = '"'+data[index]+'"'
        sql = '''
                insert into movie250 (
                info_link,pic_link,cname,ename,score,rated,introduction,info)
                values(%s)          
            '''%",".join(data)
        cur.execute(sql)
        conn.commit()
        #print(sql)
    cur.close()
    conn.close()


def init_db(dbpath):
    sql = '''
        create table if not exists movie250
        (
            id integer primary key autoincrement,
            info_link text,
            pic_link test,
            cname varchar,
            ename varchar,
            score numeric,
            rated numeric,
            introduction text,
            info text
        )
        '''
    # 创建数据库
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


#当程序执行时, 控制管理函数
if __name__ == "__main__":
    #call functions
    main()
    init_db("movie.db")
    print("爬取完毕!")