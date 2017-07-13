# -*- coding: UTF-8 -*-
import dokuwiki
from dokuwiki import DokuWikiError
import urllib
from urllib import error
from urllib import request



WIKI_URL = "http://itbaike.contoso.com"
FULL_TEXT_SEARCH_KEY = "outlook"
RPCUser = "testuser"
Pwd = "P@ssw0rd"

try:
    wiki = dokuwiki.DokuWiki(WIKI_URL+"/wiki",RPCUser,Pwd)
except(DokuWikiError,Exception) as err:
    print('unable to connect: %s' % err)


Pages = wiki.pages
SearchResult = Pages.search(FULL_TEXT_SEARCH_KEY)

ResultPages = [];

try:
    for i in range(len(SearchResult)):
        print(SearchResult[i]['id'])
        html = request.urlopen(WIKI_URL+"/wiki/doku.php?id="+urllib.parse.quote(SearchResult[i]['id'])).read().decode("utf-8")
        ResultPages.append(html)
        html = ""
except error.HTTPError as e:
    print(e.reason)
except error.URLError as e:
    print(e.reason)

for i in range(len(ResultPages)):
    print(ResultPages[i])

