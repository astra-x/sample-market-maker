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

SYMBOL = "btc"
CONTRACT = "BTC_USD"

# -----------------------------------Client  Setting-----------------------------------------

##url

Client_HTTP_URL = "https://api.hudex.one/"
Client_WS_URL = "ws://18.183.178.183:19090"

# order -quantitiy是否随机生成
RANDOM_ORDER_SIZE = False
# 随机生成的quantitiy最大是多少
MAX_ORDER_SIZE = 0.3
# 随机生成的quantitiy最小是多少
MIN_ORDER_SIZE = 0.01

# 基础数量最大
ORDER_START_MAX_SIZE = 1
# 基础数量最小
ORDER_START_MIN_SIZE = 0.01

# 数量间隔
ORDER_STEP_SIZE = 0.01

# 成交量放大倍速
VOLUME_MINIFICATION = 4

# 价格缩放倍数
PRICE_MINIFICATION = 1

# 价格间隔
PRICE_INTERVAL = 0.05  # 现在的

# How many pairs of buy/sell orders to keep open
ORDER_PAIRS = 15

# Client token ，可以不配置，可以根据账户密码实时更新生成
ClientToken = ""

# 登录账户，如果创建进程时没传则使用该默认账户
Email = "youtao.xing@icloud.com"
# 登录密码，如果创建进程时没传则使用该默认密码
Password = "1234!abcd"

# 交易品种
ClientContract = "BTC/USDT"
# 每次place_order间隔时间,如果创建进程时没传则使用该默认CycleTime
CycleTime = 10
# 运行时间
RunTime = 1000000000000000

# Wait times between orders / errors
TIMEOUT = 7

# 基础计价方式，相当于人民币
ClientSymbol = "USDT"

# 创建多个账户共同执行
MarketMakers = [
    # 创建3s周期的market-maker服务
    {"CycleTime": 3, "Email": "btc_yuhu01@163.com", "Password": "123456yuhu"},
    {"CycleTime": 5, "Email": "btc_yuhu02@163.com", "Password": "123456yuhu"},
    {"CycleTime": 7, "Email": "btc_yuhu03@163.com", "Password": "123456yuhu"},
    {"CycleTime": 9, "Email": "btc_yuhu04@163.com", "Password": "123456yuhu"},
    #
    {"CycleTime": 11, "Email": "btc_yuhu01@163.com", "Password": "123456yuhu"},
    {"CycleTime": 13, "Email": "btc_yuhu02@163.com", "Password": "123456yuhu"},
    {"CycleTime": 15, "Email": "btc_yuhu03@163.com", "Password": "123456yuhu"},
    {"CycleTime": 17, "Email": "btc_yuhu04@163.com", "Password": "123456yuhu"},
    #
    {"CycleTime": 19, "Email": "btc_yuhu01@163.com", "Password": "123456yuhu"},
    {"CycleTime": 21, "Email": "btc_yuhu02@163.com", "Password": "123456yuhu"},
    {"CycleTime": 23, "Email": "btc_yuhu03@163.com", "Password": "123456yuhu"},
    {"CycleTime": 25, "Email": "btc_yuhu04@163.com", "Password": "123456yuhu"},
    #     #
    {"CycleTime": 27, "Email": "btc_yuhu01@163.com", "Password": "123456yuhu"},
    {"CycleTime": 29, "Email": "btc_yuhu02@163.com", "Password": "123456yuhu"},
    {"CycleTime": 31, "Email": "btc_yuhu03@163.com", "Password": "123456yuhu"},
    {"CycleTime": 33, "Email": "btc_yuhu04@163.com", "Password": "123456yuhu"}
]
