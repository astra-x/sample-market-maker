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
from market_maker import local_data
from market_maker.settings import settings
from market_maker.utils import constants, errors, math
from market_maker.utils.log import logger
# Used for reloading the bot - saves modified times of key files
import os
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED

executor = ThreadPoolExecutor(max_workers=16)

# Helpers

watched_files_mtimes = [(f, getmtime(f)) for f in settings.WATCHED_FILES]


class ClientExchangeInterface:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        if len(sys.argv) > 1:
            self.symbol = sys.argv[1]
        else:
            self.symbol = settings.ClientContract
        self.client = client.Client(client_http_url=settings.Client_HTTP_URL,
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
        orders = self.get_orders()
        self.quick_cancel_orders(orders)

    def get_orders(self):
        return self.client.http_open_orders()

    def create_bulk_orders(self, orders):
        orders_created = []
        for order in orders:
            self.executive_info["create_order_num"] += 1
            response = self.client.create_order(order=order)
            if "error" in response and response["error"] == None:
                # 取出订单进行处理,将其放入orders_created中
                self.executive_info["create_order_ok_num"] += 1
                orders_created.append(response["result"])
        return orders_created

    def slow_cancel_orders(self, orders):
        for order in orders:
            self.executive_info["cancel_order_num"] += 1
            time.sleep(1)
            response = self.client.cancel_order(orderid=order["id"])
            if "error" in response and response["error"] == None:
                self.executive_info["cancel_order_ok_num"] += 1

    def quick_cancel_orders(self, orders):
        all_task = [executor.submit(self._quick_cancel_orders_thread, (order)) for order in orders]
        wait(all_task, return_when=ALL_COMPLETED)

    def _quick_cancel_orders_thread(self, order):
        self.executive_info["cancel_order_num"] += 1
        response = self.client.cancel_order(orderid=order["id"])
        if "error" in response and response["error"] == None:
            self.executive_info["cancel_order_ok_num"] += 1




class OrderManager:
    def __init__(self, cycleTime, email, password):

        self.CycleTime = settings.CycleTime if settings.CycleTime else cycleTime
        self.email = email if email else settings.Email
        self.password = password if password else settings.Password
        time.sleep(self.CycleTime)  # 这是为了两个目的，  一是不同时那么多请求去链接local websocket以免被禁用，二是不同时重置order
        self.exchange_client = ClientExchangeInterface(email=self.email, password=self.password)
        # Once exchange is created, register exit handler that will always cancel orders
        # on any error.
        atexit.register(self.exit)
        signal.signal(signal.SIGCHLD, self.exit)
        self.Exit = False
        # self.reset()

    def reset(self):
        self.exchange_client.cancel_all_orders()

    def get_price_offset(self):
        max_set_price = settings.MaxSetPrice
        min_set_price = settings.MinSetPrice
        start_position_price = round(random.uniform(min_set_price, max_set_price),2)
        return start_position_price
    ###
    # Orders
    ###
    def place_orders(self):
        """Create order items for use in convergence."""
        buy_orders = []
        sell_orders = []
        price = self.get_price_offset()
        quantity = round(random.uniform(settings.OrderMinQuantity, settings.OrderMaxQuantity), 2)
        buy_order = {"id": 1000000015, "price": str(price), "amount": str(quantity), "side": 2}
        sell_order = {"id": 1000000015, "price": str(price), "amount": str(quantity), "side": 1}
        buy_orders.append(buy_order)
        sell_orders.append(sell_order)
        self.converge_orders(buy_orders, sell_orders)

    def prepare_order(self, index):
        """Create an order object."""
        # 这是创造价格的策略
        price = self.get_price_offset()
        return {"id": 1000000015, "price": str(price), "amount": "0", "side": 2 if index < 0 else 1}

    def converge_orders(self, buy_orders, sell_orders):

        to_create = []
        orders_created = []
        to_create.extend(buy_orders)
        to_create.extend(sell_orders)
        if len(to_create) > 0:
            orders_created = self.exchange_client.create_bulk_orders(to_create)

        return orders_created

    def cancel_bulk_orders(self, to_cancel):
        self.exchange_client.quick_cancel_orders(orders=to_cancel)

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
        pass

    def run_loop(self):
        while True:
            # 更新token
            self.exchange_client.client.update_token()
            # 如果"self.Exit"为false，则进程退出
            if self.Exit:
                print("-----------------子进程正在退出------------")
                self.print_executive_report()
                self.exit()
            # 根据配置的时间判断，是否可执行
            now = time.time()
            start_time_timestamp = int(time.mktime(time.strptime(settings.StartTime, "%Y-%m-%d %H:%M:%S")))
            end_time_timestamp = int(time.mktime(time.strptime(settings.EndTime, "%Y-%m-%d %H:%M:%S")))
            if not (start_time_timestamp < now < end_time_timestamp):
                time.sleep(self.CycleTime)
                self.print_executive_report()
                continue
            # 周期内执行几次（随机）
            low_frequency = settings.LowFrequency
            high_frequency = settings.HighFrequency
            random_frequency = random.randint(low_frequency, high_frequency)
            for i in range(random_frequency):
                sleep(self.CycleTime / random_frequency)
                try:
                    self.place_orders()
                except Exception as e:
                    print("run_loop Exception as e:", e)
                    continue

    def restart(self):
        logger.info("Restarting the market maker...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

#
#
