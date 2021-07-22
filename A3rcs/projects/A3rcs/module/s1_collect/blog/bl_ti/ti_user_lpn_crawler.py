
# coding: utf-8

# In[ ]:


from selenium import webdriver
from bs4 import BeautifulSoup


import time

import pandas as pd

import module.s1_collect.comm.util as util

BLOG_NAME = "TISTORY"
root_dir = util.get_root_dir()
file_dir = util.get_file_dir()
# blog_mgr = util.get_blog_mgr()


BLOG_CODE = util.get_blog_code(BLOG_NAME)
BASE_URL  = util.get_post_url(BLOG_CODE)
driver_path = util.get_webdriver_path()


# def get_driver(driver_path):
#     '''
#         웹드라이브를 호출하는 메소드
#         parmam : None
#         Result : driver(ChromeWebDriver)
#     '''
#
#     driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
#
#     return driver

def get_headless_driver(driver_path):
    '''
        웹드라이브를 호출하는 메소드
        parmam : None
        Result : driver  , ChromeWebDriver
    '''

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(driver_path, chrome_options=options) # executable_path=driver_path

    return driver



# ############################################################################################
# # STEP1. id, last_post_num의 리스트 만들기
# ############################################################################################


def make_list(dataframe):
    user_ids = list(dataframe['user_id'])
    last_post_nums = list(dataframe['newest_post_num'])
    user_nick = list(dataframe['user_nick'])
    collecting_date = list(dataframe['collecting_date'])

    return user_ids, last_post_nums, user_nick, collecting_date

# ############################################################################################
# # STEP2. id, latest_post_num 정보 가져오기
# ############################################################################################


def get_blog_url(user_id):
    '''
    user_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
    (일반적인 blog_url 형식 : https://brunch.co.kr/(@user_id )#articles(글 목록)

        :param user_id(str)
        :return: blog_url(str)
    '''

    base_url = BASE_URL

    blog_url = base_url.split('www')[0] + user_id + base_url.split('www')[1] + 'm/'
    return blog_url


def get_latest_post_num(driver, user_id, last_post_num,  user_nick, collecting_date):
    '''

        :param     blog_info(bs4)
        :return    blogger_info(dict)
    '''
    global blogger_info
    # print(driver.current_url)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    post_list = soup.find('div', class_='blog_list')  # (class_ = wrap_article_list - > blog_list)

    is_url = True if post_list else False
    if is_url:
        posts = post_list.find_all('li')
        is_posts = True if posts else False
        if is_posts:
            find_post = posts[0].find('a')['href']
            find_num = posts[0].find('a')['href'].find('/m/') +3
            latest_post_num = find_post[find_num:]
        # if len(posts[0]) == 3:
        #         latest_post_num = posts[0].find('a')['href'][posts[0].find('a')['href'].find('/', 1) + 1:]
        # else:
        #     latest_post_num = posts[0].find_all('a')[1]['href'][posts[0].find_all('a')[1]['href'].find('/', 1) + 1:]
                # try
            if latest_post_num.isdigit():
                blogger_info = dict()
                blogger_info['user_id'] = user_id
                blogger_info['oldest_post_num'] = last_post_num
                blogger_info['newest_post_num'] = int(latest_post_num)
                blogger_info['user_nick']       = user_nick
                blogger_info['collecting_date'] = collecting_date
            else:
                pass
        else:
            pass
    else:
        pass
    return blogger_info



def gather_all_lpn(user_ids, last_post_nums, user_nick, collecting_date):
    all_blogger_info = list()
    driver = get_headless_driver(driver_path)

    for num in range(len(user_ids)):
        blog_url = get_blog_url(user_ids[num])
        driver.get(blog_url)
        time.sleep(0.5)
        blogger_info = get_latest_post_num(driver, user_ids[num], last_post_nums[num], user_nick[num], collecting_date[num])
        all_blogger_info.append(blogger_info)

    return all_blogger_info

# ############################################################################################
# # STEP3. 데이터프레임 및 저장
# ############################################################################################

def make_save_df(all_blogger_info):
    '''
    수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장
        :param   : all_blogger_info(list)
        :return  : blogger_info_df(with. csv file)
    '''
    blogger_info_df = pd.DataFrame(all_blogger_info)

    print('수집한 아이디 개수 : ', len(blogger_info_df))

    blogger_info_df.sort_values(by=['user_id'], axis=0, inplace=True)  # sorting
    blogger_info_df = blogger_info_df.reset_index()  # index reset
    del blogger_info_df['index']  # index column 제거

    rep_dir = root_dir + util.get_user_dir(file_dir)
    # print('기존 아이디 업데이트 한거 저장합니다.')
    blogger_info_df.to_csv(rep_dir +
        'TI_ID_List.csv',
        index=False, encoding='utf-8')  # csv file로 저장

    return None

############################################################################################
# 실행
############################################################################################

def run_step(dataframe):
    print('기존 아이디들을 업데이트 합니다.')

    user_ids, last_post_nums, user_nick, collecting_date = make_list(dataframe)
    all_blogger_info = gather_all_lpn(user_ids, last_post_nums, user_nick, collecting_date)
    make_save_df(all_blogger_info)

    return None


















# 개별 수집

# ############################################################################################
# # STEP1. Blog Main 접속
# ############################################################################################
#
# def get_blog_url(user_id):
#     '''
#     user_id 기본 blog_url을 합쳐 일반적인 blog_url 형식으로 만들어준다.
#     (일반적인 blog_url 형식 : https://brunch.co.kr/(@user_id )#articles(글 목록)
#
#         :param user_id(str)
#         :return: blog_url(str)
#     '''
#
#     base_url = BASE_URL
#
#     blog_url = 'https://' + user_id + '.' + base_url + '/m/'
#
#     return blog_url
#
# ############################################################################################
# # STEP2. 블로거 정보 수집
# ############################################################################################
#
# def get_latest_post_num(driver, user_id, last_post_num):
#     '''
#
#         :param     blog_info(bs4)
#         :return    blogger_info(dict)
#     '''
#     blogger_info = dict()
#
#     soup = BeautifulSoup(driver.page_source, 'lxml')
#     post_list = soup.find('ul', class_ = 'list_post')
#     posts = post_list.find_all('li')
#     latest_post_num = posts[0].find('a')['href'][posts[0].find('a')['href'].find('/m/')+3:]
#
#     blogger_info['blogger_id'] = blogger_id
#     blogger_info['last_post_num'] = last_post_num
#     blogger_info['latest_post_num'] = int(latest_post_num)
#
#     return blogger_info
#
#
#
# ############################################################################################
# # STEP3. 데이터프레임에 저장 및 csv 파일 저장
# ############################################################################################
#
# def make_save_df(all_blogger_info):
#     '''
#     수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장
#         :param   : all_blogger_info(list)
#         :return  : blogger_info_df(with. csv file)
#     '''
#     now = datetime.datetime.now()
#
#     blogger_info_df = pd.DataFrame(blogger_info)
#
#     blogger_info_df.sort_values(by=['user_id'], axis=0, inplace=True)  # sorting
#     blogger_info_df = blogger_info_df.reset_index()  # index reset
#     del blogger_info_df['index']  # index column 제거
#
#     blogger_info_df.to_csv(
#         'TI_user_id_over_1st_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
#         encoding='utf-8')  # csv file로 저장
#
#     return blogger_info_df  # blogger_info_df
#
#
# ############################################################################################
# # 실행
# ############################################################################################
#
# def run_step():
#     driver = go_blog_main()
#     all_blogger_info = get_latest_post_num(driver, blogger_id, last_post_num)
#     make_save_df(all_blogger_info)
#
#     return None

