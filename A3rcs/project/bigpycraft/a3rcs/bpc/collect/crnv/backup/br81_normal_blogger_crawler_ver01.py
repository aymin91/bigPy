#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Project : AI-based Auto Analysis Report Creating System
# History :


from selenium import webdriver
from bs4 import BeautifulSoup

import platform
import pandas as pd

import datetime
import time

BASE_URL = 'https://brunch.co.kr/now'

PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
# PROJECT_ROOT = './'
WD_CHROME_PATH_WIN = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'


def get_driver() :

    '''
        웹드라이브를 호출하는 메소드
        parmam : None
        Result : driver  , ChromeWebDriver
    '''

    if platform.system() == 'Windows' :  # MacOS
        driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_WIN)
    elif platform.system() == 'Darwin' :  # Windows
        driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_MAC)
    elif platform.system() == 'Linux' :  # Linux
        driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_LINUX)
    else :
        print("It's unknown system. Hangul fonts are not supported!")
        
    driver.get(BASE_URL)

    return driver


def scroll_to_end(driver):

    '''
        정보를 모두 보기 위해 스크롤을 내리는 메소드
        parmam : driver  , ChromeWebDriver
        Result : driver  , ChromeWebDriver
    '''

    scr_count = 28    # 2019.10.23 현재 확인횟수
    
    for i in range(scr_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
    return driver 

def get_blogger_info(driver):

    '''
        모든 정보가 보여진 driver를 받아 parisng한 후 각각 blogger들의
        id, nickname 정보를 딕셔너리에 담아 리스트에 추가하여 반환
        parmam : driver  , ChromeWebDriver
        Result :all_blogger_info  , list
    '''

    all_blogger_info = list()
    
    soup = BeautifulSoup(driver.page_source, 'lxml')   
    posts = soup.find_all('div', class_ = 'append_common')
    
    for post in posts:
        if len(post) == 9:
            blogger_info = dict()
        
            blogger_id = post.find('a')['href'][1:]
            blogger_nick = post.find('a').text
        
            blogger_info['blogger_id'] = blogger_id
            blogger_info['blogger_nick'] = blogger_nick
    
            all_blogger_info.append(blogger_info)
        else:
            blogger_info = dict()
        
            blogger_id = post.find_all('a')[1]['href'][1:]
            blogger_nick = post.find_all('a')[1].text
        
            blogger_info['blogger_id'] = blogger_id
            blogger_info['blogger_nick'] = blogger_nick
    
            all_blogger_info.append(blogger_info)
            

    return all_blogger_info


def make_save_df(all_blogger_info):
    
    '''
        수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장 
        :param   : all_now_blogger_info(list), all_friend_empathize_blogger_info(list)
        :return  : blogger_info_df(with. csv file)
    '''
    
    now = datetime.datetime.now()
    
    
    all_blogger_info_df = pd.DataFrame(all_blogger_info)

    blogger_info_df = all_blogger_info_df.drop_duplicates()                    # 중복값 제거
    blogger_info_df.sort_values(by=['blogger_id'], axis=0, inplace=True)   # sorting
    blogger_info_df = blogger_info_df.reset_index()                        # index reset
    del blogger_info_df['index']                                           # index column 제거



    blogger_info_df.to_csv(
        'BR_blogger_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
        encoding='cp949')  # csv file로 저장

    return blogger_info_df

