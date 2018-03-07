#encoding: utf-8
import time
import requests
import pymongo
import json
import random
import urllib3
def random_useragent():
    #设置随机请求头
    useragentlists = ['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
                      'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
                      'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
                      'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
                      'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
                      'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
                      'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14',
                      'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52',
                      'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
                      'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0',
                      'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
                      'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0',
                      'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0']
    user_agent = random.choice(useragentlists)
    return user_agent

def parse_commonts_data(response):
    json_response = json.loads(response)
    commentSummarys = json_response['comments']
    # print(commentSummarys['hotCommentTagStatistics']['comments'])
    # if commentSummarys['hotCommentTagStatistics']['comments'] is None:
    #     pass
    result_datas = []
    for commentSummary in commentSummarys:
        id = commentSummary['id']
        content = commentSummary['content']
        if commentSummary.get('afterUserComment') is not None:
            content2 = commentSummary['afterUserComment']['hAfterUserComment']['content']
            content = content + '。' + content2
        support_count = commentSummary['usefulVoteCount']
        score = commentSummary['score']
        create_time = commentSummary['creationTime']

        result_data = {
            'id': id,
            'content': content,
            'support_count': support_count,
            'score': score,
            'create_time': create_time
        }
        result_datas.append(result_data)
    return result_datas

def putong():
    # 连接mongoDB数据库
    client = pymongo.MongoClient('127.0.0.1', port=27017)# 获取连接的对象
    db = client.iphonx                                    # 获取数据库(把iphonx库映射到db中，iphonx库没有则会自己创建)
    collection = db.comments4  # 获取集合（表）（把comments表映射到collection中）

    params = {
          'productId':None,
          'score':0,
          'sortType':5,
          'page':0,
          'pageSize':10,
          'isShadowSku':0,
          'fold':1
    }
    #[5089235,21473392527,15354128254,15501730722,18605531857,16577740725,16904192913,16555705767,16904192913,18601046769] #这些是商品id

    for productId in [18601046769,16579173311]:
        for score in range(1,3):
            page = 0
            while True:
                params['page'] = page
                params['score'] = score
                params['productId'] = productId
                headers = {'User-Agent': random_useragent()}
                try:
                    response = requests.get("https://sclub.jd.com/comment/productPageComments.action", params=params, headers=headers).text
                except requests.exceptions.ConnectionError or TimeoutError or urllib3.exceptions.NewConnectionError or urllib3.exceptions.MaxRetryError:

                    print('************* 403抛出异常啦1 *************')
                    time.sleep(120)
                    headers = {'User-Agent': random_useragent()}
                    response = requests.get("https://sclub.jd.com/comment/productPageComments.action", params=params,
                                            headers=headers).text
                except requests.exceptions.ConnectionError or TimeoutError or urllib3.exceptions.NewConnectionError or urllib3.exceptions.MaxRetryError:

                    print('************* 403抛出异常啦2 *************')
                    time.sleep(120)
                    headers = {'User-Agent': random_useragent()}
                    response = requests.get("https://sclub.jd.com/comment/productPageComments.action", params=params,
                                            headers=headers).text

                result_datas = parse_commonts_data(response)
                page +=1

                if len(result_datas)>0:
                    #插入到数据库中
                    collection.insert_many(result_datas)
                else:
                    #已经拿不到数据了
                    break
                time.sleep(3)
                print("ID编号为：%s，得分为:%s，正在爬取第%s页" %(productId, score,page))
                print(result_datas)
    return None

def main():
    putong()

if __name__ == '__main__':
    main()