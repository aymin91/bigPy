#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import module.s1_collect.blog.bl_nv.nv_blog_post_crawler as nv_crawler
import module.s1_collect.blog.bl_dm.dm_blog_post_crawler as dm_crawler
import module.s1_collect.blog.bl_eg.eg_blog_post_crawler as eg_crawler
import module.s1_collect.blog.bl_br.br_blog_post_crawler as br_crawler
import module.s1_collect.blog.bl_ts.ti_blog_post_crawler as ti_crawler
import module.s1_collect.comm.util as util


def run_blog_post_crawler(*blog_type) :
    '''
    블로그 타입에 따라 맞는 blog_post_crawler를 실행시켜주는 메소드
    :param  : blog_type(tuple)
               latest_post_num,
              blogger_id,
              start_date,
              end_date,
              last_post_num=1
    :return : None
    '''

    for bl_type in blog_type :

        if bl_type.upper() == 'ALL' :
            try:
                nv_crawler.run_step()
                print('NV blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                
            try:
                dm_crawler.run_step(blogger_id, start_date, end_date)
                print('DM blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                
            try:
                eg_crawler.run_step(blogger_id, start_date, end_date)
                print('EG blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                
            try:
                br_crawler.run_step(latest_post_num, blogger_id, start_date, end_date, last_post_num=1)
                print('BR blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                
            try:
                ti_crawler.run_step(latest_post_num, blogger_id, start_date, end_date, last_post_num=1)
                print('TI blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
            
            print('All Blog Post Crawlers are done..')

        elif bl_type.upper() == 'NV' :
            try:
                nv_crawler.run_step()
                print('NV blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())

        elif bl_type.upper() == 'DM' :
            try:
                dm_crawler.run_step(blogger_id, start_date, end_date)
                print('DM blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                
        elif bl_type.upper() == 'EG' :
            try:
                eg_crawler.run_step(blogger_id, start_date, end_date)
                print('EG blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                
        elif bl_type.upper() == 'BR' :
            try:
                br_crawler.run_step(latest_post_num, blogger_id, start_date, end_date, last_post_num=1)
                print('BR blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
                
        elif bl_type.upper() == 'TI' :
            try:
                ti_crawler.run_step(latest_post_num, blogger_id, start_date, end_date, last_post_num=1)
                print('TI blog post Crawler is done..')
            except Exception as e: 
                error_type = str(e.with_traceback).split(' ')[4]
                util.make_error_log_message(error_type, bl_type.upper())
    return None

