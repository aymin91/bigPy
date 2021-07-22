# Project : AI-based Auto Analysis Report Creating System
# History :
#       2019.10.24
#        - 아직 tistory, egloos url을 mobile url로 바꾸는 함수는 추가되지 않았습니다. by MAY

import re

NAVER_BASE = 'https://blog.naver.com/'
DAUM_BASE = 'http://blog.daum.net/'
TISTORY_BASE = 'https://www.tistory.com/'
EGLOOS_BASE = 'http://www.egloos.com/'
BRUNCH_BASE = 'https://brunch.co.kr/'


def make_mobile_board_url(dataframe) :
    '''
        web 블로그 주소를 mobile 블로그 주소로 변환시켜주는 메소드
        :param  : dataframe(blod_type, blogger_id, post_num, key 칼럼이 채워져 있는 데이터프레임)
        :return : mb_board_url_list(list)
    '''
    mb_board_url_list = list()
    for i in range(0, len(dataframe)) :
        if dataframe['board_url'][i].split('.')[1] == 'naver' :
            mb_board_url_list.append(re.sub('https://', 'https://m.', NAVER_BASE) + dataframe['blogger_id'][0] + '/' + dataframe['post_num'][
                i])
            # print(mb_board_url)

        elif dataframe['board_url'][i].split('.')[1] == 'daum' :
            mb_board_url_list.append(re.sub('http://', 'http://m.', DAUM_BASE) + dataframe['blogger_id'][0] + '/' + dataframe['post_num'][i])
            # print(mb_board_url)

    #         elif dataframe['board_url'][i].split('.')[1] == 'tistory' :
    #             board_url = re.sub('com/', 'com/m/', TISTORY_BASE)'/'+dataframe['post_num'][i]

    #         elif dataframe['board_url'][i].split('.')[1] == 'egloos':
    #             board_url = re.sub('com/', 'com/m/', dataframe['board_url'][i])

    return mb_board_url_list