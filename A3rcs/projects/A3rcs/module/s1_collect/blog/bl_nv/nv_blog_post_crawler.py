# Project : AI-based Auto Analysis Report Creating System
# History :
#       2019.10.17
#           - 'as wd' is changed to 'webdriver' by MAY
#       2019.10.21
#           - 'category' - > 'board_category'(update_save_NB_DF)
#           - 'url' -> 'board_url' (insert_NB_DF)   by MIN
#           - driver.find_element_by_xpath --> driver.find_element_css_selector (get_last_page_num, board_url_collect)
#
#       2019.11.11
#           - 'def driver_open', 'def make_basic_DF', 'def insert_NV_DF', 'update_save_NV_DF' are deleteld
#           - name changed 'def get_blog_url' -> 'def get_url'
#           - name changed 'def blog_url_open -> 'def get_blog_url
#             add    blog_url = get_url(blogger_id)
#                    dir_url = switch_url(blog_url)
#             update : driver = driver_open(driver, dir_url) -> driver.get(dir_url)
#           - 'def find_content_info'
#             update : add   'content_info['board_url'] = board_url'
#
#       2019.11.13
#           - 주석처리 부분 모두 삭제 by MAY
#           - def board_url_collect in 'board_url' variable name is changed to 'b_url' by MIN
#
#       2019.11.15
#           - def nick_present/def nick_no_present are changed by MAY
#             (util.regex_convert_date/util.check_is_valid_date are added by MAY)
#
#       2019.11.18
#           - def make_NV_DF, dataframe.dropna() is added by MAY
#           - def nick_present / def nick_no_present, content['board_url] = board_url is added by MAY
#
#       2019.11.21
#             add  def get_headless_driver()
#       2019.11.28
#             - delete def run_step
#

from requests.adapters import HTTPAdapter
import requests

from selenium import webdriver
from bs4 import BeautifulSoup

import platform
import pandas as pd
import datetime

import time
import re

import module.s1_collect.comm.util as util

BLOG_NAME = "NAVER"
root_dir = util.get_root_dir()
file_dir = util.get_file_dir()
# blog_mgr = util.get_blog_mgr()


BLOG_CODE = util.get_blog_code(BLOG_NAME)
BASE_URL  = util.get_post_url(BLOG_CODE)
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

######################################
# STEP1. 블로그에 접속  --> go_main_blog로 (id크롤러참고)
######################################
def get_url(user_id):
    '''
    user_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
    (일반적인 blog_url 형식 : www.blog.naver.comm/(user_id) )
        :param   user_id(str)
        :return  blog_url(str)
    '''
    base_url = BASE_URL

    blog_url = base_url + user_id




    return blog_url


def switch_url(blog_url) :
    '''
    http://blog.naver.com/ 주소에 한정된 iframe switching 모듈입니다.
    iframe 전환 및 blog 메뉴로 곧바로 접속됩니다.
        :param   blog_url(str)
        :return  dir_url(str)
    '''

    dir_url = blog_url.replace('com/', 'com/PostList.nhn?blogId=') + \
              '&directAccess=true&userTopListOpen=True&userTopListCount=30&userTopListCurrentPage=1'

    return dir_url

def get_blog_url(user_id):
    '''
    user_id 받아 iframe swtiching 된 주소를 완성하고
    웹드라이버를 구동시켜 블로거의 블로그로 이동합니다.
        :param   user_id(str)
        :return  driver(ChromeWebDriver)
    '''

    blog_url = get_url(user_id)
    dir_url = switch_url(blog_url)

    # driver = get_driver(driver_path)
    driver = get_headless_driver(driver_path)
    driver.get(dir_url)

    return driver


######################################
# STEP2. 전체 게시물 url 가져오기
######################################

def get_last_page_num(driver):
    '''
    블로거의 블로그에 접속한 웹드라이버를 받아
    게시글 목록 마지막 페이지를 구합니다.
        :param    driver(ChromeWebDriver)
        :return   last_page_num(int)
    '''
    time.sleep(2)   # 드라이버를 열고 바로 이 모듈을 호출할 경우 데이터를 못 불러와 에러남

    all_post_path = driver.find_element_by_xpath('//*[@id="category-name"]/div/table[2]/tbody/tr/td[2]/div/h4').text
    post = all_post_path.split(' ')[1][:-2]
    all_post_num = int(post.replace(',',''))

    # 30줄 보기 버전

    if all_post_num % 30 == 0:
        last_page_num = all_post_num // 30
    else:
        last_page_num = (all_post_num // 30) + 1

    # print('총 ', all_post_num,'개의 글이 있으며 마지막 페이지는 ', last_page_num,'입니다.')

    return last_page_num

def board_url_collect(driver):
    '''
    게시글 목록이 열려진 페이지에서 url을 수집하는 모듈입니다.
    list로 반환
        :param    driver(ChromeWebDriver)
        :return   board_url
    '''
    board_url = list()

    board_url_path = driver.find_element_by_xpath('//*[@id="listTopForm"]/table')
    b_url = board_url_path.find_elements_by_tag_name('a')

    for b in b_url:
        board_url.append(b.get_attribute('href'))

    return board_url

def get_all_board_url(driver) :
    '''
    글목록 url 주소를 받아 마지막페이지를 구하고 돌면서
    board_url_collect 모듈을 사용, 전체 글 url을 수집해 리스트로 반환합니다.
        :param   driver(ChromeWebDriver)
        :return  board_url_list(list)
    '''
    board_url_list = list()
    dir_url = driver.current_url

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
# STEP3. 게시물 내용 파싱
######################################

def nick_present(board_url, content_info, blog_div, start_date, end_date) :
    '''
    parsing된 데이터인 all_content와 닉네임 여부인 blog_div를 받아,
    게시물에 닉네임이 있을 경우 사용하는 모듈
    :param    all_conten(bs4), blog_div(str), start_date(str), end_date(str)
    :return   nick_not_in_info
    '''

    nick_in_info = dict()
    crawl_date = content_info.find('span', class_='se_publishDate pcol2').text
    upload_date = util.regex_convert_date(crawl_date)  # 날짜

    is_valid_date = True if util.check_is_valid_date(start_date, end_date, upload_date) else False
    if is_valid_date:
        nickname = content_info.find('span', class_='nick').text  # 글쓴이

        board_category = re.sub('\n', '', content_info.find('div', class_='blog2_series').text)
        title = re.sub('\n', '', content_info.find('div', class_='pcol1').text)  # 제목
        date = util.datetime_fmt(crawl_date)
        is_valid_content = True if content_info.find('div', class_='se-main-container') else False

        if is_valid_content :
            content = re.sub('\n|\u200b|\xa0|\uf0fc|\t', '', content_info.find('div', class_='se-main-container').text)  # 본문
        else :
            content = re.sub('\n|\u200b|\xa0|\uf0fc|\t', '',
                             content_info.find('div', class_='se_component_wrap sect_dsc __se_component_area').text)  # 본문

        nick_in_info['nickname']  = nickname
        nick_in_info['board_url'] = board_url
        nick_in_info['date']      = str(date)
        nick_in_info['category']  = board_category
        nick_in_info['title']     = title
        nick_in_info['content']   = content
        nick_in_info['blog_div']  = blog_div   # nick네임 존재 여부 판단

    else:
        pass

    return nick_in_info


def nick_no_present(board_url, content_info, blog_div, start_date, end_date) :
    '''
    parsing된 데이터인 all_content와 닉네임 여부인 blog_div를 받아,
    게시물에 닉네임이 없을 경우 사용하는 모듈
    :param    all_conten(bs4), blog_div(str), start_date(str), end_date(str)
    :return   nick_not_in_info
    '''

    nick_not_in_info = dict()
    crawl_date = content_info.find('p', class_='date fil5 pcol2 _postAddDate').text
    upload_date = util.regex_convert_date(crawl_date)  # 날짜

    is_valid_date = True if util.check_is_valid_date(start_date, end_date, upload_date) else False
    if is_valid_date :
        nickname = ''
        board_category = re.sub('\t|\n|\xa0', '', content_info.find('span', class_='cate pcol2').text)
        title = re.sub('\n', '', content_info.find('span', class_='pcol1 itemSubjectBoldfont').text)
        content = re.sub('\n|\u200b|\xa0|\uf0fc|\t', '', content_info.find('div', id='postViewArea').text)
        date = util.datetime_fmt(crawl_date)

        nick_not_in_info['nickname']  = nickname
        nick_not_in_info['board_url'] = board_url
        nick_not_in_info['date']      = str(date)
        nick_not_in_info['category']  = board_category
        nick_not_in_info['title']     = title
        nick_not_in_info['content']   = content
        nick_not_in_info['blog_div']  = blog_div   # nick네임 존재 여부 판단

    else :
        pass

    return nick_not_in_info


def find_content_info(board_url, start_date, end_date) :  # 신형 파서
    '''
    board_url_list에서 board_url(한 게시물 주소)를 받아 parsing 한 후
    닉네임 여부를 판별해 각 정보 수집 모듈로 보낸 후 나온 dict 형태의
    정보를 반환합니다.
        :param    board_url(str)
        :return   content_info(dict)
    '''

    is_valid = False  # 게시물 존재 여부

    # 페이지 내 본문 parser
    sess = requests.Session()
    sess.mount(board_url, HTTPAdapter(max_retries=3))
    resp = sess.get(board_url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    board_content_info = soup.find('div', class_='post _post_wrap _param(1)')

    is_vaild = True if board_content_info.find('span', class_='nick') else False

    if is_vaild :
        content_info = nick_present(board_url, board_content_info, 'IN_INFO', start_date, end_date)
    else :
        content_info = nick_no_present(board_url, board_content_info, 'NO_INFO', start_date, end_date)

    return content_info


def gather_all_content(board_url_list, start_date, end_date) :
    '''
    parsing에 관련된 모든 모듈들을 실행시키는 모듈
        :param    url_list(list)
        :return   all_content_info(list)
    '''

    all_content_info = list()
    nums_of_posts = 0

    for b_url in board_url_list :
        nums_of_posts += 1
        if nums_of_posts % 100 == 0:
            time.sleep(1)


        # print(b_url)
        parsing = find_content_info(b_url, start_date, end_date)
        all_content_info.append(parsing)
    print(nums_of_posts)

    return all_content_info


######################################
# STEP4. all_content_info 데이터프레임에 저장
######################################

def make_blog_DF(all_content_info, user_id, full_path):
    '''
    all_content_info를 이용 데이터 프레임을 만든 뒤, 나머지 정보들(type, id, post_num, key)도 구한 후
    데이터 프레임을 저장한 뒤 반환한다.
        :param  : all_content_info(list), user_id(str)
        :return : dataframe(dataframe)
    '''
    try:
        cols = ['blog_code', 'user_id', 'post_num', 'key', 'board_url', 'title', 'content', 'category', 'nickname',
                'date']

        dataframe = pd.DataFrame(all_content_info, columns=cols)

        dataframe['blog_code'] = BLOG_CODE
        dataframe['user_id'] = user_id
        dataframe['post_num'] = ''
        dataframe['key'] = ''

        pattern = re.compile('logNo=\w+')

        for j in range(len(dataframe)):
            if str(dataframe['board_url'][j]) != 'nan' :
                reg_post_num = pattern.search(dataframe['board_url'][j])
                post_num = reg_post_num.group().split('=')[1]
                dataframe['post_num'][j] = str(post_num)
            else :
                pass

        for k in range(len(dataframe)):
            dataframe['key'][k] = BLOG_CODE + "_" + user_id + "_" + dataframe['post_num'][k]

        dataframe = dataframe.dropna(axis=0)

        # dataframe.to_csv('{0}_{1}.csv'.format(blog_code, user_id), index=False)

        is_saved = util.save_df2csv(dataframe, full_path)

        is_made = True


    except Exception as e:
        print(e)
        is_made = False

    return is_made
