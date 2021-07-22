# Project : AI-based Auto Analysis Report Creating System
# History :


from selenium import webdriver
from bs4 import BeautifulSoup
import platform
import datetime
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

BASE_URL = 'http://blog.daum.net/'

PROJECT_ROOT = '/project/bigpycraft/a3rcs/'

WD_CHROME_PATH_WIN = 'driver/chromedriver.exe'
WD_CHROME_PATH_MAC = 'driver/macos/chromedriver'
WD_CHROME_PATH_LINUX = 'driver/linux/chromedriver'

############################################################################################
# STEP1.
############################################################################################

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
        
    driver.get('http://blog.daum.net/')

    return driver

############################################################################################
# STEP2.
############################################################################################

def get_now_blogger_info(driver):
    
    '''
        현재 드라이버에 있는 다음 블로그 페이지에서 '지금, 이 블로그' 목록에 있는
        블로거 id, nickname 정보를 딕셔너리에 담은 후 리스트로 반환(3개의 정보)
        :param   : driver
        :return  : now_bloggers_info(list)
    '''
    
    now_bloggers_info = list()
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    now_info = soup.find_all('div', class_ = 'item_post_type3')
    
    for ni in now_info:
        
        now_blogger_info = dict()
        
        href = ni.find('a',target = '_blank')['href']
        blogger_id = href[href.find('net')+4:]
        
        blogger_nick = ni.find('dd', class_ = 'txt_post_type2').text.strip()
        
        now_blogger_info['blogger_id'] = blogger_id
        now_blogger_info['blogger_nick'] = blogger_nick
        
        now_bloggers_info.append(now_blogger_info)
                
    return now_bloggers_info
    

def gather_now_blogger_info(driver):
    
    '''
        현재 드라이버에 있는 '지금, 이 블로그' 첫 페이지를 가져온 후 버튼을 세 번 누르며
        계속 현재 페이지의 블로거 ickname 정보를 딕셔너리에 담아 리스트에 추가하여
        반환(총 12개의 정보)

        :param   : driver
        :return  : all_now_blogger_info(list)
    '''
    
    all_now_blogger_info = list()
    btn_count = 3        # 최대 3번 버튼을 누를 수 있다.(2019.10.22 기준)
    
    # 처음 세 개의 블로그 정보를 가져온다.
    
    now_bloggers_info = get_now_blogger_info(driver)
    all_now_blogger_info.extend(now_bloggers_info)

    # 버튼을 클릭하며 블로그 정보를 가져온다.
    
    for i in range(btn_count):
        try : 
            driver.find_element_by_css_selector('#nowBlog > div > div.slide_post > div.wrap_btn > button.btn_arrow.btn_next.btn_on').click()
            get_info_2 = get_now_blogger_info(driver)
            all_now_blogger_info.extend(get_info_2)
        except :                                    # 다음 버튼이 활성화 되지 않을 시의 코드 
            pass
            print('모든 게시글을 보았습니다. 다시 페이지를 앞으로 돌려 시도해주세요') 
            
    return all_now_blogger_info

############################################################################################
# STEP3.
############################################################################################

def click_friend_more_btn(driver):
        
    '''
        현재 드라이버에서 '친구글'의 '더보기' 버튼을 클릭합니다.
        누르는 횟수는 최대 4번입니다.(2019.10.22 기준)
        :param   : driver
        :return  : driver
    '''
    
    btn_count = 4
    for i in range(btn_count):
        try:
            driver.find_element_by_css_selector('#mArticle > div:nth-child(1) > div > button').click()
            wait = WebDriverWait(driver, 20)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mArticle > div:nth-child(1) > div > button')))
        except :
            pass
    return driver 

def click_empathize_more_btn(driver):
        
    '''
        현재 드라이버에서 '공감글'의 '전체'보기를 클릭한 후 더보기' 버튼을 클릭합니다.
        누르는 횟수는 최대 19번입니다.(2019.10.22 기준)
        :param   : driver
        :return  : driver
    '''
    
    # 전체 보기를 클릭합니다.
    
    driver.find_element_by_css_selector('#mArticle > div:nth-child(3) > div > div.section_empathy > ul > li:nth-child(1) > a').click()
    
    # 더보기 버튼을 클릭합니다. 
    
    btn_count = 19
    
    for i in range(btn_count):
        try:
            driver.find_element_by_css_selector('#mArticle > div:nth-child(3) > div > div.section_empathy > a').click()
            wait = WebDriverWait(driver, 20)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mArticle > div:nth-child(3) > div > div.section_empathy > a')))
        except :
            pass
    return driver


def click_more_btn(driver):
    '''
        '친구글', '공감글' 게시물을 모두 보기 위하여 '더보기' 버튼을 각각에 맞게 클릭합니다.
        :param   : driver
        :return  : driver
    '''

    driver = click_friend_more_btn(driver)
    time.sleep(1)
    driver = click_empathize_more_btn(driver)

    return driver

############################################################################################
# STEP4.
############################################################################################

def get_soup(driver):
        
    '''
        '친구글', '공감글' 더보기 버튼을 눌러 모든 정보를 펼친 후에 bs4를
        이용하여 parsing 한 후 soup 데이터를 반환합니다.
        :param   : driver
        :return  : soup(bs4.soup)
    '''
    
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    return soup 

def get_friend_blogger_info(soup):
            
    '''
        parsing된 soup 정보를 받아 '친구글'에 있는 블로거 id, nickname 정보를 딕셔너리에 담아 
        리스트에 추가하여 반환
        :param   : soup
        :return  : friend_blogger_info(list)
    '''
    
    friend_blogger_info = list()
    
    all_info = soup.find_all('div', class_ = 'list_post')
    friend   = all_info[1].find_all('div', class_ = 'item_post')
    
    for f in friend:
        blogger_info = dict()
        
        href = f.find('a')['href']
        b_id = href[href.find('net')+4:]
        blogger_id = b_id[:b_id.find('/')]
        
        blogger_nick = f.find('dd', class_ = 'txt_post_type1 txt_name').text
        
        blogger_info['blogger_id'] = blogger_id
        blogger_info['blogger_nick'] = blogger_nick
        
        friend_blogger_info.append(blogger_info)

    return friend_blogger_info
        
def get_empathize_blogger_info(soup):
                
    '''
        parsing된 soup 정보를 받아 '공감글'에 있는 블로거 id, nickname 정보를 딕셔너리에 담아 
        리스트에 추가하여 반환
        :param   : soup
        :return  : empathize_blogger_info(list)
    '''
    
    
    empathize_blogger_info = list()
    
    empathize = soup.find_all('div', class_ = 'item_post item_post_type4')
    
    for emp in empathize:
        blogger_info = dict()
        
        href = emp.find('a')['href']
        b_id = href[href.find('net')+4:]
        blogger_id = b_id[:b_id.find('/')]
        
        blogger_nick = emp.find('dd', class_ = 'txt_post_type1').text
        
        
        blogger_info['blogger_id'] = blogger_id
        blogger_info['blogger_nick'] = blogger_nick
        
        empathize_blogger_info.append(blogger_info)
        
    return empathize_blogger_info

def gather_friend_empathize_blogger_info(driver):
                
    '''
        driver를 받아 get_soup, get_friend_blogger_info, get_empathize_blogger_info 모듈을 이용하여
        '친구글', '공감글' 블로거들의 id, nickname 정보를 딕셔너리에 담아 최종적으로
        리스트 형태로 반환
        :param   : driver
        :return  : all_friend_empathize_blogger_info(list)
    '''
    
    all_friend_empathize_blogger_info = list()
    
    soup = get_soup(driver)
    
    friend_blogger_info = get_friend_blogger_info(soup)
    empathize_blogger_info = get_empathize_blogger_info(soup)
    
    all_friend_empathize_blogger_info.extend(friend_blogger_info)
    all_friend_empathize_blogger_info.extend(empathize_blogger_info)
    
    return all_friend_empathize_blogger_info

############################################################################################
# STEP5.
############################################################################################

def make_save_df(all_now_blogger_info, all_friend_empathize_blogger_info):
    
    '''
        수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장 
        :param   : all_now_blogger_info(list), all_friend_empathize_blogger_info(list)
        :return  : blogger_info_df(with. csv file)
    '''
    
    now = datetime.datetime.now()
    
    
    now_blogger_info_df = pd.DataFrame(all_now_blogger_info)
    friend_empathize_blogger_info_df = pd.DataFrame(all_friend_empathize_blogger_info)
    blogger_info_df = pd.concat([now_blogger_info_df, friend_empathize_blogger_info_df] )

    blogger_info_df = blogger_info_df.drop_duplicates()                    # 중복값 제거
    blogger_info_df.sort_values(by=['blogger_id'], axis=0, inplace=True)   # sorting
    blogger_info_df = blogger_info_df.reset_index()                        # index reset
    del blogger_info_df['index']                                           # index column 제거



    blogger_info_df.to_csv(
        'DM_blogger_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
        encoding='cp949')  # csv file로 저장

    return blogger_info_df

