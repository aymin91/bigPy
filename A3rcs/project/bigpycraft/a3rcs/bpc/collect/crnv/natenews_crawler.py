import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime


BASE_URL = "https://news.nate.com/"   # 경제 부분
DEAFAULT_YEAR = '2000'


def get_company_info() :
    '''
    언론사 코드를 구하는 메소드
    :return: cpList(list, 언론사 코드 리스트)
    '''
    req = requests.get(BASE_URL)
    soup = BeautifulSoup(req.text, 'html.parser')
    company_info = soup.find('div', {'class' : 'speechNewsLinkArea f_clear'})
    compant_info_tag = company_info.find_all('li')
    cpList = list()

    for a in compant_info_tag :
        href = a.find('a')['href']
        res = re.findall('cp=(\w\w)&', href)[0]
        cpList.append(res)

    return cpList


def make_date_range() :
    '''
    수집년도를 입력값으로 받아 현재까지의 기사를 수집하는 메소드
    :return: date_range(list, 날짜)
    '''
    init_year = input("시작 년도 : ")

    if init_year == '' :
        print(DEAFAULT_YEAR + '년부터 수집합니다')
        init_year = DEAFAULT_YEAR

    now = datetime.date.today()

    init_day = datetime.date(int(init_year), 1, 1)

    day = init_day
    date_range = list()

    while day <= now :
        date_range.append(day.strftime("%Y%m%d"))
        day += datetime.timedelta(days=1)

    return date_range


def get_total_page_num(cpList, date_range) :
    '''
    날짜별 게시된 기사의 게시판의 맨 마지막 페이지를 구하는 메소드
    :param cpList(list, 언론사 코드 리스트)
    :param date_range(list, 날짜)
    :return: total_page_num(dict, 언론사/날짜/페이지를 키값으로 가지는 딕셔너리)
    '''
    total_page_num = dict()

    for c in range(0, len(cpList)) :
        page_num = list()

        for i in range(0, len(date_range)) :

            print(i, cpList[c], date_range[i])
            req = requests.get('https://news.nate.com/MediaList?cp={cp}&mid=n1101&type=c&date={date}&page=100'
                               .format(cp=cpList[c], date=date_range[i]))

            soup = BeautifulSoup(req.text, 'html.parser')

            is_valid = True if soup.find('span', {'class' : 'page'}).text.split('\n')[-2] else False

            if is_valid :
                page_num.append(soup.find('span', {'class' : 'page'}).text.split('\n')[-2])

            else :
                print("기사가 없습니다. ", date_range[i])

            total_page_num[cpList[c]] = page_num

    return total_page_num


def make_com_in_url(total_page_num) :
    '''
    언론사별 기사 게시판 url을 생성해주는 메소드
    :param total_page_num(dict, 언론사/날짜/페이지를 키값으로 가지는 딕셔너리)
    :return: com_in_url(list, 언론사별 기사 게시판 끝 페이지가 들어간 url을 생성해놓은 리스트)
    '''
    com_in_url = list()
    for i in range(0, len(total_page_num)) :
        c_url = 'https://news.nate.com/MediaList?cp={cp}&mid=n1101&type=c&date={date}&page={page_num}' \
            .format(cp=total_page_num[i]['company'], date=total_page_num[i]['date'],
                    page_num=total_page_num[i]['page_num'])
        com_in_url.append(c_url)
    return com_in_url

def make_page_url(com_in_url):
    '''
    com_in_url(list)에서 받아온 url을 사용하여 기사 게시판 1페이지부터 끝 페이지까지의 게시판 url을 생성해주는 메소드
    :param com_in_url(list, 언론사별 기사 게시판 끝 페이지가 들어간 url을 생성해놓은 리스트)
    :return: page_url(list, 언론사별 기사 게시판 첫페이지부터 끝 페이지까지 들어간 url을 생성해놓은 리스트)
    '''
    page_url = list()
    for i in range(0, len(com_in_url)):
        for k in range(1, int(com_in_url[i][74:])+1):
            page_url.append(com_in_url[i].replace(com_in_url[i][69:], 'page='+str(k)))
    return page_url


def make_all_page_url(total_page_num) :
    '''
    게시판 페이지를 생성하는 메소드들을 실행시켜 모든 게시판 페이지별 url을 구하는 메소드
    :param total_page_num(dict, 언론사/날짜/페이지를 키값으로 가지는 딕셔너리)
    :return: all_page_url(list, 모든 게시판 페이지별 url)
    '''
    all_page_url = list()
    com_in_url = make_com_in_url(total_page_num)
    all_page_url += make_page_url(com_in_url)

    return all_page_url


def find_article_info(all_page_url) :
    '''
    모든 기사 정보를 수집하는 메소드
    :param all_page_url(list, 모든 게시판 페이지별 url)
    :return: all_article_info(list, (기사 내용을 제외한) 모든 기사 정보를 저장하고 있는 리스트)
    '''
    all_article_info = list()

    for i in all_page_url :
        r = requests.get(i)
        soup = BeautifulSoup(r.text, 'html.parser')

        article_tag = soup.find_all('div', {'class' : 'mduSubjectList'})

        for j in article_tag :
            all_article_info.append(get_article_info(j))

    return all_article_info


def get_article_info(soup) :
    '''
    soup 정보를 받아 기사 정보를 수집하는 메소드
    :param soup(bs4.tag)
    :return: article_info(dict, 기사 정보를 가진 딕셔너리)
    '''
    article_info = dict()
    article_info['title'] = soup.find('strong', {"class" : "tit"}).text
    article_info['article_url'] = 'https:' + soup.find('a', {"class" : "lt1"}).attrs['href']
    article_info['upload_date'] = re.sub('[\t\n]', '', soup.find('span', {"class" : "medium"}).text[4 :])
    article_info['company'] = re.sub('[\t\n]', '', soup.find('span', {"class" : "medium"}).text[:4])

    return article_info


def make_DF(all_article_info) :
    '''
    수집된 기사 정보를 저장하는 데이터프레임 메소드
    :param all_article_info(list, (기사 내용을 제외한) 모든 기사 정보를 저장하고 있는 리스트)
    :return: dataframe
    '''
    cols = ['article_url', 'company', 'upload_date', 'title']

    dataframe = pd.DataFrame(all_article_info)

    dataframe = dataframe[cols]

    return dataframe


def get_save_article_content(date_range, dataframe) :
    '''
    기사 url에 접근하여 기사 내용을 수집하고 데이터 프레임에 업데이트 후 저장하는 메소드
    :param date_range(list, 날짜)
    :param dataframe
    :return: dataframe(with. csv file)
    '''
    dataframe['content'] = ''

    for i in range(0, len(dataframe)) :
        req = requests.get(dataframe['article_url'][i])
        soup = BeautifulSoup(req.text, 'html.parser')

        is_valid = True if soup.find('div', {'id' : 'realArtcContents'}) else False

        if is_valid :
            dataframe['content'][i] = re.sub("\n|\t", '', soup.find('div', {'id' : 'realArtcContents'}).text)
        else :
            dataframe['content'][i] = ''

    dataframe.to_csv('{0}_{1}.csv'.format(date_range[0], date_range[-1]), index=False)

    return dataframe


def run_step() :
    '''
    모든 메소드들을 실행시키는 메소드
    :return: dataframe(with. csv file)
    '''
    cpList = get_company_info()
    date_range = make_date_range()
    total_page_num = get_total_page_num(cpList, date_range)
    all_page_url = make_all_page_url(total_page_num)
    all_article_info = find_article_info(all_page_url)
    dataframe = make_DF(all_article_info)
    dataframe = get_save_article_content(date_range, dataframe)

    return dataframe