# History
#   2019.11.12
#       - def get_total_page_num valid checking 부분 오류 수정
#       - 시작년도 입력 > 시작년월일자 입력
#
#   2019.11.13
#       - def make_date_range 부분 : 종료년월일자 입력 추가
#       - def get_save_article_content 부분 : 수집 및 저장 완료 출력 문구 입력
#       - def make_date_range 부분 : 종료년월일자 함수 수정
#       - def get_save_article_content 부분 : HTTPAdapter Session 추가
#
#   2019.11.14
#       - def get_total_page_num 부분 : cpList 전체를 받는 것이 아니라 1개의 cp만 받고 데이터프레임에 각각
#                                       cp별로 저장할 수 있게 변경
#
#
#

import requests
from requests.adapters import HTTPAdapter

from bs4 import BeautifulSoup

import re
import pandas as pd
import datetime

BASE_URL = "https://news.nate.com/"  # 경제 부분
DEAFAULT_DATE = '20000101'


def get_company_info() :
    req = requests.get(BASE_URL)
    soup = BeautifulSoup(req.text, 'html.parser')
    company_info = soup.find('div', {'class' : 'speechNewsLinkArea f_clear'})
    compant_info_tag = company_info.find_all('li')
    cpList = []

    for a in compant_info_tag :
        href = a.find('a')['href']
        res = re.findall('cp=(\w\w)&', href)[0]
        cpList.append(res)

    return cpList


def make_date_range() :
    '''
    수집년월일을 입력값으로 받아 현재까지의 기사를 수집하는 메소드
    :return: date_range(list, 날짜)
    '''
    init_year = input("시작 일자를 입력하세요.(YYYYMMDD) : ")
    end_year = input("마지막 일자를 입력하세요 (YYYYMMDD) : ")

    if init_year == '' :
        init_year = DEAFAULT_DATE
        print(DEAFAULT_DATE[:4] + '년 ' + DEAFAULT_DATE[4:6] + '월 ' + DEAFAULT_DATE[6:] + '일부터 수집합니다')

    if end_year == '':
        end_year = str(datetime.date.today()).replace('-','')
        print(end_year[:4] + '년 ' + end_year[4:6] + '월 ' + end_year[6:] + '일까지 수집합니다')

    # now = datetime.date.today()

    init_day = datetime.date(int(init_year[:4]), int(init_year[4:6]), int(init_year[6:]))
    end_day = datetime.date(int(end_year[:4]), int(end_year[4:6]), int(end_year[6:]))

    date_range = list()

    while init_day <= end_day:
        date_range.append(init_day.strftime("%Y%m%d"))
        init_day += datetime.timedelta(days=1)

    return date_range


def get_total_page_num(one_cp, date_range) :
    total_page = list()

    total_page_num = dict()
    page_num = list()

    for i in range(0, len(date_range)) :
        req = requests.get('https://news.nate.com/MediaList?cp={cp}&mid=n1101&type=c&date={date}&page=1000'
                           .format(cp=one_cp, date=date_range[i]))

        soup = BeautifulSoup(req.text, 'html.parser')

        is_valid = True if soup.find('span', {'class' : 'page'}) else False

        if is_valid :
            print(one_cp + ' / ' + date_range[i] + '의 총 페이지 : ' +
                  soup.find('span', {'class' : 'page'}).text.split('\n')[-2])
            page_num.append(soup.find('span', {'class' : 'page'}).text.split('\n')[-2])

        else :
            page_num.append('0')
            print(one_cp, "기사가 없습니다. ", date_range[i])

        total_page_num['company'] = one_cp
        total_page_num['date'] = date_range[i]
        total_page_num['page_num'] = page_num

    total_page.append(total_page_num)

    return total_page

# --------------------------------------------------------------------------------------------------------
def make_com_in_url(total_page) :
    com_in_url = list()
    for i in range(0, len(total_page)) :
        for j in range(0, len(total_page[i]['page_num'])) :
            c_url = 'https://news.nate.com/MediaList?cp={cp}&mid=n1101&type=c&date={date}&page={page_num}' \
                .format(cp=total_page[i]['company'], date=total_page[i]['date'], page_num=total_page[i]['page_num'][j])
            com_in_url.append(c_url)
    return com_in_url


def make_page_url(com_in_url) :
    page_url = list()
    for i in range(0, len(com_in_url)) :
        for k in range(1, int(com_in_url[i][74:]) + 1) :
            page_url.append(com_in_url[i].replace(com_in_url[i][69:], 'page=' + str(k)))
    return page_url


def make_all_page_url(total_page) :
    all_page_url = list()
    com_in_url = make_com_in_url(total_page)
    all_page_url += make_page_url(com_in_url)

    return all_page_url

# --------------------------------------------------------------------------------------------------------
def find_article_info(all_page_url) :
    all_article_info = list()

    for i in all_page_url:
        s = requests.Session()
        s.mount(i, HTTPAdapter(max_retries=3))
        req = s.get(i)
        soup = BeautifulSoup(req.text, 'html.parser')

        article_tag = soup.find_all('div', {'class' : 'mduSubjectList'})

        for j in article_tag :
            all_article_info.append(get_article_info(j))

    return all_article_info


def get_article_info(soup) :
    article_info = dict()
    article_info['title'] = soup.find('strong', {"class" : "tit"}).text
    article_info['article_url'] = 'https:' + soup.find('a', {"class" : "lt1"}).attrs['href']
    article_info['upload_date'] = re.sub('[\t\n]', '', soup.find('span', {"class" : "medium"}).text[4:])
    article_info['company'] = re.sub('[\t\n]', '', soup.find('span', {"class" : "medium"}).text[:4])

    return article_info

# --------------------------------------------------------------------------------------------------------
def make_DF(all_article_info) :
    cols = ['article_url', 'company', 'upload_date', 'title']

    dataframe = pd.DataFrame(all_article_info)

    dataframe = dataframe[cols]

    return dataframe


def get_save_article_content(one_cp, date_range, dataframe) :
    dataframe['content'] = ''

    for i in range(0, len(dataframe)) :

        s = requests.Session()
        s.mount(dataframe['article_url'][i], HTTPAdapter(max_retries=3))
        req = s.get(dataframe['article_url'][i])
        soup = BeautifulSoup(req.text, 'html.parser')

        is_valid = True if soup.find('div', {'id' : 'realArtcContents'}) else False

        if is_valid :
            dataframe['content'][i] = re.sub("\n|\t", '', soup.find('div', {'id' : 'realArtcContents'}).text)
        else :
            dataframe['content'][i] = ''



    dataframe.to_csv('{0}_{1}_{2}.csv'.format(one_cp,date_range[0], date_range[-1]), index=False)

    print('ALL PROCESS IS DONE...'+'{0}_{1}_{2}.csv'.format(one_cp,date_range[0], date_range[-1]))

    return dataframe

# --------------------------------------------------------------------------------------------------------
def run_step() :

    cpList = get_company_info()
    date_range = make_date_range()

    for cp in cpList:
        total_page = get_total_page_num(one_cp=cp, date_range=date_range)
        if total_page != '0':
            all_page_url = make_all_page_url(total_page)
            all_article_info = find_article_info(all_page_url)
            dataframe = make_DF(all_article_info)
            get_save_article_content(one_cp=cp, date_range=date_range, dataframe=dataframe)
        else:
            continue

    return None