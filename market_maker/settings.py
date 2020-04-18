from os.path import join
import logging
import os


Market_Maker_Dir = os.path.dirname(os.path.abspath(__file__))

########################################################################################################################
# Connection/Auth
########################################################################################################################

# API URL.
BITMEX_URL = "https://testnet.bitmex.com/api/v1/"


# BASE_URL = "https://www.bitmex.com/api/v1/" # Once you're ready, uncomment this.

# The BitMEX API requires permanent API keys. Go to https://testnet.bitmex.com/app/apiKeys to fill these out.


# astra的

API_KEY = "nqKnXrwSkzplG3S-nACTQBvF"
API_SECRET = "M0JrmZz7AO_ts4Lvim897hL-Vf-V53B_dAs_Y0CYEI0kRFI6"

########################################################################################################################
# Target
########################################################################################################################

# Instrument to market make on BitMEX.
SYMBOL = "XBTUSD"


########################################################################################################################
# Order Size & Spread
########################################################################################################################

# How many pairs of buy/sell orders to keep open
ORDER_PAIRS = 10

# ORDER_START_SIZE will be the number of contracts submitted on level 1
# Number of contracts from level 1 to ORDER_PAIRS - 1 will follow the function
# [ORDER_START_SIZE + ORDER_STEP_SIZE (Level -1)]
# ORDER_START_SIZE = 10
# ORDER_STEP_SIZE = 10

# Distance between successive orders, as a percentage (example: 0.005 for 0.5%)
# INTERVAL = 0.005 #原来的


# Minimum spread to maintain, in percent, between asks & bids
MIN_SPREAD = 0.01

# If True, market-maker will place orders just inside the existing spread and work the interval % outwards,
# rather than starting in the middle and killing potentially profitable spreads.
MAINTAIN_SPREADS = False

# This number defines far much the price of an existing order can be from a desired order before it is amended.
# This is useful for avoiding unnecessary calls and maintaining your ratelimits.
#
# Further information:
# Each order is designed to be (INTERVAL*n)% away from the spread.
# If the spread changes and the order has moved outside its bound defined as
# abs((desired_order['price'] / order['price']) - 1) > settings.RELIST_INTERVAL)
# it will be resubmitted.
#
# 0.01 == 1%
RELIST_INTERVAL = 0.01


########################################################################################################################
# Trading Behavior
########################################################################################################################

# Position limits - set to True to activate. Values are in contracts.
# If you exceed a position limit, the bot will log and stop quoting that side.
CHECK_POSITION_LIMITS = False
MIN_POSITION = -10000
MAX_POSITION = 10000

# If True, will only send orders that rest in the book (ExecInst: ParticipateDoNotInitiate).
# Use to guarantee a maker rebate.
# However -- orders that would have matched immediately will instead cancel, and you may end up with
# unexpected delta. Be careful.
POST_ONLY = False

########################################################################################################################
# Misc Behavior, Technicals
########################################################################################################################

# If true, don't set up any orders, just say what we would do
DRY_RUN = True


# How often to re-check and replace orders.
# Generally, it's safe to make this short because we're fetching from websockets. But if too many
# order amend/replaces are done, you may hit a ratelimit. If so, email BitMEX if you feel you need a higher limit.


# Wait times between orders / errors
API_REST_INTERVAL = 1
API_ERROR_INTERVAL = 10
TIMEOUT = 7

# If we're doing a dry run, use these numbers for BTC balances
DRY_BTC = 50

# Available levels: logging.(DEBUG|INFO|WARN|ERROR)
LOG_LEVEL = logging.INFO

# To uniquely identify orders placed by this bot, the bot sends a ClOrdID (Client order ID) that is attached
# to each order so its source can be identified. This keeps the market maker from cancelling orders that are
# manually placed, or orders placed by another bot.
#
# If you are running multiple bots on the same symbol, give them unique ORDERID_PREFIXes - otherwise they will
# cancel each others' orders.
# Max length is 13 characters.
ORDERID_PREFIX = "mm_bitmex_"

# If any of these files (and this file) changes, reload the bot.ll
WATCHED_FILES = [os.path.join(Market_Maker_Dir,'market_maker_inner.py'), os.path.join(Market_Maker_Dir,'bitmex.py'),\
                  os.path.join(Market_Maker_Dir,'settings.py')]



CONTRACTS = ['XBTUSD']

# --------------------------------DCEX  setting-----------------------------------------

##url

DCEX_HTTP_URL="http://47.97.125.121:3000"
DCEX_WS_URL="ws://47.96.155.19:19090"




#order -quantitiy是否随机生成
RANDOM_ORDER_SIZE=False
# 随机生成的quantitiy最大是多少
MAX_ORDER_SIZE=1
# 随机生成的quantitiy最小是多少
MIN_ORDER_SIZE=0.01

# 基础数量最大
ORDER_START_MAX_SIZE = 0.30
# 基础数量最小
ORDER_START_MIN_SIZE = 0.01

# 数量间隔
ORDER_STEP_SIZE = 0.01

#价格缩放倍数
PRICE_MINIFICATION=10

#价格间隔
PRICE_INTERVAL = 0.05  #现在的



# DCEX token ，可以不配置，可以根据账户密码实时更新生成
DCEXToken=""

# 登录账户，如果创建进程时没传则使用该默认账户
Email="youtao.xing@icloud.com"
# 登录密码，如果创建进程时没传则使用该默认密码
Password="1234!abcd"

# 交易品种
DCEXSymbol="ICPDCA"
# 每次place_order间隔时间,如果创建进程时没传则使用该默认CycleTime
CycleTime=10
# 运行时间
RunTime=1000000000000000
#基础计价方式，相当于人民币
BaseValuation="DCA"

# 创建多个账户共同执行
MarketMakers = [

    {"CycleTime": 3, "Email": "youtao.xing@icloud.com", "Password": "1234!abcd"},
    {"CycleTime": 5, "Email": "python_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 7, "Email": "go_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 9, "Email": "1263624209@qq.com", "Password": "135246zr"},

    # {"CycleTime": 11, "Email": "youtao.xing@icloud.com", "Password": "1234!abcd"},
    # {"CycleTime": 13, "Email": "python_runzhang@163.com", "Password": "135246zr"},
    # {"CycleTime": 15, "Email": "go_runzhang@163.com", "Password": "135246zr"},
    # {"CycleTime": 17, "Email": "1263624209@qq.com", "Password": "135246zr"},
    #
    {"CycleTime": 19, "Email": "youtao.xing@icloud.com", "Password": "1234!abcd"},
    {"CycleTime": 21, "Email": "python_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 23, "Email": "go_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 25, "Email": "1263624209@qq.com", "Password": "135246zr"},
    #
    {"CycleTime": 27, "Email": "youtao.xing@icloud.com", "Password": "1234!abcd"},
    {"CycleTime": 29, "Email": "python_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 31, "Email": "go_runzhang@163.com", "Password": "135246zr"},
    {"CycleTime": 33, "Email": "1263624209@qq.com", "Password": "135246zr"},
]

# 网络代理设置
NetworkProxy="http://127.0.0.1:7890"
ProxyHOST="http://127.0.0.1"
ProxyPORT=7890



