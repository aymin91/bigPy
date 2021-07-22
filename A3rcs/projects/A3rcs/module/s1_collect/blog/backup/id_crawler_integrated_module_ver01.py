# Project : AI-based Auto Analysis Report Creating System
# History :
#   2019.11.13
#       - import path is changed by MAY
#
#

import module.s1_collect.blog.bl_nv.nv_user_id_crawler as nv_crawler
import module.s1_collect.blog.bl_dm.dm_user_id_crawler as dm_crawler
import module.s1_collect.blog.bl_eg.eg_user_id_crawler as eg_crawler
import module.s1_collect.blog.bl_br.br_user_id_crawler as br_crawler


def main() :
    '''
        모든 id 크롤러를 실행시켜주는 메소드
        :param : None
        :return: nv_df(dataframe with.csv file), dm_df(dataframe with.csv file), br_df(dataframe with.csv file), eg_df(dataframe with.csv file)
    '''
    nv_driver = nv_crawler.go_blog_main()
    dm_driver = dm_crawler.go_blog_main()
    br_drver = br_crawler.go_blog_main()

    nv_blogger_info = nv_crawler.gather_blogger_info(nv_driver)
    dm_blogger_info = dm_crawler.gather_blogger_info(dm_driver)
    br_blogger_info = br_crawler.gather_blogger_info(br_drver)
    eg_blogger_info = eg_crawler.gather_blogger_info()

    nv_df = nv_crawler.make_save_df(nv_blogger_info)
    dm_df = dm_crawler.make_save_df(dm_blogger_info)
    br_df = br_crawler.make_save_df(br_blogger_info)
    eg_df = eg_crawler.make_save_df(eg_blogger_info)

    return nv_df, dm_df, br_df, eg_df
