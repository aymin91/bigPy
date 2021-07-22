# Project : AI-based Auto Analysis Report Creating System
# History :

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

BASE_URL = 'http://www.egloos.com/'
BLOG_TYPE = 'EG'

# blogger_id = 'swanjun, gerckm, kuroneko78, zen5852, alex2836, relucent, lcj1120'

#######################################################################
# step 1. 블로그 url 만들기
#######################################################################
def make_blog_url(blogger_id) :
    '''
        blogger id를 받아와 blog url을 만들어주는 메소드
        :param   : blogger_id(str)
        :return  : blog_url
    '''
    blog_url = re.sub('http://www.', 'http://' + blogger_id + '.', BASE_URL)

    return blog_url

#######################################################################
# step 2. archive url 만들기
#######################################################################
def make_archive_url(blog_url) :
    '''
        blog_url을 받아와 년도별 게시판으로 접속하는 archive url을 만들어주는 메소드
        :param   : blog_url(str)
        :return  : arch_url(str)
    '''
    arch_url = blog_url + 'archives'

    return arch_url

#######################################################################
# step 3. archive 내에 있는 년도별 url 구하기
#######################################################################
def find_per_year_info_tag(arch_url) :
    '''
        archive url을 받아와 년도별 url을 수집하기 위한 bs4.tag 정보를 찾는 메소드
        :param   : arch_url(str)
        :return  : archive_info(bs4.tag)
    '''
    req = requests.get(arch_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    archive_info = soup.find('div', {'class' : 'content'})

    return archive_info


def get_per_year_url(blog_url, archive_info) :
    '''
        blog_url과 archive info(bs4.tag)를 받아와 년도별 url을 수집하는 메소드
        :param   : blog_url(str), archive_info(bs4.tag)
        :return  : per_year_url_list(list, 년도별 게시판 url)
    '''
    per_year_url_list = list()
    archive_tag = archive_info.find_all('a')

    for i in archive_tag :
        per_year_url_list.append(blog_url + i['href'])

    return per_year_url_list

#######################################################################
# step 4. 전체 게시물 숫자 구하기
#######################################################################
def get_board_total_num(archive_info) :
    '''
        archive info(bs4.tag)를 받아와 년도별 게시물 개수와 년도별 게시판 페이지 개수를 구하는 메소드
        :param   : archive_info(bs4.tag)
        :return  : board_total_page_num(list)
    '''
    board_total_num = list()
    board_total_page_num = list()

    archive_num = archive_info.find_all('span')

    for i in archive_num :
        board_total_num = i.text[1 :-1]
        board_total_page_num.append(str(int(i.text[1 :-1]) // 10 + 1))

        print('전체 게시물 숫자는 ' + i.text[1 :-1] + '개, 전체 게시판 페이지 숫자는 ' + str(int(i.text[1 :-1]) // 10 + 1) + '입니다.')

    return board_total_page_num

#######################################################################
# step 5. 전체 게시판 페이지 url 만들기
#######################################################################
def make_board_page_url(per_year_url_list, board_total_page_num) :
    '''
        archive info(bs4.tag)를 받아와 년도별 게시물 개수와 년도별 게시판 페이지 개수를 구하는 메소드
        :param   : archive_info(bs4.tag)
        :return  : board_total_page_num(list)
    '''
    board_page_url_list = list()

    for i in range(0, len(per_year_url_list)) :
        for j in range(1, int(board_total_page_num[i]) + 1) :
            board_page_url_list.append(per_year_url_list[i] + '/list/' + str(j))

    return board_page_url_list

#######################################################################
# step 6. 게시물 url 가져오기
#######################################################################
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
        :return  : board_url(str)
    '''
    board_url = list()

    board_url_href = board_url_tag.find_all('a')

    for i in board_url_href :
        board_url.append(blog_url + i['href'][1 :])

    return board_url


def gather_board_url_list(blog_url, board_page_url_list) :
    '''
        게시판 url_list를 받아 게시물 url을 수집하여 list로 저장하는 메소드
        :param   : blog_url(str), board_page_url_list(list)
        :return  : board_url_list(list)
    '''
    board_url_list = list()

    for i in range(0, len(board_page_url_list)) :
        board_url_list += get_board_url(blog_url, find_board_url_tag(board_page_url_list[i]))

    return board_url_list

#######################################################################
# step 7. dataframe에 1차로 저장
#######################################################################
def make_basic_DF():
    '''
        기본 데이터프레임을 만들어 주는 메소드
        :param   : None
        :return  : dataframe
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

def insert_DM_DF(dataframe, blogger_id, board_url_list):
    '''
        수집된 게시물 url을 기존 정보들과 함께 1차적으로 데이터프레임에 넣어주는 메소드
        :param   : dataframe, blogger_id(str), board_url_list(list)
        :return  : dataframe
    '''

    blog_type = BLOG_TYPE
    blogger_id = blogger_id

    dataframe['board_url']   = board_url_list
    dataframe['blog_type']   = blog_type
    dataframe['blogger_id']  = blogger_id

    for u in range(0, len(board_url_list)):
        post_num                  = board_url_list[u].split('/')[-1]
        dataframe['post_num'][u]  = post_num

    for i in range(0, len(dataframe)):
        dataframe['key'][i] = blog_type+"_"+blogger_id+"_"+dataframe['post_num'][i]

    return dataframe

#######################################################################
# step 8. 게시글 내용 가져오기
#######################################################################
def find_content_info_tag(one_board_url_list) :
    '''
        1개의 게시물 url을 받아와 게시물 내용이 있는 bs4.tag를 찾는 메소드
        :param   : one_board_url_list(str)
        :return  : content_info_tag(bs4.tag)
    '''

    req = requests.get(one_board_url_list)
    soup = BeautifulSoup(req.text, 'html.parser')

    content_info_tag = soup.find('div', {'class' : 'content'})

    return content_info_tag


def get_content_info(content_info_tag) :
    '''
        content_info_tag을 받아와 게시물 내용을 수집하는 메소드
        :param   : content_info_tag(bs4.tag)
        :return  : content_info(dict)
    '''

    content_info = dict()

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

    print(content_info)

    return content_info


def gather_all_content_info(board_url_list) :
    '''
        board_url_list을 받아와 게시물 내용을 모두 수집하는 메소드
        :param   : board_url_list(list)
        :return  : all_content_info(list)
    '''
    all_content_info = list()

    for i in range(0, len(board_url_list)) :
        print(board_url_list[i])
        content_info_tag = find_content_info_tag(board_url_list[i])

        all_content_info.append(get_content_info(content_info_tag))

    return all_content_info

#######################################################################
# step 9. 모든 정보 저장
#######################################################################
def update_save_DM_DF(dataframe, all_content_info, blogger_id) :
    '''
       기존에 만들어져 있던 데이터 프레임에 모든 게시물의 내용을 추가 및 저장하는 메소드
        :param : dataframe, all_content_info, blogger_id
        :return : dataframe(all_information in it)
    '''

    blog_type = BLOG_TYPE

    for num in range(len(all_content_info)) :
        dataframe['title'][num]           = all_content_info[num]['title']
        dataframe['content'][num]         = all_content_info[num]['content']
        dataframe['board_category'][num]  = all_content_info[num]['board_category']
        dataframe['blogger_nick'][num]    = all_content_info[num]['nickname']
        dataframe['date'][num]            = all_content_info[num]['upload_date']

    dataframe.to_csv('{0}_{1}.csv'.format(blog_type, blogger_id), index = False)

    return dataframe