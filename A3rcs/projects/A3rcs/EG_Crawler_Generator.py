from module.s1_collect.blog.bl_eg import eg_blog_post_crawler as eg_crawler
from module.s1_collect.comm import util

import pandas as pd
import datetime
import time

import os
import glob

BLOG_NAME = "EGLOOS"
BLOG_CODE = util.get_blog_code(BLOG_NAME)
dates = util.get_today_day()
collecting_day = str(int(dates) - 1)

root_dir = util.get_root_dir()
file_dir = util.get_file_dir()

id_path = root_dir + util.get_user_dir(file_dir)
rep_dir = root_dir + util.get_pblog_id_dir(file_dir)
folder_path = '/'.join(rep_dir.split('/')[:-1]).format(yyyy=dates[:4], blog_code=BLOG_CODE,
                                                       yyyymmdd=dates)

id_list = pd.read_csv(id_path + '{blog_code}_ID_List.csv'.format(blog_code=BLOG_CODE), engine='python', encoding = 'utf-8')
id_list = id_list.to_dict(orient='record')


def valid(BLOG_CODE) :
    is_valid = util.get_valid(BLOG_CODE)

    return is_valid


def generate_eg_crawler(user_info, start_date, end_date) :
    try :
        # print("Blog code : ", BLOG_CODE, '// Number of User id : ', len(id_list))

        start_time = time.time()

        full_path = rep_dir.format(yyyy=dates[:4], blog_code=BLOG_CODE, yyyymmdd=dates,
                                   user_id=user_info['user_id'])

        blog_url = eg_crawler.get_blog_url(user_info['user_id'])
        per_year_url_list = eg_crawler.get_per_year_url(blog_url)
        board_total_page_num = eg_crawler.get_board_total_num(blog_url)
        board_page_url_list = eg_crawler.make_board_page_url(per_year_url_list, board_total_page_num)
        board_url_list = eg_crawler.get_all_board_url(blog_url, board_page_url_list)

        all_content_info = eg_crawler.gather_all_content(board_url_list, start_date, end_date)

        eg_crawler.make_blog_DF(all_content_info, user_info['user_id'], full_path)

        end_time = time.time()
        p_hour, p_min, p_sec = util.chk_processing_time(start_time, end_time)

        log_message = 'user_id={user_id}, number_of_posts={n_of_posts}, processing_time={p_hour}:{p_min}:{p_sec}'.format(
            user_id=user_info['user_id'],
            n_of_posts=len(all_content_info),
            p_hour=p_hour,
            p_min=p_min,
            p_sec=p_sec)

        print(log_message)

        util.make_log_message(log_message, BLOG_CODE)

        is_success = True

    except Exception as e :
        error_msg = str(e.with_traceback).split(' ')[4] + str(e)

        log_message = 'user_id={user_id}, error_message={error_message}'.format(
            user_id=user_info['user_id'], error_message=error_msg)

        util.make_log_message(log_message, BLOG_CODE.upper())
        is_success = False

    return is_success


def concat_post_date(folder_path) :
    result = pd.DataFrame()

    try :
        csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

        dataframes = []

        for csv_file in csv_files :
            df = pd.read_csv(csv_file)
            dataframes.append(df)

        result = pd.concat(dataframes, ignore_index=True)

        pblog_date_path = root_dir + util.get_pblog_date_dir(file_dir).format(yyyy=dates[:4], blog_code=BLOG_CODE,
                                                                              yyyymmdd=dates)

        util.save_df2csv(result, pblog_date_path)

        is_success = True

    except Exception as e :
        error_message = str(e.with_traceback).split(' ')[4] + str(e)
        util.make_log_message(error_message, BLOG_CODE.upper())
        is_success = False

    return result, is_success


def main(id_list) :
    concat_result = pd.DataFrame()
    crawler_success = bool()
    is_cct_success = bool()
    is_success = bool()

    print("Blog code : ", BLOG_CODE, '// Number of User id : ', len(id_list))
    print(BLOG_CODE, " crawler is now crawling...")

    start_time = time.time()

    is_valid = valid(BLOG_CODE)

    if is_valid :
        for user_info in id_list:

            if user_info['collecting_date'] is ' ' :
                start_date = '19000101'
            else :
                start_date = user_info['collecting_date']

            end_date = collecting_day

            try :

                crawler_success = generate_eg_crawler(user_info, start_date, end_date)

            except Exception as e :
                error_message = str(e.with_traceback).split(' ')[4] + str(e)
                util.make_log_message(error_message, BLOG_CODE.upper())

        try :
            concat_result, is_cct_success = concat_post_date(folder_path)
        except Exception as e :
            error_message = str(e.with_traceback).split(' ')[4] + str(e)
            util.make_log_message(error_message, BLOG_CODE.upper())

        end_time = time.time()
        p_hour, p_min, p_sec = util.chk_processing_time(start_time, end_time)
        print('processing_time : {p_hour}:{p_min}:{p_sec}'.format(p_hour=p_hour, p_min=p_min, p_sec=p_sec))

        log_message = 'Crawling Completed  [ number_of_user_id={number_of_user_id}, number_of__all_posts={n_of_all_posts}, processing_time={p_hour}:{p_min}:{p_sec}]'.format(

            number_of_user_id=len(id_list),
            n_of_all_posts=len(concat_result),
            p_hour=p_hour,
            p_min=p_min,
            p_sec=p_sec)

        util.make_log_message(log_message, BLOG_CODE.upper())
        util.update_state(dates, BLOG_CODE, crawler_success, is_cct_success)

        is_success = True

    else :
        print(BLOG_CODE, " crawler 'Valid' is False. Run next crawler")
        is_success = False

    return is_success


if __name__ == '__main__' :
    main(id_list)

