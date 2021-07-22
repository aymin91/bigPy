# Project : AI-based Auto Analysis Report Creating System
# History :

import requests
from bs4 import BeautifulSoup
import pandas as pd

import datetime
import re

BASE_URL = 'http://valley.egloos.com/index.php?page=1'

############################################################################################
# STEP1. Blog Main 접속
############################################################################################



############################################################################################
# STEP2. 전체 블로거 정보 확인
############################################################################################
def find_blogger_info_tag(one_valley_url) :
    '''
        블로거 정보가 있는 태그를 찾아주는 메소드
        :param   : one_valley_url(str)
        :return  : blogger_info_tag(bs4.tag)
    '''
    req = requests.get(one_valley_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    blogger_info_tag = soup.find('ul', {'class' : 'postList1 f_clear'})

    return blogger_info_tag


def get_blogger_info(blogger_info_tag) :
    '''
        blogger_info_tag에서 찾은 블로거들의 정보를 dict형태로 저장한 후,
        페이지 별(페이지 당 15개)로 리스트로 저장하여 반환하는 메소드
        :param  : blogger_info_tag(bs4.tag)
        :return : blogger_info_list(list)
    '''
    blogger_info_list = list()

    blogger_tags = blogger_info_tag.find_all('dd', {'class' : 'content'})

    for i in range(0, len(blogger_tags)) :
        blogger_info_dict = dict()

        blogger_info_dict['nickname'] = blogger_tags[i].find_all('a')[1].text
        blogger_info_dict['blogger_id'] = blogger_tags[i].find_all('a')[1]['href'][7 :].split('.')[0]

        blogger_info_list.append(blogger_info_dict)

    return blogger_info_list


############################################################################################
# STEP3. 블로거 정보 수집
############################################################################################
def gather_blogger_info() :
    '''
        이글루스 벨리 페이지 리스트를 받아 블로거의 정보를 수집하여 최종적으로 반환해주는 메소드
        :param  : None
        :return : all_blogger_info(list)
    '''
    all_blogger_info = list()

    for v in range(1, 11) :
        valley_url = make_valley_url_list(v)
        blogger_info_tag = find_blogger_info_tag(valley_url)
        all_blogger_info += get_blogger_info(blogger_info_tag)

    return all_blogger_info

def make_valley_url_list(page_num) :
    '''
        이글루스 벨리에서 [현재 인기글] 페이지 url을 생성하는 메소드
        :param  : None
        :return : valley_url_list(list)
    '''

    valley_url = re.sub('page=1', 'page=' + str(page_num), BASE_URL)

    return valley_url


############################################################################################
# STEP4. 데이터프레임에 저장 및 csv 파일 저장
############################################################################################
def make_save_df(all_blogger_info) :
    '''
        수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장하는 메소드
        :param   : all_blogger_info(list)
        :return  : blogger_info_df(with. csv file)
    '''

    now = datetime.datetime.now()

    blogger_info_df = pd.DataFrame(all_blogger_info)

    blogger_info_df = blogger_info_df.drop_duplicates()  # 중복값 제거
    blogger_info_df.sort_values(by=['blogger_id'], axis=0, inplace=True)  # sorting
    blogger_info_df = blogger_info_df.reset_index()  # index reset
    del blogger_info_df['index']  # index column 제거

    blogger_info_df.to_csv(
        'EG_blogger_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute),
        index=False, encoding='cp949')  # csv file로 저장

    return blogger_info_df
