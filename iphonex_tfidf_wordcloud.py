#encoding: utf-8
import pymongo
import numpy as np
import pandas as pd
import jieba
import jieba.analyse as analyse
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator

client = pymongo.MongoClient('127.0.0.1',port=27017)# 获取连接的对象
db = client.iphonx
collection = db.comment_total#（把comment_total表映射到collection中）
cursor = collection.find()
iphonex_raw_data = []
for x in cursor:
    iphonex_raw_data.append(x)

print(len(iphonex_raw_data)) #共有11051条中文数据
#把数据都写成pandas形式
d = {'comment':[x['content'] for x in iphonex_raw_data],
	 'support_num':[x['support_count'] for x in iphonex_raw_data],
	 'score':[x['score'] for x in iphonex_raw_data]}
raw_data = pd.DataFrame(d)
raw_data = raw_data.dropna()

#定义三个列表存放三种情感的词
good_word_list=raw_data[raw_data['score']>3].comment.values.tolist()
midien_word_list=raw_data[(raw_data['score']<=3) & (raw_data['score']>=2)].comment.values.tolist()
bad_word_list = raw_data[raw_data['score'] <= 1].comment.values.tolist()

#对评论数据进行分词，jieba
# for x in [good_word_list,midien_word_list,bad_word_list]:
for x in [bad_word_list]:
    segment = []
    comment = x
    for line in comment:
        try:
            segs=jieba.lcut(line)
            for seg in segs:
                if len(seg)>1 and seg!='\r\n':
                    segment.append(seg)
        except:
            print(line)
            continue
    #去掉停用词(这里加载来自4个地方的停用词表进行剔除停用词)
    words_df=pd.DataFrame({'segment':segment})
    for i in ['baiodu_stopwords_table','chinese_stopwords_table','hada_stopwors_table','sichuanda_stopwords_table','myselfstopword']:
        stopwords=pd.read_csv("stopwords-master/%s.txt"%i,index_col=False,quoting=3,sep="\t",names=['stopword'], encoding='utf-8')#quoting=3全不引用
        words_df=words_df[~words_df.segment.isin(stopwords.stopword)]

    content = words_df.segment.values.tolist()
    comment = "".join(content)
    words_stat= analyse.extract_tags(comment, topK=2000, withWeight=True, allowPOS=())

    #做词云
    background = np.array(Image.open("background.jpg"))
    image_colors = ImageColorGenerator(background)
    wordcloud = WordCloud(font_path="font/simhei.ttf",background_color="white", max_font_size=80,mask=background)
    word_frequence = {x[0]: x[1] for x in words_stat}
    wordcloud = wordcloud.fit_words(word_frequence)
    plt.imshow(wordcloud)





