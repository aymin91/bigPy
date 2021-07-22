#      2019.11.13
#         - add new module 'def run_step()'
#
#       2019.11.15
#           - PROJECT_ROOT :  '/source/bigpycraft/a3rcs/' -- >  '../../'
#       2019.11.18
#           change def make_save_df
#                  'TI_user_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
#                   -> 'TI_ID_List_{0}_{1}_{2}.csv'.format(now.year, now.month, now.day), index=False,

from selenium import webdriver
from bs4 import BeautifulSoup

import glob
import pandas as pd
import time
import os
import module.s1_collect.comm.util as util
from module.s1_collect.blog.bl_ti import ti_user_lpn_crawler as tulc

BLOG_NAME = "TISTORY"
root_dir = util.get_root_dir()
file_dir = util.get_file_dir()
rep_dir = root_dir + util.get_user_dir(file_dir)
# blog_mgr = util.get_blog_mgr()


BLOG_CODE = util.get_blog_code(BLOG_NAME)
BASE_URL  = util.get_user_url(BLOG_CODE)
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


############################################################################################
# STEP1. Blog Main 접속
############################################################################################

def go_blog_main():
    '''
    웹드라이브를 호출하는 메소드
        :param None
        :return: driver(ChromeWebDriver)
    '''
    # driver = get_driver()
    driver = get_headless_driver(driver_path)
    driver.get(BASE_URL)

    return driver


############################################################################################
# STEP2. 블로거 정보 수집
############################################################################################

def scroll_to_end(driver):
    '''
    웹드라이버를 받아 스크롤을 내린다.
    :param    driver(ChromeWebDriver)
    :return   driver(ChromeWebDriver)
    '''
    for i in range(50):   # 50
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

    return driver


def get_blogger_info(blog_info):
    '''
    블로그 목록 중 하나의 bs4 parsing된 정보를 받아
    user_id.tistory.com 형태의 주소 user_id, blogger_nick을
    dict 형태로 수집
        :param     blog_info(bs4)
        :return    blogger_info(dict)
    '''
    href = blog_info.find('a')['href']
    url_adr = href.find('/', 7)
    url = href[:url_adr]
    newest_num = href[url_adr+1:]
    if newest_num.isdigit():  # url 주소가 숫자가 아니라 글자로 이루어진 사이트 발견 ex) https://semo-gif.tistory.com/
        if 'tistory' in url:
            blogger_info = dict()
            user_id = url.split('.')[0][7:]
            user_nick = blog_info.find('span', class_='txt_date').get_text()[3:]

            blogger_info['user_id'] = user_id
            blogger_info['user_nick'] = user_nick
            blogger_info['newest_post_num'] = int(newest_num)
            # print(blogger_info)
        elif 'tistory' not in url:

           blogger_info = None
    else:
        blogger_info = None

    return blogger_info


def gather_best_blogger_info(driver):
    '''
    웹드라이버를 받아 현재 카테고리에서 '베스트'에 해당하는
    user_id와 nick을 수집해 리스트로 반환
        :param    driver(ChromeWebDriver):
        :return   best_blogger_info(list)
    '''
    best_blogger_info = list()

    soup = BeautifulSoup(driver.page_source, 'lxml')

    best_blogs = soup.find('ul', class_='list_tistory list_slide')
    best_blog = best_blogs.find_all('li')

    for bb in best_blog:
        blogger_info = get_blogger_info(bb)
        best_blogger_info.append(blogger_info)
    best_blogger_info = [bbi for bbi in best_blogger_info if bbi != None]

    return best_blogger_info


def gather_list_blogger_info(driver):
    '''
    웹드라이버를 받아 현재 카테고리에서 '리스트'에 해당하는
    user_id와 nick을 수집해 리스트로 반환
        :param    driver(ChromeWebDriver)
        :return   list_blogger_info(list)
    '''
    list_blogger_info = list()

    soup = BeautifulSoup(driver.page_source, 'lxml')

    list_blogs = soup.find('div', class_='section_list')
    list_blog = list_blogs.find_all('li')

    for lb in list_blog:
        blogger_info = get_blogger_info(lb)
        list_blogger_info.append(blogger_info)
    list_blogger_info = [lbi for lbi in list_blogger_info if lbi != None]

    return list_blogger_info


def one_category_blogger_info(best_blogger_info, list_blogger_info):
    '''
    user_id, blogger_nick 이 담긴 '베스트' 리스트와 '리스트' 리스트를 받아
    하나의 카테고리 리스트로 합친다.
    :param     best_blogger_info(list)
                list_blogger_info(list)
    :return    category_blogger_info(list)
    '''
    category_blogger_info = best_blogger_info + list_blogger_info

    return category_blogger_info


def gather_blogger_info(driver):
    '''
    웹드라이버를 받아 6가지 카테고리를 돌면서 각 카테고리에서 스크롤을 내려
    정보를 모두 표시한 후 best, list user_id와 blogger_nick을 수집한다.
    :param    driver(ChromeWebDriver)
    :return   all_blogger_info(list)
    '''
    all_blogger_info = list()

    categorys = ['life', 'travel', 'culture', 'it', 'sports', 'current']
    # categorys = ['life']

    for cat in categorys:
        cat_url = BASE_URL + cat
        driver.get(cat_url)
        open_page = scroll_to_end(driver)  # driver.가 아니라 web_page를 돌렸을 때 드라이버가 없다는 오류가 났었음
        time.sleep(0.5)

        list_blogger_info = gather_list_blogger_info(open_page)
        best_blogger_info = gather_best_blogger_info(open_page)

        category_blogger_info = one_category_blogger_info(best_blogger_info, list_blogger_info)

        all_blogger_info.extend(category_blogger_info)
        time.sleep(1)

    driver.quit();
    return all_blogger_info


############################################################################################
# STEP3. 데이터프레임에 저장 및 csv 파일 저장
############################################################################################

def make_user_df(all_blogger_info):
    '''
    수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장
        :param   : all_blogger_info(list)
        :return  : blogger_info_df(with. csv file)
    '''
    # blogger_info_df = pd.DataFrame(all_blogger_info)

    cols = ['user_id', 'user_nick', 'collecting_date', 'oldest_post_num', 'newest_post_num']

    blogger_info_df = pd.DataFrame(all_blogger_info, columns=cols)

    print('수집한 아이디 개수 : ', len(blogger_info_df))

    # print(blogger_info_df)
    # blogger_info_df = all_blogger_info_df.drop_duplicates()                    # 중복값 제거
    blogger_info_df = blogger_info_df[blogger_info_df['user_id'] != '']

    blogger_info_df = blogger_info_df.groupby(['user_id', 'user_nick'], as_index=False).agg({'newest_post_num': max})
    blogger_info_df.sort_values(by=['user_id'], axis=0, inplace=True)  # sorting
    blogger_info_df = blogger_info_df.reset_index()  # index reset
    del blogger_info_df['index']  # index column 제거



    blogger_info_df['oldest_post_num'] = 1
    blogger_info_df['collecting_date'] = ' '

    try:
        util.create_file_dir(rep_dir)
    except:
        print('repository path is already existed!')
        pass

    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))
    # print('rep_dir ', rep_dir)
    if len(csv_files) == 1:
        print('새로운 id list가 수집되었습니다. new id list saved!')
        blogger_info_df.to_csv(rep_dir+'{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')  # csv file로 저장
    else:
        print('기존 id list가 없어 기존 이름 id list로 저장됩니다.')
        blogger_info_df.to_csv(rep_dir+'{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')

    return None

############################################################################################
# STEP4. 기존 ID  newest_post_num 수집
############################################################################################

def updating_newest_post_num():
    # csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    if os.path.isfile(rep_dir+ '{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE)):
        existing_csv = pd.read_csv(rep_dir + '{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), engine='python', encoding = 'utf-8')
        tulc.run_step(existing_csv)

    else:
        print('기존 아이디가 안됩니다.')
        pass

    return None

############################################################################################
# STEP5. ID_LISt 갱신 및 저장
############################################################################################

def make_save_df():

    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))
    # print('csv파일들 : ', csv_files)

    dataframes = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, engine='python') #  encoding = 'utf-8'
        dataframes.append(df)


    result = pd.concat(dataframes, ignore_index=True)
    result = result.drop_duplicates(['user_id'], keep='first')
    result.to_csv(rep_dir + '{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')

    if os.path.isfile(rep_dir+ '{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE)):
        os.remove(rep_dir + '{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE))
        print('병합 성공, new id list는 삭제합니다')



    return None



############################################################################################
# 실행
############################################################################################

def main():
    driver = go_blog_main()

    all_blogger_info = gather_blogger_info(driver)   # 신규 id 저장(TI_new_ID_List.csv)
    make_user_df(all_blogger_info)
    updating_newest_post_num()    # 신규 id 저장(TI_new_ID_List.csv)

    make_save_df()

    return None

if __name__ == '__main__':
    main()