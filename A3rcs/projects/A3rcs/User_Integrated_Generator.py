from module.s1_collect.blog.bl_nv import nv_user_id_crawler as NV_crawler
from module.s1_collect.blog.bl_dm import dm_user_id_crawler as DM_crawler
from module.s1_collect.blog.bl_eg import eg_user_id_crawler as EG_crawler
from module.s1_collect.blog.bl_ti import ti_user_id_crawler as TI_crawler
from module.s1_collect.blog.bl_br import br_user_id_crawler as BR_crawler


def main():

    NV_crawler.main()
    DM_crawler.main()
    EG_crawler.main()
    TI_crawler.main()
    BR_crawler.main()

    return None


if __name__ == '__main__':
    main()
