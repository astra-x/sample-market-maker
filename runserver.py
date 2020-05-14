import sys, os
RootDir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RootDir)
import json
import time
from flask import Flask
from flask import request


app = Flask(__name__)

def run(mm,a_dic):
    from market_maker.utils import constants
    from market_maker.utils.log import logger
    from market_maker.market_maker_inner import OrderManager
    logger.info('Market Maker Version: %s\n' % constants.VERSION)
    # mm,l,r=args


    om = OrderManager(cycleTime=mm["CycleTime"],email=mm["Email"],password=mm["Password"])
    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        # 这边起线程去run_loop
        def  wait_exit_sign():
            while True:
                try:

                    if mm["CycleTime"] in a_dic:
                        exit_flag = a_dic.pop(mm["CycleTime"])
                        if exit_flag==0:
                            om.Exit_Flag = True
                            print("服务%s:"%(mm["CycleTime"]) ,exit_flag)
                except EOFError:  # 当管道的另一端l发送端 关闭时，管道的r端接收端就不需要再等着接收消息了
                    break
        t2 = threading.Thread(target=wait_exit_sign)
        t2.daemon = True
        t2.start()

        om.run_loop()


    except (KeyboardInterrupt, SystemExit):
        sys.exit()

if __name__=="__main__":
    from multiprocessing import Process,Manager
    import threading

    MarketMakers = [
        # 创建3s周期的market-maker服务
        {"CycleTime": 3, "Email": "youtao.xing@icloud.com", "Password": "1234!abcd","STATUS":1}, #"STATUS":1代表活着
                                                                                                         #0代表死了
        {"CycleTime": 5, "Email": "python_runzhang@163.com", "Password": "135246zr","STATUS":1},

        {"CycleTime": 7, "Email": "go_runzhang@163.com", "Password": "135246zr","STATUS":1},

        {"CycleTime": 9, "Email": "1263624209@qq.com", "Password": "135246zr","STATUS":1}


    ]

    # #第一步：起服务，将参数传入MM进程里，对setting配置进行重置
    p_dic ={}
    manager = Manager()
    a_dic = manager.dict()

    for mm in MarketMakers:
        # 这边开启子进程
        p=Process(target=run,args=(mm,a_dic,))
        p.start()
        p_dic[mm["CycleTime"]] = p

    # 开启线程去监视进程是否挂了，如果挂了就重启
    # -------------------------------------------------------
    def check_child_process_alive():

        while True:
            running_mm_list = []
            for pname,p in p_dic.items():
                if not p.is_alive():
                    for mm in  MarketMakers:
                       if mm["CycleTime"]==pname and  mm["STATUS"]:
                           p = Process(target=run, args=(mm,a_dic,))
                           p.start()
                           p_dic[mm["CycleTime"]] = p

                else:
                    print("------》》》当前运行的服务名为：%s,对应运行周期为%s"%(p.name,str(pname)))

                running_mm_list.append(pname)

            #这是新增mm机器人
            for mm in MarketMakers:
                if mm["CycleTime"] not in running_mm_list and  mm["STATUS"]:
                    p = Process(target=run, args=(mm,a_dic,))
                    p.start()
                    p_dic[mm["CycleTime"]] = p

            #todo 删减mm机器人

            time.sleep(3)
    t1 = threading.Thread(target=check_child_process_alive)
    t1.daemon=True
    t1.start()



    # --------------------------------------------------------

    @app.route('/reset_config',methods=["POST"])
    def reset_config():
        data=request.json
        if data==None:
            return "配置参数有问题"
        with open("settings.json", "r", encoding='utf-8')  as f:
            config = json.load(f)
            for k in data:
                if k not in config:
                    return "配置参数有问题"
            config.update(data)
        with open("settings.json", "w", encoding='utf-8')  as f:
            json.dump(config, f)
        for pname in p_dic:
            a_dic[pname]=0


        return "ok"





if __name__ == '__main__':


    app.run(host='0.0.0.0',port=5000)
