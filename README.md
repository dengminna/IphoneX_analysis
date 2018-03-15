# IphoneX_analysis
文本挖掘の玩转IphoneX评论数据

1.爬取京东售卖IphoneX评论数前5多的店铺评论文本数据  
2.对IphoneX评论文本数据进行词云展示  
3.对IphoneX评论文本数据做分词操作  
4.对IphoneX评论文本数据做进行特征转换（bag-of-word，TF-IDF，Word2Vec）    
5.对IphoneX评论文本数据做LDA主题模型  
6.对IphoneX评论文本数据做L分类模型（情感分析）  


脚本介绍：    
background.jpg：用来做词云wordcloud的形状底图  
iphonex_clasfication.py：使用各种分类算法对IphoneX的评论数据建模的脚本  
iphonex_frequent_wordcloud.py：对IphoneX的评论数据做词云展示的脚本  
iphonex_lda.py：对IphoneX的评论数据做做LDA主题模型的脚本  
iphonex_spider.py：爬取京东售卖IphoneX评论数前5多的店铺评论文本数据的脚本  
iphonex_tfidf_wordcloud.py：对IphoneX的评论数据使用TF-IDF统计后再用词云展示的脚本  
stop_word.txt：停用词表  
