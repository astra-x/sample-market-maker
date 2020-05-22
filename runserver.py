import os,time
import numpy as np
import settings
import utils
from flask import Flask
from threading import Thread




app = Flask(__name__)


# 第一步：读取filename.npy数据

# 注意：生成多个filename.npy  以时间戳方式  1233233222-134334334.npy


# 第二步：每秒放置一个数据出来

# 注意：这边要实时保存截取后的数据，因为为了记录数据读取到什么位置了，防止服务停了重启后还能接上


# 第三步：如果有请求过来将放置的数据取出返回给请求方


@app.route('/get_current_price')
def index():
    return {'current_price':current_price}


# 用一个单独的线程去检测当前时间是否过了一半开始生成第二份数据

def generate_next_data():

    while True:
        now_time = int(time.time())

        filename=utils.get_current_load_filename(now_time)
        filename_no_ext, ext = os.path.splitext(filename)
        filename_period = filename_no_ext.split("-")
        filename_period_l = list(map(int, filename_period))

        if now_time>(filename_period_l[0]+filename_period_l[1])/2:
            file_path=os.path.join(settings.DataDir,filename)
            price_array = np.load(file_path)
            final_price = price_array[-1][0]
            utils.make_price(current_time=filename_period_l[1]+1,S0=final_price)

        time.sleep(10)



current_price = 500

file_cache={}

def loop_set_current_price():
    while True:
        # 判断读取哪个文件， 当前时间在哪个文件区间内
        # 当前时间在哪个文件的区间内，如果在该区间内，则当前时间减去开始时间就知道该从哪个位置开始读了
        now_time = int(time.time())
        filename = utils.get_current_load_filename(now_time)
        file_path=os.path.join(settings.DataDir,filename)

        if filename in file_cache:
            price_array=file_cache.get(filename)
        else:
            file_cache.clear()
            price_array = np.load(file_path)
            file_cache[filename]=price_array

        # 取价格
        filename_no_ext, ext = os.path.splitext(filename)
        filename_period = filename_no_ext.split("-")
        filename_period_l = list(map(int, filename_period))

        offset = now_time - filename_period_l[0]
        global current_price
        current_price = price_array[offset][0]

        time.sleep(1)
        print(current_price)



if __name__ == '__main__':
    t1 = Thread(target=generate_next_data)
    t1.daemon = True
    t1.start()

    t2 = Thread(target=loop_set_current_price)
    t2.daemon = True
    t2.start()

    app.run(host='0.0.0.0',port=6005)







