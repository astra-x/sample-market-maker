import sys, os
RootDir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RootDir)

import time
from market_maker.utils import  constants
from market_maker.utils.log import logger
from market_maker.market_maker_inner import OrderManager
from market_maker import settings



def run(mm):
    logger.info('Market Maker Version: %s\n' % constants.VERSION)

    om = OrderManager(cycleTime=mm["CycleTime"],email=mm["Email"],password=mm["Password"])
    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        om.run_loop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

if __name__=="__main__":

    from multiprocessing import Process
    import threading



    # #第一步：起服务，将参数传入MM进程里，对setting配置进行重置
    p_dic ={}
    for mm in settings.MarketMakers:
        # 这边开启子进程
        p=Process(target=run,args=(mm,))
        p.start()
        p_dic[mm["CycleTime"]] = p

    # 开启线程去监视进程是否挂了，如果挂了就重启
    # -------------------------------------------------------
    def check_child_process_alive():
        while 1:
            for pname,p in p_dic.items():
                if not p.is_alive():
                    for mm in  settings.MarketMakers:
                       if mm["CycleTime"]==pname:
                           p.close()
                           p = Process(target=run, args=(mm,))
                           p.start()
                           p_dic[mm["CycleTime"]] = p

                else:
                    print("------》》》当前运行的服务名为：%s,对应运行周期为%s"%(p.name,str(pname)))
            time.sleep(3)
    t1 = threading.Thread(target=check_child_process_alive)
    t1.daemon=True
    t1.start()
    # --------------------------------------------------------

    for pname,p in p_dic.items():
        p.join()
    # OrderManager().restart()
    print('结束了')