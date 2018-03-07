#encoding: utf-8
import pymongo
import numpy as np
import pandas as pd
import jieba
import jieba.analyse as analyse
from gensim import corpora,models
import gensim

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


# word_list=raw_data.comment.values.tolist()
word_list=bad_word_list

#对评论数据进行分词，去停用词
# 去掉停用词(这里加载来自4个地方的停用词表进行剔除停用词)
stopwords = []
for i in ['baiodu_stopwords_table', 'chinese_stopwords_table', 'hada_stopwors_table', 'sichuanda_stopwords_table',
		  'myselfstopword']:
	temp = pd.read_csv("stopwords-master/%s.txt" % i, index_col=False, quoting=3, sep="\t", names=['stopword'],
							encoding='utf-8')  # quoting=3全不引用
	stopwords = stopwords + temp.stopword.values.tolist()

sentences = []
for line in word_list:
	try:
		segs=jieba.lcut(line)
		segs = list(filter(lambda x: len(x) > 1, segs))
		segs = list(filter(lambda x: x not in stopwords, segs))
		if segs:
			sentences.append(segs)
	except Exception:
		print(line)
		continue

#词袋模型
dictionary = corpora.Dictionary(sentences)
corpus = [dictionary.doc2bow(sentence) for sentence in sentences]

#基于词袋模型的LDA建模
lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=20) #最多使用20个关键词表示
print(lda.print_topic(3, topn=20)) #第三个分类 用20个关键词表示
for topic in lda.print_topics(num_topics=3, num_words=5): #查看前3个主题，以5个关键字表示
	print(topic)

#TF-IDF
tfidf_model = models.TfidfModel(corpus)
corpus_tfidf = tfidf_model[corpus]

#基于TF-IDF的LDA建模
lda = gensim.models.ldamodel.LdaModel(corpus=corpus_tfidf, id2word=dictionary, num_topics=20) #最多使用20个关键词表示
print(lda.print_topic(3, topn=20)) #第三个分类 用20个关键词表示
for topic in lda.print_topics(num_topics=3, num_words=5): #查看前3个主题，以5个关键字表示
	print(topic)


