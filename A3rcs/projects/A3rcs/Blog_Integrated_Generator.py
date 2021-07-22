import NV_Crawler_Generator as NV_crawler
import DM_Crawler_Generator as DM_crawler
import EG_Crawler_Generator as EG_crawler
import TI_Crawler_Generator as TI_crawler
import BR_Crawler_Generator as BR_crawler

def main():
    NV_crawler.main()
    DM_crawler.main()
    EG_crawler.main()
    TI_crawler.main()
    BR_crawler.main()

    return None


if __name__ == '__main__':
    main()

