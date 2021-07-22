# Project : AI-based Auto Analysis Report Creating System
# History :

import bpc.collect.crnv.test.nv41_blogger_id_crawler as nv_crawler
import bpc.collect.crnv.test.dm51_blogger_id_crawler as dm_crawler
import bpc.collect.crnv.test.br81_blogger_id_crawler as br_crawler
import bpc.collect.crnv.test.eg71_blogger_id_crawler as eg_crawler


def blogger_id_crawler_main() :
    # step 1
    nv_driver = nv_crawler.go_blog_main()
    dm_driver = dm_crawler.go_blog_main()
    br_drver = br_crawler.go_blog_main()

    # step 2
    nv_blogger_info = nv_crawler.gather_blogger_info(nv_driver)
    dm_blogger_info = dm_crawler.gather_blogger_info(dm_driver)
    br_blogger_info = br_crawler.gather_blogger_info(br_drver)
    eg_blogger_info = eg_crawler.gather_blogger_info()

    # step 3
    nv_crawler.make_save_df(nv_blogger_info)
    dm_crawler.make_save_df(dm_blogger_info)
    br_crawler.make_save_df(br_blogger_info)
    eg_crawler.make_save_df(eg_blogger_info)

    success = print('Crawling is Success')
    return success