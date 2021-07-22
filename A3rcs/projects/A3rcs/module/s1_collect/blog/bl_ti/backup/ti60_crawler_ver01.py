#!/usr/bin/env python
# coding: utf-8

# In[ ]:
# 'hohodang', 'diarystory' : type1
# History

from bs4 import BeautifulSoup
from urllib.request import urlopen

import pandas as pd 

BASE_URL = 'tistory.comm/'
BLOG_TYPE = 'TI'

######################################
# STEP1
######################################


# id를 가져와서 블로그 주소를 완성
def get_blog_url(blogger_id):   
    
    '''
    blogger_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
    (일반적인 blog_url 형식 : (blogger_id).tistory.comm )
    
    param  : blogger_id,  str
    return : blog_url,    str
    '''
    
    base_url = BASE_URL

    blog_url =  'https://' + blogger_id + '.' + base_url #'category'

    return blog_url

    
######################################
# STEP2
######################################


def get_last_page_num(blog_url):
    '''
    blog_url을 받아 전체글 목록에서 전체 글 개수와 마지막 글목록 페이지를 보여주고
    마지막 글목록 페이지를 반환한다.

    param   : blog_url,        str
    return  : last_page_num,   int
    '''

    http = urlopen(blog_url)
    soup = BeautifulSoup(http, 'lxml')
    pages = soup.find('div', id='paging')
    try:
        last_page_num = pages('a')[-2]['href']
        last_page_num = int(last_page_num[last_page_num.find('=') + 1:])
    except:
        blog_url_2 = blog_url + 'category'
        http = urlopen(blog_url_2)
        soup_2 = BeautifulSoup(http, 'lxml')

        pages = soup_2.find('div', id='paging')
        last_page_num = pages('a')[-2]['href']
        last_page_num = int(last_page_num[last_page_num.find('=') + 1:])

    side = soup.find('ul', class_='tt_category')
    all_post = side.find_all('span', class_='c_cnt')[0].text[1:-1]

    print('총 게시글은', all_post, '개 글이며 게시글', '마지막 페이지는 ', last_page_num, '입니다.')

    return last_page_num


def board_url_collect(page_soup, blog_url):
    '''
    게시글 목록이 있는 페이지의 파싱된 데이터(page_soup)을 받아
    url 주소들을 수집해 리스트 형태로 반환한다.

    param  : page_soup(bs4)
    return : board_url_list(list)
    '''

    board_urls = list()

    board_url_path = page_soup.find('div', class_='list')
    board_url = board_url_path.find_all('li')

    for b in board_url:
        url_num = b.find('a')['href'][1:]
        url = blog_url + url_num
        board_urls.append(url)

    return board_urls


def get_all_board_url(blog_url):
    '''
    blog_url을 받아 get_last_page_num 모듈을 실행한 뒤 글목록 페이지를 돌아다니며
    board_url_collect 모듈을 실행해 url 주소를 리스트 단위로 모은 후 합쳐서
    최종 board_url_list로 반환한다.

    param  : blog_url(str)
    return : board_url_list(list)
    '''

    board_url_list = list()

    http = urlopen(blog_url)
    soup = BeautifulSoup(http, 'lxml')

    last_page_num = get_last_page_num(blog_url)

    for num in range(1, last_page_num + 1):
        navi_page_url = blog_url + '?page=' + str(num)

        http = urlopen(navi_page_url)
        page_soup = BeautifulSoup(http, 'lxml')

        board_urls = board_url_collect(page_soup, blog_url)
        board_url_list.extend(board_urls)

    print("------------------------------------------------------------------------------------")
    print('총 ', len(board_url_list), '개의 url을 수집하였습니다.')

    return board_url_list


######################################
# STEP3
######################################


def common_util(board_url_list):
        
    '''
    게시글 url을 모바일 형태로 변환해 리스트로 반환한다.
    
    param  : board_url_list,    list
    return : m board_url_list ,  list 
    
    '''
    m_board_url_list = list()
    
    for u in board_url_list:
        loc_m = u.find('m/')
        m_url = u[:loc_m] + 'm/' + u[loc_m:]
        m_board_url_list.append(m_url)
        
    return m_board_url_list
    

######################################
# STEP4
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

def insert_TI_DF(dataframe, blogger_id, board_url_list):
              
    '''
    기본 데이터프레임을 받아 blogger_id, board_url, blog_type, post_num, key 등의
    기본 정보를 입력한다. 
    
    param  : dataframe(df), blogger_id(str), board_url_list(list)
    return : dataframe(df)
    ''' 
    
    blog_type = BLOG_TYPE
    blogger_id = blogger_id

    dataframe['board_url']  = board_url_list
    dataframe['blog_type']  = blog_type
    dataframe['blogger_id'] = blogger_id
    
    post_num_list = list()
    
    for u in board_url_list:
        post_num = u[u.find('m/')+2:]
        post_num_list.append(post_num)
    
    dataframe['post_num'] = post_num_list

    for i in range(0, len(dataframe)):
        dataframe['key'][i] = blog_type+"_"+blogger_id+"_"+dataframe['post_num'][i]

    return dataframe

######################################
# STEP5
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

    
    nickname = soup.find('span', class_ = 'txt_by').text # 글쓴이
    upload_date = soup.find('time', class_ = 'txt_date').text  # 날짜
    board_category =  soup.find('a', class_ = 'txt_category').text if soup.find('a', class_ = 'txt_category') else '분류없음'    
    title = soup.find('h2', class_ = 'tit_blogview').text 
        
    content = ''
    cont = soup.find('div' , class_ = 'blogview_content') 
    con = cont.find_all(['p', 'b', 'strong'])   
    cons = con[:-2] if '태그' in con[-2].text else con[:-1]
    for c in cons:
        content += c.text
    
        
    content_info['nickname'] = nickname
    content_info['date'] = upload_date
    content_info['category'] = board_category
    content_info['title'] = title
    content_info['content'] = content
    
    return content_info

def gather_all_content(m_board_url_list):

    '''

    게시글의 url 주소 리스트를 받아 게시글 주소를 하나씩
    'find_content_info' 모듈에 넣어 나온 딕셔너리 형태의 정보를
    리스트로 저장해 반환한다.

    param  : board_url_list,    list
    return : all_content_info,  list
    '''

    all_content_info = list()

    for b_url in m_board_url_list :
        parsing = find_content_info(b_url)
        all_content_info.append(parsing)

    return all_content_info

######################################
# STEP6
######################################

def update_save_TI_DF(dataframe, all_content_info, blogger_id) :
    '''
    기존에 만들어져 있던 데이터 프레임에 모든 게시물의 내용을 추가 및 저장

    params : dataframe(df), all_content_info(list), blogger_id(str)
    return : dataframe(df)

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

