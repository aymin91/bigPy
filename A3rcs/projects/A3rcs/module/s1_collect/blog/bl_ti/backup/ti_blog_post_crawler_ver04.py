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
#                               cons = con[:-2] if 'ํ๊ทธ' in con[-2].text else con[:-1]
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
#                   date = soup.find('time', class_='txt_date').text  # ๋ ์ง
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
# STEP1. ๋ธ๋ก๊ทธ์ ์ ์
######################################

def get_blog_url(blogger_id):
    '''
    blogger_id ๊ธฐ๋ณธ blog_url์ ํฉ์ณ ์ผ๋ฐ์ ์ธ blog_url ํ์์ผ๋ก ๋ง๋ค์ด์ค๋ค.
    (์ผ๋ฐ์ ์ธ blog_url ํ์ : (blogger_id).tistory.com )

        :param blogger_id(str)
        :return: blog_url(str)
    '''
    
    base_url = BASE_URL

    blog_url =  'https://' + blogger_id + '.' + base_url  #'category'

    return blog_url

######################################
# STEP2. ์ ์ฒด ๊ฒ์๋ฌผ url ๊ฐ์ ธ์ค๊ธฐ
######################################

# def common_util(board_url_list):
#     '''
#     ๊ฒ์๊ธ url์ ๋ชจ๋ฐ์ผ ํํ๋ก ๋ณํํด ๋ฆฌ์คํธ๋ก ๋ฐํํ๋ค.
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
    ๊ฒ์๊ธ์ url ์ฃผ์์ ์์๊ณผ ๋๋ ์๋ฅผ ๋ฐ์ ์์งํ๋ ๊ธฐ๊ฐ ๋ด์ ๊ฒ์๊ธ์ด๋ฉด
    ๊ฒ์๊ธ ์ ๋ณด๋ฅผ ๊ฐ์ ธ์จ๋ค.

        :param    board_url(str)
        :return   content_info(dict)
    '''

    content_info = dict()

    http = urlopen(board_url)
    soup = BeautifulSoup(http, 'lxml')

    nickname = soup.find('span', class_='txt_by').text  # ๊ธ์ด์ด
    # upload_date = soup.find('time', class_ = 'txt_date').text  # ๋ ์ง
    date = soup.find('time', class_='txt_date').text  # ๋ ์ง
    # upload_date = date[:-6].replace('.', '')
    upload_date = util.regex_convert_date(date)

    is_valid_date = check_is_valid_date(start_date, end_date, upload_date)
    if is_valid_date:
        nickname = soup.find('span', class_='txt_by').text
        board_category = soup.find('a', class_='txt_category').text if soup.find('a', class_='txt_category') else '๋ถ๋ฅ์์'
        title = soup.find('h2', class_='tit_blogview').text

        content = ''
        cont = soup.find('div', class_='blogview_content')
        con = cont.find_all(['p', 'b', 'strong'])
            try:
                cons = con[:-2] if 'ํ๊ทธ' in con[-2].text else con[:-1]
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
# STEP3. ๊ฒ์๋ฌผ ๋ด์ฉ ํ์ฑ
######################################


def gather_all_content(blog_url, latest_post_num, last_post_num=1):
    '''
    ๊ฐ์ฅ ์ต์  ๊ฒ์๊ธ ๋ฒํธ ๋ถํฐ for๋ฌธ์ ๋๋ฆฌ๋ฉฐ ๊ฒ์๊ธ url์ ๋ง๋ค์ด ๋ด๊ณ ,
    ๋ง์ฝ์ ๊ฒ์๊ธ์ด ์กด์ฌํ๋ฉด  find_content_info๋ฅผ ์ํํด
    ๊ฒ์๊ธ ์ ๋ณด๋ฅผ ๊ฐ์ ธ์จ๋ค.
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
# STEP4. all_content_info ๋ฐ์ดํฐํ๋ ์์ ์ ์ฅ
#####################################

def make_TI_DF(all_content_info, blogger_id):
    '''
    all_content_info๋ฅผ ์ด์ฉ ๋ฐ์ดํฐ ํ๋ ์์ ๋ง๋  ๋ค, ๋๋จธ์ง ์ ๋ณด๋ค(type, id, post_num, key)๋ ๊ตฌํ ํ
    ๋ฐ์ดํฐ ํ๋ ์์ ์ ์ฅํ ๋ค ๋ฐํํ๋ค.
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
# STEP4. all_content_info ๋ฐ์ดํฐํ๋ ์์ ์ ์ฅ
#####################################


def run_step(latest_post_num, blogger_id, start_date, end_date, last_post_num=1):
    blog_url =  get_blog_url(blogger_id)
    all_content_info =  gather_all_content(blog_url, latest_post_num, start_date, end_date, last_post_num=1)
    make_TI_DF(all_content_info, blogger_id)

    return None

# blogger_id = 'sixsimi'
# latest_post_num = 88 # ๊ธ์ 82๊ฐ
#
# blogger_id = 'futureindustry'
# latest_post_num = 455 # ๊ธ์ 423๊ฐ
#
# blogger_id = 'neotrois'
# latest_post_num = 571