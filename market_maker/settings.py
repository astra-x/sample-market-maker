from os.path import join
import logging
import os

# -----------------------------------System Setting---------------------------------------
Market_Maker_Dir = os.path.dirname(os.path.abspath(__file__))

# Available levels: logging.(DEBUG|INFO|WARN|ERROR)
LOG_LEVEL = logging.INFO


# If any of these files (and this file) changes, reload the bot.ll
# WATCHED_FILES = [os.path.join(Market_Maker_Dir,'market_maker_inner.py'), os.path.join(Market_Maker_Dir,'gateio.py'),\
#                   os.path.join(Market_Maker_Dir,'settings.py')]

WATCHED_FILES = []


# -----------------------------------GateIo  Setting---------------------------------------

# API URL.
GATEIO_URL = "wss://fx-ws-testnet.gateio.ws/v4/ws"


SYMBOL = "eos"
CONTRACT = "EOS_USD"


# -----------------------------------Client  Setting-----------------------------------------

##url

Client_HTTP_URL="http://47.75.14.147:3000"
Client_WS_URL="ws://47.56.8.19:19090"


#order -quantitiy是否随机生成
RANDOM_ORDER_SIZE=False
# 随机生成的quantitiy最大是多少
MAX_ORDER_SIZE=0.3
# 随机生成的quantitiy最小是多少
MIN_ORDER_SIZE=0.01

# 基础数量最大
ORDER_START_MAX_SIZE = 1
# 基础数量最小
ORDER_START_MIN_SIZE = 0.01

# 数量间隔
ORDER_STEP_SIZE = 0.01

#价格缩放倍数
PRICE_MINIFICATION=1

#价格间隔
PRICE_INTERVAL = 0.05  #现在的

# How many pairs of buy/sell orders to keep open
ORDER_PAIRS = 15

# Client token ，可以不配置，可以根据账户密码实时更新生成
ClientToken=""

# 登录账户，如果创建进程时没传则使用该默认账户
Email="youtao.xing@icloud.com"
# 登录密码，如果创建进程时没传则使用该默认密码
Password="1234!abcd"

# 交易品种
ClientContract="EOS/USDT"
# 每次place_order间隔时间,如果创建进程时没传则使用该默认CycleTime
CycleTime=10
# 运行时间
RunTime=1000000000000000

# Wait times between orders / errors
TIMEOUT = 7

#基础计价方式，相当于人民币
ClientSymbol="USDT"

# 创建多个账户共同执行
MarketMakers = [
    #创建3s周期的market-maker服务
    {"CycleTime": 3, "Email": "youtao.xing@icloud.com", "Password": "1234!abcd"},
    {"CycleTime": 5, "Email": "python_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 7, "Email": "go_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 9, "Email": "1263624209@qq.com", "Password": "135246zr"},
#
    # {"CycleTime": 11, "Email": "youtao.xing@icloud.com", "Password": "1234!abcd"},
    # {"CycleTime": 13, "Email": "python_runzhang@163.com", "Password": "135246zr"},
    # {"CycleTime": 15, "Email": "go_runzhang@163.com", "Password": "135246zr"},
    # {"CycleTime": 17, "Email": "1263624209@qq.com", "Password": "135246zr"},
    #
    {"CycleTime": 19, "Email": "youtao.xing@icloud.com", "Password": "1234!abcd"},
    {"CycleTime": 21, "Email": "python_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 23, "Email": "go_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 25, "Email": "1263624209@qq.com", "Password": "135246zr"},
#     #
    {"CycleTime": 27, "Email": "youtao.xing@icloud.com", "Password": "1234!abcd"},
    {"CycleTime": 29, "Email": "python_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 31, "Email": "go_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 33, "Email": "1263624209@qq.com", "Password": "135246zr"}
]








