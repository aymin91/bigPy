#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Project : AI-based Auto Analysis Report Creating System
# History :
#       2019.10.29
#         - is_valid_mag(post) 모듈 신설 by MIN
#           : 매거진 여부 체크해서 url 수집하는 모듈(기존의 긴 코드 정리)
#       2019.11.06
#          - add new module 'def go_blog_main()' by Min
#          - delete 'def is_valid_mag'
#          - 'def gather_blogger_info' is updated
#            add    'is_valid = True if len(post) == 9 else False'
#                   if is_valid:
#                       blogger_info = get_mag_info(post)
#                   else:
#                       blogger_info = get_normal_info(post)
#      2019.11.07
#         - 'def gather_blogger_info'
#           update : add  'driver = scroll_to_end(driver)'
#
#
#
#




from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import platform
import pandas as pd

import datetime
import time

BASE_URL = 'https://brunch.co.kr/now'

# PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
PROJECT_ROOT = './'
WD_CHROME_PATH_WIN = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'



def get_driver():
    '''
        웹드라이브를 호출하는 메소드
        parmam : None
        Result : driver(ChromeWebDriver)
    '''

    if platform.system() == 'Windows':  # MacOS
        driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_WIN)
    elif platform.system() == 'Darwin':  # Windows
        driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_MAC)
    elif platform.system() == 'Linux':  # Linux
        driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_LINUX)
    else:
        print("It's unknown system. Hangul fonts are not supported!")

    return driver

############################################################################################
# STEP1. Blog Main 접속
############################################################################################

def go_blog_main() :
    '''
    웹드라이브를 호출하는 메소드
    :param None
    :return: driver(ChromeWebDriver)
    '''
    driver = get_driver()
    driver.get(BASE_URL )

    return driver

############################################################################################
# STEP2. 전체 블로거 정보 수집
############################################################################################

def scroll_to_end(driver):

    '''
    정보를 모두 보기 위해 스크롤을 내리는 메소드
    :param driver(ChromeWebDriver)
    :return: driver(ChromeWebDriver)
    '''

    scr_count = 28    # 2019.10.23 현재 확인횟수
    
    for i in range(scr_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    return driver


def get_mag_info(post):
    '''
    매거진인 글의 blogger id와 nick을 딕셔너리로 반환한다.
    :param post(bs4)
    :return blogger_info(dict)
    '''
    blogger_info = dict()

    blogger_id = post.find('a')['href'][1:]
    blogger_nick = post.find('a').text

    blogger_info['blogger_id'] = blogger_id
    blogger_info['blogger_nick'] = blogger_nick

    return blogger_info

def get_normal_info(post):
    '''
    매거진이 아닌 게시글의 blogger id와 nick을 딕셔너리로 반환한다.
    :param post(bs4)
    :return blogger_info(dict)
    '''
    blogger_info = dict()

    blogger_id = post.find_all('a')[1]['href'][1:]
    blogger_nick = post.find_all('a')[1].text

    blogger_info['blogger_id'] = blogger_id
    blogger_info['blogger_nick'] = blogger_nick

    return blogger_info

def gather_blogger_info(driver):
    '''
    모든 정보가 보여진 driver를 스크롤을 내린 후
    parisng한 후에 각각 blogger들의 id, nickname 정보를 딕셔너리에
    담아 리스트에 추가하여 반환
    :parmam : driver(ChromeWebDriver)
    :Result : all_blogger_info(list)
    '''
    driver = scroll_to_end(driver)
    all_blogger_info = list()
    
    soup = BeautifulSoup(driver.page_source, 'lxml')   
    posts = soup.find_all('div', class_ = 'append_common')
    for post in posts:
        is_valid = True if len(post) == 9 else False
        if is_valid:
            blogger_info = get_mag_info(post)
        else:
            blogger_info = get_normal_info(post)
        all_blogger_info.append(blogger_info)
            

    return all_blogger_info

############################################################################################
# STEP3. 데이터프레임에 저장 및 csv 파일 저장
############################################################################################

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

