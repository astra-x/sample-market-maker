"""Client API Connector."""
from __future__ import absolute_import
import requests
import time
import datetime
import json
import logging
import math
from market_maker.ws.client_ws_thread import ClientWebsocket


class Client(object):
    """Client API Connector."""

    def __init__(self, client_ws_url=None, client_http_url=None, symbol=None, token=None,
                 email=None, password=None, timeout=7):
        """Init connector."""
        self.logger = logging.getLogger('root')
        self.client_ws_url = client_ws_url
        self.client_http_url = client_http_url
        self.token = token
        self.client_symbol = symbol
        self.retries = 0  # initialize counter
        # Create websocket for streaming data
        self.timeout = timeout
        self.email = email
        self.password = password
        self.ws = ClientWebsocket()
        self.ws.connect(endpoint=client_ws_url, symbol=symbol)
        self.update_token()

    # Public methods
    def is_connected(self):
        # todo:需要请求过去判断
        return True

    # 去更新token
    def update_token(self):
        # print("self.email:",self.email)
        # print("self.password:",self.password)
        token = self.get_token(email=self.email, password=self.password)
        if token:
            self.token = token
        else:
            raise Exception("No token")

    def get_token(self, email, password):
        path = '/auth/email/login'
        response = self._curl_client(
            path=path,
            postdict={
                "email": email,
                "password": password
            },
            verb="POST"
        )
        token = ""
        if "success" in response:
            token = response["data"]["token"]["access_token"]
        return token

    def get_balace(self):
        path = '/spots/balance/query'
        response = self._curl_client(
            path=path,
            postdict={
                "id": 1000000015,
                "params": []
            },
            verb="POST"
        )
        if "error" in response and response["error"] == None:
            return response["result"]
        return []

    def get_depath_info(self, symbol):
        depath_info = self.ws.get_depath(symbol)
        return depath_info

    def get_deal_order_info(self, start_time, finish_time, side, offset=0, limit=10):
        # todo：待处理
        orders = []
        return orders

    def create_order(self, order):
        """Create multiple orders."""
        path = "/spots/order/put_limit"
        if "market" not in order:
            order["market"] = self.client_symbol
        postdict = order
        return self._curl_client(path=path, postdict=postdict, verb="POST")

    def http_open_orders(self, offset=0, limit=10):
        orders = []
        """Get open orders via HTTP. Used on close to ensure we catch them all."""
        path = '/spots/order/pending'
        response = self._curl_client(
            path=path,
            postdict={
                "id": 1000000001,
                "market": self.client_symbol,
                "offset": offset,
                "limit": limit
            },
            verb="POST"
        )
        if "result"in response and response["result"]:
            orders.extend(response["result"]["records"])
            total_order_num = response["result"]["total"]
            offset_amount = math.ceil(total_order_num / limit)
            for off in range(1, offset_amount):
                response = self._curl_client(
                    path=path,
                    postdict={
                        "id": 1000000001,
                        "market": self.client_symbol,
                        "offset": off * limit,
                        "limit": limit
                    },
                    verb="POST"
                )
                if "result" in response and response["result"]:
                    orders.extend(response["result"]["records"])
        return orders

    def cancel_order(self, orderid):
        """Cancel an existing order."""
        path = "/spots/order/cancel"
        postdict = {
            "id": 1000000002,  # 这个其实是标识哪次请求，前端创造的
            'order': orderid,
            'market': self.client_symbol
        }
        return self._curl_client(path=path, postdict=postdict, verb="POST")

    def _curl_client(self, path, query=None, postdict=None, timeout=None, verb=None, rethrow_errors=False,
                     max_retries=None):
        """Send a request to client Servers."""
        # Handle URL
        url = self.client_http_url + path

        if timeout is None:
            timeout = self.timeout

        # Default to POST if data is attached, GET otherwise
        if not verb:
            verb = 'POST' if postdict else 'GET'

        if max_retries is None:
            max_retries = 0 if verb in ['POST', 'PUT'] else 3

        header = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer {}".format(self.token),
        }

        def exit_or_throw(e):
            if rethrow_errors:
                raise e
            else:
                exit(1)

        def retry():
            self.retries += 1
            if self.retries > max_retries:
                raise Exception("Max retries on %s (%s) hit, raising." % (path, json.dumps(postdict or '')))
            return self._curl_client(path, query, postdict, timeout, verb, rethrow_errors, max_retries)

        # Make the request
        response = ""

        try:

            # print("url:{}---->postdict:{}".format(url,postdict))
            response = requests.request(verb, url, json=postdict, headers=header, params=query)
            # prepped = self.session.prepare_request(req)

            response.raise_for_status()

        except requests.exceptions.HTTPError as e:


            # 401 - Auth error. This is fatal.
            if response.status_code == 401:
                self.logger.error("API Key or Secret incorrect, please check and restart.")
                self.logger.error("Error: " + response.text)
                if postdict:
                    self.logger.error(postdict)
                # Always exit, even if rethrow_errors, because this is fatal
                exit(1)

            # 404, can be thrown if order canceled or does not exist.
            elif response.status_code == 404:
                if verb == 'DELETE':
                    self.logger.error("Order not found: %s" % postdict['orderID'])
                    return
                self.logger.error("Unable to contact the client API (404). " +
                                  "Request: %s \n %s" % (url, json.dumps(postdict)))
                exit_or_throw(e)

            # 429, ratelimit; cancel orders & wait until X-RateLimit-Reset
            elif response.status_code == 429:
                self.logger.error("Ratelimited on current request. Sleeping, then trying again. Try fewer " +
                                  "order pairs or contact support@client.com to raise your limits. " +
                                  "Request: %s \n %s" % (url, json.dumps(postdict)))

                # Figure out how long we need to wait.
                ratelimit_reset = response.headers['X-RateLimit-Reset']
                to_sleep = int(ratelimit_reset) - int(time.time())
                reset_str = datetime.datetime.fromtimestamp(int(ratelimit_reset)).strftime('%X')

                # We're ratelimited, and we may be waiting for a long time. Cancel orders.
                self.logger.warning("Canceling all known orders in the meantime.")
                self.cancel([o['orderID'] for o in self.open_orders()])

                self.logger.error("Your ratelimit will reset at %s. Sleeping for %d seconds." % (reset_str, to_sleep))
                time.sleep(to_sleep)

                # Retry the request.
                return retry()

            # 503 - client temporary downtime, likely due to a deploy. Try again
            elif response.status_code == 503:

                time.sleep(3)
                return retry()

            elif response.status_code == 400:
                error = response.json()['error']
                message = error['message'].lower() if error else ''

                # Duplicate clOrdID: that's fine, probably a deploy, go get the order(s) and return it
                if 'duplicate clordid' in message:
                    orders = postdict['orders'] if 'orders' in postdict else postdict

                    IDs = json.dumps({'clOrdID': [order['clOrdID'] for order in orders]})
                    orderResults = self._curl_client('/order', query={'filter': IDs}, verb='GET')

                    for i, order in enumerate(orderResults):
                        if (
                                order['orderQty'] != abs(postdict['orderQty']) or
                                order['side'] != ('Buy' if postdict['orderQty'] > 0 else 'Sell') or
                                order['price'] != postdict['price'] or
                                order['symbol'] != postdict['symbol']):
                            raise Exception(
                                'Attempted to recover from duplicate clOrdID, but order returned from API ' +
                                'did not match POST.\nPOST data: %s\nReturned order: %s' % (
                                    json.dumps(orders[i]), json.dumps(order)))
                    # All good
                    return orderResults

                elif 'insufficient available balance' in message:
                    self.logger.error('Account out of funds. The message: %s' % error['message'])
                    exit_or_throw(Exception('Insufficient Funds'))

            # If we haven't returned or re-raised yet, we get here.
            self.logger.error("Unhandled Error: %s: %s" % (e, response.text))
            self.logger.error("Endpoint was: %s %s: %s" % (verb, path, json.dumps(postdict)))
            exit_or_throw(e)

        except requests.exceptions.Timeout as e:
            # Timeout, re-run this request
            self.logger.warning("Timed out on request: %s (%s), retrying..." % (path, json.dumps(postdict or '')))
            try:
                retry()
            except:
                print("retry error")
                return response

        except requests.exceptions.ProxyError as e:
            self.logger.warning("Unable to contact the client API (%s). Please check the URL. Retrying. " +
                                "Request: %s %s \n %s" % (e, url, json.dumps(postdict)))
            time.sleep(1)
            try:
                retry()
            except:
                print("retry error")
                return response
        except Exception as e:
            print("_curl_client  except Exception as e:",e)



        # Reset retry counter on success
        self.retries = 0

        if response:
            response=response.json()
            print("url---------->:{},----------------->postdic:{}---------response----->:{}".format(url,postdict,response))
        return response
