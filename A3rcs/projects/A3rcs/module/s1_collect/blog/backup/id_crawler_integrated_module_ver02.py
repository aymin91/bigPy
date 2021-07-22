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
import module.s1_collect.blog.bl_ts.ti_user_id_crawler as ti_crawler


def run_id_crawler(*blog_type) :
    '''
        블로그 타입에 따라 맞는 user_id_crawler를 실행시켜주는 메소드
        :param  : blog_type(tuple)
        :return : None
    '''

    for bl_type in blog_type :

        if bl_type.upper() == 'ALL' :
            nv_crawler.run_step()
            dm_crawler.run_step()
            eg_crawler.run_step()
            br_crawler.run_step()
            ti_crawler.run_step()
            print('All User Id Crawlers are done..')

        elif bl_type.upper() == 'NV' :
            nv_crawler.run_step()
            print('NV User Id Crawler is done..')

        elif bl_type.upper() == 'DM' :
            dm_crawler.run_step()
            print('DM User Id Crawler is done..')

        elif bl_type.upper() == 'EG' :
            eg_crawler.run_step()
            print('EG User Id Crawler is done..')

        elif bl_type.upper() == 'BR' :
            br_crawler.run_step()
            print('BR User Id Crawler is done..')

        elif bl_type.upper() == 'TI' :
            ti_crawler.run_step()
            print('TI User Id Crawler is done..')

    return None
