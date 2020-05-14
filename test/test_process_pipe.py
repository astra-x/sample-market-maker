# from multiprocessing import Pipe
# from multiprocessing import Process
# def func(p):  # 消费者（管道的r端，用来接收数据）
#     l,r=p  # 代表管道的左右两端，这里其实是子进程来执行的函数，只用到管道的r端，之所以也写l，是想说明在进程中不用的管道那端需要及时关闭
#     l.close()  # 该子进程执行 只用到管道r端用来接收数据，所以管道的另一端l需要及时关闭
#     while True:
#         try:
#             print(r.recv()) # 消费者从管道一端r端取数据
#         except EOFError:  # 当管道的另一端l发送端 关闭时，管道的r端接收端就不需要再等着接收消息了
#             break
#
# if __name__=="__main__":
#     l,r=Pipe()  # 管道的两端，l,r 在主进程中执行生产数据（l端发送数据）
#     p=Process(target=func,args=((l,r),))  # 把管道的两端都传到func函数中，由子进程来执行func，但子进程中l端是用不到的，所以在子进程中需要及时关闭
#     p.start()
#     r.close()  # 由于在主进程中没有用到r端，所以需要及时关闭管道的r端
#     for i in range(10):
#         l.send("hello,xuanxuan-%s"%i)
#     l.close()   # 主进程中执行完毕之后需要及时关闭发送端管道的l端


# import multiprocessing
#
#
# def func(num):
#     print("子进程中的打印：",num.value)
#     # num.value = 10.78  # 子进程改变数值的值，主进程跟着改变
#
#
# if __name__ == "__main__":
#     num = multiprocessing.Value("d", 10.0)  # d表示数值,主进程与子进程共享这个value。（主进程与子进程都是用的同一个value）
#     print(num.value)
#     # p_list=[]
#     for  i in range(10):
#         p = multiprocessing.Process(target=func, args=(num,))
#         p.start()
#         p.join()

#
#
#
# import os,time
# from multiprocessing import Pipe,Process
#
# #进程函数（）
# #a为形参，代表着child_conn
# def func(name,a):
#         time.sleep(1)
#         #把字符串往管道里发送
#         # a.send('博主最帅'+str(name))
#         print('子进程的id为:',os.getpid(),a.recv())
#         # print('父进程的id为:',os.getppid(),"--------",'子进程的id为:',os.getpid())
#
#
# #创建五个进程
# if __name__ == '__main__':
#     # 创建管道对象
#     # 管道函数返回了两个对象
#     child_conn,parent_conn = Pipe()
#     job = []
#     for i in range(5):
#         p = Process(target=func,args=(i,child_conn))
#     #把新的进程添加到列表里
#         job.append(p)
#         p.start()
#     #从管道中接收，此时写在了join前面，意味着这个for循环时和所有子进程同步进行的
#     # for i in range(5):
#     #     data = parent_conn.recv()
#     #
#     #     print(data)
#     for i in range(5):
#         parent_conn.send("主进程发送的消息")
#     for i in job:
#         i.join()



#
# # -*- coding:utf-8 -*-
# from multiprocessing import Process, Manager
# import time
# import random
#
#
#
#
#
# def jjj(a_list):
#     for i in range(10):
#         time.sleep(1)
#         print(a_list)
#
#
# if __name__ == '__main__':
#     a_list = []
#     process_0 = Process(target=jjj, args=(a_list,))
#     process_0.start()
#     a_list.append("主进程放置进去的数据")
#
#     process_0.join()
#
#     # print(a_list)
#
#     print('it\'s ok')



# -*- coding:utf-8 -*-
from multiprocessing import Process, Manager
import time
import random





def jjj(a_dic,i):

    while True:
        time.sleep(1)
        print(a_dic)
        if i in a_dic:
            item=a_dic.pop(i)
            print(item)


if __name__ == '__main__':
    manager = Manager()
    a_dic = manager.dict()
    # a_list = []
    for i in range(3):
        process_0 = Process(target=jjj, args=(a_dic,i,))
        process_0.start()
    time.sleep(3)
    for i in range(3):

        a_dic[i]=0
    time.sleep(10000)

