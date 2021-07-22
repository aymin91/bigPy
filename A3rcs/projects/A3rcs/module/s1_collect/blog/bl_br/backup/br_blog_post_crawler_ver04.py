#!/usr/bin/env python
# coding: utf-8

# In[1]:
# History:
#       2019.11.01
#           - def is_valid_N_make_url 모듈 추가
#              : 글 개수 1개, 글 번호 4인 사례가 발견되어 케이스를 나눠
#                for문을 돌아가며 게시글 url 존재여부 판별
#       2019.11.11
#           - 'def make_basic_DF', 'def insert_BR_DF', 'update_save_BR_DF' are deleteld
#           -  make new module 'def make_BR_DF'
#           - 'def find_content_info'
#             update : add   'content_info['board_url'] = board_url'
#       2019.11.13
#           - 'def find_content_info' is updated(revise 'upload_date'
#             add:
#                   date = soup.find('span', class_='f_l date').text  # 날짜
#
#                   if date[-1] == '전':
#                       now = datetime.datetime.now()
#                       upload_date = str(now.year) + str(now.month) + str(now.day)
#                   else:
#                       months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
#                                 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
#                       year = date.split()[2]
#                       month = months[date.split()[0]]
#                       day = date.split()[1][:-1]
#                       upload_date = year + month + day
#       2019.11.15
#           - PROJECT_ROOT :  '/source/bigpycraft/a3rcs/' -- >  '../../'
#
#       2019.11.15
#           - PROJECT_ROOT :  '/source/bigpycraft/a3rcs/' -- >  '../../'
#       2019.11.18
#           - ver04 updated
#           - deleted : def get_num_of_articles / def is_valid_N_make_url / def get_all_board_url
#           - updated : def find_content_info(board_url) -> def find_content_info(board_url,start_date, end_date)
#                           is_valid_date = check_is_valid_date(start_date, end_date, upload_date)
#                           if is_valid_date: / else pass
#                       def gather_all_content(blog_url_list) -> def gather_all_content(blog_url, latest_post_num, last_post_num=1)
#                           for i in range(last_post_num, latest_post_num):
#                               post_url = blog_url + '{}'.format(i + 1)
#                               m_post_url = util.convert_mobile_url(BLOG_TYPE , post_url)
#                               try:
#                                   all_content_info.append(content_info)
#                               except:
#                               pass
#           - add : def run_step(latest_post_num, blogger_id, start_date, end_date, last_post_num=1):

from bs4 import BeautifulSoup
from urllib.request import urlopen

import pandas as pd

import datetime

import module.s1_collect.comm.util as ut

BASE_URL = 'https://brunch.co.kr/'
BLOG_TYPE = 'BR'

PROJECT_ROOT = '../../'

WD_CHROME_PATH_WIN = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'

######################################
# STEP1. 블로그에 접속
######################################

def get_blog_url(blogger_id):
    '''
    blogger_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
    (일반적인 blog_url 형식 : https://brunch.co.kr/(@blogger_id )#articles(글 목록)

        :param blogger_id(str)
        :return: blog_url(str)
    '''

    base_url = BASE_URL

    blog_url = base_url + '@' + blogger_id + '/'

    return blog_url


######################################
# STEP2. 전체 게시물 url 가져오기
######################################

def find_content_info(board_url,start_date, end_date):
    '''
    게시글의 url 주소와 시작과 끝날자를 받아 수집하는 기간 내의 게시글이면
    게시글 정보를 가져온다.
        :param    board_url(str)
        :return   content_info(dict)
    '''

    content_info = dict()

    http = urlopen(board_url)
    soup = BeautifulSoup(http, 'lxml')


    upload_date = util.regex_convert_date(date)

    is_valid_date = check_is_valid_date(start_date, end_date, upload_date)

    if is_valid_date:
        nickname = soup.find('div', id='wrapArticleInfo').find('a').text  # 글쓴이
        date = soup.find('span', class_='f_l date').text  # 날짜
        board_category = '분류없음'  # brunch는 블로거의 카테고리가 따로 존재 X. (단, 매거진 keyword별 수집 추후 검토, 매거진명은 상관없는 것들이 많아서 제외)
        title = soup.find('div', class_='wrap_cover').find('h1', class_='cover_title').text  # sub title 제외

        content = ''
        r_contents = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'blockquote'])
        contents = r_contents[4:]
        for con in contents:
            content += con.text.strip()
    else:
        pass

    # if date[-1] == '전':
    #     now = datetime.datetime.now()
    #     upload_date = str(now.year) + str(now.month) + str(now.day)
    # else:
    #     months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
    #               'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    #     year = date.split()[2]
    #     month = months[date.split()[0]]
    #     day = date.split()[1][:-1]
    #     upload_date = year + month + day

    content_info['nickname'] = nickname
    content_info['date'] = upload_date
    content_info['category'] = board_category
    content_info['title'] = title
    content_info['content'] = content
    content_info['board_url'] = board_url

    return content_info

######################################
# STEP3. 게시물 내용 파싱
######################################

def gather_all_content(blog_url, latest_post_num, last_post_num=1):
    '''
    가장 최신 게시글 번호 부터 for문을 돌리며 게시글 url을 만들어 내고,
    만약에 게시글이 존재하면  find_content_info를 수행해
    게시글 정보를 가져온다.
    :param blog_url(str)
    :param latest_post_num(str)
    :param last_post_num(str)
    :return: all_content_info(list)
    '''
    all_content_info = list()

    for i in range(last_post_num, latest_post_num):
        post_url = blog_url + '{}'.format(i + 1)
        try:
            content_info = find_content_info(post_url, start_date, end_date)
            all_content_info.append(content_info)
        except:
            pass

    return all_content_info

######################################
# STEP4. all_content_info 데이터프레임에 저장
######################################

def make_BR_DF(all_content_info, blogger_id):
    '''
    all_content_info를 이용 데이터 프레임을 만든 뒤, 나머지 정보들(type, id, post_num, key)도 구한 후
    데이터 프레임을 저장한 뒤 반환한다.
        :param    all_content_info(list), blogger_id(str)
        :return   dataframe(dataframe)
    '''

    cols = ['blog_type', 'blogger_id', 'post_num', 'key', 'board_url', 'title', 'content', 'category', 'nickname',
            'date']

    dataframe = pd.DataFrame(all_content_info)

    dataframe['blog_type'] = BLOG_TYPE
    dataframe['blogger_id'] = blogger_id
    dataframe['post_num'] = ''
    dataframe['key'] = ''
    for j in range(len(dataframe)) :
        dataframe['post_num'][j] = dataframe['board_url'][j][dataframe['board_url'][j].find('/', 21) + 1:]

    for k in range(len(dataframe)) :
        dataframe['key'][k] = BLOG_TYPE + "_" + blogger_id + "_" + dataframe['post_num'][k]

    dataframe = dataframe[cols]

    dataframe.to_csv('{0}_{1}.csv'.format(BLOG_TYPE, blogger_id), index=False)

    return dataframe

######################################
# STEP4. all_content_info 데이터프레임에 저장
#####################################

def run_step(latest_post_num, blogger_id, start_date, end_date, last_post_num=1):
    blog_url =  get_blog_url(blogger_id)
    all_content_info =  gather_all_content(blog_url, latest_post_num, start_date, end_date, last_post_num=1)
    make_BR_DF(all_content_info, blogger_id)

    return None

# blogger_id = 'sydney'
# latest_post_num = 58 # 글은 9개
#
# blogger_id = 'dies-imperi'
# latest_post_num = 174
#
# blogger_id = 'goodnews1472'
# latest_post_num = 119