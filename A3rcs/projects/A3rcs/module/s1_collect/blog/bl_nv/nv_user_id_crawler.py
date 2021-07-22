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
#      2019.11.13
#         - add new module 'def run_step()'
#
#       2019.11.15
#           - PROJECT_ROOT :  '/source/bigpycraft/a3rcs/' -- >  '../../'
#       2019.11.18
#           change def make_save_df
#                  'NV_user_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
#                   -> 'NV_ID_List_{0}_{1}_{2}.csv'.format(now.year, now.month, now.day), index=False,
#       2019.11.21
#             add  def get_headless_driver()

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import pandas as pd
import os
import glob

import datetime
import re
import module.s1_collect.comm.util as util

BLOG_NAME = "NAVER"
root_dir  = util.get_root_dir()
file_dir  = util.get_file_dir()
rep_dir   = root_dir + util.get_user_dir(file_dir)
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
        Blog Main Home에 접속하는 메소드
        :param   : None
        :return  : driver(ChromeWebdriver)
    '''
    # driver = get_driver(driver_path)
    driver = get_headless_driver(driver_path)
    driver.get(BASE_URL)

    return driver

############################################################################################
# STEP2. 전체 블로거 정보 수집
############################################################################################
def get_blogger_info(blogger_info_tag):
    '''
        블로거들의 정보를 담은 tag에서 blogger_nick, user_id를 찾아 dictionary로 반환해주는 메소드
        :param   : blogger_tag(bs4.tag)
        :return  : blogger_info(dict)
    '''
    blogger_info = dict()

    user_id = blogger_info_tag.a['href'].split('/')[-1]
    user_nick = blogger_info_tag.find('em').text

    blogger_info['user_id']    = user_id
    blogger_info['user_nick']  = user_nick

    return blogger_info

def gather_blogger_info(driver) :
    '''
        blogger의 정보를 얻는 데에 필요한 메소드들을 실행시키는 메소드
        :param   : driver
        :return  : all_blogger_info(list, with. blogger_nick, user_id)
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

    driver.quit();

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
# STEP3. 데이터프레임에 저장 및 csv 파일 저장
############################################################################################
def make_save_df(all_blogger_info) :
    '''
        수집한 blogger들의 정보를 데이터프레임으로 만들고 저장하는 메소드
        :param   : all_blogger_info
        :return  : NV_normal_blogger_df(with. csv file)
    '''

    blogger_info_df = pd.DataFrame(all_blogger_info)

    blogger_info_df['crawling_date'] = ''

    blogger_info_df = blogger_info_df.drop_duplicates()                    # 중복값 제거

    blogger_info_df.sort_values(by=['user_id'], axis=0, inplace=True)   # sorting

    blogger_info_df = blogger_info_df.reset_index()                        # index reset

    del blogger_info_df['index']                                           # index column 제거

    blogger_info_df['collecting_date'] = ' '

    try:
        util.create_file_dir(rep_dir)
    except:
        print('repository path is already existed!')
        pass

    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    if len(csv_files) == 1 :
        print('새로운 id list가 수집되었습니다. new id list saved!')
        blogger_info_df.to_csv(rep_dir + '{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE),
                               index=False, encoding='utf-8')  # csv file로 저장
    else :
        print('기존 id list가 없어 기존 이름 id list로 저장됩니다.')
        blogger_info_df.to_csv(rep_dir + '{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False,
                               encoding='utf-8')

    return blogger_info_df

############################################################################################
# STEP4. 기존 csv file과 새롭게 수집한 csv file을 합쳐 중복 아이디 제거
############################################################################################
def concat_id_list():
    # folder_path = 'C:/projects/A3rcs/repository/user_id'
    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    dataframes = []

    for csv_file in csv_files :
        df = pd.read_csv(csv_file, engine='python')
        dataframes.append(df)
    #     print(csv_file)

    result = pd.concat(dataframes, ignore_index=True)
    result = result.drop_duplicates(['user_id', 'user_nick'], keep='first') #

    result = result.reset_index()  # index reset

    del result['index']  # index column 제거

    result.to_csv(rep_dir+'{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')

    print('병합 성공, new id list는 삭제합니다')

    os.remove(rep_dir+'{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE),)
    return None


############################################################################################
# 실행
############################################################################################

def main():
    driver = go_blog_main()
    all_blogger_info = gather_blogger_info(driver)
    make_save_df(all_blogger_info)

    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    if len(csv_files) == 2 :
        concat_id_list()
    else :
        pass

    return None

if __name__ == '__main__':
    main()


# run_step()