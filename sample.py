# -*- coding:UTF-8 -*-
from urllib import request
from urllib import parse
from urllib import error
from bs4 import BeautifulSoup
import re
import csv
import time

if __name__ == "__main__":
    #craete a CSV
    ResultFile = open('ksou.csv', 'w', encoding='utf-8')

    ProxyEnabled = False

    #search ksou
    Target_URL = 'http://house.ksou.cn/p.php'
    Query_String = {}
    Query_String['q'] = 'Toorak'
    Query_String['p'] = '3'
    Query_String['s'] = 1
    Query_String['st'] = ''
    Query_String['type'] = ''
    Query_String['count'] = '300'
    Query_String['region'] = 'Toorak'
    Query_String['lat'] = '0'
    Query_String['lng'] = '0'
    Query_String['sta'] = 'vic'
    Query_String['htype'] = ''
    Query_String['agent'] = '0'
    Query_String['minprice'] = '0'
    Query_String['maxprice'] = '0'
    Query_String['minned'] = '0'
    Query_String['maxbed'] = '0'
    Query_String['minland'] = '0'
    Query_String['maxland'] = '0'

    SearchData = parse.urlencode(Query_String).encode('utf-8')
    #User-Agent
    if ProxyEnabled:
        proxy = {'http': '113.121.188.81:808'}
        proxy_support = request.ProxyHandler(proxy)
        opener = request.build_opener(proxy_support)
        request.install_opener(opener)
    #define Head
    Head = {}
    Head['User-Agent'] = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19'

    Target_Req = request.Request(url = Target_URL, headers = Head)
    try:
        Target_Response = request.urlopen(Target_Req,SearchData)
    except error.HTTPError as e:
        ErrorLog = open('SpiderError.log', 'a', encoding='utf-8')
        ErrorLog.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' HTTPError:' + e.code  + ' When processing:' + Target_Req.full_url +'\n')
        ErrorLog.close()
    except error.URLError as e:
        ErrorLog = open('SpiderError.log', 'a', encoding='utf-8')
        ErrorLog.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' URLError:' + e.reason.strerror + ' When processing:' + Target_Req.full_url + '\n')
        ErrorLog.close()
    #to do: hanle exception do not continue
    Target_Html = Target_Response.read().decode('utf-8','ignore')

    #new BeautifulSoup object
    soup = BeautifulSoup(Target_Html,'lxml')

    All_Result_List = []
    for addr in soup.find_all('span',class_='addr'):
        Result = {}

        ADDR_URL = addr.a.get('href')[5:]
        Detail_Req = request.Request(url = Target_URL+ADDR_URL, headers = Head)

        try:
            Detail_Response = request.urlopen(Detail_Req)
        except error.HTTPError as e:
            ErrorLog = open('SpiderError.log', 'a', encoding='utf-8')
            ErrorLog.write(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) + ' HTTPError:' + e.code  + ' When processing:' + Detail_Req.full_url)
            ErrorLog.close()
        except error.URLError as e:
            ErrorLog = open('SpiderError.log', 'a', encoding='utf-8')
            ErrorLog.write(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) + ' URLError:'  + e.reason.strerror + ' When processing:' + Detail_Req.full_url)
            ErrorLog.close()
        print('Processing: ' + Target_URL+ADDR_URL)
        Detail_Html = Detail_Response.read().decode('utf-8','ignore')
        Detail_Soup = BeautifulSoup(Detail_Html,'lxml')
        addr_tag = Detail_Soup.find('span', class_='addr')
        detail_tag = addr_tag.parent.parent.next_sibling
        # find detail info in the currnet page

        # Get Address
        Result['Addr'] = addr_tag.text

        #Get Sold Price
        if detail_tag.find(text=re.compile('Sold')):
            Result['SoldPrice'] = detail_tag.find(text=re.compile('Sold'))
        else:
            Result['SoldPrice'] = 'null'
        # Get Sold Date
        if detail_tag.find(text=re.compile('Sold')):
            Result['SoldDate'] = detail_tag.find(text=re.compile('Sold')).parent.next_sibling
        else:
            Result['SoldDate'] = 'null'
        #Get Last Sold Price
        if detail_tag.find(text=re.compile('Last Sold')):
            Result['LastSold'] = detail_tag.find(text=re.compile('Last Sold')).parent.next_sibling
        else:
            Result['LastSold'] = 'null'
        #Get Rent Price
        if detail_tag.find(text=re.compile('Rent')):
            if detail_tag.find(text=re.compile('Rent')).parent.parent.find('a'):
                Result['RentPrice'] = detail_tag.find(text=re.compile('Rent')).parent.parent.a.string #with Rent link
            else:
                Result['RentPrice'] = detail_tag.find(text=re.compile('Rent')).parent.next_sibling #<td><b>Rent</b> $1,150pw in Jun 2014</td>
        else:
            Result['RentPrice'] = 'null'
        #get property type
        if detail_tag.find(text=re.compile('Apartment|Unit|House')):
            Result['Type'] = detail_tag.find(text=re.compile('Apartment|Unit|House'))
        else:
            Result['Type'] = 'null'
        #get Bed Room Number
        if detail_tag.find(title='Bed rooms'):
            Result['BedRoom'] = detail_tag.find(title='Bed rooms').previous_sibling
        else:
            Result['BedRoom'] = '0'
        # get Bath Room Number
        if detail_tag.find(title='Bath rooms'):
            Result['BathRoom'] = detail_tag.find(title='Bath rooms').previous_sibling
        else:
            Result['BathRoom'] = '0'
        #Get car space
        if detail_tag.find(title='Car spaces'):
            Result['CarSpace'] = detail_tag.find(title='Car spaces').previous_sibling
        else:
            Result['CarSpace'] = '0'
        #Get Land Size
        if detail_tag.find(text=re.compile('Land size:')):
            Result['LandSize'] = detail_tag.find(text=re.compile('Land size:')).parent.next_sibling
            if Result['LandSize']  == ' \xa0':
                Result['LandSize'] = 'null'
        else:
            Result['LandSize'] = 'null'
        #get Build Year
        if detail_tag.find(text=re.compile('Build year:')):
            Result['BuildYear'] = detail_tag.find(text=re.compile('Build year:')).parent.next_sibling
        else:
            Result['BuildYear'] = 'null'
        # Get Agent Name
        if detail_tag.find(text=re.compile('Agent')):
            # <td><b>Agent:</b> <a href="http://www.ksouhouse.com/agent.php?id=21225&amp;name=Rodney+Morley+Pty+Ltd+-" title="View more about this realestate agent">Rodney Morley Pty Ltd -</a></td>
            if detail_tag.find(text=re.compile('Agent')).parent.parent.find('a'):
                Result['Agent'] = detail_tag.find(text=re.compile('Agent')).parent.parent.a.string
            else:#<td><b>Agent:</b> hockingstuart  Armadale</td>
                Result['Agent'] = detail_tag.find(text=re.compile('Agent')).parent.next_sibling
        else:
            Result['Agent'] = 'null'
        #get distance to cbd
        if detail_tag.find(text=re.compile('Distance')):
            Result['Distance'] = detail_tag.find(text=re.compile('Distance')).parent.next_sibling
        else:
            Result['Distance'] = 'null'

        #append dict to the dict list
        All_Result_List.append(Result)
    writer = csv.writer(ResultFile)
    ResultFile.write('Addr,SoldPrice,SoldDate,LastSold,RentPrice,Type,BedRoom,BathRoom,CarSpace,LandSize,BuildYear,Agent,Distance\n')
    for item in All_Result_List:
        #ResultFile.write(item['Addr'] +',' + item['SoldPrice']+',' + item['SoldDate']+',' +item['LastSold']+',' +item['RentPrice']+',' +item['Type']+',' +item['BedRoom']+',' +item['BathRoom']+',' +item['CarSpace']+',' +item['LandSize']+',' +item['BuildYear']+',' +item['Agent']+',' +item['Distance'] +'\n')
        writer.writerow([item['Addr'],item['SoldPrice'], item['SoldDate'],item['LastSold'],item['RentPrice'],item['Type'],item['BedRoom'],item['BathRoom'],item['CarSpace'],item['LandSize'],item['BuildYear'],item['Agent'],item['Distance']])
    ResultFile.close()