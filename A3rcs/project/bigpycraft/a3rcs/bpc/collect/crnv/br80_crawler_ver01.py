# History :
#       2019.10.29
#           - def find_content_info
#              : soup.find_all('p') -> soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'blockquote'])
#                본문 내용 태그가 p태그 이외에도 있어서 모두 가져오게 수정


from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlopen

import platform
import pandas as pd

import time

BASE_URL = 'https://brunch.co.kr/'
BLOG_TYPE = 'BR'

PROJECT_ROOT = '/project/bigpycraft/a3rcs/'
# PROJECT_ROOT = './'
WD_CHROME_PATH_WIN = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'

######################################
# STEP0
######################################

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

    blog_url =  base_url + '@' + blogger_id + '#articles'

    return blog_url


######################################
# STEP2
######################################

def blog_url_open(blog_url):

    '''
    blog_url을 받아 웹 드라이버를 실행하고, 페이지를 띄어준다.

    param  : blog_url,   str
    return : driver,     ChromeWebDriver
    '''

    driver = get_driver()
    driver.get(blog_url)

    return driver

######################################
# STEP3
######################################

def get_num_of_articles(driver):

    '''
    블로거 홈페이지가 떠 있는 웹드라이버를 받아 블로그의 게시글 수 를 가져온다

    param  : driver,     ChromeWebDriver
    return : n_articles, int
    '''

    soup = BeautifulSoup(driver.page_source, 'lxml')
    n_article = soup.find('ul', id = 'contentsTab')
    num = n_article.find_all('li')
    n_articles = int(num[1].text[2:])

    print('이 블로거의 게시글은 총 ', n_articles,'입니다.')

    return n_articles

def scr_to_end(driver, n_articles):

    '''
    웹 드라이버와 게시글 수를 받아 스크롤을 내려 모든 정보를
    가져온 상태의 웹 드라이버를 반환환다.

    param  : driver,     ChromeWebDriver
             n_articles, int
    return : driver,     ChromeWebDriver
    '''

    n_scr = n_articles - 20   # 처음 화면에 20개의 게시글 정보가 떠있다.

    '''
     만약 게시글 수가 75개면 처음 화면에 있는 20개를 뺀 나머지는 55개이다.
     한 번 스크롤을 아래로 내릴 시 20개의 추가 정보가 뜨기 때문에 20으로 나눠서
     딱 떨어지면 몫만큼만 스크롤을 내리고 나머지가 나오면 한 번 더 스크롤을 내려준다.
    '''
    if n_scr % 20 != 0:
        scr = n_scr // 20 + 1
        for i in range(scr):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
    else :
        scr = n_scr// 20
        for i in range(scr):  
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
    return driver


def get_all_board_url(driver) :

    '''
    모든 게시글 정보가 떠 있는 웹 드라이버를 받아서 게시글 url을 수집,
    리스트로 반환한다.

    param  : driver,          ChromeWebDriver
    return : board_url_list,  list
    '''

    board_url_list = list()
    base_url = BASE_URL
    
    n_articles = get_num_of_articles(driver)
    time.sleep(1)
    driver = scr_to_end(driver, n_articles)

    soup = BeautifulSoup(driver.page_source, 'lxml')   
    posts = soup.find('div', id = 'wrapArticle')
    post = posts.find_all('li')

   # 스크롤이 잘 내려가지 않을 때 적용
    if len(post) == n_articles:
        pass
    elif len(post) != n_articles:
        while len(post) == n_articles:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            soup = BeautifulSoup(driver.page_source, 'lxml')
            posts = soup.find('div', id='wrapArticle')
            post = posts.find_all('li')


    '''
    브런치에는 '보통 글'과 '매거진' 두 종류가 나뉘는 데 
    매거진의 경우 매거진 주소 정보와 게시글 주소 정보 두 가지가 있다.
    매거진일 경우엔 두 번째 주소 정보를, 아닐 경우 첫 번째 주소 정보를 가져온다.
    '''

    for po in post:
        if len(po) == 5:
            href = po.find_all('a')[1]['href'][1:]   
            board_url = base_url + href
            board_url_list.append(board_url)
        else:
            href = po.find('a')['href'][1:]
            board_url = base_url + href
            board_url_list.append(board_url)

    print('총 ', len(board_url_list), '개의 url을 수집하였습니다.')

    return board_url_list
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

    dataframe['board_url']   = board_url_list
    dataframe['blog_type']   = blog_type
    dataframe['blogger_id']  = blogger_id

    for u in range(0, len(board_url_list)):
        p_num = board_url_list[u][board_url_list[u].find('/',30) + 1 : ]
        dataframe['post_num'][u] = p_num

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

    nickname = soup.find('div', id='wrapArticleInfo').find('a').text  # 글쓴이
    upload_date = soup.find('span', class_='f_l date').text  # 날짜
    board_category = '분류없음'          # brunch는 블로거의 카테고리가 따로 존재 X. (단, 매거진 keyword별 수집 추후 검토
    title = titles = soup.find('div', class_='wrap_cover').find('h1', class_='cover_title').text  # sub title 제외

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


def gather_all_content(board_url_list) :

    '''

    게시글의 url 주소 리스트를 받아 게시글 주소를 하나씩
    'find_content_info' 모듈에 넣어 나온 딕셔너리 형태의 정보를
    리스트로 저장해 반환한다.

    param  : board_url_list,    list
    return : all_content_info,  list
    '''

    all_content_info = list()

    for b_url in board_url_list :
        parsing = find_content_info(b_url)
        all_content_info.append(parsing)

    return all_content_info

######################################
# STEP6
######################################

def update_save_BR_DF(dataframe, all_content_info, blogger_id) :

    '''
    기존에 만들어져있던 데이터 프레임에 새로운 정보를 추가하고 csv파일로
    저장한 뒤 데이터프레임을 반환한다.

    param  : dataframe,          dataframe(pandas)
             all_content_info,   list
             blogger_id,         str

    return : dataframe,          dataframe(pandas)
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

