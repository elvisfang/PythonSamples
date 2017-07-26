# -*- coding:UTF-8 -*-
"""
-------------------------------------------------
   File Name：     crawler.py
   Description :  crawl all AU regions from http://www.ksouhouse.com/region_auto_state.php
                  the url return all matched regions after 2 letters input
                  example:
                  sta:vic
                  q:ac
                  limit:10
                  timestamp:1501061781414
   Author :       elvisfang
   date：          2017/7/26
-------------------------------------------------
"""
__author__ = 'elvisfang'

from urllib import request
from urllib import parse
from urllib import error
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo import errors
import re
import csv
import time
import string

if __name__ == "__main__":
    ProxyEnabled = False
    Target_URL = 'http://www.ksouhouse.com/region_auto_state.php'

    Query_String = {}
    Query_String['sta'] = ''
    Query_String['q'] = ''
    Query_String['limit'] = 100
    Query_String['timestamp'] = ''

    statelist = ['vic','nsw','qld','sa','act','wa','nt','tas']

    if ProxyEnabled:
        proxy = {'http': '113.121.188.81:808'}
        proxy_support = request.ProxyHandler(proxy)
        opener = request.build_opener(proxy_support)
        request.install_opener(opener)
    #define Head
    Head = {}
    Head['User-Agent'] = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19'

    Target_Req = request.Request(url=Target_URL, headers=Head)

    # connect to mongo
    Mongo = MongoClient('127.0.0.1', 27017)
    DB = Mongo['KsouData']
    PropertyCollection = DB['regions']

    for state in statelist:
        Query_String['sta'] = state
        regionlist = []
        for letter1 in string.ascii_lowercase:
            for letter2 in string.ascii_lowercase:
                Query_String['q'] = letter1+letter2
                Query_String['timestamp'] = int(time.time())
                SearchData = parse.urlencode(Query_String).encode('utf-8')
                try:
                    Target_Response = request.urlopen(Target_Req, SearchData)
                except error.HTTPError as e:
                    ErrorLog = open('SpiderError.log', 'a', encoding='utf-8')
                    ErrorLog.write(time.strftime("%Y-%m-%d %H:%M:%S",
                                                 time.localtime()) + ' HTTPError:' + e.code + ' When processing:' + Target_Req.full_url + '\n')
                    ErrorLog.close()
                except error.URLError as e:
                    ErrorLog = open('SpiderError.log', 'a', encoding='utf-8')
                    ErrorLog.write(time.strftime("%Y-%m-%d %H:%M:%S",
                                                 time.localtime()) + ' URLError:' + e.reason.strerror + ' When processing:' + Target_Req.full_url + '\n')
                    ErrorLog.close()
                else:
                    Result = Target_Response.read().decode('utf-8', 'ignore')
                    if Result:
                        #print(state + ':' +Result)
                        resultlist = Result.split('\n')


                        for reg in resultlist:
                            if reg:
                                regionlist.append(reg)
                                print(state + ':' +reg)

                    time.sleep(2)

        document = {
            'state': state,
            'region': regionlist,
        }
        try:
            PropertyCollection.insert(document)
        except errors as e:
            ErrorLog = open('SpiderError.log', 'a', encoding='utf-8')
            ErrorLog.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' MongoDBError:' + e.reason.strerror)
            ErrorLog.close()
            continue


