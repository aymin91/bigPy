# Project : AI-based Auto Analysis Report Creating System
# History :
#       2019.10.17
#           - 'as wd' is changed to 'webdriver' by MAY
#       2019.10.21
#           - 'category' - > 'board_category'(update_save_NB_DF)
#           - 'url' -> 'board_url' (insert_NB_DF)   by MIN
#
#       2019.11.04
#           - 'def driver_open' function is deleted by MAY
#           - 'driver = driver_open(driver, dir_url)' in 'def blog_url_open' function is changed by MAY
#              >> 'driver = driver_open(driver, dir_url)' -> 'driver = driver.get(dir_url)'
#           - 'def get_blog_url' function is deleted by MAY
#           - 'def switch_url' function's name is changed 'def switch_all_list_page' function by MAY
#           - 'blog_url = BASE_URL + blogger_id' is added in 'def switch_all_list_page' function by MAY
#
#
#

from urllib.request import urlopen
from requests.adapters import HTTPAdapter
import requests

from selenium import webdriver
from bs4 import BeautifulSoup

import platform
import pandas as pd

import time
import re 

PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
WD_CHROME_PATH_WIN   = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC   = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'

BASE_URL = 'https://blog.naver.com/'
BLOG_TYPE = 'NV'

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


################################################################################################
# STEP1. 블로그에 접속
################################################################################################



################################################################################################
# STEP2. 전체 게시물 url 가져오기
################################################################################################



################################################################################################
# STEP3. 게시물 내용 파싱
################################################################################################


################################################################################################
# STEP4. all_content_info 데이터프레임에 저장
################################################################################################


######################################
# STEP1
######################################

def switch_all_list_page(blogger_id) :
    '''
    blogger_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
    (일반적인 blog_url 형식 : www.blog.naver.com/(blogger_id) )
    http://blog.naver.com/ 주소에 한정된 iframe switching 모듈입니다.
    iframe 전환 및 blog 메뉴로 곧바로 접속됩니다.
    :param   : blogger_id(str, 블로거 id)
    :return  : dir_url (str)
    '''

    blog_url = BASE_URL + blogger_id
    dir_url = blog_url.replace('com/', 'com/PostList.nhn?blogId=') + \
             '&directAccess=true&userTopListOpen=True&userTopListCount=30&userTopListCurrentPage=1'

    return dir_url

######################################
# STEP2
######################################

def open_dir_url(dir_url):
    driver = get_driver()
    driver = driver.get(dir_url)

    return driver

######################################
# STEP3
######################################
def get_last_page_num(driver):
    time.sleep(2)   # 드라이버를 열고 바로 이 모듈을 호출할 경우 데이터를 못 불러와 에러남

    all_post_path = driver.find_element_by_xpath('//*[@id="category-name"]/div/table[2]/tbody/tr/td[2]/div/h4').text
    post = all_post_path.split(' ')[1][:-2]
    all_post_num = int(post.replace(',',''))

    # 30줄 보기 버전

    if all_post_num % 30 == 0:
        last_page_num = all_post_num // 30
    else:
        last_page_num = (all_post_num // 30) + 1

    print('총 ', all_post_num,'개의 글이 있으며 마지막 페이지는 ', last_page_num,'입니다.')

    return last_page_num

def board_url_collect(driver):
    '''
    게시글 목록이 열려진 페이지에서 url을 수집하는 모듈입니다.
    list로 반환
    '''
    board_url_list = []

    board_url_path = driver.find_element_by_xpath('//*[@id="listTopForm"]/table')
    board_url = board_url_path.find_elements_by_tag_name('a')

    for b in board_url:
        board_url_list.append(b.get_attribute('href'))

    return board_url_list

def get_all_board_url(driver, dir_url) :
    '''
        글목록 url 주소를 받아 마지막페이지까지 돌면서
        url_collect 모듈을 사용,
        전체 글 url을 수집한다.

        Args:
            re_url     : 글목록 url주소, str
            last_page  : 글목록 마지막 페이지, int

        Return:
            url_list   : 전체 글 url 정보 list

    '''
    board_url_list = list()
    last_page_num = get_last_page_num(driver)

    for i in range(last_page_num) :
        navi_page = dir_url.replace('Page=1', 'Page={0}')
        next_page_url = navi_page.format(i + 1)

        driver.get(next_page_url)

        time.sleep(1)

        board_url = board_url_collect(driver)
        board_url_list.extend(board_url)

    print('총 ', len(board_url_list), '개의 url을 수집하였습니다.')

    return board_url_list

######################################
# STEP5
######################################

def make_basic_DF():
    '''
        기본 데이터프레임을 만들어 주는 모듈
        :return: df
    '''
    dataframe = pd.DataFrame()
    dataframe['blog_type']       = ''
    dataframe['blogger_id']      = ''
    dataframe['post_num']        = ''
    dataframe['key']             = ''
    dataframe['board_url']       = ''
    dataframe['title']           = ''
    dataframe['content']         = ''
    dataframe['board_category']  = ''
    dataframe['blogger_nick']    = ''
    dataframe['date']            = ''

    return dataframe

def insert_NB_DF(dataframe, blogger_id, board_url_list):
    blog_type = BLOG_TYPE
    blogger_id = blogger_id

    dataframe['board_url'] = board_url_list
    dataframe['blog_type'] = blog_type
    dataframe['blogger_id'] = blogger_id

    pattern = re.compile('logNo=\w+')
    for u in range(0, len(board_url_list)):
        reg_post_num    = pattern.search(board_url_list[u])
        post_num = reg_post_num.group().split('=')[1]
        dataframe['post_num'][u] = post_num

    for i in range(0, len(dataframe)):
        dataframe['key'][i] = blog_type+"_"+blogger_id+"_"+dataframe['post_num'][i]

    return dataframe

######################################
# STEP6
######################################

def nick_present(all_content, blog_div) :
    '''
        게시물에 닉네임이 있을 때 사용하는 모듈
        :return : info(list)
    '''

    nick_in_info = dict()

    nickname = all_content.find('span', class_='nick').text  # 글쓴이
    upload_date = all_content.find('span', class_='se_publishDate pcol2').text  # 날짜
    board_category = re.sub('\n', '', all_content.find('div', class_='blog2_series').text)
    title = re.sub('\n', '', all_content.find('div', class_='pcol1').text)  # 제목

    is_valid_content = True if all_content.find('div', class_='se-main-container') else False

    if is_valid_content :
        content = re.sub('\n|\u200b|\xa0|\uf0fc|\t', '', all_content.find('div', class_='se-main-container').text)  # 본문
    else :
        content = re.sub('\n|\u200b|\xa0|\uf0fc|\t', '',
                         all_content.find('div', class_='se_component_wrap sect_dsc __se_component_area').text)  # 본문

    nick_in_info['nickname'] = nickname
    nick_in_info['date'] = upload_date
    nick_in_info['category'] = board_category
    nick_in_info['title'] = title
    nick_in_info['content'] = content
    nick_in_info['blog_div'] = blog_div

    return nick_in_info


def nick_no_present(all_content, blog_div) :
    '''
        게시물에 닉네임이 없을 경우 사용하는 모듈
        :return : info(list)
    '''

    nick_not_in_info = dict()

    # else_all_content   = soup.find('div', id='postListBody')
    nickname = ''
    upload_date = all_content.find('p', class_='date fil5 pcol2 _postAddDate').text
    board_category = re.sub('\t|\n|\xa0', '', all_content.find('span', class_='cate pcol2').text)
    title = re.sub('\n', '', all_content.find('span', class_='pcol1 itemSubjectBoldfont').text)
    content = re.sub('\n|\u200b|\xa0|\uf0fc|\t', '', all_content.find('div', id='postViewArea').text)

    nick_not_in_info['nickname'] = nickname
    nick_not_in_info['date'] = upload_date
    nick_not_in_info['category'] = board_category
    nick_not_in_info['title'] = title
    nick_not_in_info['content'] = content
    nick_not_in_info['blog_div'] = blog_div

    # print('nick not in : ', nick_not_in_info)
    # print('=' * 100)
    return nick_not_in_info


def find_content_info(board_url) :  # 신형 파서
    '''
        soup module에서 가져온 url_list(list)를 통해
        글쓴이, 업로드 날짜, 제목, 내용을 가져옵니다.
    '''

    is_valid = False  # 게시물 존재 여부

    # 페이지 내 본문 parser
    sess = requests.Session()
    sess.mount(board_url, HTTPAdapter(max_retries=3))
    resp = sess.get(board_url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    all_content = soup.find('div', class_='post _post_wrap _param(1)')

    is_vaild = True if all_content.find('span', class_='nick') else False

    if is_vaild :
        content_info = nick_present(all_content, 'IN_INFO')
    else :
        content_info = nick_no_present(all_content, 'NO_INFO')

    return content_info


def gather_all_content(board_url_list) :
    '''
        parsing에 관련된 모든 모듈들을 실행시키는 모듈
        :param: url_list(모든 게시물에 대한 url list)
        :return: 모든 게시물에 대한 정보(list)
    '''

    all_content_info = list()

    for b_url in board_url_list :
        # print(b_url)
        parsing = find_content_info(b_url)
        all_content_info.append(parsing)

    return all_content_info

######################################
# STEP7
######################################

def update_save_NB_DF(dataframe, all_content_info, blogger_id) :
    '''
    기존에 만들어져 있던 데이터 프레임에 모든 게시물의 내용을 추가 및 저장

    :params : dataframe, parsed content, blog_type, user_id
    :return : dataframe(all_information in it)

    '''

    blog_type = BLOG_TYPE

    for num in range(len(dataframe)) :
        dataframe['title'][num]          = all_content_info[num]['title']
        dataframe['content'][num]        = all_content_info[num]['content']
        dataframe['board_category'][num]       = all_content_info[num]['category']
        dataframe['blogger_nick'][num]   = all_content_info[num]['nickname']
        dataframe['date'][num]           = all_content_info[num]['date']

    dataframe.to_csv('{0}_{1}.csv'.format(blog_type, blogger_id), index = False)

    return dataframe

