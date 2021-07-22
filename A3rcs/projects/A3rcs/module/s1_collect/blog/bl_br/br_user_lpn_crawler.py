
# coding: utf-8

# In[ ]:


from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import platform
import datetime
import time

import pandas as pd

import os
import json
import module.s1_collect.comm.util as util

BLOG_NAME = "BRUNCH"
root_dir = util.get_root_dir()
file_dir = util.get_file_dir()
# blog_mgr = util.get_blog_mgr()


BLOG_CODE = util.get_blog_code(BLOG_NAME)
BASE_URL  = util.get_post_url(BLOG_CODE)
driver_path = util.get_webdriver_path()

# def get_driver(driver_path):
#     '''
#         웹드라이브를 호출하는 메소드
#         parmam : None
#         Result : driver(ChromeWebDriver)
#     '''
#
#     driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
#
#     return driver

def get_headless_driver(driver_path):
    '''
        웹드라이브를 호출하는 메소드
        parmam : None
        Result : driver  , ChromeWebDriver
    '''

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(driver_path, chrome_options=options) # executable_path=driver_path

    return driver


# ############################################################################################
# # STEP1. id, last_post_num의 리스트 만들기
# ############################################################################################


def make_list(dataframe):
    user_id = list(dataframe['user_id'])
    last_post_nums = list(dataframe['newest_post_num'])

    return user_id, last_post_nums

# ############################################################################################
# # STEP2. id, latest_post_num 정보 가져오기
# ############################################################################################


def get_blog_url(user_id):
    '''
    user_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
    (일반적인 blog_url 형식 : https://brunch.co.kr/(@user_id )#articles(글 목록)

        :param user_id(str)
        :return: blog_url(str)
    '''

    base_url = BASE_URL

    blog_url = base_url + '@' + user_id + '#articles'

    return blog_url


def get_latest_post_num(driver, user_id, last_post_num):
    '''

        :param     blog_info(bs4)
        :return    blogger_info(dict)
    '''
    blogger_info = dict()

    # wait = WebDriverWait(driver, 20)
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list_article list_post1 #post_list")))

    soup = BeautifulSoup(driver.page_source, 'lxml')
    post_list = soup.find('ul', class_='list_article list_post1 #post_list')

    try:
        posts = post_list.find_all('li')
        if len(posts[0].find_all('a')) == 1:
            nums = posts[0].find_all('a')[0]['href']
            latest_post_num = nums[nums.find('/', 2) + 1:]

        else:
            nums = posts[0].find_all('a')[1]['href']
            latest_post_num = nums[nums.find('/', 2) + 1:]

        blogger_info['user_id'] = user_id
        blogger_info['oldest_post_num'] = last_post_num
        blogger_info['newest_post_num'] = int(latest_post_num)

    except:
        blogger_info['user_id'] = user_id
        blogger_info['oldest_post_num'] = last_post_num
        blogger_info['newest_post_num'] = last_post_num

    # posts = post_list.find_all('li')
    # if len(posts[0].find_all('a')) == 1:
    #     nums = posts[0].find_all('a')[0]['href']
    #     latest_post_num = nums[nums.find('/', 2) + 1:]
    #
    # else:
    #     nums = posts[0].find_all('a')[1]['href']
    #     latest_post_num = nums[nums.find('/', 2) + 1:]
    #
    # blogger_info['user_id'] = user_id
    # blogger_info['last_post_num'] = last_post_num
    # blogger_info['latest_post_num'] = int(latest_post_num)

    return blogger_info



def gather_all_lpn(user_ids, last_post_nums):
    all_blogger_info = list()
    driver = get_headless_driver(driver_path)
    k = 0
    for num in range(len(user_ids)):
        blog_url = get_blog_url(user_ids[num])
        driver.get(blog_url)
        time.sleep(1)
        blogger_info = get_latest_post_num(driver, user_ids[num], last_post_nums[num])
        all_blogger_info.append(blogger_info)
        k += 1
        print(k)
    return all_blogger_info

# ############################################################################################
# # STEP3. 데이터프레임 및 저장
# ############################################################################################

def make_save_df(all_blogger_info):
    '''
    수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장
        :param   : all_blogger_info(list)
        :return  : blogger_info_df(with. csv file)
    '''
    now = datetime.datetime.now()

    blogger_info_df = pd.DataFrame(all_blogger_info)

    blogger_info_df.sort_values(by=['user_id'], axis=0, inplace=True)  # sorting
    blogger_info_df = blogger_info_df.reset_index()  # index reset
    del blogger_info_df['index']  # index column 제거

    rep_dir = root_dir + util.get_user_dir(file_dir)
    blogger_info_df.to_csv(rep_dir +
        'BR_ID_List_ver2.csv',
        index=False,
        encoding='utf-8')  # csv file로 저장

    return blogger_info_df  # blogger_info_df


############################################################################################
# 실행
############################################################################################

def run_step(dataframe):
    user_ids, oldest_post_num = make_list(dataframe)
    all_blogger_info = gather_all_lpn(user_ids, oldest_post_num)
    make_save_df(all_blogger_info)

    return None





# 개별 id, last_post_num
# ############################################################################################
# # STEP1. Blog Main 접속
# ############################################################################################
#
# def get_blog_url(user_id):
#     '''
#     user_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
#     (일반적인 blog_url 형식 : https://brunch.co.kr/(@user_id )#articles(글 목록)
#
#         :param blogger_id(str)
#         :return: blog_url(str)
#     '''
#
#     base_url = BASE_URL
#
#     blog_url = base_url + '@' + user_id + '/#articles'
#
#     return blog_url
#
#
#
# def go_blog_main(blogger_id) :
#     '''
#     웹드라이브를 호출하는 메소드
#     :param None
#     :return: driver(ChromeWebDriver)
#     '''
#
#     blog_url = get_blog_url(blogger_id)
#
#     driver = get_headless_driver()
#     driver.get(blog_url )
#
#     return driver
#
#
# ############################################################################################
# # STEP2. 블로거 정보 수집
# ############################################################################################
#
# def get_latest_post_num(driver, user_id, last_post_num):
#     '''
#
#         :param     blog_info(bs4)
#         :return    blogger_info(dict)
#     '''
#     blogger_info = dict()
#
#     soup = BeautifulSoup(driver.page_source, 'lxml')
#     post_list = soup.find('div', class_ ='wrap_article_list')
#     posts  = post_list.find_all('li')
#     if len(posts[0]) == 3:
#         latest_post_num = posts[0].find('a')['href'][posts[0].find('a')['href'].find('/', 1)+1:]
#     else:
#         latest_post_num = posts[0].find_all('a')[1]['href'][posts[0].find_all('a')[1]['href'].find('/',1)+1:]
#
#     blogger_info['user_id'] = user_id
#     blogger_info['last_post_num'] = last_post_num
#     blogger_info['latest_post_num'] = int(latest_post_num)
#
#     return blogger_info
#
#
#
#
# ############################################################################################
# # STEP3. 데이터프레임에 저장 및 csv 파일 저장
# ############################################################################################
#
# def make_save_df(all_blogger_info):
#     '''
#     수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장
#         :param   : all_blogger_info(list)
#         :return  : blogger_info_df(with. csv file)
#     '''
#     now = datetime.datetime.now()
#
#     blogger_info_df = pd.DataFrame(blogger_info)
#
#     blogger_info_df.sort_values(by=['user_id'], axis=0, inplace=True)  # sorting
#     blogger_info_df = blogger_info_df.reset_index()  # index reset
#     del blogger_info_df['index']  # index column 제거
#
#     blogger_info_df.to_csv(
#         'BR_user_id_over_1st_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
#         encoding='utf-8')  # csv file로 저장
#
#     return blogger_info_df  # blogger_info_df
#
#
# ############################################################################################
# # 실행
# ############################################################################################
#
# def run_step():
#     driver = go_blog_main()
#     all_blogger_info = get_latest_post_num(driver, blogger_id, last_post_num)
#     make_save_df(all_blogger_info)
#
#     return None

