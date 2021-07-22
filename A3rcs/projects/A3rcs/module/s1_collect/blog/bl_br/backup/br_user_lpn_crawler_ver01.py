
# coding: utf-8

# In[ ]:


from selenium import webdriver
from bs4 import BeautifulSoup

import platform
import datetime
import time

import pandas as pd

BASE_URL = 'https://brunch.co.kr/'

# PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
PROJECT_ROOT = './blogs/'

WD_CHROME_PATH_WIN = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'


# def get_driver():
#     '''
#     웹드라이브를 호출하는 메소드
#         :param : None
#         :return: driver(ChromeWebDriver)
#     '''

#     if platform.system() == 'Windows':  # MacOS
#         driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_WIN)
#     elif platform.system() == 'Darwin':  # Windows
#         driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_MAC)
#     elif platform.system() == 'Linux':  # Linux
#         driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_LINUX)
#     else:
#         print("It's unknown system. Hangul fonts are not supported!")

#     return driver

def get_headless_driver() :

    '''
        웹드라이브를 호출하는 메소드
        parmam : None
        Result : driver  , ChromeWebDriver
    '''

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    if platform.system() == 'Windows' :  # MacOS
        driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_WIN, chrome_options=options)
    elif platform.system() == 'Darwin' :  # Windows
        driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_MAC, chrome_options=options)
    elif platform.system() == 'Linux' :  # Linux
        driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_LINUX, chrome_options=options)
    else :
        print("It's unknown system. Hangul fonts are not supported!")

    return driver

############################################################################################
# STEP1. Blog Main 접속
############################################################################################

def get_blog_url(blogger_id):
    '''
    blogger_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
    (일반적인 blog_url 형식 : https://brunch.co.kr/(@blogger_id )#articles(글 목록)

        :param blogger_id(str)
        :return: blog_url(str)
    '''

    base_url = BASE_URL

    blog_url = base_url + '@' + blogger_id + '/#articles'

    return blog_url



def go_blog_main(blogger_id) :
    '''
    웹드라이브를 호출하는 메소드
    :param None
    :return: driver(ChromeWebDriver)
    '''
    
    blog_url = get_blog_url(blogger_id)
    
    driver = get_headless_driver()
    driver.get(blog_url )

    return driver


############################################################################################
# STEP2. 블로거 정보 수집
############################################################################################

def get_latest_post_num(driver, blogger_id, last_post_num):
    '''

        :param     blog_info(bs4)
        :return    blogger_info(dict)
    '''
    blogger_info = dict()
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    post_list = soup.find('div', class_ ='wrap_article_list')
    posts  = post_list.find_all('li')
    if len(posts[0]) == 3:
        latest_post_num = posts[0].find('a')['href'][posts[0].find('a')['href'].find('/', 1)+1:]
    else:
        latest_post_num = posts[0].find_all('a')[1]['href'][posts[0].find_all('a')[1]['href'].find('/',1)+1:]
    
    blogger_info['blogger_id'] = blogger_id
    blogger_info['last_post_num'] = last_post_num
    blogger_info['latest_post_num'] = int(latest_post_num)
    
    return blogger_info




############################################################################################
# STEP3. 데이터프레임에 저장 및 csv 파일 저장
############################################################################################

def make_save_df(all_blogger_info):
    '''
    수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장
        :param   : all_blogger_info(list)
        :return  : blogger_info_df(with. csv file)
    '''
    now = datetime.datetime.now()

    blogger_info_df = pd.DataFrame(blogger_info)

    blogger_info_df.sort_values(by=['blogger_id'], axis=0, inplace=True)  # sorting
    blogger_info_df = blogger_info_df.reset_index()  # index reset
    del blogger_info_df['index']  # index column 제거

    blogger_info_df.to_csv(
        'BR_user_id_over_1st_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
        encoding='utf-8')  # csv file로 저장

    return blogger_info_df  # blogger_info_df


############################################################################################
# 실행
############################################################################################

def run_step():
    driver = go_blog_main()
    all_blogger_info = get_latest_post_num(driver, blogger_id, last_post_num)
    make_save_df(all_blogger_info)

    return None

