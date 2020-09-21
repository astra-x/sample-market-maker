from __future__ import absolute_import
from time import sleep
import sys
from datetime import datetime
from os.path import getmtime
import random, time
import requests
import atexit
import signal
from market_maker import client
from market_maker import gateio
from market_maker import huobi
from market_maker import settings
from market_maker.utils import constants, errors, math
from market_maker.utils.log import logger
# Used for reloading the bot - saves modified times of key files
import os

watched_files_mtimes = [(f, getmtime(f)) for f in settings.WATCHED_FILES]


# Helpers
#


class GateIoExchangeInterface:
    def __init__(self):

        if len(sys.argv) > 1:
            self.symbol = sys.argv[1]
        else:
            self.symbol = settings.SYMBOL
        self.gateio = gateio.GateIo(base_url=settings.GATEIO_URL, symbol=self.symbol,
                                    timeout=settings.TIMEOUT)

    def get_orders(self):
        return self.gateio.ticker_data()

    def get_ticker(self):

        return self.gateio.ticker_data()

    def is_open(self):
        """Check that websockets are still open."""
        return not self.gateio.ws.exited


class HuobiExchangeInterface:
    def __init__(self):
        self.huobi = huobi.Huobi(base_url=settings.HUOBI_URL)

    def get_start_position(self):
        depath=self.huobi.get_depath()
        bids = depath.get("bids",[])
        asks = depath.get("asks",[])
        bids_price_l = []
        asks_price_l = []
        for a in asks:
            asks_price_l.append(a[0])
        for b in bids:
            bids_price_l.append(b[0])
        start_position = (max(bids_price_l) + min(asks_price_l)) / 2

        return start_position


class ClientExchangeInterface:
    def __init__(self, email, password, dry_run=False):
        self.email = email
        self.password = password
        self.dry_run = dry_run
        if len(sys.argv) > 1:
            self.symbol = sys.argv[1]
        else:
            self.symbol = settings.ClientContract
        self.client = client.Client(client_ws_url=settings.Client_WS_URL, client_http_url=settings.Client_HTTP_URL,
                                    symbol=self.symbol,
                                    email=self.email, password=self.password,
                                    timeout=settings.TIMEOUT)
        self.executive_info = {"create_order_num": 0,
                               "create_order_ok_num": 0,
                               "cancel_order_num": 0,
                               "cancel_order_ok_num": 0,
                               "init_balance": {},
                               "finish_balance": {},
                               "deal_order_info": [],
                               "start_time": 0,
                               "finish_time": 0
                               }

    def is_open(self):
        """Check that websockets are still open."""
        return self.client.is_connected()

    def cancel_all_orders(self):
        if self.dry_run:
            return
        orders = self.get_orders()
        self.cancel_bulk_orders(orders)

    def get_orders(self):
        if self.dry_run:
            return []
        return self.client.http_open_orders()

    def create_bulk_orders(self, orders):
        if self.dry_run:
            return orders
        orders_created = []

        for order in orders:
            self.executive_info["create_order_num"] += 1
            response = self.client.create_order(order=order)

            if "error" in response and response["error"] == None:
                # 取出订单进行处理,将其放入orders_created中
                self.executive_info["create_order_ok_num"] += 1
                orders_created.append(response["result"])

        return orders_created

    def cancel_bulk_orders(self, orders):
        if self.dry_run:
            return orders
        for order in orders:
            self.executive_info["cancel_order_num"] += 1
            time.sleep(1)

            response = self.client.cancel_order(orderid=order["id"])
            if "error" in response and response["error"] == None:
                self.executive_info["cancel_order_ok_num"] += 1

    def sell_all_assert(self):
        # 取消所有委托订单
        self.cancel_all_orders()
        # 获取账户资产情况
        balace = self.client.get_balace()
        if settings.ClientSymbol and settings.ClientSymbol in balace:
            for k, v in balace.items():
                if k != settings.ClientSymbol:
                    symbol = k + settings.ClientSymbol
                    available = float(v["available"])
                    # 获取盘口价格信息
                    depath_info = self.client.get_depath_info(symbol)
                    if depath_info:
                        asks = depath_info[1].get("asks", [])
                        bids = depath_info[1].get("bids", [])
                        b_account = float(0)
                        for b in bids:  # bids 盘口的买盘
                            b_account += float(b[1])
                            if available <= b_account:
                                order_account = b_account
                                order_price = available / order_account
                                order = [{
                                    "id": 1000000015, "price": str(order_price), "amount": str(order_account),
                                    "side": 1, "market": symbol
                                }]
                                # 创建好可以卖的掉的订单，将手里股票资产卖掉
                                self.create_bulk_orders(orders=order)
                                break

    def init_executive_info(self):
        balace = self.client.get_balace()
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.executive_info["init_balance"] = balace
        self.executive_info["start_time"] = start_time

    def get_executive_report(self):

        self.sell_all_assert()
        finish_balance = self.client.get_balace()
        finish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.executive_info["finish_balance"] = finish_balance
        self.executive_info["finish_time"] = finish_time

        return self.executive_info


class OrderManager:
    def __init__(self, cycleTime, email, password):

        self.CycleTime = cycleTime if cycleTime else settings.CycleTime
        self.email = email if email else settings.Email
        self.password = password if password else settings.Password
        time.sleep(self.CycleTime)  # 这是为了两个目的，  一是不同时那么多请求去链接gateio websocket以免被禁用，二是不同时重置order
        # self.exchange = GateIoExchangeInterface()
        self.exchange_client = ClientExchangeInterface(email=email, password=password)
        self.huobi_exchange = HuobiExchangeInterface()
        # Once exchange is created, register exit handler that will always cancel orders
        # on any error.
        atexit.register(self.exit)
        signal.signal(signal.SIGCHLD, self.exit)

        # self.reset()

    def reset(self):

        self.exchange_client.cancel_all_orders()
        self.exchange_client.init_executive_info()

    def get_ticker(self):
        self.start_position = self.huobi_exchange.get_start_position()
        return self.start_position

    def get_price_offset(self, index):

        start_position = self.start_position
        print("------------start_position:",start_position)
        # 这是创造价格的策略
        return math.toNearest2(start_position, index)  # 现在的

    ###
    # Orders
    ###
    def place_orders(self):
        """Create order items for use in convergence."""
        buy_orders = []
        sell_orders = []
        for i in reversed(range(1, settings.ORDER_PAIRS + 1)):
            self.get_ticker()
            buy_order = self.prepare_order(-i)
            sell_order = self.prepare_order(i)
            buy_orders.append(buy_order)
            sell_orders.append(sell_order)

        orders_created = self.converge_orders(buy_orders, sell_orders)
        time.sleep(self.CycleTime)
        random.shuffle(orders_created)
        self.cancel_bulk_orders(to_cancel=orders_created)

    def prepare_order(self, index):
        """Create an order object."""
        # 这是创造数量的策略
        quantity = round(random.uniform(settings.ORDER_START_MIN_SIZE, settings.ORDER_START_MAX_SIZE) + \
                         (abs(index) - 1) ** 2 * settings.ORDER_STEP_SIZE, 4)
        # 这是创造价格的策略
        price = self.get_price_offset(index)

        # 模拟拉盘和砸盘
        if index<0 and random.randint(1, 9) == 1:
            price=price*1.1
            quantity=quantity*4
        if index>0 and random.randint(1,9)==2:
            price=price*0.9
            quantity=quantity*4

        return {"id": 1000000015, "price": str(price), "amount": str(quantity), "side": 2 if index < 0 else 1}

    def converge_orders(self, buy_orders, sell_orders):
        to_create = []
        orders_created = []
        to_create.extend(buy_orders)
        to_create.extend(sell_orders)
        if len(to_create) > 0:
            # print("to_create:", to_create)
            random.shuffle(to_create)
            time.sleep(1)
            orders_created = self.exchange_client.create_bulk_orders(to_create)

        return orders_created

    def cancel_bulk_orders(self, to_cancel):
        self.exchange_client.cancel_bulk_orders(orders=to_cancel)

    ###
    # Sanity
    ##

    def sanity_check(self):
        """Perform checks before placing orders."""
        # Check if OB is empty - if so, can't quote.
        # self.exchange.check_if_orderbook_empty()
        # Ensure market is still open.
        # Get ticker, which sets price offsets and prints some debugging info.
        ticker = self.get_ticker()
        if not ticker:
            self.exit()

    ###
    # Running
    ###

    def check_file_change(self):
        """Restart if any files we're watching have changed."""
        for f, mtime in watched_files_mtimes:
            if getmtime(f) > mtime:
                self.restart()

    def check_connection(self):
        """Ensure the WS connections are still open."""
        return  self.exchange_client.is_open()

    def exit(self):
        logger.info("Shutting down. All open orders will be cancelled.")
        try:
            self.exchange_client.cancel_all_orders()
        except errors.AuthenticationError as e:
            logger.info("Was not authenticated; could not cancel orders.")
        except Exception as e:
            logger.info("Unable to cancel orders: %s" % e)
        sys.exit()

    def print_executive_report(self):
        # self.exchange_client.client()
        client_executive_report = self.exchange_client.get_executive_report()
        print("---------------------------执行报告--------------------------")
        print("create_order_num:", client_executive_report["create_order_num"])
        print("create_order_ok_num:", client_executive_report["create_order_ok_num"])
        print("cancel_order_num:", client_executive_report["cancel_order_num"])
        print("cancel_order_ok_num:", client_executive_report["cancel_order_ok_num"])
        print("init_balance:", client_executive_report["init_balance"])
        print("finish_balance:", client_executive_report["finish_balance"])
        print("start_time:", client_executive_report["start_time"])
        print("finish_time:", client_executive_report["finish_time"])
        print("_____________________________________________________________")

    def run_loop(self):
        start_time = time.time()
        while True:
            sys.stdout.write("-----\n")
            sys.stdout.flush()
            self.check_file_change()
            sleep(self.CycleTime)
            # This will restart on very short downtime, but if it's longer,
            # the MM will crash entirely as it is unable to connect to the WS on boot.
            if not self.check_connection():
                logger.error("Realtime data connection unexpectedly closed, restarting.")

                return
            self.sanity_check()  # Ensures health of mm - several cut-out points here
            try:
                self.exchange_client.client.update_token()
                self.place_orders()  # Creates desired orders and converges to existing orders
            except Exception as e:
                print("run_loop Exception as e:", e)
                continue

            now_time = time.time()
            run_time = now_time - start_time
            if run_time > settings.RunTime:
                # todo:这边打印当前MM名称，执行时间，创建订单数，撤销订单数，账户状态
                self.print_executive_report()
                break

    def restart(self):

        logger.info("Restarting the market maker...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

#
#
