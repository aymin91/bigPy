from time import localtime
import time
import EG_Crawler_Generator as EG_crawler

weekdays = ['월', '화', '수', '목', '금', '토', '일']

while True:
    interval = 60
    t = localtime()

    # if t.tm_hour > 0 and t.tm_min > 0 and t.tm_sec%5==0:
    if t.tm_hour == 1 and t.tm_min == 0 and t.tm_sec == 0:
        msg = '{yy}.{mm}.{dd}({wd}) {hr}:{mi}:{se}'.format(
            yy=t.tm_year, mm=t.tm_mon, dd=t.tm_mday, wd=weekdays[t.tm_wday],
            hr=t.tm_hour, mi=t.tm_min, se=t.tm_sec
        )
        print(msg)
        print('Virtual Scheduler is running!!')
        # call crawler modude
        EG_crawler.main()
        print('Virtual Scheduler is finished!!')

    else:
        print('■', end='')

    time.sleep(interval)

print('Finish')