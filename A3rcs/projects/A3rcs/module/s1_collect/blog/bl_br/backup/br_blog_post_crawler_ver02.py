#!/usr/bin/env python
# coding: utf-8

# In[1]:
# History:
#       2019.11.01
#           - def is_valid_N_make_url 모듈 추가
#              : 글 개수 1개, 글 번호 4인 사례가 발견되어 케이스를 나눠
#                for문을 돌아가며 게시글 url 존재여부 판별


from bs4 import BeautifulSoup
from urllib.request import urlopen

import pandas as pd

BASE_URL = 'https://brunch.co.kr/'
BLOG_TYPE = 'BR'

PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
WD_CHROME_PATH_WIN = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'

######################################
# STEP1
######################################

def get_blog_url(blogger_id):
    '''
    blogger_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
    (일반적인 blog_url 형식 : https://brunch.co.kr/(@blogger_id )#articles(글 목록)

    param  : blogger_id,  str
    return : blog_url,    str
    '''

    base_url = BASE_URL

    blog_url = base_url + '@' + blogger_id + '/'

    return blog_url


######################################
# STEP2
######################################

def get_num_of_articles(blog_url):

    '''
    블로거 주소를 받아 블로그의 게시글 수 를 가져온다

    param  : blog_url,   str
    return : n_articles, int
    '''

    http = urlopen(blog_url)
    soup = BeautifulSoup(http, 'lxml')
    n_article = soup.find('ul', id='contentsTab')
    num = n_article.find_all('li')
    n_articles = int(num[1].text[2:])

    print('이 블로거의 게시글은 총 ', n_articles, '입니다.')

    return n_articles


def is_valid_N_make_url(n_articles, blog_url):

    '''
    총 게시글 수를 가져와 기본 2배수 만큼 for문을 돌려가며
    임의의 'https://brunch.co.kr/블로거id/글번호' url 주소를 만들고,
    urlopen으로 게시글 존재 여부를 판별, 존재하는 url 주소를 수집한다.

    param  : blog_url,   str
    return : n_articles, int
    '''

    url_list = list()
    if n_articles <= 10:
        for i in range(n_articles * 5):  # 글 1개에 글번호 4번인 경우 존재, 글이 10개 이하면 더 많은 배수를 취한다.
            post_url = blog_url + '{}'.format(i + 1)
            try:
                http = urlopen(post_url)
                url_list.append(post_url)
            except:
                pass

    elif n_articles > 10:
        for i in range(n_articles * 2):
            post_url = blog_url + '{}'.format(i + 1)
            try:
                http = urlopen(post_url)
                url_list.append(post_url)
            except:
                pass

    return url_list


def get_all_board_url(blog_url):

    '''
    블로거 주소를 받아 총 게시물 개수를 구하여 임의의 블로그 주소를 만들고,
    존재하는 게시물 주소인지 판별한다.

    param  : blog_url,        str
    return : board_url_list,  list
    '''

    board_url_list = list()

    n_articles = get_num_of_articles(blog_url)

    url_list = is_valid_N_make_url(n_articles, blog_url)

    if n_articles != len(board_url_list):
        for j in range(1, n_articles + 1):
            post_url = blog_url + '{}'.format((n_articles * 2) + j)
            try:
                http = urlopen(post_url)
                board_url_list.append(post_url)
            except:
                pass
    board_url_list.extend(url_list)

    print('총 ', len(board_url_list), '개의 url을 수집하였습니다.')

    return board_url_list


######################################
# STEP3
######################################

def make_basic_DF():
    '''
        기본 데이터프레임을 만들어 주는 모듈
        :return: df
    '''
    dataframe = pd.DataFrame()
    dataframe['blog_type'] = ''
    dataframe['blogger_id'] = ''
    dataframe['post_num'] = ''
    dataframe['key'] = ''
    dataframe['board_url'] = ''
    dataframe['title'] = ''
    dataframe['content'] = ''
    dataframe['board_category'] = ''
    dataframe['blogger_nick'] = ''
    dataframe['date'] = ''

    return dataframe


def insert_BR_DF(dataframe, blogger_id, board_url_list):
    '''
    데이터프레임에 기본 정보를 넣어준다.
    블로거 id, 블로그 타입(BR-Brunch), 게시글 번호, key값

    param  : dataframe,        dataframe(pandas)
             blogger_id,       str
             board_url_list,   list
    return : dataframe,        dataframe(pandas)
    '''

    blog_type = BLOG_TYPE
    blogger_id = blogger_id

    dataframe['board_url'] = board_url_list
    dataframe['blog_type'] = blog_type
    dataframe['blogger_id'] = blogger_id

    for u in range(0, len(board_url_list)):
        p_num = board_url_list[u][board_url_list[u].find('/', 21) + 1:]
        dataframe['post_num'][u] = p_num

    for i in range(0, len(dataframe)):
        dataframe['key'][i] = blog_type + "_" + blogger_id + "_" + dataframe['post_num'][i]

    return dataframe


######################################
# STEP4
######################################

def find_content_info(board_url):
    '''
    게시글의 url 주소를 받아 게시글 블로거의 nickname, 등록날짜, 카테고리,
    제목, 내용 추가 정보를 수집해 딕셔너리 형태로 반환한다.

    param  : board_url,      str
    return : content_info,   dict
    '''

    content_info = dict()

    http = urlopen(board_url)
    soup = BeautifulSoup(http, 'lxml')

    nickname = soup.find('div', id='wrapArticleInfo').find('a').text  # 글쓴이
    upload_date = soup.find('span', class_='f_l date').text  # 날짜
    board_category = '분류없음'  # brunch는 블로거의 카테고리가 따로 존재 X. (단, 매거진 keyword별 수집 추후 검토, 매거진명은 상관없는 것들이 많아서 제외)
    title = soup.find('div', class_='wrap_cover').find('h1', class_='cover_title').text  # sub title 제외

    content = ''
    r_contents = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'blockquote'])
    contents = r_contents[4:]
    for con in contents:
        content += con.text.strip()

    content_info['nickname'] = nickname
    content_info['date'] = upload_date
    content_info['category'] = board_category
    content_info['title'] = title
    content_info['content'] = content

    return content_info


def gather_all_content(board_url_list):
    '''

    게시글의 url 주소 리스트를 받아 게시글 주소를 하나씩
    'find_content_info' 모듈에 넣어 나온 딕셔너리 형태의 정보를
    리스트로 저장해 반환한다.

    param  : board_url_list,    list
    return : all_content_info,  list
    '''

    all_content_info = list()

    for b_url in board_url_list:
        parsing = find_content_info(b_url)
        all_content_info.append(parsing)

    return all_content_info


######################################
# STEP5
######################################

def update_save_BR_DF(dataframe, all_content_info, blogger_id):
    '''
    기존에 만들어져있던 데이터 프레임에 새로운 정보를 추가하고 csv파일로
    저장한 뒤 데이터프레임을 반환한다.

    param  : dataframe,          dataframe(pandas)
             all_content_info,   list
             blogger_id,         str

    return : dataframe,          dataframe(pandas)
    '''

    blog_type = BLOG_TYPE

    for num in range(len(dataframe)):
        dataframe['title'][num] = all_content_info[num]['title']
        dataframe['content'][num] = all_content_info[num]['content']
        dataframe['board_category'][num] = all_content_info[num]['category']
        dataframe['blogger_nick'][num] = all_content_info[num]['nickname']
        dataframe['date'][num] = all_content_info[num]['date']

    dataframe.to_csv('{0}_{1}.csv'.format(blog_type, blogger_id), index=False)

    return dataframe