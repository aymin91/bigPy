# Project : AI-based Auto Analysis Report Creating System
# History :
#
#
#
#
#
#
#
import logging
import os
import re
import datetime


def regex_convert_date(upload_date):
    '''
    수집된 날짜를 'YYYYMMDD'형식에 맞춰 변환시켜주는 메소드
    :param  : upload_date(str)
    :return : rgx_date(str)
    '''

    upload_date = re.sub('\s+', '', upload_date)

    first_format_time = '\d+시간전'
    first_format_day  = '\d+일전'
    second_format     = '\w{3}\d{1,2}[.]\d{4}'

    if re.search(first_format_time, upload_date):
        # print('first_format_time is matched')
        rgx_date = datetime.datetime.now().strftime("%Y%m%d")

    elif re.search(first_format_day, upload_date):
        # print('first_format_day is matched')
        rgx_date = str(int(datetime.datetime.now().strftime("%Y%m%d")) - int(upload_date[:-2]))

    elif re.search(second_format, upload_date):
        # print('second_format is matched')
        months = {'Jan' : '01', 'Feb' : '02', 'Mar' : '03', 'Apr' : '04', 'May' : '05', 'Jun' : '06',
                  'Jul' : '07', 'Aug' : '08', 'Sep' : '09', 'Oct' : '10', 'Nov' : '11', 'Dec' : '12'}
        year = upload_date[6:]
        month = months[upload_date[:3]]
        day = upload_date[3:5]
        rgx_date = year + month + day

    else :
        # print('nothing matched')
        rgx_date = re.sub('[^0-9]+', '', upload_date)[:8]

    return rgx_date


def check_is_valid_date(start_date, end_date, upload_date):
    '''
        게시물 날짜가 유효 날짜 범위에 드는지 유효 검사를 해주는 메소드
        :param  : start_date(str), end_date(str), upload_date(str)
        :return : valid_result(boolean)
    '''
    start_rgx = int(start_date) - int(upload_date)
    rgx_end = int(upload_date) - int(end_date)

    print(start_rgx, rgx_end)

    if start_rgx >= 0 and rgx_end >= 0:
        valid_result = True

    elif start_rgx < 0 or rgx_end < 0:
        valid_result = False

    return valid_result


def make_error_log_message(error_type, blog_type):
    '''
    로그 메세지를 생성하는 메소드
    :param  : error_type(str, the name of error), blog_type(str, the type of blog)
    :return : None(log message file.log)
    '''
    path = './module/s1_collect/blog/log_message'
    create_log_folder(path)
    FORMAT = "%(asctime)-15s  %(levelname)s %(message)s"
    logging.basicConfig(filename=path+'/{0}_log_message.log'.format(blog_type.upper()), level=logging.ERROR, format=FORMAT)
    logging.exception(error_type + ' is occurred')

    return None


def create_log_folder(directory):
    '''
    file directory를 받아 file이 존재하면 경로를 새로 만들지 않고, 존재하지 않으면 경로를 새로 만들어 주는 메소드
    :param  : directory(file path)
    :return : None
    '''
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)


def convert_mobile_url(post_url):
    '''
    게시글 url을 모바일 형태로 변환해 리스트로 반환하는 메소드
    :param  : board_url_list(list)
    :return : m_board_url_list(list)
    '''
    loc_m = post_url.find('m/')
    m_post_url = post_url[:loc_m] + 'm/' + post_url[loc_m:]

    return m_post_url