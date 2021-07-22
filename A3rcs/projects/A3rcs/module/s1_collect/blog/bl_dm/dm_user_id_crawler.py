#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Project : AI-based Auto Analysis Report Creating System
# History :
#
#       2019.11.06
#           -  delete 'def get_soup' by MIN
#           -  add new module 'def go_blog_main()' by Min
#           - 'def gather_friend_empathize_blogger_info' is updated
#              get_soup --> BeautifulSoup(driver.page_source, 'lxml') in MIN
#           - 'def gather_friend_empathize_blogger_info(driver)' --> gather_blogger_info(driver, all_now_blogger_info)
#              delete 'all_friend_empathize_info'(list) / add 'all_blogger_info(list)' / add all_blogger_info(list).extend(all_now_blogger_info)
#           -  delete 'def click_more_btn'
#           - 'def make_save_df' is updated
#              param : (all_friend_empathize_info, all_now_blogger_info) --> (all_blogger_info)
#       2019.11.07
#           -  'def gather_blogger_info' is updated
#           -  add     all_now_blogger_info = gather_now_blogger_info(driver)
#                      driver = click_friend_more_btn(driver)
#                      driver = click_empathize_more_btn(driver)
#              param: (driver, all_now_bloggers_info) --> (driver)
#      2019.11.13
#         - add new module 'def run_step()'
#
#       2019.11.15
#           - PROJECT_ROOT :  '/source/bigpycraft/a3rcs/' -- >  '../../'
#       2019.11.18
#           change def make_save_df
#                  'DM_user_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
#                   -> 'DM_ID_List_{0}_{1}_{2}.csv'.format(now.year, now.month, now.day), index=False,
#       2019.11.21
#             add  def get_headless_driver()



from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

import os
import glob
import module.s1_collect.comm.util as util
import module.s1_collect.comm.util as util_v

BLOG_NAME = "DAUM"
root_dir = util.get_root_dir()
file_dir = util.get_file_dir()
rep_dir = root_dir + util.get_user_dir(file_dir)
# print('root', root_dir)
# print('file', file_dir)
# print('rep', rep_dir)
# blog_mgr = util.get_blog_mgr()


BLOG_CODE = util.get_blog_code(BLOG_NAME)
BASE_URL  = util.get_user_url(BLOG_CODE)
driver_path = util.get_webdriver_path()
# print('driver_path',driver_path)



# root_dir = util_v.get_root_dir()
# file_dir = util_v.get_file_dir()
# rep_dir = root_dir + util_v.get_user_dir(file_dir)
# # blog_mgr = util.get_blog_mgr()
#
#
# BLOG_CODE = util_v.get_blog_code(BLOG_NAME)
# BASE_URL  = util_v.get_user_url(BLOG_CODE)
# driver_path = util_v.get_webdriver_path()

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

def go_blog_main() :
    '''
    웹드라이브를 호출하는 메소드
        :param    None
        :return  driver(ChromeWebDriver)
    '''
    # driver = get_driver(driver_path)
    driver = get_headless_driver(driver_path)
    driver.get(BASE_URL )

    return driver


############################################################################################
# STEP2. 블로거 정보 수집
############################################################################################

def get_now_blogger_info(driver):
    '''
    웹드라이버를 받아 '지금, 이 블로그' 정보를 수집해 리스트로 반환
    :param driver(ChromeWebDriver)
    :return: now_bloggers_info(list)
    '''
    now_bloggers_info = list()
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    now_info = soup.find_all('div', class_ = 'item_post_type3')
    
    for ni in now_info:
        
        now_blogger_info = dict()
        
        href = ni.find('a',target = '_blank')['href']
        user_id = href[href.find('net')+4:]

        user_nick = ni.find('dd', class_ = 'txt_post_type2').text.strip()
        
        now_blogger_info['user_id'] = user_id
        now_blogger_info['user_nick'] = user_nick
        
        now_bloggers_info.append(now_blogger_info)
                
    return now_bloggers_info
    

def gather_now_blogger_info(driver):
    '''
    현재 드라이버에 있는 '지금, 이 블로그' 첫 페이지를 가져온 후 버튼을 세 번 누르며
    계속 현재 페이지의 블로거 ickname 정보를 딕셔너리에 담아 리스트에 추가하여
    반환(총 12개의 정보)
    :param   : driver(ChromeWebDriver)
    :return  : all_now_blogger_info(list)
    '''

    all_now_blogger_info = list()
    btn_count = 3        # 최대 3번 버튼을 누를 수 있다.(2019.10.22 기준)
    
    # 처음 세 개의 블로그 정보를 가져온다.
    
    now_bloggers_info = get_now_blogger_info(driver)
    all_now_blogger_info.extend(now_bloggers_info)

    # 버튼을 클릭하며 블로그 정보를 가져온다.
    
    for i in range(btn_count):
        try : 
            driver.find_element_by_css_selector('#nowBlog > div > div.slide_post > div.wrap_btn > button.btn_arrow.btn_next.btn_on').click()
            get_info_2 = get_now_blogger_info(driver)
            all_now_blogger_info.extend(get_info_2)
        except :                                    # 다음 버튼이 활성화 되지 않을 시의 코드 
            pass
            print('모든 게시글을 보았습니다. 다시 페이지를 앞으로 돌려 시도해주세요') 
            
    return all_now_blogger_info

def click_friend_more_btn(driver):
    '''
    현재 드라이버에서 '친구글'의 '더보기' 버튼을 클릭합니다.
    누르는 횟수는 최대 4번입니다.(2019.10.22 기준)
    :param   : driver(ChromeWebDriver)
    :return  : driver(ChromeWebDriver)
    '''

    btn_count = 4
    for i in range(btn_count):
        try:
            driver.find_element_by_css_selector('#mArticle > div:nth-child(1) > div > button').click()
            wait = WebDriverWait(driver, )
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mArticle > div:nth-child(1) > div > button')))
        except :
            pass
    return driver 

def click_empathize_more_btn(driver):
    '''
    현재 드라이버에서 '공감글'의 '전체'보기를 클릭한 후 더보기' 버튼을 클릭합니다.
    누르는 횟수는 최대 19번입니다.(2019.10.22 기준)
    :param   : driver(ChromeWebDriver)
    :return  : driver(ChromeWebDriver)
    '''
    
    # 전체 보기를 클릭합니다.
    
    # driver.find_element_by_css_selector('#mArticle > div:nth-child(3) > div > div.section_empathy > ul > li:nth-child(1) > a').click()
    driver.find_element_by_css_selector(
        '#mArticle > div:nth-child(3) > div > div.section_empathy > ul > li.on > a > span').click()
    
    # 더보기 버튼을 클릭합니다. 
    
    btn_count = 19
    
    for i in range(btn_count):
        try:
            driver.find_element_by_css_selector('#mArticle > div:nth-child(3) > div > div.section_empathy > a').click()
            wait = WebDriverWait(driver, 20)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mArticle > div:nth-child(3) > div > div.section_empathy > a')))
        except :
            pass
    return driver

def get_friend_blogger_info(soup):
    '''
    parsing된 soup 정보를 받아 '친구글'에 있는 블로거 id, nickname 정보를 딕셔너리에 담아
    리스트에 추가하여 반환
    :param   : soup(bs4)
    :return  : friend_blogger_info(list)
    '''

    friend_blogger_info = list()

    all_info = soup.find_all('div', class_ = 'list_post')
    friend   = all_info[1].find_all('div', class_ = 'item_post')
    
    for f in friend:
        blogger_info = dict()
        
        href = f.find('a')['href']
        b_id = href[href.find('net')+4:]
        user_id = b_id[:b_id.find('/')]

        user_nick = f.find('dd', class_ = 'txt_post_type1 txt_name').text
        
        blogger_info['user_id'] = user_id
        blogger_info['user_nick'] = user_nick
        
        friend_blogger_info.append(blogger_info)

    return friend_blogger_info
        
def get_empathize_blogger_info(soup):
    '''
    parsing된 soup 정보를 받아 '공감글'에 있는 블로거 id, nickname 정보를 딕셔너리에 담아
    리스트에 추가하여 반환
    :param   : soup(bs4)
    :return  : empathize_blogger_info(list)
    '''

    empathize_blogger_info = list()
    empathize = soup.find_all('div', class_ = 'item_post item_post_type4')
    
    for emp in empathize:
        blogger_info = dict()
        
        href = emp.find('a')['href']
        b_id = href[href.find('net')+4:]
        user_id = b_id[:b_id.find('/')]

        user_nick = emp.find('dd', class_ = 'txt_post_type1').text
        
        
        blogger_info['user_id'] = user_id
        blogger_info['user_nick'] = user_nick
        
        empathize_blogger_info.append(blogger_info)
        
    return empathize_blogger_info

def gather_blogger_info(driver):
    '''
    driver와 get_friend_blogger_info, get_empathize_blogger_info 모듈을 이용하여
    '지금, 이 이블로그', '친구글', '공감글' 블로거들의 id, nickname 정보를 딕셔너리에 담아 all_now_blogger_info와 최종적으로
    합쳐서 리스트 형태로 반환
    :param   : driver
    :return  : all_blogger_info(list)
    '''

    all_blogger_info = list()

    all_now_blogger_info = gather_now_blogger_info(driver)

    driver = click_friend_more_btn(driver)
    driver = click_empathize_more_btn(driver)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    friend_blogger_info = get_friend_blogger_info(soup)
    empathize_blogger_info = get_empathize_blogger_info(soup)

    all_blogger_info.extend(friend_blogger_info)
    all_blogger_info.extend(empathize_blogger_info)
    all_blogger_info.extend(all_now_blogger_info)

    driver.quit();
    return all_blogger_info

# ############################################################################################
# # STEP3. 데이터프레임에 저장 및 csv 파일 저장
# ############################################################################################

def make_save_df(all_blogger_info) :
    '''
        수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장하는 메소드
        :param   : all_blogger_info(list)
        :return  : blogger_info_df(with. csv file)
    '''

    blogger_info_df = pd.DataFrame(all_blogger_info)

    blogger_info_df['collecting_date'] = ''

    blogger_info_df = blogger_info_df.drop_duplicates()  # 중복값 제거

    blogger_info_df.sort_values(by=['user_id'], axis=0, inplace=True)  # sorting

    blogger_info_df = blogger_info_df.reset_index()  # index reset

    del blogger_info_df['index']  # index column 제거

    blogger_info_df['collecting_date'] = ' '

    try:
        util.create_file_dir(rep_dir)
    except:
        print('repository path is already existed!')
        pass

    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    if len(csv_files) == 1:
        print('새로운 id list가 수집되었습니다. new id list saved!')
        # print(rep_dir)
        blogger_info_df.to_csv(rep_dir+'{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE),
                               index=False, encoding='utf-8')  # csv file로 저장
    else:
        print('기존 id list가 없어 기존 이름 id list로 저장됩니다.')
        # print(rep_dir)
        blogger_info_df.to_csv(rep_dir+'{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')

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

    # os.remove(rep_dir+'{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')

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

    if len(csv_files) == 2:
        concat_id_list()
    else:
        pass

    return None

if __name__ == '__main__':
    main()



