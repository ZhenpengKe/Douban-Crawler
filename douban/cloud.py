'''
@Author: your name
@Date: 2020-07-12 09:55:02
@LastEditTime: 2020-07-12 10:12:11
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: \douban\cloud.py
'''

import sqlite3
import jieba    # 分词
from matplotlib import pyplot as plt # 绘图，数据可视化
from wordcloud import WordCloud # 词云
import numpy as np  # 矩阵运算
from PIL import Image   # 图片处理

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
print(len(string))

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
#plt.savefig(r'.\static\assets\img\word.jpg',dpi=500)
#plt.show()