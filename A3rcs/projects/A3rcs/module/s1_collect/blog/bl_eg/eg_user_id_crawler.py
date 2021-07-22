# Project : AI-based Auto Analysis Report Creating System
# History :
#      2019.11.13
#         - add new module 'def run_step()'
#
#       2019.11.18
#           change def make_save_df
#                  'EG_user_id_{0}_{1}_{2}_{3}_{4}.csv'.format(now.year, now.month, now.day, now.hour, now.minute), index=False,
#                   -> 'EG_ID_List_{0}_{1}_{2}.csv'.format(now.year, now.month, now.day), index=False,


import requests
from bs4 import BeautifulSoup
import pandas as pd

import os
import glob
import datetime
import re
import module.s1_collect.comm.util as util


BLOG_NAME = "EGLOOS"

root_dir  = util.get_root_dir()
file_dir  = util.get_file_dir()
rep_dir   = root_dir + util.get_user_dir(file_dir)
# blog_mgr = util.get_blog_mgr()

BLOG_CODE = util.get_blog_code(BLOG_NAME)
BASE_URL  = util.get_user_url(BLOG_CODE)

############################################################################################
# STEP1. Blog Main 접속
############################################################################################



############################################################################################
# STEP2. 전체 블로거 정보 수집
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

        blogger_info_dict['user_id'] = blogger_tags[i].find_all('a')[1]['href'][7 :].split('.')[0]
        blogger_info_dict['user_nick'] = blogger_tags[i].find_all('a')[1].text

        blogger_info_list.append(blogger_info_dict)

    return blogger_info_list

def gather_blogger_info() :
    '''
        이글루스 벨리 페이지 리스트를 받아 블로거의 정보를 수집하여 최종적으로 반환해주는 메소드
        :param  : None
        :return : all_blogger_info(list)
    '''
    all_blogger_info = list()

    for v in range(1, 11) :
        valley_url = regex_insert_page_num(v)
        blogger_info_tag = find_blogger_info_tag(valley_url)
        all_blogger_info.extend(get_blogger_info(blogger_info_tag))

    return all_blogger_info

def regex_insert_page_num(page_num) :
    '''
        이글루스 벨리에서 [현재 인기글] 페이지 url을 생성하는 메소드
        :param  : None
        :return : regex_page_url(str)
    '''

    regex_page_url = re.sub('page=1', 'page=' + str(page_num), BASE_URL)

    return regex_page_url


############################################################################################
# STEP3. 데이터프레임에 저장 및 csv 파일 저장
############################################################################################
def make_save_df(all_blogger_info) :
    '''
        수집한 blogger들의 정보를 데이터프레임으로 만들고 csv파일로 저장하는 메소드
        :param   : all_blogger_info(list)
        :return  : blogger_info_df(with. csv file)
    '''

    blogger_info_df = pd.DataFrame(all_blogger_info)

    blogger_info_df['crawling_date'] = ''

    blogger_info_df = blogger_info_df.drop_duplicates()  # 중복값 제거

    blogger_info_df.sort_values(by=['user_id'], axis=0, inplace=True)  # sorting

    blogger_info_df = blogger_info_df.reset_index()  # index reset

    del blogger_info_df['index']  # index column 제거

    blogger_info_df['collecting_date'] = ' '

    try:
        util.create_file_dir(rep_dir)
    except:
        print('repository path is already existed!')
        pass

    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    if len(csv_files) == 1:
        print('새로운 id list가 수집되었습니다. new id list saved!')
        blogger_info_df.to_csv(rep_dir+'{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE),
                               index=False, encoding='utf-8')  # csv file로 저장
    else:
        print('기존 id list가 없어 기존 이름 id list로 저장됩니다.')
        blogger_info_df.to_csv(rep_dir+'{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')

    return blogger_info_df

############################################################################################
# STEP4. 기존 csv file과 새롭게 수집한 csv file을 합쳐 중복 아이디 제거
############################################################################################
def concat_id_list():
    # folder_path = 'C:/projects/A3rcs/repository/user_id'
    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    dataframes = []

    for csv_file in csv_files :
        df = pd.read_csv(csv_file, engine='python')
        dataframes.append(df)
    #     print(csv_file)

    result = pd.concat(dataframes, ignore_index=True)
    result = result.drop_duplicates(['user_id', 'user_nick'], keep='first') #

    result = result.reset_index()  # index reset

    del result['index']  # index column 제거

    result.to_csv(rep_dir+'{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), index=False, encoding='utf-8')

    print('병합 성공, new id list는 삭제합니다')

    os.remove(rep_dir+'{blog_code}_new_ID_List.csv'.format(blog_code=BLOG_CODE),)
    return None


############################################################################################
# 실행
############################################################################################

def main():

    all_blogger_info = gather_blogger_info()
    make_save_df(all_blogger_info)

    csv_files = glob.glob(os.path.join(rep_dir, '{blog_code}_*.csv').format(blog_code=BLOG_CODE))

    if len(csv_files) == 2:
        concat_id_list()
    else:
        pass

    return None
if __name__ == '__main__':
    main()

# run_step()
