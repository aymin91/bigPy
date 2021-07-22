from module.s1_collect.blog.bl_br import br_blog_post_crawler as br_crawler
from module.s1_collect.comm import util

import pandas as pd
import datetime
import time

import os
import glob

BLOG_NAME   = "BRUNCH"
BLOG_CODE   = util.get_blog_code(BLOG_NAME)
dates       = datetime.datetime.now()

root_dir    = util.get_root_dir()
file_dir    = util.get_file_dir()

id_path     = root_dir + util.get_user_dir(file_dir)
rep_dir     = root_dir + util.get_pblog_id_dir(file_dir)
folder_path = '/'.join(rep_dir.split('/')[:-1]).format(yyyy=dates.year, blog_code=BLOG_CODE,
                                                       yyyymmdd=dates.strftime('%Y%m%d'))

id_list = pd.read_csv(id_path+'BR_ID_List.csv', encoding = 'cp949')
id_list = id_list.to_dict(orient='record')


def valid(BLOG_CODE):
    is_valid = util.get_valid(BLOG_CODE)

    return  is_valid

def generate_br_crawler(id_list, start_date, end_date) :
    try :
        print("Blog code : ", BLOG_CODE, '// Number of User id : ', len(id_list))
        for user_info in id_list:
            start_time = time.time()

            full_path = rep_dir.format(yyyy=dates.year, blog_code=BLOG_CODE, yyyymmdd=dates.strftime('%Y%m%d'),
                                       user_id=user_info['user_id'])

            blog_url = br_crawler.get_blog_url(user_info['user_id'])
            all_content_info = br_crawler.gather_all_content(blog_url, start_date, end_date,
                                                             user_info['newest_post_num'], oldest_post_num=1)
            br_crawler.make_blog_DF(all_content_info, user_info['user_id'], full_path)

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
        error_message = str(e.with_traceback).split(' ')[4] + str(e)
        util.make_log_message(error_message, BLOG_CODE.upper())
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

        pblog_date_path = root_dir + util.get_pblog_date_dir(file_dir).format(yyyy=dates.year, blog_code=BLOG_CODE,
                                                                              yyyymmdd=dates.strftime('%Y%m%d'))

        util.save_df2csv(result, pblog_date_path)

        is_success = True

    except Exception as e :
        error_message = str(e.with_traceback).split(' ')[4] + str(e)
        util.make_log_message(error_message, BLOG_CODE.upper())
        is_success = False

    return result, is_success

def main(start_date=None, end_date=None):
    concat_result = pd.DataFrame()

    if start_date is None:
        start_date = '19000101'

    if end_date is None:               # is None
        end_date = util.get_today_day()


    is_valid = valid(BLOG_CODE)
    if is_valid:
        start_time = time.time()
        print(BLOG_CODE, " crawler is now crawling...")
        try:

            crawler_success = generate_br_crawler(id_list, start_date, end_date)

        except Exception as e:
            error_message = str(e.with_traceback).split(' ')[4] + str(e)
            util.make_log_message(error_message, BLOG_CODE.upper())

        try:
            concat_result, is_cct_success = concat_post_date(folder_path)
        except Exception as e:
            error_message = str(e.with_traceback).split(' ')[4] + str(e)
            util.make_log_message(error_message, BLOG_CODE.upper())

        end_time = time.time()
        p_hour, p_min, p_sec = util.chk_processing_time(start_time, end_time)
        print('processing_time : {p_hour}:{p_min}:{p_sec}'.format(p_hour=p_hour,p_min=p_min,p_sec=p_sec))

        log_message = 'Crawling Completed  [ number_of_user_id={number_of_user_id}, number_of__all_posts={n_of_all_posts}, processing_time={p_hour}:{p_min}:{p_sec}]'.format(

            number_of_user_id=len(id_list),
            n_of_all_posts=len(concat_result),
            p_hour=p_hour,
            p_min=p_min,
            p_sec=p_sec)

        util.make_log_message(log_message, BLOG_CODE.upper())
        util.update_state(dates.strftime('%Y%m%d'), BLOG_CODE, crawler_success, is_cct_success)


        is_success = True
    else:
        print(BLOG_CODE, " crawler 'Valid' is False. Run next crawler")
        is_success = False

    return is_success


if __name__ == '__main__':
            main()

