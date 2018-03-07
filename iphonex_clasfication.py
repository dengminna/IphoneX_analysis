#encoding: utf-8
import pymongo
import numpy as np
import pandas as pd
import jieba
import jieba.analyse as analyse
from gensim import corpora,models
import gensim
import random
from sklearn.model_selection import train_test_split

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

word_list=raw_data.comment.values.tolist()

#对评论数据进行分词，去停用词
# 去掉停用词(这里加载来自4个地方的停用词表进行剔除停用词)
stopwords = []
for i in ['baiodu_stopwords_table', 'chinese_stopwords_table', 'hada_stopwors_table', 'sichuanda_stopwords_table',
		  'myselfstopword']:
	temp = pd.read_csv("stopwords-master/%s.txt" % i, index_col=False, quoting=3, sep="\t", names=['stopword'],
							encoding='utf-8')  # quoting=3全不引用
	stopwords = stopwords + temp.stopword.values.tolist()

#保存分完词后的文本列表
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
#对得分进行处理 分值>=3的为好评，其余为差评
score_list = raw_data.score.values.tolist()
for i in range(len(score_list)):
    if score_list[i] >= 3:
        score_list[i] = 1
    else :
        score_list[i] = 0

#组合起来
total = list(zip(sentences,score_list))
#生成训练集,打乱一下顺序
random.shuffle(total)
x, y = list(zip(*total))
xed = list((" ".join(a) for a  in x))
x_train, x_test, y_train, y_test = train_test_split(xed, y, random_state=1234)
len(x_test)

#使用词袋模型进行建模
from sklearn.feature_extraction.text import CountVectorizer
vec = CountVectorizer(
    analyzer='word', # tokenise by character ngrams
    ngram_range=(1,4),  # 可选使用-gram
    max_features=20000,  # 你可以词维度
)
vec.fit(x_train)

def get_features(x):
    vec.transform(x)

#使用tfidf
from sklearn.feature_extraction.text import TfidfVectorizer
vec = TfidfVectorizer(analyzer='word', ngram_range=(1,3), max_features=12000)
vec.fit(x_train)

def get_features(x):
    vec.transform(x)

#使用word2vec
model = gensim.models.Word2Vec(sentences, size=300, window=5, min_count=5)
model.save("gensim_word2vec.model")

#把文章中的词语转化为word2vec
def get_vector(context):
	final_vec = np.zeros([len(context),300],dtype=float) #新建一行
	for i in range(0,len(context)):
		vec = np.zeros(300,dtype=float)
		for w in context[i].split(" "):
			if w in model:
				vec += model[w]
		vec /= len(context[i].split(" "))
		final_vec = np.vstack((final_vec, vec))  # 拼在下面
	return final_vec[len(context)-1:-1, :]

print(len(x_test))
test= get_vector(x_test)

#使用贝叶斯分类器进行分类
from sklearn.naive_bayes import MultinomialNB
classifier = MultinomialNB()
classifier.fit(vec.transform(x_train), y_train)
classifier.score(vec.transform(x_test), y_test)

classifier.fit(np.maximum(get_vector(x_train),0), y_train)
classifier.score(np.maximum(get_vector(x_test),0), y_test)

#使用svm分类器进行分类
from sklearn.svm import SVC
svm = SVC(kernel='linear')
svm.fit(vec.transform(x_train), y_train)
svm.score(vec.transform(x_test), y_test)

svm.fit(get_vector(x_train), y_train)
svm.score(get_vector(x_test), y_test)



#使用LR分类器进行分类
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression()
clf.fit(vec.transform(x_train), y_train)
clf.score(vec.transform(x_test), y_test)

clf.score(get_vector(x_test), y_test)
clf.score(get_vector(x_test), y_test)

#使用DT分类器进行分类
from sklearn import tree
clf = tree.DecisionTreeClassifier()
clf.fit(vec.transform(x_train), y_train)
clf.score(vec.transform(x_test), y_test)

#使用RF分类器进行分类
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(n_estimators=30)
clf.fit(vec.transform(x_train), y_train)
clf.score(vec.transform(x_test), y_test)



