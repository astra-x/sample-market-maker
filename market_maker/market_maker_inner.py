from __future__ import absolute_import
from time import sleep
import sys
from datetime import datetime
from os.path import getmtime
import random, time
import requests
import atexit
import signal
from market_maker import dcex
from market_maker import bitmex
from market_maker import settings
from market_maker.utils import constants, errors, math
from market_maker.utils.log import logger
# Used for reloading the bot - saves modified times of key files
import os

watched_files_mtimes = [(f, getmtime(f)) for f in settings.WATCHED_FILES]


# Helpers
#


class ExchangeInterface:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        if len(sys.argv) > 1:
            self.symbol = sys.argv[1]
        else:
            self.symbol = settings.SYMBOL
        self.bitmex = bitmex.BitMEX(base_url=settings.BITMEX_URL, symbol=self.symbol,
                                    apiKey=settings.API_KEY, apiSecret=settings.API_SECRET,
                                    orderIDPrefix=settings.ORDERID_PREFIX, postOnly=settings.POST_ONLY,
                                    timeout=settings.TIMEOUT)

    def cancel_order(self, order):
        tickLog = self.get_instrument()['tickLog']
        logger.info("Canceling: %s %d @ %.*f" % (order['side'], order['orderQty'], tickLog, order['price']))
        while True:
            try:
                self.bitmex.cancel(order['orderID'])
                sleep(settings.API_REST_INTERVAL)
            except ValueError as e:
                logger.info(e)
                sleep(settings.API_ERROR_INTERVAL)
            else:
                break

    def cancel_all_orders(self):
        if self.dry_run:
            return

        logger.info("Resetting current position. Canceling all existing orders.")
        tickLog = self.get_instrument()['tickLog']

        # In certain cases, a WS update might not make it through before we call this.
        # For that reason, we grab via HTTP to ensure we grab them all.
        orders = self.bitmex.http_open_orders()

        for order in orders:
            logger.info("Canceling: %s %d @ %.*f" % (order['side'], order['orderQty'], tickLog, order['price']))
        if len(orders):
            self.bitmex.cancel([order['orderID'] for order in orders])

        sleep(settings.API_REST_INTERVAL)

    def get_portfolio(self):
        contracts = settings.CONTRACTS
        portfolio = {}
        for symbol in contracts:
            position = self.bitmex.position(symbol=symbol)
            instrument = self.bitmex.instrument(symbol=symbol)

            if instrument['isQuanto']:
                future_type = "Quanto"
            elif instrument['isInverse']:
                future_type = "Inverse"
            elif not instrument['isQuanto'] and not instrument['isInverse']:
                future_type = "Linear"
            else:
                raise NotImplementedError("Unknown future type; not quanto or inverse: %s" % instrument['symbol'])

            if instrument['underlyingToSettleMultiplier'] is None:
                multiplier = float(instrument['multiplier']) / float(instrument['quoteToSettleMultiplier'])
            else:
                multiplier = float(instrument['multiplier']) / float(instrument['underlyingToSettleMultiplier'])

            portfolio[symbol] = {
                "currentQty": float(position['currentQty']),
                "futureType": future_type,
                "multiplier": multiplier,
                "markPrice": float(instrument['markPrice']),
                "spot": float(instrument['indicativeSettlePrice'])
            }

        return portfolio

    def calc_delta(self):
        """Calculate currency delta for portfolio"""
        portfolio = self.get_portfolio()
        spot_delta = 0
        mark_delta = 0
        for symbol in portfolio:
            item = portfolio[symbol]
            if item['futureType'] == "Quanto":
                spot_delta += item['currentQty'] * item['multiplier'] * item['spot']
                mark_delta += item['currentQty'] * item['multiplier'] * item['markPrice']
            elif item['futureType'] == "Inverse":
                spot_delta += (item['multiplier'] / item['spot']) * item['currentQty']
                mark_delta += (item['multiplier'] / item['markPrice']) * item['currentQty']
            elif item['futureType'] == "Linear":
                spot_delta += item['multiplier'] * item['currentQty']
                mark_delta += item['multiplier'] * item['currentQty']
        basis_delta = mark_delta - spot_delta
        delta = {
            "spot": spot_delta,
            "mark_price": mark_delta,
            "basis": basis_delta
        }
        return delta

    def get_delta(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        return self.get_position(symbol)['currentQty']

    def get_instrument(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        return self.bitmex.instrument(symbol)

    def get_margin(self):
        if self.dry_run:
            return {'marginBalance': float(settings.DRY_BTC), 'availableFunds': float(settings.DRY_BTC)}
        return self.bitmex.funds()

    def get_orders(self):
        if self.dry_run:
            print("self.bitmex.open_orders():", self.bitmex.open_orders())
            return []
        return self.bitmex.open_orders()

    def get_highest_buy(self):
        buys = [o for o in self.get_orders() if o['side'] == 'Buy']
        if not len(buys):
            return {'price': -2 ** 32}
        highest_buy = max(buys or [], key=lambda o: o['price'])
        return highest_buy if highest_buy else {'price': -2 ** 32}

    def get_lowest_sell(self):
        sells = [o for o in self.get_orders() if o['side'] == 'Sell']
        if not len(sells):
            return {'price': 2 ** 32}
        lowest_sell = min(sells or [], key=lambda o: o['price'])
        return lowest_sell if lowest_sell else {'price': 2 ** 32}  # ought to be enough for anyone

    def get_position(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        return self.bitmex.position(symbol)

    def get_ticker(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        return self.bitmex.ticker_data(symbol)

    def is_open(self):
        """Check that websockets are still open."""
        return not self.bitmex.ws.exited

    def check_market_open(self):
        instrument = self.get_instrument()
        if instrument["state"] != "Open" and instrument["state"] != "Closed":
            raise errors.MarketClosedError("The instrument %s is not open. State: %s" %
                                           (self.symbol, instrument["state"]))

    def check_if_orderbook_empty(self):
        """This function checks whether the order book is empty"""
        instrument = self.get_instrument()
        if instrument['midPrice'] is None:
            raise errors.MarketEmptyError("Orderbook is empty, cannot quote")

    def amend_bulk_orders(self, orders):
        if self.dry_run:
            return orders
        return self.bitmex.amend_bulk_orders(orders)

    def create_bulk_orders(self, orders):
        if self.dry_run:
            return orders
        print("开始创建orders.....")
        return self.bitmex.create_bulk_orders(orders)

    def cancel_bulk_orders(self, orders):
        if self.dry_run:
            return orders
        return self.bitmex.cancel([order['orderID'] for order in orders])


class DcexExchangeInterface:
    def __init__(self, email,password,dry_run=False):
        self.email=email
        self.password=password
        self.dry_run = dry_run
        if len(sys.argv) > 1:
            self.symbol = sys.argv[1]
        else:
            self.symbol = settings.DCEXSymbol
        self.dcex = dcex.DCEX(dcex_ws_url=settings.DCEX_WS_URL, dcex_http_url=settings.DCEX_HTTP_URL,
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
        return self.dcex.is_connected()

    def cancel_all_orders(self):
        if self.dry_run:
            return
        orders = self.get_orders()
        self.cancel_bulk_orders(orders)

    def get_orders(self):
        if self.dry_run:
            return []
        return self.dcex.http_open_orders()

    def create_bulk_orders(self, orders):
        if self.dry_run:
            return orders
        orders_created = []

        for order in orders:
            self.executive_info["create_order_num"] += 1
            response = self.dcex.create_order(order=order)

            if response["error"] == None:
                # 取出订单进行处理,将其放入orders_created中
                self.executive_info["create_order_ok_num"] += 1
                orders_created.append(response["result"])

        return orders_created

    def cancel_bulk_orders(self, orders):
        if self.dry_run:
            return orders
        for order in orders:
            self.executive_info["cancel_order_num"] += 1
            response = self.dcex.cancel_order(orderid=order["id"])
            if response["error"] == None:
                self.executive_info["cancel_order_ok_num"] += 1

    def sell_all_assert(self):
        # 取消所有委托订单
        self.cancel_all_orders()
        # 获取账户资产情况
        balace = self.dcex.get_balace()
        if settings.BaseValuation == "DCA":
            if settings.BaseValuation in balace:
                for k, v in balace.items():
                    if k != settings.BaseValuation:
                        symbol = k + settings.BaseValuation
                        available = float(v["available"])
                        # 获取盘口价格信息
                        depath_info = self.dcex.get_depath_info(symbol)
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
        else:
            for k, v in balace.items():
                if k == "DCA":
                    symbol = settings.BaseValuation + k
                    available = float(v["available"])
                    # 获取盘口价格信息
                    depath_info = self.dcex.get_depath_info(symbol)
                    if depath_info:
                        asks = depath_info[1].get("asks", [])
                        bids = depath_info[1].get("bids", [])
                        a_account = float(0)
                        for a in asks:  # asks 盘口的卖盘
                            a_account += float(a[1])
                            if available <= a_account:
                                order_account = a_account
                                order_price = available / order_account
                                order = [{
                                    "id": 1000000015, "price": str(order_price), "amount": str(order_account),
                                    "side": 2, "market": symbol
                                }]
                                # 创建好可以卖的掉的订单，将手里股票资产卖掉
                                self.create_bulk_orders(orders=order)
                                break

    def init_executive_info(self):
        balace = self.dcex.get_balace()
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.executive_info["init_balance"] = balace
        self.executive_info["start_time"] = start_time

    def get_executive_report(self):

        self.sell_all_assert()
        finish_balance = self.dcex.get_balace()
        finish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.executive_info["finish_balance"] = finish_balance
        self.executive_info["finish_time"] = finish_time

        return self.executive_info


class OrderManager:
    def __init__(self,cycleTime,email,password):
        self.CycleTime=cycleTime if cycleTime else  settings.cycleTime
        self.email=email if email else settings.Email
        self.password=password if password  else  settings.Password
        self.exchange = ExchangeInterface(settings.DRY_RUN)
        self.exchange_dcex= DcexExchangeInterface(email=email,password=password)
        # Once exchange is created, register exit handler that will always cancel orders
        # on any error.

        atexit.register(self.exit)
        signal.signal(signal.SIGTERM, self.exit)
        if settings.DRY_RUN:
            logger.info("Initializing dry run. Orders printed below represent what would be posted to BitMEX.")
        else:
            logger.info("Order Manager initializing, connecting to BitMEX. Live run: executing real trades.")
        self.instrument = self.exchange.get_instrument()
        time.sleep(self.CycleTime)
        self.reset()

    def reset(self):

        self.exchange_dcex.cancel_all_orders()
        self.exchange_dcex.init_executive_info()

    def get_ticker(self):
        ticker = self.exchange.get_ticker()
        tickLog = self.exchange.get_instrument()['tickLog']

        # Set up our buy & sell positions as the smallest possible unit above and below the current spread
        # and we'll work out from there. That way we always have the best price but we don't kill wide

        self.start_position_buy = ticker["buy"] + self.instrument['tickSize']
        self.start_position_sell = ticker["sell"] - self.instrument['tickSize']

        if settings.MAINTAIN_SPREADS:
            if ticker['buy'] == self.exchange.get_highest_buy()['price']:
                self.start_position_buy = ticker["buy"]
            if ticker['sell'] == self.exchange.get_lowest_sell()['price']:
                self.start_position_sell = ticker["sell"]

        # Back off if our spread is too small.
        if self.start_position_buy * (1.00 + settings.MIN_SPREAD) > self.start_position_sell:
            self.start_position_buy *= (1.00 - (settings.MIN_SPREAD / 2))
            self.start_position_sell *= (1.00 + (settings.MIN_SPREAD / 2))

        # Midpoint, used for simpler order placement.
        self.start_position_mid = ticker["mid"]
        logger.info(
            "%s Ticker: Buy: %.*f, Sell: %.*f" %
            (self.instrument['symbol'], tickLog, ticker["buy"], tickLog, ticker["sell"])
        )
        logger.info('Start Positions: Buy: %.*f, Sell: %.*f, Mid: %.*f' %
                    (tickLog, self.start_position_buy, tickLog, self.start_position_sell,
                     tickLog, self.start_position_mid))

        return ticker

    def get_price_offset(self, index):
        """Given an index (1, -1, 2, -2, etc.) return the price for that side of the book.
           Negative is a buy, positive is a sell."""
        # Maintain existing spreads for max profit
        if settings.MAINTAIN_SPREADS:
            start_position = self.start_position_buy if index < 0 else self.start_position_sell
            # First positions (index 1, -1) should start right at start_position, others should branch from there
            index = index + 1 if index < 0 else index - 1
        else:
            # Offset mode: ticker comes from a reference exchange and we define an offset.
            start_position = self.start_position_buy if index < 0 else self.start_position_sell

            # If we're attempting to sell, but our sell price is actually lower than the buy,
            # move over to the sell side.
            if index > 0 and start_position < self.start_position_buy:
                start_position = self.start_position_sell
            # Same for buys.
            if index < 0 and start_position > self.start_position_sell:
                start_position = self.start_position_buy

        # 这是创造价格的策略
        return math.toNearest(start_position * (1 + settings.INTERVAL) ** index, self.instrument['tickSize'])

    ###
    # Orders
    ###
    def place_orders(self):
        """Create order items for use in convergence."""
        buy_orders = []
        sell_orders = []
        for i in reversed(range(1, settings.ORDER_PAIRS + 1)):
            buy_orders.append(self.prepare_order(-i))
            sell_orders.append(self.prepare_order(i))
        to_cancel = self.converge_orders(buy_orders, sell_orders)
        time.sleep(self.CycleTime)
        random.shuffle(to_cancel)
        self.cancel_bulk_orders(to_cancel=to_cancel)

    def prepare_order(self, index):
        """Create an order object."""
        # 这是创造数量的策略
        if settings.RANDOM_ORDER_SIZE is True:
            quantity = random.randint(settings.MIN_ORDER_SIZE, settings.MAX_ORDER_SIZE)
        else:
            quantity = settings.ORDER_START_SIZE + ((abs(index) - 1) * settings.ORDER_STEP_SIZE)
        # 这是创造价格的策略
        price = self.get_price_offset(index)

        # 模拟拉盘和砸盘
        if index<0 and random.randint(1, 9) == 1:
            price=price*1.1
            quantity=quantity*4
        if index>0 and random.randint(1,9)==2:
            price=price*0.9
            quantity=quantity*4

        return {"id": 1000000015, "price": str(price / 1000), "amount": str(quantity), "side": 2 if index < 0 else 1}

    def converge_orders(self, buy_orders, sell_orders):
        to_create = []
        orders_created = []
        to_create.extend(buy_orders)
        to_create.extend(sell_orders)
        if len(to_create) > 0:
            print("to_create:", to_create)
            time.sleep(0.5)
            orders_created = self.exchange_dcex.create_bulk_orders(to_create)

        return orders_created

    def cancel_bulk_orders(self, to_cancel):
        self.exchange_dcex.cancel_bulk_orders(orders=to_cancel)

    ###
    # Position Limits
    ###

    def short_position_limit_exceeded(self):
        """Returns True if the short position limit is exceeded"""
        if not settings.CHECK_POSITION_LIMITS:
            return False
        position = self.exchange.get_delta()
        return position <= settings.MIN_POSITION

    def long_position_limit_exceeded(self):
        """Returns True if the long position limit is exceeded"""
        if not settings.CHECK_POSITION_LIMITS:
            return False
        position = self.exchange.get_delta()
        return position >= settings.MAX_POSITION

    ###
    # Sanity
    ##

    def sanity_check(self):
        """Perform checks before placing orders."""

        # Check if OB is empty - if so, can't quote.
        self.exchange.check_if_orderbook_empty()
        # Ensure market is still open.
        self.exchange.check_market_open()

        # Get ticker, which sets price offsets and prints some debugging info.
        ticker = self.get_ticker()

        # Sanity check:
        if self.get_price_offset(-1) >= ticker["sell"] or self.get_price_offset(1) <= ticker["buy"]:
            logger.error("Buy: %s, Sell: %s" % (self.start_position_buy, self.start_position_sell))
            logger.error("First buy position: %s\nBitMEX Best Ask: %s\nFirst sell position: %s\nBitMEX Best Bid: %s" %
                         (self.get_price_offset(-1), ticker["sell"], self.get_price_offset(1), ticker["buy"]))
            logger.error("Sanity check failed, exchange data is inconsistent")
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
        return self.exchange.is_open() and self.exchange_dcex.is_open()

    def exit(self):
        logger.info("Shutting down. All open orders will be cancelled.")
        try:
            self.exchange_dcex.cancel_all_orders()
            self.exchange.bitmex.exit()
        except errors.AuthenticationError as e:
            logger.info("Was not authenticated; could not cancel orders.")
        except Exception as e:
            logger.info("Unable to cancel orders: %s" % e)
        sys.exit()

    def print_executive_report(self):
        # self.exchange_dcex.dcex()
        dcex_executive_report = self.exchange_dcex.get_executive_report()
        print("---------------------------执行报告--------------------------")
        print("create_order_num:", dcex_executive_report["create_order_num"])
        print("create_order_ok_num:", dcex_executive_report["create_order_ok_num"])
        print("cancel_order_num:", dcex_executive_report["cancel_order_num"])
        print("cancel_order_ok_num:", dcex_executive_report["cancel_order_ok_num"])
        print("init_balance:", dcex_executive_report["init_balance"])
        print("finish_balance:", dcex_executive_report["finish_balance"])
        print("start_time:", dcex_executive_report["start_time"])
        print("finish_time:", dcex_executive_report["finish_time"])
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
                self.restart()
            self.sanity_check()  # Ensures health of mm - several cut-out points here
            try:
                self.exchange_dcex.dcex.update_token()
            except:
                raise Exception("Token update err")
            self.place_orders()  # Creates desired orders and converges to existing orders
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
# Helpers
#


def XBt_to_XBT(XBt):
    return float(XBt) / constants.XBt_TO_XBT


def cost(instrument, quantity, price):
    mult = instrument["multiplier"]
    P = mult * price if mult >= 0 else mult / price
    return abs(quantity * P)


def margin(instrument, quantity, price):
    return cost(instrument, quantity, price) * instrument["initMargin"]
