# -*- coding: utf-8 -*-
import sys, os
RootDir = os.path.dirname(os.path.abspath(__file__))
Market_Maker_Dir = os.path.join(RootDir,"market_maker")
sys.path.insert(0, RootDir)
sys.path.insert(0, Market_Maker_Dir)
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
                            om.Exit = True
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
    DRY_RUN=False

    MarketMakers = [
        # 创建1s周期的market-maker服务
        {"CycleTime": 1, "Email": "sdc_yuhu01@163.com", "Password": "123456yuhu","STATUS":1},
    ]

    # #第一步：起服务，将参数传入MM进程里，对setting配置进行重置
    p_dic ={}
    manager = Manager()
    a_dic = manager.dict()
    def check_is_DRY_RUN():
        while True:
            if not DRY_RUN:
                for mm in MarketMakers:
                    if mm["CycleTime"] in p_dic:
                        continue
                    # 这边开启子进程
                    p=Process(target=run,args=(mm,a_dic,))
                    p.start()
                    p_dic[mm["CycleTime"]] = p
            time.sleep(1)
    t = threading.Thread(target=check_is_DRY_RUN)
    t.daemon=True
    t.start()

    # 开启线程去监视进程是否挂了，如果挂了就重启
    # -------------------------------------------------------
    def check_child_process_alive():
        while True:
            for pname,p in p_dic.items():
                if not p.is_alive():
                    for mm in  MarketMakers:
                       if mm["CycleTime"]==pname and  mm["STATUS"] and not DRY_RUN:
                           p = Process(target=run, args=(mm,a_dic,))
                           p.start()
                           p_dic[mm["CycleTime"]] = p
                else:
                    print("------》》》当前运行的服务名为：%s,对应运行周期为%s"%(p.name,str(pname)))
            time.sleep(3)
    t1 = threading.Thread(target=check_child_process_alive)
    t1.daemon=True
    t1.start()

    # --------------------------------------------------------
    # 重置参数
    @app.route('/reset_config',methods=["POST"])
    def reset_config():
        data=request.json
        if data==None:
            return {"err_code":1,"err_msg":"配置参数未传"}
        settings_json_path = os.path.join(Market_Maker_Dir, "settings.json")
        with open(settings_json_path, "r", encoding='utf-8')  as f:
            config = json.load(f)
            for k in data:
                if k not in config:
                    return {"err_code":2,"err_msg":"配置参数有问题"}
            config.update(data)
        with open(settings_json_path, "w", encoding='utf-8')  as f:
            json.dump(config, f)
        for pname in p_dic:
            a_dic[pname]=0

        return {"err_code":0,"err_msg":"ok"}

    # 获取配置参数
    @app.route('/get_config',methods=["GET"])
    def get_config():
        settings_json_path = os.path.join(Market_Maker_Dir, "settings.json")
        with open(settings_json_path, "r", encoding='utf-8')  as f:
            config = json.load(f)

        return config

    # 启动服务
    @app.route('/start',methods=["POST"])
    def start():
        global DRY_RUN
        DRY_RUN = False

        return {"err_code":0,"err_msg":"ok"}

    # 停止服务
    @app.route('/stop', methods=["POST"])
    def stop():
        # 设置DRY_RUN为True
        global DRY_RUN
        DRY_RUN=True
        # 将目前的task全停了
        for pname in p_dic:
            a_dic[pname]=0

        return {"err_code": 0, "err_msg": "ok"}


if __name__ == '__main__':

    app.run(port=5000)
