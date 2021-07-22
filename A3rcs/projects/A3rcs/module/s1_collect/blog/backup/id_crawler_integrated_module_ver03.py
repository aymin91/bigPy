# Project : AI-based Auto Analysis Report Creating System
# History :
#   2019.11.13
#       - import path is changed by MAY
#       - module is made by May
#


import module.s1_collect.blog.bl_nv.nv_user_id_crawler as nv_crawler
import module.s1_collect.blog.bl_dm.dm_user_id_crawler as dm_crawler
import module.s1_collect.blog.bl_eg.eg_user_id_crawler as eg_crawler
import module.s1_collect.blog.bl_br.br_user_id_crawler as br_crawler
import module.s1_collect.blog.bl_ti.ti_user_id_crawler as ti_crawler
import module.s1_collect.comm.util as util


def run_id_crawler(*blog_type) :
    '''
        블로그 타입에 따라 맞는 user_id_crawler를 실행시켜주는 메소드
        :param  : blog_type(tuple)
        :return : None
    '''
    if str(blog_type).upper() == 'all' or str(blog_type).upper() == '':
        blog_type = ['nv','dm','eg','br','ti']

    for bl_type in blog_type :

        if bl_type.upper() == 'NV' :
            try :
                nv_crawler.run_step()
                print('NV User Id Crawler is done..')
            except Exception as e:
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                continue

        elif bl_type.upper() == 'DM' :
            try:
                dm_crawler.run_step()
                print('DM User Id Crawler is done..')
            except Exception as e:
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                continue

        elif bl_type.upper() == 'EG' :
            try:
                eg_crawler.run_step()
                print('EG User Id Crawler is done..')
            except Exception as e:
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                continue

        elif bl_type.upper() == 'BR' :
            try:
                br_crawler.run_step()
                print('BR User Id Crawler is done..')
            except Exception as e:
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                continue

        elif bl_type.upper() == 'TI' :
            try:
                ti_crawler.run_step()
                print('TI User Id Crawler is done..')
            except Exception as e:
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                continue

    return None

