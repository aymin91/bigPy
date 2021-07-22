# Project : AI-based Auto Analysis Report Creating System
# History :
#       2019.10.17
#           - 'as wd' is changed to 'webdriver' by MAY
#           - 'make_save_df' module is updated by MAY
#             (update : 'blogger_info_df['blogger_div']', sorting, drop_duplicates)
#
#       2019.10.21
#           - 'def navigate_url' -> 'def regex_insert_page_num' by MAY
#           - 'navi_url' -> 'regex_page_url' by MAY
#           - 'all_url' -> 'all_page_url' by MAY
#           - 중복값 제거 함수 추가 by MAY

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import platform
import pandas as pd

import datetime
import re

BASE_URL = 'https://section.blog.naver.com/BlogHome.nhn?directoryNo=0&currentPage=1&groupId=0'

PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
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

    return driver


############################################################################################
# STEP1. Blog Main 접속
############################################################################################
def go_blog_main():
    '''
        Blog Main Home에 접속하는 메소드
        :param   : None
        :return  : driver(ChromeWebdriver)
    '''
    driver = get_driver()
    driver.get(BASE_URL)

    return driver

############################################################################################
# STEP2. 전체 블로거 정보 확인
############################################################################################
def get_blogger_info(blogger_info_tag):
    '''
        블로거들의 정보를 담은 tag에서 blogger_nick, blogger_id를 찾아 dictionary로 반환해주는 메소드
        :param   : blogger_tag(bs4.tag)
        :return  : blogger_info(dict)
    '''
    blogger_info = dict()

    blogger_id = blogger_info_tag.a['href'].split('/')[-1]
    blogger_nick = blogger_info_tag.find('em').text

    blogger_info['blogger_id']    = blogger_id
    blogger_info['blogger_nick']  = blogger_nick

    return blogger_info

############################################################################################
# STEP3. 블로거 정보 수집
############################################################################################
def gather_blogger_info(driver) :
    '''
        blogger의 정보를 얻는 데에 필요한 메소드들을 실행시키는 메소드
        :param   : driver, all_page_url
        :return  : all_blogger_info(list, with. blogger_nick, blogger_id)
    '''

    all_blogger_info = list()

    for i in range(1, 101) :
        driver.get(regex_insert_page_num(i))

        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "info_post")))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        find_blogger_info_tag = soup.find_all('div', class_='info_post')

        for j in find_blogger_info_tag :
            get_info = get_blogger_info(j)
            all_blogger_info.append(get_info)

    return all_blogger_info

def regex_insert_page_num(page_num) :
    '''
        페이지를 넣어주는 모듈
        :param   : page_num(int)
        :return  : regex_page_url(url주소)
    '''

    regex_page_url = re.sub('currentPage=1', 'currentPage=' + str(page_num), BASE_URL)

    return regex_page_url

############################################################################################
# STEP4. 데이터프레임에 저장 및 csv 파일 저장
############################################################################################
def make_save_df(all_blogger_info) :
    '''
        수집한 blogger들의 정보를 데이터프레임으로 만들고 저장하는 메소드
        :param   : all_info
        :return  : NV_normal_blogger_df(with. csv file)
    '''
    now = datetime.datetime.now()

    blogger_info_df = pd.DataFrame(all_blogger_info)

    blogger_info_df = blogger_info_df.drop_duplicates()                    # 중복값 제거
    blogger_info_df.sort_values(by=['blogger_id'], axis=0, inplace=True)   # sorting
    blogger_info_df = blogger_info_df.reset_index()                        # index reset
    del blogger_info_df['index']                                           # index column 제거



    blogger_info_df.to_csv(
        'NV_blogger_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
        encoding='cp949')  # csv file로 저장

    return blogger_info_df

