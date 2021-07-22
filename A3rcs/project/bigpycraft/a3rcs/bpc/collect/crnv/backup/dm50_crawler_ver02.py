# Project : AI-based Auto Analysis Report Creating System
# History :
#       2019.11.04
#           - 'from selenium import webdriver' is deleted by MAY
#           - 'PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
#              WD_CHROME_PATH_WIN   = 'driver/chromedriver.exe'
#              WD_CHROME_PATH_MAC   = 'driver/macos/chromedriver'
#              WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'' is deleted by MAY
#           - 'def get_driver' function is delected by MAY
#
#       2019.11.08
#           - 모듈 step별로 재정리 및 재배열 by MAY
import requests

from selenium import webdriver
from bs4 import BeautifulSoup

import platform
import pandas as pd

import re


BLOG_TYPE = 'DM'
DAUM_BASE = 'http://blog.daum.net/'

BASE_URL = 'http://blog.daum.net/'
ALL_LIST_PARAM = '_blog/ArticleCateList.do?blogid='
PAGE_PARAM = '&vblogid=&beforePage=1&maxarticleno={0}&minarticleno={1}&maxregdt={2}&minregdt={3}&currentPage=1&listScale=12&viewKind=T&dispkind=B2202&CATEGORYID=0&categoryId=0&articleno={4}&regdt={5}&date=&calv=&chgkey={6}&totalcnt=0'

# blogger_id = 'p7777877'

################################################################################################
# STEP1. 블로그에 접속
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

def switch_all_list_page(blog_id) :
    '''
        게시글 목록의 전체를 볼 수 있는 '전체보기' 페이지로 넘어가는 url을
        만들어주는 메소드
        :param   : blog_id(str)
        :return  : all_board_list_page_url(str)
    '''
    all_board_list_page_url = BASE_URL + ALL_LIST_PARAM + blog_id

    return all_board_list_page_url

def get_param_info(all_list_page_url) :
    '''
        page를 넘길 때 필요한 파라미터들의 값을 페이지에서 구하고
        PAGE_PARAM에 넣어주는 메소드
        :param   : all_list_page_url(str)
        :return  : page_param(str)
    '''
    parm_req = requests.get(all_list_page_url)
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

def get_blog_url(blogger_id) :
    '''
        all_list_page_url page_param을 합쳐 완전한 blog_url로 만들어주는 메소드
        :param   : blogger_id(str)
        :return  : blog_url(str)
    '''
    frame_src = get_frame_src_info(blogger_id)
    blog_id = get_blog_id(frame_src)
    all_list_page_url = switch_all_list_page(blog_id)
    page_param = get_param_info(all_list_page_url)
    blog_url = all_list_page_url + page_param

    return blog_url




################################################################################################
# STEP2. 전체 게시물 url 가져오기
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
        # print("This blog's type is WebAList.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_btable = True if board_soup.find('div',{'class':'WebBTable'}) else False

    if is_valid_btable:
        board_url_list = type_webbtable(board_content)
        # print("This blog's type is WebBTable.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_clist = True if board_soup.find('table',{'class':'WebCList'}) else False

    if is_valid_clist:
        board_url_list = type_webclist(board_content)
        # print("This blog's type is WebCList.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_elist = True if board_soup.find('div',{'class':'webERightP'}) else False

    if is_valid_elist:
        board_url_list = type_webelist(board_content)
        # print("This blog's type is webERightP.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_diary = True if board_soup.find('table',{'class':'DiaryTList'}) else False

    if is_valid_diary:
        board_url_list = type_diarylist(board_content)
        # print("This blog's type is DiaryTList.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_gallery = True if board_soup.find('ul',{'class':'GalleryList'}) else False

    if is_valid_gallery:
        board_url_list = type_gallerylist(board_content)
        # print("This blog's type is GalleryList.")
    else: pass

    # 파싱 후, div, id='cContent'에 어떤 'List' 형식인지 판별하기
    is_valid_arti = True if board_soup.find('table',{'class':'artiList'}) else False

    if is_valid_arti:
        board_url_list = type_artlist(board_content)
        # print("This blog's type is artiList.")
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

def get_all_board_url(blog_url):
    '''
        게시판에 있는 게시글의 url들을 모아주는 메소드
        parmam : blog_url(str)
        Result : board_url_list(list)
    '''
    board_url_list = list()

    total_board_page_num = get_total_board_info(blog_url)
    regex_page_blog_url_list = make_regex_page_blog_url(blog_url, total_board_page_num)

    for i in range(0, len(regex_page_blog_url_list)):
        board_url_list += get_board_url(regex_page_blog_url_list[i])

    return board_url_list




################################################################################################
# STEP3. 게시물 내용 파싱
################################################################################################
def get_board_content_info(m_board_url, board_url) :
    '''
       게시글의 제목, 게시글 카테고리, 닉네임, 게시 날짜를 가져오는 메소드
       :param : m_board_url(str)
       :return : content_info(dict)
    '''
    content_info = dict()

    brd_req  = requests.get(m_board_url)
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
    content_info['board_url']       = board_url

    return content_info

def common_util(blogger_id, board_url):
    '''
        게시글 url을 모바일 형태로 변환해 리스트로 반환한다.

        param  : blogger_id(str), board_url(str)
        return : m_board_url_list(list)

    '''


    pattern = re.compile('articleno=\w+')

    reg_post_num = pattern.search(board_url)
    post_num = reg_post_num.group().split('=')[1]

    m_board_url = re.sub('http://', 'http://m.', DAUM_BASE) + blogger_id + '/' + post_num


    return m_board_url

def gather_all_content(blogger_id, board_url_list):
    '''
       게시글의 모든 정보를 수집하고 합쳐주는 메소드
       :param : blogger_id(str), board_url_list(list)
       :return : all_content_info(list)
    '''

    all_content_info = list()

    for b in board_url_list:
        m_board_url = common_util(blogger_id, b)
        board_content_info = get_board_content_info(m_board_url, b)
        all_content_info.append(board_content_info)

    return all_content_info

################################################################################################
# STEP4. all_content_info 데이터프레임에 저장
################################################################################################
def make_DM_DF(all_content_info, blogger_id) :
    '''
        기존에 만들어져있던 데이터 프레임에 새로운 정보를 추가하고 csv파일로
        저장한 뒤 데이터프레임을 반환한다.
        :param  : dataframe(dataframe), all_content_info(list), blogger_id(str)
        :return : dataframe(dataframe)
    '''

    cols = ['blog_type', 'blogger_id', 'post_num', 'key', 'board_url', 'title', 'content', 'board_category', 'nickname',
            'date']

    dataframe = pd.DataFrame(all_content_info)

    dataframe['blog_type'] = BLOG_TYPE
    dataframe['blogger_id'] = blogger_id
    dataframe['post_num'] = ''
    dataframe['key'] = ''

    pattern = re.compile('articleno=\w+')

    for j in range(len(dataframe)) :
        reg_post_num = pattern.search(dataframe['board_url'][j])
        post_num = reg_post_num.group().split('=')[1]
        dataframe['post_num'][j] = post_num


    for k in range(len(dataframe)) :
        dataframe['key'][k] = BLOG_TYPE+"_"+blogger_id+"_"+dataframe['post_num'][k]

    dataframe = dataframe[cols]

    dataframe.to_csv('{0}_{1}.csv'.format(BLOG_TYPE, blogger_id), index=False)

    return dataframe
