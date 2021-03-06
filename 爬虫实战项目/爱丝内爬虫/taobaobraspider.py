#-*-coding:utf-8-*-
import requests
import re
import time
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains#引入动作链
import pickle
import os
import sys
import win32api
import win32con
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'
COOKIES='__cfduid=d78f862232687ba4aae00f617c0fd1ca81537854419; \
            bg5D_2132_saltkey=jh7xllgK; \
            bg5D_2132_lastvisit=1540536781; \
            bg5D_2132_auth=479fTpQgthFjwwD6V1Xq8ky8wI2dzxJkPeJHEZyv3eqJqdTQOQWE74ttW1HchIUZpgsyN5Y9r1jtby9AwfRN1R89;\
            bg5D_2132_lastcheckfeed=7469%7C1541145866; \
            bg5D_2132_smile=1D1; \
            bg5D_2132_atarget=1; \
            bg5D_2132_visitedfid=41D38D65D44D81D2D73D52; \
            bg5D_2132_lip=113.116.247.56%2C1542974645; \
            bg5D_2132_ulastactivity=ebed2%2FIcR%2BJgOK4ZgbSMfbvb%2FoMicqXqOT9aou3X%2FT0z6h5dQfMS; \
            bg5D_2132_st_t=7469%7C1543028123%7C268cc1f5bc735c1406770754715736e3; \
            bg5D_2132_forum_lastvisit=D_41_1543028123; \
            bg5D_2132_sid=Bo8GCp; \
            Hm_lvt_b8d70b1e8d60fba1e9c8bd5d6b035f4c=1542594137,1542856492,1542937648,1543027830; \
            Hm_lpvt_b8d70b1e8d60fba1e9c8bd5d6b035f4c=1543028358; \
            bg5D_2132_lastact=1543028380%09misc.php%09patch'
class SeleniumCookie(object):
    def __init__(self,url):
        option = webdriver.ChromeOptions()
        
        # 设置中文
        option.add_argument('lang=zh_CN.UTF-8')
        #option.add_argument('--headless')
        option.add_argument('--disable-gpu')
        self.url_=url
        self.driver_ = webdriver.Chrome(chrome_options=option)
        self.driver_.get(self.url_)
        self.wait = WebDriverWait(self.driver_,timeout=15)
        self.initSession()
        self.path = os.path.dirname(os.path.abspath(__file__))  
        
    def initSession(self):
        self.session_=requests.Session()
        self.headers_ = {'User-Agent':USER_AGENT,}
        self.cookiejar_ = requests.cookies.RequestsCookieJar()
        for item in COOKIES.split(';'):
            name ,value = item.split('=',1)
            self.cookiejar_.set(name,value)
        pass

    def reqImgSave(self,url,imgpath):
        imgname= url.split('/')[-1]
        imgname=os.path.join(imgpath,imgname)
        if(os.path.exists(imgname)):
            return
        imgfile=self.session_.get(url,headers=self.headers_,timeout=5).content
        with open(imgname,'wb') as file:
            file.write(imgfile)

    def login(self):
        self.driver_.delete_all_cookies()
        for item in COOKIES.split(';'):
            name, value = item.split('=',1)
            name=name.replace(' ','').replace('\r','').replace('\n','')
            value=value.replace(' ','').replace('\r','').replace('\n','')
            cookie_dict = {
                    'name':name,
                    'value':value
                }                
            self.driver_.add_cookie(cookie_dict)
        self.refresh_page()
        time.sleep(5)

    def refresh_page(self):
        self.driver_.refresh()
            
    def findItemList(self):
        try:
            itemnode = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="portal_block_36_content"]')) )
            print(type(itemnode))   
            itemlist=itemnode.find_elements_by_tag_name('li')
            for item in itemlist[1:]:
                divtag=item.find_element_by_tag_name('div')
                itemdata=divtag.find_element_by_tag_name('a')
                #self.getItemPage(itemdata)
                self.getItemPage2(itemdata)
                #print(itemdata.get_attribute('href'))
            #print(itemlist)                                                               
            #//*[@id="portal_block_36_content"]/li[1]
            print("success!!!")
            pass
        except TimeoutException :
            print('TimeoutException')
            self.driver_.close()
        except NoSuchElementException:
            print('No Element')
            self.driver_.close()
        except:
            print('exception')
            self.driver_.close()
            pass

    def getItemPage(self,itemelement):
        try:
            actionChain = ActionChains(self.driver_)
            actionChain.context_click(itemelement).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
            time.sleep(2)
            self.switchWindow(1)
            self.driver_.execute_script('window.scrollBy(0,2000)')
            #点击大图
            '''
            node=self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="postlist"]/div[3]/div[1]/div[2]/div/table/tbody/tr/td[2]/div[2]/div/div[2]/div[2]/div[1]/a[2]') ) )
            print(node.text)
            node.click()
            time.sleep(2)
            '''
            #直接抓列表
            picliststr = '//*[@id="postlist"]/div[3]/div[1]/div[2]/div/table/tbody/tr/td[2]/div[2]/div/div[2]/div[2]/div[2]'
            picnodelist=self.wait.until(EC.presence_of_element_located((By.XPATH,picliststr) ) )
            piclist = picnodelist.find_elements_by_tag_name('ignore_js_op')
            listsize=len(piclist)
            for index in range(1,listsize+1):
                elementstr=picliststr+'/ignore_js_op['+str(index)+']/dl/dd/div[2]/img'
                picelement=self.wait.until(EC.presence_of_element_located((By.XPATH,elementstr) ) )
                print(picelement.get_attribute('file'))
                time.sleep(1)    
            # -1代表向下移动一个单位，-100也会向下移动一个单位，都是一个单位哦，亲~
            #win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,x0,-1)
            self.driver_.close()
            self.switchWindow(0)
        except TimeoutException :
            print('TimeoutException')
            self.driver_.close()
            self.switchWindow(0)
        except NoSuchElementException:
            print('No Element')
            self.driver_.close()
            self.switchWindow(0)
        except:
            print('exception')
            self.driver_.close()
            self.switchWindow(0)
            pass
    def switchWindow(self,index):
            #打开选项卡
        self.driver_.switch_to_window(self.driver_.window_handles[index])
        #self.refresh_page()

    def getItemPage2(self,itemelement):
        try:
            dirname=itemelement.get_attribute('title').split('[',1)[0].replace(' ','').replace('/','').strip()
            dirname=os.path.join(self.path,dirname)
            if(os.path.exists(dirname)==False):
                os.makedirs(dirname)
            actionChain = ActionChains(self.driver_)
            actionChain.context_click(itemelement).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
            time.sleep(2)
            self.switchWindow(1)
            self.driver_.execute_script('window.scrollBy(0,2000)')
            # 直接找到图片资源节点
            picliststr = "//ignore_js_op/descendant::img[@class='zoom']"
            picelements=self.wait.until(EC.presence_of_all_elements_located((By.XPATH,picliststr)))
            for picelement in picelements:
                picaddr=picelement.get_attribute('file')
                print(picaddr)
                self.reqImgSave(picaddr,dirname)
                time.sleep(1)
            self.driver_.close()
            self.switchWindow(0)
        except TimeoutException :
            print('TimeoutException')
            self.driver_.close()
            self.switchWindow(0)
        except NoSuchElementException:
            print('No Element')
            self.driver_.close()
            self.switchWindow(0)
        except:
            print('exception')
            self.driver_.close()
            self.switchWindow(0)
            pass

if __name__ == "__main__":
    seleniumcookie = SeleniumCookie('https://www.aisinei.org/portal.php')
    seleniumcookie.login()
    seleniumcookie.findItemList()
    

   
    
    
    
    
