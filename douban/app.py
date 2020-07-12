
'''
@Author: Mario
@Date: 2020-07-11 10:28:26
@LastEditTime: 2020-07-12 10:11:27
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: \douban\app.py
'''
import sqlite3
import jieba    # 分词
from matplotlib import pyplot as plt # 绘图，数据可视化
from wordcloud import WordCloud # 词云
import numpy as np  # 矩阵运算
from PIL import Image   # 图片处理
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/index')
def home():
    return index()


@app.route('/movie')
def movie():
    datalist = []
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select * from movie250"
    data = cur.execute(sql)
    for item in data:
        datalist.append(item)
    cur.close()
    con.close()

    return render_template("movie.html",movies = datalist)


@app.route('/score')
def score():
    score = []
    numofmovies = [] # 每个评分的电影数量
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select score, count(score) from movie250 group by score"
    data = cur.execute(sql)
    for item in data:
        score.append(item[0])
        numofmovies.append(item[1])
    cur.close()
    con.close()
    return render_template("score.html",score=score,numofmovies=numofmovies)

@app.route('/cloud')
def word():
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select introduction from movie250"
    data = cur.execute(sql)
    text = ""
    for item in data:
        text = text+item[0]
    cur.close()
    con.close()

    # 分词
    cut = jieba.cut(text)
    string = ' '.join(cut)

    # 准备一张图
    img = Image.open(r'.\static\assets\img\tree.jpg')
    img_array = np.array(img) # 将图片转化为数组
    wc = WordCloud(
        background_color='white',
        mask=img_array,
        font_path="SIMYOU.TTF" # 字体所在位置： C:\Windows\Fonts
    )
    wc.generate_from_text(string)

    # 绘制图片
    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off') # 是否显示坐标轴
    plt.savefig(r'.\static\assets\img\word.jpg',dpi=500)
    return render_template("word.html")


@app.route('/team')
def team():
    return render_template("team.html")



if __name__ == '__main__':
    app.run()