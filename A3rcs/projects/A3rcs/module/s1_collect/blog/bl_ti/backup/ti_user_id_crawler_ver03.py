#      2019.11.13
#         - add new module 'def run_step()'
#
#       2019.11.15
#           - PROJECT_ROOT :  '/source/bigpycraft/a3rcs/' -- >  '../../'
#       2019.11.18
#           change def make_save_df
#                  'TI_user_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
#                   -> 'TI_ID_List_{0}_{1}_{2}.csv'.format(now.year, now.month, now.day), index=False,

from selenium import webdriver
from bs4 import BeautifulSoup

import platform
import datetime
import time

# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

BASE_URL = 'https://www.tistory.com/category/'


# PROJECT_ROOT = '../../'
PROJECT_ROOT = './module/s1_collect/'

WD_CHROME_PATH_WIN = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'


# def get_driver():
#     '''
#     웹드라이브를 호출하는 메소드
#         :param : None
#         :return: driver(ChromeWebDriver)
#     '''
#
#     if platform.system() == 'Windows':  # MacOS
#         driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_WIN)
#     elif platform.system() == 'Darwin':  # Windows
#         driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_MAC)
#     elif platform.system() == 'Linux':  # Linux
#         driver = webdriver.Chrome(executable_path=PROJECT_ROOT + WD_CHROME_PATH_LINUX)
#     else:
#         print("It's unknown system. Hangul fonts are not supported!")
#
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

def go_blog_main():
    '''
    웹드라이브를 호출하는 메소드
        :param None
        :return: driver(ChromeWebDriver)
    '''
    # driver = get_driver()
    driver = get_headless_driver()
    driver.get(BASE_URL)

    return driver


############################################################################################
# STEP2. 블로거 정보 수집
############################################################################################

def scroll_to_end(driver):
    '''
    웹드라이버를 받아 스크롤을 내린다.
    :param    driver(ChromeWebDriver)
    :return   driver(ChromeWebDriver)
    '''
    for i in range(50):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

    return driver


def get_blogger_info(blog_info):
    '''
    블로그 목록 중 하나의 bs4 parsing된 정보를 받아
    blogger_id.tistory.com 형태의 주소 blogger_id, blogger_nick을
    dict 형태로 수집
        :param     blog_info(bs4)
        :return    blogger_info(dict)
    '''
    href = blog_info.find('a')['href']
    url_adr = href.find('/', 7)
    url = href[:url_adr]
    newest_num = href[url_adr+1:]

    if 'tistory' in url:

        blogger_info = dict()

        blogger_id = url.split('.')[0][7:]

        blogger_nick = blog_info.find('span', class_='txt_date').get_text()[3:]


        blogger_info['blogger_id'] = blogger_id
        blogger_info['blogger_nick'] = blogger_nick
        try:
            blogger_info['newest_num'] = int(newest_num)
        except:
            blogger_info['newest_num'] = ' ' # url 주소가 숫자가 아니라 글자로 이루어진 사이트 발견 ex) https://semo-gif.tistory.com/
    elif 'tistory' not in url:
        blogger_info = None

    return blogger_info


def gather_best_blogger_info(driver):
    '''
    웹드라이버를 받아 현재 카테고리에서 '베스트'에 해당하는
    blogger_id와 nick을 수집해 리스트로 반환
        :param    driver(ChromeWebDriver):
        :return   best_blogger_info(list)
    '''
    best_blogger_info = list()

    soup = BeautifulSoup(driver.page_source, 'lxml')

    best_blogs = soup.find('ul', class_='list_tistory list_slide')
    best_blog = best_blogs.find_all('li')

    for bb in best_blog:
        blogger_info = get_blogger_info(bb)
        best_blogger_info.append(blogger_info)
    best_blogger_info = [bbi for bbi in best_blogger_info if bbi != None]

    return best_blogger_info


def gather_list_blogger_info(driver):
    '''
    웹드라이버를 받아 현재 카테고리에서 '리스트'에 해당하는
    blogger_id와 nick을 수집해 리스트로 반환
        :param    driver(ChromeWebDriver)
        :return   list_blogger_info(list)
    '''
    list_blogger_info = list()

    soup = BeautifulSoup(driver.page_source, 'lxml')

    list_blogs = soup.find('div', class_='section_list')
    list_blog = list_blogs.find_all('li')

    for lb in list_blog:
        blogger_info = get_blogger_info(lb)
        list_blogger_info.append(blogger_info)
    list_blogger_info = [lbi for lbi in list_blogger_info if lbi != None]

    return list_blogger_info


def one_category_blogger_info(best_blogger_info, list_blogger_info):
    '''
    blogger_id, blogger_nick 이 담긴 '베스트' 리스트와 '리스트' 리스트를 받아
    하나의 카테고리 리스트로 합친다.
    :param     best_blogger_info(list)
                list_blogger_info(list)
    :return    category_blogger_info(list)
    '''
    category_blogger_info = best_blogger_info + list_blogger_info

    return category_blogger_info


def gather_blogger_info(driver):
    '''
    웹드라이버를 받아 6가지 카테고리를 돌면서 각 카테고리에서 스크롤을 내려
    정보를 모두 표시한 후 best, list blogger_id와 blogger_nick을 수집한다.
    :param    driver(ChromeWebDriver)
    :return   all_blogger_info(list)
    '''
    all_blogger_info = list()

    categorys = ['life', 'travel', 'culture', 'it', 'sports', 'current']

    for cat in categorys:
        cat_url = BASE_URL + cat
        web_page = driver.get(cat_url)
        open_page = scroll_to_end(driver)  # driver.가 아니라 web_page를 돌렸을 때 드라이버가 없다는 오류가 났었음
        time.sleep(0.5)

        list_blogger_info = gather_list_blogger_info(open_page)
        best_blogger_info = gather_best_blogger_info(open_page)

        category_blogger_info = one_category_blogger_info(best_blogger_info, list_blogger_info)

        all_blogger_info.extend(category_blogger_info)
        time.sleep(1)

    driver.quit();
    return all_blogger_info


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

    blogger_info_df = pd.DataFrame(all_blogger_info)

    # blogger_info_df = blogger_info_df.drop_duplicates()  # 중복값 제거
    blogger_info_df = blogger_info_df.groupby(['blogger_id', 'blogger_nick'], as_index=False).agg( {'newest_num': max}) #
    blogger_info_df.sort_values(by=['blogger_id'], axis=0, inplace=True)  # sorting
    blogger_info_df = blogger_info_df.reset_index()  # index reset
    del blogger_info_df['index']  # index column 제거

    blogger_info_df.to_csv(
        'TI_ID_List_{0}_{1}_{2}.csv'.format(now.year, now.month, now.day), index=False,
        encoding='utf-8')  # csv file로 저장

    return blogger_info_df  # blogger_info_df


############################################################################################
# 실행
############################################################################################

def run_step():
    driver = go_blog_main()
    all_blogger_info = gather_blogger_info(driver)
    make_save_df(all_blogger_info)

    return None