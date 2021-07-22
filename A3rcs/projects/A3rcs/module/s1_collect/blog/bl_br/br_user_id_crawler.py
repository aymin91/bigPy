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
#      2019.11.13
#         - add new module 'def run_step()'
#
#      2019.11.18
#         - delete 'def get_mag_info(post, is_mag)'
#         - change 'def get_normal_info' -> 'def get_blogger_info'
#           regex = re.compile('[/@]\w+[/]\d+')
#           id_num = regex.search(str(mArticles[0]))
#           num_id = id_num.group()
#
#           blogger_id = num_id[1:num_id.find('/')]
#           blogger_nick = post.find(id, class_='link_bloger #writers').text
#           newest_num = num_id[num_id.find('/') + 1:]
#         - change  def gather_blogger_info(driver)
#                   delete 'is_mag'part
#           change def make_save_df
#                  'BR_user_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
#                   -> 'BR_ID_List_{0}_{1}_{2}.csv'.format(now.year, now.month, now.day), index=False,
#       2019.11.21
#          - chaged 'def get_blooger_info
#               regex = re.compile('[/@]\w+.\w+.\w+[/]\d+')
#               is_valid_regex = True if regex.search(str(post)) else print(post)
#               if is_valid_regex:
#                   num_id = regex.search(str(post)).group()
#               else:
#                   regex_v2 = re.compile('[/@]\w+.\w+[/]\d+')
#                   num_id = regex_v2.search(str(post)).group()
#              chaged 'def make_save_df
#                      add  blogger_info_df = blogger_info_df['blogger_id'] != None
#          - add  'def get_headless_driver()
#      2019.11.26
#          - add root_dir = get_root_dir() /  blog_mgr = get_blog_mgr() / file_dir = get_file_dir()
#            BASE_URL = get_user_url(blog_mgr, blog_code)   driver_path = util.get_webdriver_path(browser='Chrome')
#          - change get_driver, get_headless_driver
#          - change make_BR_DF / rep_dir = root_dir + util.get_post_dir(file_dir)


from selenium import webdriver
from bs4 import BeautifulSoup

import pandas as pd
import re

import time
import glob
import os

import module.s1_collect.comm.util as util
from module.s1_collect.blog.bl_br import br_user_lpn_crawler as bulc


BLOG_NAME = "BRUNCH"
root_dir = util.get_root_dir()
file_dir = util.get_file_dir()
rep_dir = root_dir + util.get_user_dir(file_dir)
# blog_mgr = util.get_blog_mgr()


BLOG_CODE = util.get_blog_code(BLOG_NAME)
BASE_URL  = util.get_user_url(BLOG_CODE)
driver_path = util.get_webdriver_path()


#
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


############################################################################################
# STEP1. Blog Main 접속
############################################################################################

def go_blog_main():
    '''
    웹드라이브를 호출하는 메소드
    :param None
    :return: driver(ChromeWebDriver)
    '''
    # driver = get_driver(driver_path)
    driver = get_headless_driver(driver_path)
    driver.get(BASE_URL)

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

    scr_count = 28  # 2019.10.23 현재 확인횟수

    for i in range(scr_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    return driver


def get_blogger_info(post):
    '''
    blogger id와 nick, 최신 게시글 번호 수집
    :param post(bs4)
    :return blogger_info(dict)
    '''
    blogger_info = dict()

    try:
        regex = re.compile('[/@]\w+[/]\d+')
        is_valid_regex = True if regex.search(str(post)) else False
        if is_valid_regex:
            num_id = regex.search(str(post)).group()
        else:
            regex_v2 = re.compile('[/@]\w+.\w+[/]\d+')
            is_valid_regex_2 = True if regex_v2.search(str(post)) else False
            if is_valid_regex_2:
                num_id = regex_v2.search(str(post)).group()
            else:
                regex_v3 = re.compile('[/@]\w+.\w+.\w+[/]\d+')
                num_id = regex_v3.search(str(post)).group()

        user_id = num_id.split('/')[0]
        user_nick = post.find(id, class_='link_bloger #writers').text
        newest_num = num_id.split('/')[-1]

        blogger_info['user_id'] = user_id
        blogger_info['user_nick'] = user_nick
        blogger_info['newest_post_num'] = int(newest_num)
    except:
        pass
    # print(num_id)

    # user_id = num_id.split('/')[0]
    # blogger_nick = post.find(id, class_='link_bloger #writers').text
    # newest_num = num_id.split('/')[-1]
    #
    # blogger_info['user_id'] = user_id
    # blogger_info['blogger_nick'] = blogger_nick
    # blogger_info['newest_post_num'] = int(newest_num)

    return blogger_info


def gather_blogger_info(driver):
    '''
    모든 정보가 보여진 driver를 스크롤을 내린 후
    parisng한 후에 각각 blogger들의 id, nickname, 최신글 번호 정보를 딕셔너리에
    담아 리스트에 추가하여 반환
    :parmam : driver(ChromeWebDriver)
    :Result : all_blogger_info(list)
    '''
    driver = scroll_to_end(driver)
    all_blogger_info = list()

    soup = BeautifulSoup(driver.page_source, 'lxml')

    article = soup.find('article', id='mArticle')
    mArticles = article.find_all('li')

    for post in mArticles:
        blogger_info = get_blogger_info(post)
        all_blogger_info.append(blogger_info)

    driver.quit();

    return all_blogger_info


############################################################################################
# STEP3. 데이터프레임에 저장 및 csv 파일 저장
############################################################################################

def make_user_df(all_blogger_info):
    '''
    수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장
    :param   : all_now_blogger_info(list), all_friend_empathize_blogger_info(list)
    :return  : blogger_info_df(with. csv file)
    '''


    blogger_info_df = pd.DataFrame(all_blogger_info)


    # blogger_info_df = all_blogger_info_df.drop_duplicates()                    # 중복값 제거
    blogger_info_df = blogger_info_df[blogger_info_df['user_id'] != '']
    blogger_info_df = blogger_info_df.groupby(['user_id', 'user_nick'], as_index=False).agg({'newest_post_num': max})
    blogger_info_df.sort_values(by=['user_id'], axis=0, inplace=True)  # sorting
    blogger_info_df = blogger_info_df.reset_index()  # index reset
    del blogger_info_df['index']  # index column 제거

    blogger_info_df['oldest_post_num'] = '1'
    blogger_info_df['collecting_date'] = ' '

    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    if len(csv_files) == 1:
        print('새로운 id list가 수집되었습니다. new id list saved!')
        blogger_info_df.to_csv(rep_dir+'{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE),
                               index=False, encoding='utf-8')  # csv file로 저장
    else:
        print('기존 id list가 없어 기존 이름 id list로 저장됩니다.')
        blogger_info_df.to_csv(rep_dir+'{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')


    return None


#############################################################################################
# STEP4. 기존 ID  newest_post_num 수집
############################################################################################


def updating_newest_post_num():
    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))
    # print('기존 아이디 업데이트 합니다.')

    if '{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE) in csv_files:
        # print('기존 아이디 불러옵니다.')
        existing_csv = pd.read_csv(rep_dir + '{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), engine='python', encoding = 'utf-8')
        bulc.run_step(existing_csv)
    else:
        pass

    return None

############################################################################################
# STEP5. ID_LISt 갱신 및 저장
############################################################################################


def make_save_df():

    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    dataframes = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, engine='python')
        dataframes.append(df)

    result = pd.concat(dataframes, ignore_index=True)
    result = result.drop_duplicates(['user_id'], keep='first')
    result.to_csv(rep_dir + '{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')

    if os.path.isfile(rep_dir+ '{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE)):
        os.remove(rep_dir + '{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE))
        print('병합 성공, {blog_code} new id list는 삭제합니다'.format(blog_code=BLOG_CODE))

    return None



############################################################################################
# 실행
############################################################################################

def main():
    driver = go_blog_main()

    all_blogger_info = gather_blogger_info(driver)   # 신규 id 저장(TI_new_ID_List.csv)
    make_user_df(all_blogger_info)
    updating_newest_post_num()    # 신규 id 저장(TI_new_ID_List.csv)
    make_save_df()

    return None


if __name__ == '__main__':
    main()