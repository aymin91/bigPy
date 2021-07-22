# Project : AI-based Auto Analysis Report Creating System
# History :
#   2019.11.15
#       - def convert_mobile_url is changed by MAY
#         (add def ti/dm_convert_mobile_url are added)
#       - new modules : ti_convert_mobile_url/dm_convert_mobile_url
#
#   2019.11.19
#       - def dm_convert_mobile_url : BASE_URL variable is appended by MAY
#       - def regex_convert_date : else section is changed by MAY (dot/slash/dash_match valid are appended)
#
#
#       - new modules : get_root_dir, get_webdriver_path,
#                       get_blog_mgr, get_file_dir,
#                       get_blog_code, get_post_url, get_user_url, get_valid
#                       get_user_dir, get_post_dir, get_log_dir
#
#
import logging
import logging.handlers
import os
import re
import datetime
import json
import platform
import glob
import pandas as pd


def regex_convert_date(upload_date):
    '''
        수집된 날짜를 'YYYYMMDD'형식에 맞춰 변환시켜주는 메소드
        :param  : upload_date(str)
        :return : rgx_date(str)
    '''

    global rgx_date
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
        dot_match = '\d{4}[.]\d{1,2}[.]\d{1,2}'
        slash_match = '\d{4}[/]\d{1,2}[/]\d{1,2}'
        dash_match = '\d{4}[-]\d{1,2}[-]\d{1,2}'

        rgx_dot_match = re.search(dot_match, upload_date)
        rgx_slash_match = re.search(slash_match, upload_date)
        rgx_dash_match = re.search(dash_match, upload_date)

        if rgx_dot_match :

            year = rgx_dot_match.group().split('.')[0]
            month = rgx_dot_match.group().split('.')[1]
            day = rgx_dot_match.group().split('.')[2]

            if len(rgx_dot_match.group().split('.')[1]) != 2 :
                month = '0' + str(rgx_dot_match.group().split('.')[1])

            if len(rgx_dot_match.group().split('.')[2]) != 2 :
                day = '0' + rgx_dot_match.group().split('.')[2]

            rgx_date = year + month + day

        if rgx_slash_match :

            year = rgx_slash_match.group().split('/')[0]
            month = rgx_slash_match.group().split('/')[1]
            day = rgx_slash_match.group().split('/')[2]

            if len(rgx_slash_match.group().split('/')[1]) != 2 :
                month = '0' + str(rgx_slash_match.group().split('/')[1])

            if len(rgx_slash_match.group().split('/')[2]) != 2 :
                day = '0' + rgx_slash_match.group().split('/')[2]

            rgx_date = year + month + day

        if rgx_dash_match :

            year = rgx_dash_match.group().split('-')[0]
            month = rgx_dash_match.group().split('-')[1]
            day = rgx_dash_match.group().split('-')[2]

            if len(rgx_dash_match.group().split('-')[1]) != 2 :
                month = '0' + str(rgx_dash_match.group().split('-')[1])

            if len(rgx_dash_match.group().split('-')[2]) != 2 :
                day = '0' + rgx_dash_match.group().split('-')[2]

            rgx_date = year + month + day

    return rgx_date

def datetime_fmt(date) :
    '''
    날짜정보를 YYYYMMDDHHmmW(13자리수)로 변환시켜주는 메소드
        YYYY : 년도
        MM   : 월
        DD   : 일
        HH   : 시
        mm   : 분
        W    : 요일(0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일)
    :param  : date(str)
    :return : date_fmt(str, YYYYMMDDHHmmW(13자리수))
    '''

    first_format_time = '\d+시간전'
    first_format_day = '\d+일전'

    if re.search(first_format_time, date) :

        now = datetime.datetime.now().strftime("%Y%m%d%H%M%w")

        minus_time = int(now[8:10]) - int(date[:-3])

        if minus_time < 0:
            re_date = str(int(now[:8]) - 1)
            re_time = str(24 + minus_time)
            date_fmt = re_date + re_time + now[10:]

        else :
            date_fmt = now[:8] + str(minus_time) + now[10:]

    elif re.search(first_format_day, date) :
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%w")

        minus_date = int(now[:8]) - int(date[:-2])

        date_fmt = str(minus_date) + now[8:]

    else :
        re_date = regex_convert_date(date)

        if len(re.sub('[^0-9]', '', date.split(' ')[-1])) < 4:

            re_time = '0' + re.sub('[^0-9]', '', date.split(' ')[-1])
            date_fmt = re_date + re_time

        else:
            date_fmt = re_date + re.sub('[^0-9]', '', date.split(' ')[-1])

        date_fmt = date_fmt + get_weekday(date_fmt)

    return date_fmt

def get_weekday(date):
    '''
    날짜를 입력받아 요일을 구해주는 메소드
    :param  : date(str)
    :return : weekday(str)
    '''
    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:8])
    calcul_date = datetime.date(year, month, day)
    weekday = str(calcul_date.weekday())

    return weekday

def check_is_valid_date(start_date, end_date, upload_date):
    '''
        게시물 날짜가 유효 날짜 범위에 드는지 유효 검사를 해주는 메소드
        :param  : start_date(str), end_date(str), upload_date(str)
        :return : valid_result(boolean)
    '''
    start_rgx = int(upload_date) - int(start_date)
    end_rgx = int(end_date) - int(upload_date)

    valid_result = int()

    if start_rgx >= 0 and end_rgx >= 0 :
        valid_result = True

    elif start_rgx < 0 or end_rgx < 0 :
        valid_result = False

    return valid_result


def log_info_fmt() :
    '''
    로그 메세지의 포멧을 지정해주는 메소드
    :return: formatter(log msg format)
    '''
    log_msg = ''
    log_head = 'time : %(asctime)s [%(levelname)s]\n'
    # log_info = 'filename : %(filename)s\n'
    # log_info += 'module_name : %(module)s\n'
    # log_info += 'func_name : %(funcName)s\nline : %(lineno)d\n'
    log_info = 'message : %(message)s'
    time_format = '%Y-%m-%d %H:%M:%S'
    log_msg = log_head + log_info
    formatter = logging.Formatter(log_msg, time_format)

    return formatter

def log_error_fmt() :
    '''
    로그 메세지의 포멧을 지정해주는 메소드
    :return: formatter(log msg format)
    '''
    log_msg = ''
    log_head = 'time : %(asctime)s [%(levelname)s]\n'
    log_info = 'filename : %(filename)s\n'
    log_info += 'module_name : %(module)s\n'
    log_info += 'func_name : %(funcName)s\nline : %(lineno)d\n'
    log_info += 'message : %(message)s'
    time_format = '%Y-%m-%d %H:%M:%S'
    log_msg = log_head + log_info
    formatter = logging.Formatter(log_msg, time_format)

    return formatter


def log_path(blog_code) :
    '''
    로그 메세지가 저장되는 파일 디렉토리를 만들어주는 메소드
    :param   : blog_code(str)
    :return  : folder_path(log file directory)
    '''
    root_dir = get_root_dir()
    log_dir = get_log_dir(get_file_dir())

    total_path = root_dir + log_dir
    folder_path = '/'.join(total_path.split('/')[:-1]).format(blog_code=blog_code)
    create_file_dir(folder_path)

    return folder_path


def get_logger() :
    '''
    로거를 실행시키는 메소드
    :return: logger(패키지 api)
    '''
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    return logger


def info_msg(message, blog_code) :
    '''
    단계가 완료되는 것을 알려주는 info msg 로그를 저장하는 메소드
    :param  : message(저장할 로그 메세지), blog_code(str)
    :return : is_info(T/F)
    '''
    logger = get_logger()

    formatter = log_info_fmt()
    folder_path = log_path(blog_code)
    log_date = get_today_day()

    info_handler = logging.FileHandler(folder_path + '/{yyyymmdd}_logs.log'.format(yyyymmdd=log_date))
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    logger.addHandler(info_handler)
    logger.info('BLOG_CODE='+blog_code+', '+message + '\n')

    logger.propagate = False
    info_handler.propagate = False
    print('info를 남깁니다')
    logger.removeHandler(info_handler)
    is_info = True

    return is_info


def error_msg(message, blog_code) :
    '''
    단계에서 에러난 것을 알려주는 error msg 로그를 저장하는 메소드
    :param  : message(저장할 로그 메세지), blog_code(str)
    :return : is_error(T/F)
    '''
    logger = get_logger()

    formatter = log_error_fmt()
    folder_path = log_path(blog_code)

    log_date = get_today_day()

    error_handler = logging.FileHandler(folder_path + '/{yyyymmdd}_logs.log'.format(yyyymmdd=log_date))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(error_handler)
    logger.propagate = False
    error_handler.propagate = False

    logger.exception('BLOG_CODE='+blog_code+', '+message + '\n')

    print('error 발견 로그를 남깁니다')
    is_error = True
    logger.removeHandler(error_handler)
    return is_error


def make_log_message(message, blog_code) :
    '''
        메세지를 받아 info/error log 메세지를 생성하는 메소드
        :param  : message(str, the name of error), blog_type(str, the type of blog)
        :return : none
    '''

    if 'Error' not in message :
        info_msg(message, blog_code)

    else :
        error_msg(message, blog_code)

    return None

def create_file_dir(directory):
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

def convert_mobile_url(blog_type, *post_url, **user_id):
    '''
        게시글 url을 모바일 형태로 변환해 리스트로 반환하는 메소드
        :param  : blog_type(str),  post_url(input:str, output:tuple), blogger_id(input:str, output:dict)
        :return : result(str, mobile url)
    '''
    if blog_type == 'TI':
        result = ti_convert_mobile_url(post_url[0])

    elif blog_type == 'DM':
        result = dm_convert_mobile_url(post_url[0],  user_id['user_id'])

    return result


def ti_convert_mobile_url(post_url) :
    '''
        게시글 url을 모바일 형태로 변환해주는 메소드
        :param  : post_url(str)
        :return : m_post_url(str, mobile_url)
    '''
    loc_m = post_url.find('m/')
    m_post_url = post_url[:loc_m] + 'm/' + post_url[loc_m :]

    return m_post_url


def dm_convert_mobile_url(post_url, user_id) :
    '''
        게시글 url을 모바일 형태로 변환해주는 메소드
        param  : blogger_id(str), post_url(str)
        return : m_post_url(str)
    '''
    BASE_URL = 'http://blog.daum.net/'
    pattern = re.compile('articleno=\w+')

    reg_post_num = pattern.search(post_url)
    post_num = reg_post_num.group().split('=')[1]

    m_post_url = re.sub('http://', 'http://m.', BASE_URL) + user_id + '/' + post_num

    return m_post_url


# def get_root_dir():
#     '''
#     루트 디렉토리('stg_server) 경로를 가져오는 메소드
#     :return dir_path(str)
#     '''
#     paths = os.getcwd()
#     if platform.system() == 'Windows':  # MacOS
#         paths = paths.replace('\\', '/')
#     st_idx = paths.find('module')
#     root_dir = paths[:st_idx+1]
#
#
#     print('chk: paths = {}, st_idx = {}, root_dir = {} '.format(paths, st_idx, root_dir))
#
#     return root_dir
#
# def get_root_dir():
#     '''
#     루트 디렉토리('stg_server) 경로를 가져오는 메소드
#     :return dir_path(str)
#     '''
#     paths = os.getcwd()
#     if platform.system() == 'Windows':
#         paths = paths.replace('\\', '/')
#
#     root_dir = paths + '/'
#     #print('chk: paths = {}, st_idx = {}, root_dir = {} '.format(paths, st_idx, root_dir))
#     # print(root_dir)
#     return root_dir

def get_root_dir() :
    '''
    루트 디렉토리('stg_server) 경로를 가져오는 메소드
    :return dir_path(str)
    '''
    paths = os.getcwd()

    if platform.system() == 'Windows' :
        paths = paths.replace('\\', '/')

    rt_pt = re.compile('module[/]')

    if rt_pt.search(paths):
        m_mt = rt_pt.search(paths)
        root_dir = paths[:m_mt.start()]

    else :
        root_dir = paths + '/'

    # print('chk: paths = {}, st_idx = {}, root_dir = {} '.format(paths, st_idx, root_dir))
    # print(root_dir)

    return root_dir



def get_webdriver_path():

    driver_path = ''
    root_dir = get_root_dir()
    if platform.system() == 'Windows' :
        driver_path = root_dir+'module/s1_collect/driver/chromedriver.exe'

    elif platform.system() == 'Darwin' :
        driver_path = root_dir+'module/s1_collect/driver/macos/chromedriver'

    elif platform.system() == 'Linux' :
        driver_path = root_dir+'module/s1_collect/driver/linux/chromedriver'

    else :
        print("It's unknown system. Hangul fonts are not supported!")

    return driver_path


##########  json config ################

def get_blog_mgr():
    '''
    'stg_server'를 루트 디렉토리로 하여
    s1_blog_mgr.json 파일을 읽어오는 메소드

    :return: blog_mgr(json)
    '''
    root_dir = get_root_dir()
    json_path = root_dir + 'config/s1_blog_mgr.json'
    # print(json_path)

    with open(json_path, 'r') as b_json:
        blog_mgr = json.load(b_json)

    return blog_mgr


def get_file_dir():
    '''
    'stg_server'를 루트 디렉토리로 하여
    s1_file_dir.json 파일을 읽어오는 메소드
    :return: file_dir(json
    '''
    root_dir = get_root_dir()
    json_path = root_dir +  'config/s1_file_dir.json'
    # print(json_path)

    with open(json_path, 'r') as f_json:
        file_dir = json.load(f_json)

    return file_dir

def get_state_mgr():
    '''
    'stg_server'를 루트 디렉토리로 하여
    s1_state_mgr.json 파일을 읽어오는 메소드

    :return: state_mgr(json)
    '''
    root_dir = get_root_dir()
    json_path = root_dir + '/repository/state/s1_state_mgr.json'

    with open(json_path, 'r') as b_json:
        state_mgr = json.load(b_json)

    return state_mgr


def get_blog_code(blog_name):
    '''
    blog_mgr json에서 블로그 코드를 가져오는 메소드

    :param blog_code(str)
    :return: Blog_Code(str)
    '''
    blog_code = ''
    blog_mgr = get_blog_mgr()

    for bc in blog_mgr:
        if bc['blog_name'] == blog_name.upper():
            blog_code = bc['blog_code']

    return blog_code


def get_post_url(blog_code):
    '''
    blog_mgr json에서 해당 블로그의 blog_post 크롤러의
    base_url을 가져오는 메소드

    :param blog_code(str)
    :return: Post_Url(str)
    '''
    post_url = ''
    blog_mgr = get_blog_mgr()

    for pu in blog_mgr:
        if pu['blog_code'] == blog_code.upper():
            post_url = pu['post_base_url']

    return post_url


def get_user_url(blog_code):
    '''
    blog_mgr json에서 해당 블로그의 user id 크롤러의
    base_url을 가져오는 메소드
    :param blog_mgr(json)
    :param blog_code(str)
    :return: User_Url(str)
    '''
    user_url = ''
    blog_mgr = get_blog_mgr()

    for uu in blog_mgr:
        if uu['blog_code'] == blog_code.upper():
            user_url = uu['user_base_url']

    return user_url


def get_valid( blog_code):
    '''
    blog_mgr json에서 해당 블로그의 Valid를 가져와서
    True, False를 구분하는 메소드

    :param blog_mgr(json)
    :param blog_code(str)
    :return: Valid(bloon)
    '''
    valid = ''
    blog_mgr = get_blog_mgr()

    for val in blog_mgr:
        if val['blog_code'] == blog_code.upper():
            valid = val['blog_vaild']

    return valid


def get_user_dir(file_dir):
    '''
    file_dir json에서 user id 크롤러 저장 경로를 가져오는 메소드

    :param file_dir(json)
    :return: UserDir(str)
    '''
    user_dir = file_dir['user_id_dir']

    return user_dir


def get_post_dir(file_dir):
    '''
    file_dir json에서 blog post 크롤러 저장 경로를 가져오는 메소드

    :param file_dir(json)
    :return: UserDir(str)
    '''
    post_dir = file_dir['post_dir']

    return post_dir


def get_log_dir(file_dir):
    '''
    file_dir json에서 log 저장 경로를 가져오는 메소드

    :param file_dir(json)
    :return: UserDir(str)
    '''
    log_dir = file_dir['log_dir']

    return log_dir

def get_pblog_id_dir(file_dir):
    '''
    file_dir json에서 log 저장 경로를 가져오는 메소드

    :param file_dir(json)
    :return: UserDir(str)
    '''
    pblog_id = file_dir['pblog_id_fmt']

    return pblog_id

def get_pblog_date_dir(file_dir):
    '''
    file_dir json에서 log 저장 경로를 가져오는 메소드

    :param file_dir(json)
    :return: UserDir(str)
    '''
    pblog_date = file_dir['pblog_dt_fmt']

    return pblog_date

### 저장

def save_df2csv(dataframe, full_path):
    '''
    블로그 포스트 크롤러 dataframe과 저장 경로 full_path를 받아
    저장 경로 폴더 유무 확인하고 없으면 만들고 있으면 그대로 저장

    :param dataframe(df)
    :param full_path(str)
    :return: is_saved(bloon)
    '''
    is_saved = False

    blog_codes = ['NV', 'DM', 'TI', 'EG', 'BR']

    codes = [bc for bc in blog_codes if bc in full_path]
    blog_code = codes[0]

    try:
        # print('full_path :', full_path)
        folder_path = '/'.join(full_path.split('/')[:-1])
        # print('folder_path : ', folder_path)
        create_file_dir(folder_path)

        # if not os.path.exists(folder_path):
        #     os.makedirs(folder_path)

        dataframe.to_csv(full_path, index=False, encoding = 'utf-8')
        is_saved = True

    except Exception as e:

        error_type = str(e.with_traceback).split(' ')[4]
        make_log_message(error_type, blog_code)
        is_saved = False

    return is_saved


def save_state_mgr(state_mgr):
    '''
    'stg_server'를 루트 디렉토리로 하여
    s1_state_mgr.json 파일을 저장하는 메소드

    :return: state_mgr(json)
    '''
    root_dir = get_root_dir()
    json_path = root_dir + 'config/s1_state_mgr.json'
    # print(json_path)

    with open(json_path, 'w') as b_json:
        json.dump(state_mgr, b_json )

    return None

####날짜

def get_today_year():
    today = datetime.datetime.now()
    year = today.year

    return year


def get_today_day():
    today = datetime.datetime.now()
    day = today.strftime('%Y%m%d')

    return day


def chk_processing_time(start_time, end_time):
    process_time = end_time - start_time
    p_time = int(process_time)
    p_min, p_sec = divmod(p_time, 60)
    p_hour, p_min = divmod(p_min, 60)
    # time_message = ('processing time [ {p_hour}시간 : {p_min}분 : {p_sec}초 ] '.format(
    #                             p_hour = p_hour, p_min = p_min, p_sec = p_sec ))

    return p_hour, p_min, p_sec

#### crawler state

def update_state(c_date, blog_code, crawler_success, is_cct_success):
    state_mgr = get_state_mgr()
    # today = get_today_day()

    if crawler_success and is_cct_success:
        state = "TT"
    elif crawler_success == True or is_cct_success == False:
        state = "TF"
    elif crawler_success == False or is_cct_success == True:
        state = "FT"
    else:
        state = "FF"

    if c_date not in state_mgr:
        state_mgr[c_date] = {}
        state_mgr[c_date][blog_code] = state

    else:
        state_mgr[c_date][blog_code] = state

    save_state_mgr(state_mgr)

    return state_mgr