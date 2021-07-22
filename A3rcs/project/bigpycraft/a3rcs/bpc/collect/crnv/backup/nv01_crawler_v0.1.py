#!/usr/bin/env python
# coding: utf-8

# In[1]:


import datetime
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from requests.adapters import HTTPAdapter
import requests


from selenium import webdriver as wd 
from bs4 import BeautifulSoup
from urllib.request import urlopen
import platform
from IPython.display import Image 
import pandas as pd
import time
import re 





def get_driver(url):
    
    # 드라이브 로드
    if platform.system() == 'Darwin':    # MacOS
        driver = wd.Chrome(executable_path='./chromedriver')      
    elif platform.system() == 'Windows': # Windows
        driver = wd.Chrome(executable_path='./chromedriver.exe') # ./driver/chromedriver.exe'
    else:
         print("It's unknown system. Hangul fonts are not supported!")
            
    driver.get(url)

    return driver

def soup_url(url):
    http = urlopen(url)
    soup = BeautifulSoup(http, 'html.parser')
    
    return soup

def switch_url(url):
    '''
    http://blog.naver.com/ 주소에 한정된 iframe switching 모듈입니다.
    iframe 전환 및 blog 메뉴로 곧바로 접속됩니다.
    '''

    re_url = url.replace('com/', 'com/PostList.nhn?blogId=')+'&directAccess=true&userTopListOpen=false&userTopListCount=30&userTopListCurrentPage=1'
    
    return re_url

def blog_basic_info(re_url):
    '''
    스위칭된 url로 기본 정보를 가져온다.
    
    Args:
        re_url : 스윗칭된 url주소, str
    
    Return:
    
    '''
    
    pattern = re.compile('blogId=\w+')
    b_id    = pattern.search(re_url)
    bloger_id = b_id.group().split('=')[1]
    
    blog_type = 'NV'  # 네이버 블로그 모듈이기에 상수다
    
    blog_basic =[bloger_id, blog_type]
    return blog_basic


def url_collect(driver):
    '''
    게시글 목록이 열려진 페이지에서 url을 수집하는 모듈입니다.
    list로 반환
    '''
    url_list = []
    
    url_collect = driver.find_element_by_xpath('//*[@id="listTopForm"]/table')
    url_a = url_collect.find_elements_by_tag_name('a')
    
    for u in url_a:
        url_list.append(u.get_attribute('href'))
        
    return url_list

def last_page(driver):
    time.sleep(2)   # 드라이버를 열고 바로 이 모듈을 호출할 경우 데이터를 못 불러와 에러남
    all_p = driver.find_element_by_xpath('//*[@id="category-name"]/div/table[2]/tbody/tr/td[2]/div/h4').text
    posts = all_p.split(' ')[1][:-2]
    all_post = int(posts.replace(',',''))
   
    # 30줄 보기 버전
    
    if all_post % 30 == 0:
        last_page = all_post // 30
    else:
        last_page = (all_post // 30) + 1
        
    print('총 ', all_post,'개의 글이 있으며 마지막 페이지는 ', last_page,'입니다.')  
    
    return last_page

# def url_first_10page(driver):
#     '''
#     처음 10페이지까지의 url을 전부 수집한다. 그리고 11페이지로 넘긴다.
#     url_collect 모듈이 사용된다.
#     Args 
#         driver : 크롬 웹 드라이버
        
#     Return
#         url_list : url정보가 담긴 리스트
    
#     '''
#     url_list = url_collect(driver)               
        
#     page_list = driver.find_element_by_xpath('//*[@id="toplistWrapper"]/div[2]/div').text
#     page_list = page_list.split('\n')
    
#     if page_list[-1] == '다음':
#         for i in range(1, 10):
#             path = '//*[@id="toplistWrapper"]/div[2]/div/a[{}]'.format(i)  
#             driver.find_element_by_xpath(path).click()
            
#             time.sleep(2)
            
#             url_list.extend(url_collect(driver))               
            
#     else :
#         pages = [i + 1 for i in range(len(page_li)-1)]
#         path = '//*[@id="toplistWrapper"]/div[2]/div/a[{}]'.format(page_list[i])  
#         driver.find_element_by_xpath(path).click()
            
#         time.sleep(2)
            
#         url_list.extend(url_collect(driver))
    
#     driver.find_element_by_xpath('//*[@id="toplistWrapper"]/div[2]/div/a[10]').click()
                                 
#     return url_list

def make_DF_nv():
    df = pd.DataFrame()
    df['blog_type'] = ''
    df['bloger_id'] = ''
    df['post_num'] = ''
    df['key'] = ''
    df['url'] = ''
    df['title'] = ''
    df['content'] = ''
    df['category'] = ''
    df['bloger_nick'] = ''
    df['date'] = ''
    
    return df


def all_page_urls(re_url, last_page):   
    '''
    글목록 url 주소를 받아 마지막페이지까지 돌면서
    url_collect 모듈을 사용,
    전체 글 url을 수집한다.
    
    Args:
        re_url     : 글목록 url주소, str
        last_page  : 글목록 마지막 페이지, int

    Return:
        url_list   : 전체 글 url 정보 list
       
    ''' 
    url_list = list()

    for i in range(last_page):
        re_url = re_url.replace('Page=1', 'Page={0}')
        new_url = re_url.format(i+1)
        driver.get(new_url)
        time.sleep(1)
        url_lis = url_collect(driver)
        url_list.extend(url_lis)
     
    print('총 ',len(url_list),'개의 url을 수집하였습니다.')
    
    return url_list
   

# 일단 parser

# def parser(soup):   # 구형파서
#     '''
#     soup module에서 가져온 soup 정보를 통해
#     글쓴이, 업로드 날짜, 제목, 내용을 가져옵니다.
#     return의 형태는 dictionary 입니다.
#     '''
    
#     import re
    
#     info = {}   # 정보를 담을 딕셔너리
    
#     # 페이지 내 본문 parser
#     all_content = soup.find('div',class_='se-viewer se-theme-default')
    
#     nickname = all_content.find('span', class_='nick').text                                                     # 글쓴이
#     upload_date = all_content.find('span', class_='se_publishDate pcol2').text                                  # 날짜
#     title = re.sub('\n','',all_content.find('div', class_='se-module se-module-text se-title-text').text)       # 제목
#     content = re.sub('\n|\u200b','',all_content.find('div', class_='se-main-container').text)                   # 본문
    
#     info['nickname'] = nickname
#     info['upload_date'] = upload_date
#     info['title'] = title
#     info['content'] = content

#     return info


def parser(url_list):    # 신형 파서
    '''
    soup module에서 가져온 url_list(list)를 통해
    글쓴이, 업로드 날짜, 제목, 내용을 가져옵니다.
    return의 형태는 dictionary 입니다.
    '''
    
    info = {}   # 정보를 담을 딕셔너리
    nick = list()
    date = list()
    cate = list()
    tit = list()
    con = list()
    
    # 페이지 내 본문 parser
    for u in url_list:
        s = requests.Session()
        s.mount(u, HTTPAdapter(max_retries=3))
        r = s.get(u)
        soup = BeautifulSoup(r.text, 'html.parser')
        news_list = soup.find('div', {'class' : "postSubjectContent"})
        time.sleep(3)

        all_content = soup.find('div',class_='se-viewer se-theme-default')

        if bool(all_content) == True:
            nickname = all_content.find('span', class_='nick').text                                                     # 글쓴이
            upload_date = all_content.find('span', class_='se_publishDate pcol2').text                                  # 날짜
            category = re.sub('\n','',all_content.find('div', class_='blog2_series').text)
            title = re.sub('\n','',all_content.find('div', class_='se-module se-module-text se-title-text').text)       # 제목
            content = re.sub('\n|\u200b','',all_content.find('div', class_='se-main-container').text)                   # 본문
            url = u 
        else:
            else_all_content = soup.find('div', id='postListBody')
            nickname = nick[0]
            upload_date = else_all_content.find('p', class_='date fil5 pcol2 _postAddDate').text 
            category = re.sub('\t|\n|\xa0','',else_all_content.find('span', class_='cate pcol2').text)
            title = re.sub('\n','',else_all_content.find('span', class_='pcol1 itemSubjectBoldfont').text)
            content = re.sub('\n|\u200b','',else_all_content.find('div', id='postViewArea').text)   
            
            
        nick.append(nickname)
        date.append(upload_date)
        cate.append(category)
        tit.append(title)
        con.append(content)
        
    info['nickname'] = nick
    info['date'] = date
    info['category'] = cate
    info['title'] = tit
    info['content'] = con
    
    return info

def basic_DF(naver_blog_DF, blog_info, url_list):
    naver_blog_DF['blog_type'] = blog_info[1]
    naver_blog_DF['bloger_id'] = blog_info[0]
    naver_blog_DF['url'] = url_list
    
    pattern = re.compile('logNo=\w+')
    for u in range(0, len(url_list)):
        b_num    = pattern.search(url_list[u])
        post_num = b_num.group().split('=')[1]
        naver_blog_DF['post_num'][u] = post_num
        
    for i in range(0, len(naver_blog_DF)):
        naver_blog_DF['key'][i] = blog_info[1]+"_"+blog_info[0]+"_"+naver_blog_DF['post_num'][i]
    
    return naver_blog_DF


def complete_NB_DF(naver_blog_DF,info ):
    '''
    
    
    '''
#     naver_blog_DF['blog_type'] = bloger_id
#     naver_blog_DF['bloger_id'] = blog_type
#     naver_blog_DF['post_num'] = ''
#     naver_blog_DF['key'] = blog_type + '_' + bloger_id + '_' # + info['post_num']
#     naver_blog_DF['url'] = ''
    naver_blog_DF.loc[:,'title'] = pd.Series(info['title'])
    naver_blog_DF.loc[:,'content'] = pd.Series(info[ 'content'])
    naver_blog_DF.loc[:,'category'] = pd.Series(info['category'])
    naver_blog_DF.loc[:,'bloger_nick'] = pd.Series(info['nickname'])
    naver_blog_DF.loc[:,'date'] = pd.Series(info['date'])
    
    return naver_blog_DF

