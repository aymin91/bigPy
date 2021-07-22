#!/usr/bin/env python
# coding: utf-8

# In[ ]:
# History :
#
#       2019.11.08
#           - 'def get_all_board_url' is updated
#              add m_board_url_list = common_util(board_url_list) by Min

#           - 'def find_content_info'
#             update : add   'content_info['board_url'] = board_url'
#                      add
#                            try:
#                               cons = con[:-2] if '태그' in con[-2].text else con[:-1]
#                               for c in cons:
#                                   content += c.text
#                            except:
#                               con = cont.find_all(['p', 'b', 'strong', 'span'])
#                               cons = con[:-12]
#                               for c in cons:
#                                    content += c.text
#           - 'def make_basic_DF', 'def insert_TI_DF', 'update_save_TI_DF' are deleteld
#           - make new module 'def make_TI_DF'
#       2019.11.13
#           - 'def find_content_info' is updated(revise 'upload_date')
#             add:
#                   date = soup.find('time', class_='txt_date').text  # 날짜
#                   upload_date = date[:-6].replace('.', '')
#       2019.11.15
#           - import module.s1_collect.comm.util as ut
#       2019.11.18
#           - ver04 updated
#           - deleted : def get_num_of_articles / def is_valid_N_make_url / def common_util / def get_all_board_url
#           - updated : def find_content_info(board_url) -> def find_content_info(board_url,start_date, end_date)
#                           is_valid_date = check_is_valid_date(start_date, end_date, upload_date)
#                           if is_valid_date: / else pass
#                       def gather_all_content(blog_url_list) -> def gather_all_content(blog_url, latest_post_num, last_post_num=1)
#                           for i in range(last_post_num, latest_post_num):
#                               post_url = blog_url + '{}'.format(i + 1)
#                               m_post_url = util.convert_mobile_url(BLOG_TYPE , post_url)
#                               try:
#                                   content_info = find_content_info(m_post_url)
#                                   all_content_info.append(content_info)
#                               except:
#                               pass
#           - add : def run_step(latest_post_num, blogger_id, start_date, end_date, last_post_num=1):



from bs4 import BeautifulSoup
from urllib.request import urlopen

import pandas as pd


import module.s1_collect.comm.util as util

BASE_URL = 'tistory.com/'
BLOG_TYPE = 'TI'

PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
WD_CHROME_PATH_WIN = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'

######################################
# STEP1. 블로그에 접속
######################################

def get_blog_url(blogger_id):
    '''
    blogger_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
    (일반적인 blog_url 형식 : (blogger_id).tistory.com )

        :param blogger_id(str)
        :return: blog_url(str)
    '''
    
    base_url = BASE_URL

    blog_url =  'https://' + blogger_id + '.' + base_url  #'category'

    return blog_url

######################################
# STEP2. 전체 게시물 url 가져오기
######################################

# def common_util(board_url_list):
#     '''
#     게시글 url을 모바일 형태로 변환해 리스트로 반환한다.
#
#     :param    board_url_list(list)
#     :return   m_board_url_list(list)
#     '''
#     m_board_url_list = list()
#
#     for u in board_url_list:
#         loc_m = u.find('m/')
#         m_url = u[:loc_m] + 'm/' + u[loc_m:]
#         m_board_url_list.append(m_url)
#
#     return m_board_url_list


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

    nickname = soup.find('span', class_='txt_by').text  # 글쓴이
    # upload_date = soup.find('time', class_ = 'txt_date').text  # 날짜
    date = soup.find('time', class_='txt_date').text  # 날짜
    # upload_date = date[:-6].replace('.', '')
    upload_date = util.regex_convert_date(date)

    is_valid_date = check_is_valid_date(start_date, end_date, upload_date)
    if is_valid_date:
        nickname = soup.find('span', class_='txt_by').text
        board_category = soup.find('a', class_='txt_category').text if soup.find('a', class_='txt_category') else '분류없음'
        title = soup.find('h2', class_='tit_blogview').text

        content = ''
        cont = soup.find('div', class_='blogview_content')
        con = cont.find_all(['p', 'b', 'strong'])
            try:
                cons = con[:-2] if '태그' in con[-2].text else con[:-1]
                for c in cons:
                    content += c.text
            except:
                con = cont.find_all(['p', 'b', 'strong', 'span'])
                cons = con[:-12]
                for c in cons:
                    content += c.text
    else:
        pass

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
#        m_post_url = common_util(post_url)
        m_post_url = util.convert_mobile_url(BLOG_TYPE , post_url)
        try:
            content_info = find_content_info(m_post_url)
            all_content_info.append(content_info)
        except:
            pass

    return all_content_info


######################################
# STEP4. all_content_info 데이터프레임에 저장
#####################################

def make_TI_DF(all_content_info, blogger_id):
    '''
    all_content_info를 이용 데이터 프레임을 만든 뒤, 나머지 정보들(type, id, post_num, key)도 구한 후
    데이터 프레임을 저장한 뒤 반환한다.
        :param  : all_content_info(list), blogger_id(str)
        :return : dataframe(dataframe)
    '''

    cols = ['blog_type', 'blogger_id', 'post_num', 'key', 'board_url', 'title', 'content', 'category', 'nickname',
            'date']

    dataframe = pd.DataFrame(all_content_info)

    dataframe['blog_type'] = BLOG_TYPE
    dataframe['blogger_id'] = blogger_id
    dataframe['post_num'] = ''
    dataframe['key'] = ''
    for j in range(len(dataframe)):
        dataframe['post_num'][j] = dataframe['board_url'][j][dataframe['board_url'][j].find('m/') + 4:]

    for k in range(len(dataframe)):
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
    make_TI_DF(all_content_info, blogger_id)

    return None

# blogger_id = 'sixsimi'
# latest_post_num = 88 # 글은 82개
#
# blogger_id = 'futureindustry'
# latest_post_num = 455 # 글은 423개
#
# blogger_id = 'neotrois'
# latest_post_num = 571