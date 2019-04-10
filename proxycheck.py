#Online proxy check function use in Sibana
#author simirror
import requests
#http://ip.6655.com/ip.aspx国内检测池
#http://whatismyip.akamai.com/
import socket
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
# chrome opt set
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
##################################################################################
#
#proxy json file IO,update
#
##################################################################################
#tcping check port connection;
def tcping(ipaddr,ipport):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(3)
    try:
        sk.connect((ipaddr,ipport))
        sk.close()
        return 1
    except Exception as e:
        print(str(ipaddr)+str(e))
        sk.close()
        return 0
#load json file
def map_load_web():
    with open("proxyweb.json",'r') as load_f:
        load_dict = json.load(load_f)
        return load_dict
#save json file
def map_save_web(new_dict):
    with open("proxyweb.json",'w') as file:
        json.dump(new_dict,file)
        print("missions complete!")
#tcping proxy web connection
def proxyinfo_update():
    _jsons = map_load_web()
    proxyonline=0
    proxysum=len(_jsons['website_set'])
    for enter in _jsons['website_set']:
        if tcping(enter['check_host'],enter['check_port'])!=0:
            enter['web_last_life']=1
            proxyonline+=1
        else:
            enter['web_last_life']=0
    _jsons['proxysum']=proxysum
    _jsons['proxyonline']=proxyonline
    map_save_web(_jsons)
##################################################################################
#
#proxypool json file IO,and check
#
##################################################################################
def map_load_pool():
    with open("proxypool.json",'r') as load_f:
        load_dict = json.load(load_f)
        return load_dict
def map_save_pool(new_dict):
    with open("proxypool.json",'w') as file:
        json.dump(new_dict,file)
        print("missions complete!")
#init proxy pool
def proxy_inject():
    _onlineproxy = map_load_web()
    print("Online proxy website :"+str(_onlineproxy['proxyonline']))
    print("proxy website data :"+str(_onlineproxy['proxysum']))
    _onlinepool = map_load_pool()
    temp_proxy={}
    print("working proxy number is "+str(_onlinepool['proxysum']))
    if _onlinepool['proxysum']==0:
        _onlinepool['website_set']=[]
        for getting_url in _onlineproxy['website_set']:
            if getting_url['web_last_life']==0:
                continue
            else:
                S_ip_set = getproxylist(getting_url['weburl'])
                print(S_ip_set)
                for field in S_ip_set:
                    temp_proxy={}
                    if tcping(field[0],int(field[1]))==1:
                        temp_proxy['is_ping']=1
                        if proxyuse_check(field[0],int(field[1]),field[2])==1:
                            temp_proxy['proxy_host']=field[0]
                            temp_proxy['proxy_port']=field[1]
                            temp_proxy['is_use']=1
                            temp_proxy['http_type']=field[2]
                            _onlinepool.append(temp_proxy)
                    else:
                        continue
    map_save_pool(_onlinepool)
def proxypool_update():
    _jsons = map_load_pool()
    proxyonline=0
    proxysum=len(_jsons['website_set'])
    for enter in _jsons['website_set']:
        if tcping(enter['proxy_host'],enter['proxy_port'])!=0:
            enter['is_ping']=1
            if proxyuse_check(enter['proxy_host'],enter['proxy_port'],enter['proxy_type'])!=200:
                enter['is_use']=1
                proxyonline+=1
            else:
                enter['is_use']=0
        else:
            enter['is_ping']=0
    _jsons['proxysum']=proxysum
    _jsons['proxyonline']=proxyonline
    map_save_web(_jsons)
#get proxy url and info
def getproxylist(addr):
    return_array=[]
    temp_array=[]
    selectormode=99
    ip_pattern = re.compile(r'(I|ip)|IP')
    port_pattern = re.compile(r'port|PORT|Port|端口')
    type_pattern = re.compile(r'type|类型')
    selector_ip_index=0
    selector_port_index=0
    selector_type_index=99
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get(addr)
    if browser.find_elements_by_tag_name("thead")!=[]:
        test = browser.find_element_by_tag_name("thead")
        selectormode=0
    else :
        test = browser.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[0]
        selectormode=1
    print(len(browser.find_elements_by_tag_name("thead")))
    print(test.text)
    print("selector mode:"+str(selectormode))
    if test==[]:
        test=test.find_element_by_tag_name("tr")
        print(test)
        print("test modify is complete")
    selector = test.text.split(" ")
    print(selector)
    for indexer in selector:
        if ip_pattern.match(indexer):
            selector_ip_index = selector.index(indexer)
        if port_pattern.match(indexer):
            selector_port_index = selector.index(indexer)
        if type_pattern.match(indexer):
            selector_type_index = selector.index(indexer)
    print("index:"+str(selector_ip_index)+str(selector_port_index)+str(selector_type_index))
    test = browser.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
    for tester in test:
        temp_array=[]
        if selectormode==1:
            selectormode=0
            continue
        else:
            testersolo_ip=re.sub(r'[^\d.]',"",tester.find_elements_by_tag_name("td")[selector_ip_index].text)
            temp_array.append(testersolo_ip)
            testersolo_port=re.sub(r'[^\d]',"",tester.find_elements_by_tag_name("td")[selector_port_index].text)
            temp_array.append(testersolo_port)
            if selector_type_index==99:
                temp_array.append("html")
            else:
                temp_array.append(tester.find_elements_by_tag_name("td")[selector_type_index].text)
            return_array.append(temp_array)
    return return_array
def proxyuse_check(checkhost,checkport,types):
    try:
        requests.adapters.DEFAULT_RETRIES = 3
        IP = checkhost+":"+str(checkport)
        thisProxy = "http://" + IP
        s = requests.session()
        s.keep_alive = False # 关闭多余连接
        header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        res = s.get(url="http://ip.6655.com/ip.aspx",headers=header,timeout=5,proxies={types:thisProxy})
        proxyIP = res.text
        print(proxyIP)
        print(IP)
        if(proxyIP == checkhost):
            print(proxyIP+"is work")
            return 200
        else:
            print("mother fuck 1")
            return 0
    except:
        print("mother fuck 2")
        return 0
proxyinfo_update()
proxy_inject()