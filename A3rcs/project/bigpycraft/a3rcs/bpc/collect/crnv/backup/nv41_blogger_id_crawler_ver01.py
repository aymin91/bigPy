# Project : AI-based Auto Analysis Report Creating System
# History : 
#

from selenium import webdriver as wd
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

import platform
import pandas as pd

import datetime
import re

BASE_URL = 'https://section.blog.naver.com/BlogHome.nhn?directoryNo=0&currentPage=1&groupId=0'
PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
WD_CHROME_PATH_WIN   = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC   = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'

def get_driver() :
    '''
        웹드라이브를 호출하는 메소드
        parmam : None
        Result : driver  , ChromeWebDriver
    '''

    if platform.system() == 'Windows' :  # MacOS
        driver = wd.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_WIN)
    elif platform.system() == 'Darwin' :  # Windows
        driver = wd.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_MAC)
    elif platform.system() == 'Linux' :  # Linux
        driver = wd.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_LINUX)
    else :
        print("It's unknown system. Hangul fonts are not supported!")

    return driver

############################################################################################
# STEP1.
############################################################################################
def navigating_page(page_num) :
    '''
        페이지를 넣어주는 모듈
        :param   : page_num(int)
        :return  : navi_url(url주소)
    '''
    navi_url = BASE_URL
    navi_url = re.sub('currentPage=1', 'currentPage=' + str(page_num), navi_url)

    return navi_url


def making_url() :
    '''
        페이지 별 url을 만들어주는 모듈
        :param   : None
        :return  : all_url(list)
    '''

    all_url = list()

    for i in range(1, 101) :
        all_url.append(navigating_page(i))

    return all_url

############################################################################################
# STEP2.
############################################################################################
def find_info(driver) :
    '''
        blogger_nick, blogger_id가 담긴 tag를 찾는 메소드
        :param   : driver, blog_home_url
        :return  : blogger_info(bs4.tag)
    '''
    tag_element = WebDriverWait(driver, 20).until(lambda x : x.find_element_by_class_name('info_post'))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    blogger_tag = soup.find_all('div', class_='info_post')

    return blogger_tag

############################################################################################
# STEP3.
############################################################################################
def get_blogger_info(blogger_tag) :
    '''
        블로거들의 정보를 담은 tag에서 blogger_nick, blogger_id를 찾아 dictionary로 반환해주는 메소드
        :param   : blogger_tag(bs4.tag)
        :return  : blogger_info(dict)
    '''
    blogger_info = dict()

    blogger_id = blogger_tag.a['href'].split('/')[-1]
    blogger_nick = blogger_tag.find('em').text

    blogger_info['blogger_id'] = blogger_id
    blogger_info['blogger_nick'] = blogger_nick

    return blogger_info

############################################################################################
# STEP4.
############################################################################################
def gather_blogger_info(driver, blog_home_url) :
    '''
        blogger의 정보를 얻는 데에 필요한 메소드들을 실행시키는 메소드
        :param   : driver, blog_home_url
        :return  : all_info(list, with. blogger_nick, blogger_id)
    '''

    all_info = list()

    for i in range(0, len(blog_home_url)) :
        driver = driver.get(blog_home_url[i])
        find_tag = find_info(driver)

        for j in find_tag :
            get_info = get_blogger_info(j)
            all_info.append(get_info)

    return all_info

############################################################################################
# STEP6.
############################################################################################
def make_save_df(all_info) :
    '''
        수집한 blogger들의 정보를 데이터프레임으로 만들고 저장하는 메소드
        :param   : all_info
        :return  : NV_normal_blogger_df(with. csv file)
    '''
    now = datetime.datetime.now()

    blogger_info_df = pd.DataFrame(all_info)

    blogger_info_df.to_csv(
        'NV_nm_blogger_{0}_{1}_{2}_{3}_{4}'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
        encoding='cp949')

    return blogger_info_df

















