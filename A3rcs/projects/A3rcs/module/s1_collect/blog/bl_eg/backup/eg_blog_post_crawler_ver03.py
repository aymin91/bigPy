# Project : AI-based Auto Analysis Report Creating System
# History :
#       2019.11.11
#           - 모듈 step 변경 by MAY
#
#       2019.11.15
#           - def get_content_info is changed by MAY
#             (add util.regex_convert_date/util.check_is_valid_date module)
#
#

import requests
from bs4 import BeautifulSoup

import re
import pandas as pd

import module.s1_collect.comm.util as util

BASE_URL = 'http://www.egloos.com/'
BLOG_TYPE = 'EG'

# blogger_id = 'swanjun, gerckm, kuroneko78, zen5852, alex2836, relucent, lcj1120'

################################################################################################
# STEP1. 블로그에 접속
################################################################################################
def get_blog_url(blogger_id) :
    '''
        blogger id를 받아와 blog url을 만들어주는 메소드
        :param   : blogger_id(str)
        :return  : blog_url(str)
    '''
    blog_url = re.sub('http://www.', 'http://' + blogger_id + '.', BASE_URL)

    return blog_url

################################################################################################
# STEP2. 전체 게시물 url 가져오기
################################################################################################
def find_per_year_info_tag(blog_url) :
    '''
        blog_url을 받아와 archive url을 만들고 년도별 url을 수집하기 위한 bs4.tag 정보를 찾는 메소드
        :param   : blog_url(str)
        :return  : archive_info(bs4.tag)
    '''
    arch_url = blog_url + 'archives'

    req = requests.get(arch_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    archive_info = soup.find('div', {'class' : 'content'})

    return archive_info


def get_per_year_url(blog_url) :
    '''
        blog_url과 archive info(bs4.tag)를 받아와 년도별 url을 수집하는 메소드
        :param   : blog_url(str)
        :return  : per_year_url_list(list, 년도별 게시판 url)
    '''
    per_year_url_list = list()

    archive_info = find_per_year_info_tag(blog_url)
    archive_tag = archive_info.find_all('a')

    for i in archive_tag :
        per_year_url_list.append(blog_url + i['href'])

    return per_year_url_list


def get_board_total_num(blog_url) :
    '''
        archive info(bs4.tag)를 받아와 년도별 게시물 개수와 년도별 게시판 페이지 개수를 구하는 메소드
        :param   : blog_url(str)
        :return  : board_total_page_num(list)
    '''
    board_total_num = list()
    board_total_page_num = list()

    archive_info = find_per_year_info_tag(blog_url)
    archive_num = archive_info.find_all('span')

    for i in archive_num :
        board_total_num = i.text[1 :-1]
        board_total_page_num.append(str(int(i.text[1 :-1]) // 10 + 1))

        print('전체 게시물 숫자는 ' + i.text[1 :-1] + '개, 전체 게시판 페이지 숫자는 ' + str(int(i.text[1 :-1]) // 10 + 1) + '입니다.')

    return board_total_page_num


def make_board_page_url(per_year_url_list, board_total_page_num) :
    '''
        per_year_url_list와 board_total_page_num를 받아와 년도별 게시판 페이지 url을 만드는 메소드
        :param   : per_year_url_list(list, 년도별 게시판 url), board_total_page_num(list)
        :return  : board_page_url_list(list)
    '''
    board_page_url_list = list()

    for i in range(0, len(per_year_url_list)) :
        for j in range(1, int(board_total_page_num[i]) + 1) :
            board_page_url_list.append(per_year_url_list[i] + '/list/' + str(j))

    return board_page_url_list


def find_board_url_tag(one_board_page_url) :
    '''
        1개의 게시판 url을 받아와 게시물들의 bs4.tag 위치를 찾는 메소드
        :param   : one_board_page_url(str)
        :return  : board_url_tag(bs4.tag)
    '''
    board_page_url = one_board_page_url
    req = requests.get(board_page_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    board_url_tag = soup.find('ul', {'class' : 'f_clear'})

    return board_url_tag


def get_board_url(blog_url, board_url_tag) :
    '''
        blog_url과 board_url_tag를 받아와 완전한 게시물 url로 만들어주는 메소드
        :param   : blog_url(str), board_url_tag(bs4.tag)
        :return  : board_url(list)
    '''
    board_url = list()

    board_url_href = board_url_tag.find_all('a')

    for i in board_url_href :
        board_url.append(blog_url + i['href'][1 :])

    return board_url


def get_all_board_url(blog_url, board_page_url_list) :
    '''
        게시판 url_list를 받아 게시물 url을 수집하여 list로 저장하는 메소드
        :param   : blog_url(str), board_page_url_list(list)
        :return  : board_url_list(list)
    '''
    board_url_list = list()

    for i in range(0, len(board_page_url_list)) :
        board_url_list += get_board_url(blog_url, find_board_url_tag(board_page_url_list[i]))

    return board_url_list


################################################################################################
# STEP3. 게시물 내용 파싱
################################################################################################
def find_content_info_tag(one_board_url) :
    '''
        1개의 게시물 url을 받아와 게시물 내용이 있는 bs4.tag를 찾는 메소드
        :param   : one_board_url(str)
        :return  : content_info_tag(bs4.tag)
    '''

    req = requests.get(one_board_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    content_info_tag = soup.find('div', {'class' : 'content'})

    return content_info_tag


def get_content_info(content_info_tag, start_date, end_date,) :
    '''
        content_info_tag을 받아와 게시물 내용을 수집하는 메소드
        :param   : content_info_tag(bs4.tag), start_date(str), end_date(str)
        :return  : content_info(dict)
    '''

    content_info = dict()

    upload_date = util.regex_convert_date(re.sub('\n|/|작성시간 :', '', content_info_tag.find('li', {'class' : 'post_info_date'}).text))

    is_valid_date = True if util.check_is_valid_date(start_date, end_date, upload_date) else False

    if is_valid_date:
        is_valid_cate_name = True if content_info_tag.find('span', {'class' : 'post_title_category'}) else False

        if is_valid_cate_name :
            board_category = re.sub('\n', '', content_info_tag.find('span', {'class' : 'post_title_category'}).text)
        else :
            board_category = re.sub('\n|카테고리 : ', '', content_info_tag.find('li', {'class' : 'post_info_category'}).text)

        title = re.sub('\n', '',content_info_tag.find('h2', {'class' : 'entry-title'}).text[:-len(board_category) - 1])
        content = re.sub('\n|♠|\xa0', '', content_info_tag.find('div', {'class' : 'hentry'}).text)
        nickname = re.sub('\n', '', content_info_tag.find('li', {'class' : 'post_info_author'}).text[3 :]).strip()
        upload_date = re.sub('\n|/|작성시간 :', '', content_info_tag.find('li', {'class' : 'post_info_date'}).text)

        content_info['title'] = title
        content_info['board_category'] = board_category
        content_info['upload_date'] = upload_date
        content_info['nickname'] = nickname
        content_info['content'] = content

    else:
        pass
    # print(content_info)

    return content_info


def gather_all_content(board_url_list, start_date, end_date) :
    '''
        board_url_list을 받아와 게시물 내용을 모두 수집하는 메소드
        :param   : board_url_list(list), start_date(str), end_date(str)
        :return  : all_content_info(list)
    '''
    all_content_info = list()

    for i in range(0, len(board_url_list)) :
        content_info_tag = find_content_info_tag(board_url_list[i])

        all_content_info.append(get_content_info(content_info_tag, start_date, end_date))

    return all_content_info

################################################################################################
# STEP4. all_content_info 데이터프레임에 저장
################################################################################################
def make_EG_DF(all_content_info, blogger_id) :
    '''
        기존에 만들어져있던 데이터 프레임에 새로운 정보를 추가하고 csv파일로 저장한 뒤 데이터프레임을 반환하는 메소드
        :param  : all_content_info(list), blogger_id(str)
        :return : dataframe(dataframe)
    '''

    cols = ['blog_type', 'blogger_id', 'post_num', 'key', 'board_url', 'title', 'content', 'board_category', 'nickname',
            'date']

    dataframe = pd.DataFrame(all_content_info)

    dataframe['blog_type'] = BLOG_TYPE
    dataframe['blogger_id'] = blogger_id
    dataframe['post_num'] = ''
    dataframe['key'] = ''

    for j in range(len(dataframe)) :
        post_num = dataframe['board_url'][j].split('/')[-1]
        dataframe['post_num'][j] = post_num

    for k in range(len(dataframe)) :
        dataframe['key'][k] = BLOG_TYPE+"_"+blogger_id+"_"+dataframe['post_num'][k]

    dataframe = dataframe[cols]

    dataframe.to_csv('{0}_{1}.csv'.format(BLOG_TYPE, blogger_id), index=False)

    return dataframe

def run_step(blogger_id, start_date, end_date):
    '''
        eg_blog_post_crawler의 모든 모듈을 실행시켜주는 메소드
        :param blogger_id(str), start_date(str), end_date(str)
        :return: None
    '''
    # step 1
    blog_url = get_blog_url(blogger_id)
    # step 2
    per_year_url_list = get_per_year_url(blog_url)
    board_total_page_num = get_board_total_num(blog_url)
    board_page_url_list = make_board_page_url(per_year_url_list, board_total_page_num)
    board_url_list = get_all_board_url(blog_url, board_page_url_list)
    # step 3
    all_content_info = gather_all_content(board_url_list, start_date,end_date)
    # step 4
    make_EG_DF(all_content_info, blogger_id)
    return None