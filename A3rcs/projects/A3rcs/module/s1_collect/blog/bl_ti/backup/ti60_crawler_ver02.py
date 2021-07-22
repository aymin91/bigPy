#!/usr/bin/env python
# coding: utf-8

# In[ ]:
# History


from bs4 import BeautifulSoup
from urllib.request import urlopen

import pandas as pd 

BASE_URL = 'tistory.comm/'
BLOG_TYPE = 'TI'

######################################
# STEP1
######################################

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

def get_num_of_articles(blog_url):

    '''
    총 게시글 수를 가져온다.
    만약 총 게시글 수를 가져올 수 없다면(웹페이지상 정보가 없다면),
    None값을 반환한다.

    param  : blog_url,   str
    return : n_articles, int
    '''

    http = urlopen(blog_url)
    soup = BeautifulSoup(http, 'lxml')
    
    if soup.find('ul', class_='tt_category'):
        side = soup.find('ul', class_='tt_category')
        all_post = side.find_all('span', class_='c_cnt')
        n_articles = int(all_post[0].text[1:-1])
          
    elif soup.find('div', id = 'text_0'):
        side = soup.find('div', id = 'text_0')
        all_post = side.find('span', class_='c_cnt')
        n_articles = int(all_post.text[1:-1])

    else:
        n_articles = None

    print('이 블로거의 게시글은 총 ', n_articles, '입니다.')

    return n_articles


def is_valid_N_make_url(n_articles, blog_url):

    '''
    총 게시글 수를 가져와 기본 2배수 만큼 for문을 돌려가며
    임의의 'https://brunch.co.kr/블로거id/글번호' url 주소를 만들고,
    urlopen으로 게시글 존재 여부를 판별, 존재하는 url 주소를 수집한다.

    param  : n_articles, int
             blog_url,   str
    return : url_list,   list
    '''

    url_list = list()
    if n_articles <= 10:
        for i in range(n_articles*5):    # 글 1개에 글번호 4번인 경우 존재
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
    만약 총 게시글 수를 가져올 수 없다면(웹페이지상 정보가 없다면),
    '크롤러 종료'를 알린다.

    param  : blog_url,        str
    return : board_url_list,  list
    '''

    board_url_list = list()

    n_articles = get_num_of_articles(blog_url)
    
    if n_articles:
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
    else:
        print('크롤러 종료')
        board_url_list = None

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

