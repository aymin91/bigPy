# Project : AI-based Auto Analysis Report Creating System
# History :
#

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

BLOG_TYPE = 'DM'

BASE_URL = 'http://blog.daum.net/'
ALL_LIST_PARAM = '_blog/ArticleCateList.do?blogid='
PAGE_PARAM = '&vblogid=&beforePage=1&maxarticleno={0}&minarticleno={1}&maxregdt={2}&minregdt={3}&currentPage=1&listScale=12&viewKind=T&dispkind=B2202&CATEGORYID=0&categoryId=0&articleno={4}&regdt={5}&date=&calv=&chgkey={6}&totalcnt=0'

# blogger_id = 'p7777877'

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
# step1. blogger_id 받아와서 blog에 접속하여 bs4 soup을 통해 frame src 정보 가져오기
################################################################################################
def get_frame_src_info(blogger_id) :
    '''
        iframe의 해제를 위해 frame src 정보를 가져오는 메소드
        :param   : blogger_if(str)
        :return  : frame_src_info(str)
    '''
    url = BASE_URL + blogger_id
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    frame_src_info = soup.frame['src']

    return frame_src_info


################################################################################################
# step2. frame src에서 blog_id 정보 가져오기
################################################################################################
def get_blog_id(frame_src_info) :
    '''
        frame src에서 blog id를 가져오는 메소드
        :param   : frame_src_info(str)
        :return  : blog_id(str)
    '''
    p = re.compile('[blogid=]\w+[&]')
    m = p.search(frame_src_info)
    blog_id = m.group(0)[1 :-1]

    return blog_id

################################################################################################
# step3.  '전체보기' 페이지로 전환하기
################################################################################################
def switch_all_list_page(blog_id) :
    '''
        게시글 목록의 전체를 볼 수 있는 '전체보기' 페이지로 넘어가는 url을
        만들어주는 메소드
        :param   : blog_id(str)
        :return  : all_board_list_page_url(str)
    '''
    all_board_list_page_url = BASE_URL + ALL_LIST_PARAM + blog_id

    return all_board_list_page_url

################################################################################################
# step4. bs4 soup을 통해 필요 param 구해서 PAGE_PARAM 채우기
################################################################################################
def get_param_info(all_board_list_page_url) :
    '''
        page를 넘길 때 필요한 파라미터들의 값을 페이지에서 구하고
        PAGE_PARAM에 넣어주는 메소드
        :param   : all_board_list_page_url(str)
        :return  : page_param(str)
    '''
    parm_req = requests.get(all_board_list_page_url)
    parm_soup = BeautifulSoup(parm_req.text, 'html.parser')

    parm_form = parm_soup.find_all('form')

    # 구하는 value 값들이 제대로 들어 있는 곳을 찾기 위함
    for par in parm_form :
        if len(str(par.find('input')).split('\n')) == 19 :
            parm_values = str(par.find('input')).split('\n')

    maxarticleno = parm_values[3].split('"')[-2]
    minarticleno = parm_values[4].split('"')[-2]
    maxregdt = parm_values[5].split('"')[-2]
    minregdt = parm_values[6].split('"')[-2]
    articleno = parm_values[13].split('"')[-2]
    regdt = parm_values[14].split('"')[-2]
    chgkey = parm_values[17].split('"')[-2]

    page_param = PAGE_PARAM.format(maxarticleno, minarticleno, maxregdt, minregdt, articleno, regdt, chgkey)

    return page_param

################################################################################################
# step5. '전체보기'가 가능한 blog_url과 page_param을 더해 frame이 해제되고 page를 바꿀 수 있는 완전한 url로 변환
################################################################################################
def make_blog_url(all_board_list_page_url, page_param) :
    '''
        all_board_list_page_url page_param을 합쳐 완전한 blog_url로 만들어주는 메소드
        :param   : all_board_list_page_url(str), page_param(str)
        :return  : blog_url(str)
    '''
    blog_url = all_board_list_page_url + page_param

    return blog_url

################################################################################################
# step6. 전체 게시물 숫자 및 전체 게시물 페이지 구하기
################################################################################################
def get_total_board_info(blog_url) :
    '''
        전체 게시판 페이지 개수와 전체 게시물 개수를 구하는 메소드
        :param   : blog_url(str)
        :return  : total_board_page_num(str)
    '''
    blog_req = requests.get(blog_url)
    blog_soup = BeautifulSoup(blog_req.text, 'html.parser')

    total_board_num = get_total_board_num(blog_soup)
    total_board_page_num = get_total_board_page_num(blog_soup)
    print('전체 게시물은 ' + total_board_num + '개, 전체 게시물 페이지는 ' + total_board_page_num + '개입니다.')

    return total_board_page_num


def get_total_board_num(blog_soup) :
    '''
        전체 게시글 개수를 구하는 메소드
        :param   : blog_soup(bs4.tag)
        :return  : total_board_num(str)
    '''
    total_board = blog_soup.h2.text

    p = re.compile('[(]\d+[)]')
    m = p.search(total_board)
    total_board_num = m.group()[1 :-1]

    return total_board_num


def get_total_board_page_num(blog_soup) :
    '''
        전체 게시판 페이지 개수를 구하는 메소드
        :param   : blog_soup(bs4.tag)
        :return  : total_board_page_num(str)
    '''
    total_board_page = blog_soup.find('div', {'id' : 'cNumbering'}).text

    p = re.compile('[...]\d+\s')
    m = p.search(total_board_page)
    total_board_page_num = m.group()[1 :-1]

    return total_board_page_num

################################################################################################
# step7. 전체 게시물 페이지 url(list) 구하기
################################################################################################
def make_regex_page_blog_url(blog_url,total_board_page_num):
    '''
        전체 게시판 페이지 url을 구하는 메소드
        :param   : blog_url(str), total_board_page_num(str)
        :return  : regex_page_blog_url_list(list)
    '''
    regex_page_blog_url_list = list()

    for i in range(1, int(total_board_page_num)+1):
        regex_page_blog_url_list.append(re.sub('currentPage=1', 'currentPage='+str(i), blog_url))
    return regex_page_blog_url_list

################################################################################################
# step8. 한 페이지에 있는 모든 게시물 url 가져오기
################################################################################################
def get_board_url(one_regex_page_blog_url):
    '''
        게시판 1개 페이지에 있는 게시물 url을 수집하는 메소드
        :param   : one of regex_page_blog_url(str/one value of list)
        :return  : board_url_list(list)
    '''
    # 게시판 1 페이지 파싱
    board_req = requests.get(one_regex_page_blog_url)
    board_soup = BeautifulSoup(board_req.text, 'html.parser')

    board_content = board_soup.find('div', {'id':'cContent'})

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_alist = True if board_content.find('table',{'class':'WebAList'}) else False

    if is_valid_alist:
        board_url_list = type_webalist(board_content)
        print("This blog's type is WebAList.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_btable = True if board_soup.find('div',{'class':'WebBTable'}) else False

    if is_valid_btable:
        board_url_list = type_webbtable(board_content)
        print("This blog's type is WebBTable.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_clist = True if board_soup.find('table',{'class':'WebCList'}) else False

    if is_valid_clist:
        board_url_list = type_webclist(board_content)
        print("This blog's type is WebCList.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_elist = True if board_soup.find('div',{'class':'webERightP'}) else False

    if is_valid_elist:
        board_url_list = type_webelist(board_content)
        print("This blog's type is webERightP.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_diary = True if board_soup.find('table',{'class':'DiaryTList'}) else False

    if is_valid_diary:
        board_url_list = type_diarylist(board_content)
        print("This blog's type is DiaryTList.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_gallery = True if board_soup.find('ul',{'class':'GalleryList'}) else False

    if is_valid_gallery:
        board_url_list = type_gallerylist(board_content)
        print("This blog's type is GalleryList.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_arti = True if board_soup.find('table',{'class':'artiList'}) else False

    if is_valid_arti:
        board_url_list = type_artlist(board_content)
        print("This blog's type is artiList.")
    else: pass

    return board_url_list


def type_webalist(board_content) :
    '''
        게시판의 type이 WebAList인 경우에 type에 맞게 tag를 파싱해 url을 가져오는 메소드
        :param   : board_content(bs4.tag)
        :return  : one_page_board_url(list)
    '''
    # WebAList = WebAFirst + WebAList
    one_page_board_url = list()

    # WebAFirst
    board_first = board_content.find('div', {'class' : 'webAFirst'})
    one_page_board_url.append(BASE_URL + board_first.a['href'][1 :])

    # WebAList
    board = board_content.find_all('td', {'class' : 'title'})
    for t in board :
        one_page_board_url.append(BASE_URL + t.a['href'][1 :])

    return one_page_board_url


def type_webbtable(board_content) :
    '''
        게시판의 type이 WebBTable 경우에 type에 맞게 tag를 파싱해 url을 가져오는 메소드
        :param   : board_content(bs4.tag)
        :return  : one_page_board_url(list)
    '''
    # WebBTable
    one_page_board_url = list()

    board = board_content.find_all('td', {'class' : 'title'})
    for t in board :
        one_page_board_url.append(BASE_URL + t.a['href'][1 :])

    return one_page_board_url


def type_webclist(board_content) :
    '''
        게시판의 type이 WebCList 경우에 type에 맞게 tag를 파싱해 url을 가져오는 메소드
        :param   : board_content(bs4.tag)
        :return  : one_page_board_url(list)
    '''
    # WebCList
    one_page_board_url = list()

    board = board_content.find_all('td', {'class' : 'title'})
    for t in board :
        one_page_board_url.append(BASE_URL + t.a['href'][1 :])

    return one_page_board_url


def type_webelist(board_content) :
    '''
        게시판의 type이 WebEList 경우에 type에 맞게 tag를 파싱해 url을 가져오는 메소드
        :param   : board_content(bs4.tag)
        :return  : one_page_board_url(list)
    '''
    # WebEList
    one_page_board_url = list()

    board = board_content.find_all('td', {'class' : 'title'})
    for t in board :
        one_page_board_url.append(BASE_URL + t.a['href'][1 :])

    return one_page_board_url


def type_diarylist(board_content) :
    '''
        게시판의 type이 DiaryList 경우에 type에 맞게 tag를 파싱해 url을 가져오는 메소드
        :param   : board_content(bs4.tag)
        :return  : one_page_board_url(list)
    '''
    # DiaryList
    one_page_board_url = list()

    board = board_content.find_all('td', {'class' : 'contArea'})
    for t in board :
        one_page_board_url.append(BASE_URL + t.a['href'][1 :])

    return one_page_board_url


def type_gallerylist(board_content) :
    '''
        게시판의 type이 GalleryList 경우에 type에 맞게 tag를 파싱해 url을 가져오는 메소드
        :param   : board_content(bs4.tag)
        :return  : one_page_board_url(list)
    '''
    # GalleryList
    one_page_board_url = list()

    board_gallery = board_content.find('ul', {'class' : 'GalleryList'})
    board = board_gallery.find_all('li')
    for t in board :
        one_page_board_url.append(BASE_URL + t.a['href'][1 :])

    return one_page_board_url


def type_artlist(board_content) :
    '''
        게시판의 type이 artList 경우에 type에 맞게 tag를 파싱해 url을 가져오는 메소드
        :param   : board_content(bs4.tag)
        :return  : one_page_board_url(list)
    '''
    # artList
    one_page_board_url = list()

    board = board_content.find_all('td', {'class' : 'title'})
    for t in board :
        one_page_board_url.append(BASE_URL + t.a['href'][1 :])

    return one_page_board_url

def gather_board_url_list(regex_page_blog_url_list):
    '''
        게시판에 있는 게시글의 url들을 모아주는 메소드
        parmam : regex_page_blog_url(list)
        Result : board_url_list(list)
    '''
    board_url_list = list()

    for i in range(0, len(regex_page_blog_url_list)):
        board_url_list += get_board_url(regex_page_blog_url_list[i])

    return board_url_list

################################################################################################
# step9. blog_type, blogger_id, 수집한 게시물 url, post_num을 dataframe에 저장
################################################################################################
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

    pattern = re.compile('articleno=\w+')

    for u in range(0, len(board_url_list)):
        reg_post_num              = pattern.search(board_url_list[u])
        post_num                  = reg_post_num.group().split('=')[1]
        dataframe['post_num'][u]  = post_num

    for i in range(0, len(dataframe)):
        dataframe['key'][i] = blog_type+"_"+blogger_id+"_"+dataframe['post_num'][i]

    return dataframe

################################################################################################
# step10. 게시글 parsing
################################################################################################
''''''
# def regex_front_content_text(content_text) :
#     '''
#        게시글 서두에 나오는 불필요한 문자를 삭제해주는 메소드
#        :param : content_text(str)
#        :return : regex_content_text(str)
#    '''
#     p1_start = re.compile('[<!--]')
#     m1_start = p1_start.search(content_text)
#
#     p1_end = re.compile('[>]')
#     m1_end = p1_end.search(content_text)
#
#     regex_content_text = re.sub(content_text[m1_start.start() :m1_end.end()], '', content_text)
#
#     return regex_content_text
#
#
# def regex_tail_content_text(content_text) :
#     '''
#        게시글 말미에 나오는 불필요한 문자를 삭제해주는 메소드
#        :param : content_text(str)
#        :return : regex_content_text(str)
#     '''
#     regex_content_text = content_text[:content_text.find('var flashVersion')]
#
#     return regex_content_text
def get_board_content_info(df_board_url) :
    '''
       게시글의 제목, 게시글 카테고리, 닉네임, 게시 날짜를 가져오는 메소드
       :param : df_board_url(str)
       :return : content_info(dict)
    '''
    content_info = dict()

    brd_req  = requests.get(df_board_url)
    brd_soup = BeautifulSoup(brd_req.text, 'html.parser')

    title = brd_soup.find('h3', {'class' : 'tit_view'}).text.replace('\n', '').replace('\t', '').rstrip()

    is_valid_cate = True if brd_soup.find('span', {'class' : 'txt_cate'}) else False
    if is_valid_cate:
        board_category = re.sub('\n','',brd_soup.find('span', {'class' : 'txt_cate'}).text).strip()
    else:
        board_category = ''

    nickname = re.sub('\n','',brd_soup.find('span', {'class' : 'txt_writer'}).text).strip()
    upload_date = brd_soup.find('time', {'class' : 'txt_time'}).text
    content = re.sub('\n|\u200b|\xa0|\uf0fc|\t|\ufeff', '', brd_soup.find('div',{'id':'article'}).text)

    content_info['title']           = title
    content_info['board_category']  = board_category
    content_info['nickname']        = nickname
    content_info['date']            = upload_date[:10].replace('.', '')
    content_info['content']         = content

    return content_info


# def get_content_info(driver, df_board_url, df_post_num) :
#     '''
#        게시글의 내용을 가져오는 메소드
#        :param : driver, df_board_url(str), df_post_num(str)
#        :return : content_info(dict)
#     '''
#     content_info = dict()
#
#     driver.get(df_board_url)
#     time.sleep(1)
#     driver.switch_to_frame('if_b_' + df_post_num)
#     test_soup = BeautifulSoup(driver.page_source, 'html.parser')
#
#     content = re.sub('\n|\u200b|\xa0|\uf0fc|\t', '', test_soup.find('div', {'id' : 'cContent'}).text)
#
#     content = regex_tail_content_text(regex_front_content_text(content))
#
#     content_info['content'] = content
#
#     return content_info


def gather_all_content(mobile_url_list) :
    '''
       게시글의 모든 정보를 수집하고 합쳐주는 메소드
       :param : dm_df(dataframe)
       :return : all_content_info(list)
    '''

    all_content_info = list()
    for i in range(0, len(mobile_url_list)):
        board_content_info = get_board_content_info(mobile_url_list[i])
        all_content_info.append(board_content_info)

    return all_content_info

################################################################################################
# step11. 데이터프레임에 업데이트 및 저장
################################################################################################
def update_save_DM_DF(dm_df, all_content_info, blogger_id) :
    '''
       기존에 만들어져 있던 데이터 프레임에 모든 게시물의 내용을 추가 및 저장하는 메소드
        :param : dm_df, all_content_info, blogger_id
        :return : dm_df(all_information in it)
    '''

    blog_type = BLOG_TYPE

    for num in range(len(all_content_info)) :
        dm_df['title'][num]           = all_content_info[num]['title']
        dm_df['content'][num]         = all_content_info[num]['content']
        dm_df['board_category'][num]  = all_content_info[num]['board_category']
        dm_df['blogger_nick'][num]    = all_content_info[num]['nickname']
        dm_df['date'][num]            = all_content_info[num]['date']

    dm_df.to_csv('{0}_{1}.csv'.format(blog_type, blogger_id), index = False)

    return dm_df


