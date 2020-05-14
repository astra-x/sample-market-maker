import math
import numpy as np
import os,time
import numpy.random as npr
import settings



def make_price(current_time=int(time.time()),S0=settings.S0):
    r = settings.R
    sigma = settings.Sigma
    T = settings.T
    # simulation loops
    I = settings.I
    # simulation interval
    M = settings.M
    # M = 60
    dt = T / M
    S = np.zeros((M + 1, I))
    S[0] = S0
    for t in range(1, M + 1):
        S[t] = S[t - 1] * np.exp((r - 0.5 * sigma ** 2) * dt +
                                 sigma * math.sqrt(dt) * npr.standard_normal(I))


    future_time = current_time + M
    filename = "{}-{}.npy".format(current_time, future_time)
    file_path=os.path.join(settings.DataDir,filename)
    np.save(file_path, S)
    return filename




def get_final_price(files_dic):
    filename = max(files_dic, key=lambda x: files_dic[x])

    file_path=os.path.join(settings.DataDir,filename)
    price_array = np.load(file_path)
    final_price = price_array[-1][0]

    return final_price


def get_current_load_filename(now_time):
    # 读取所有文件
    # {"filename1":[11222212,323332123],"filename2":[11222212,323332123],"filename3":[11222212,323332123]}
    #   比较一下该当前时间落在哪个文件时间区间内，如果落在该区间内则读取该文件


    filenames = os.listdir(settings.DataDir)
    # 过滤出csv结尾的
    filenames = [filename for filename in filenames if filename.endswith("npy")]
    files_dic_0 = {}
    if not filenames:
        filename = make_price()
        filenames=[filename]
    # 将文件按开始时间进行排序
    for filename in filenames:
        filename_no_ext, ext = os.path.splitext(filename)
        filename_period = filename_no_ext.split("-")
        filename_period_l = list(map(int, filename_period))
        files_dic_0[filename] = filename_period_l[0]

    filenames = sorted(files_dic_0.keys())

    files_dic_1 = {}
    for filename in filenames:
        filename_no_ext, ext = os.path.splitext(filename)
        filename_period = filename_no_ext.split("-")
        filename_period_l = list(map(int, filename_period))
        files_dic_1[filename] = filename_period_l[1]

        if filename_period_l[0] <= now_time <= filename_period_l[1]:

            return filename

    # 如果都没有，则开始造价，造价起始需要从最后一个文件的最后一个价格获取得到
    final_price = get_final_price(files_dic_1)
    filename = make_price(S0=final_price)

    return filename