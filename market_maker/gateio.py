"""GateIo API Connector."""
from __future__ import absolute_import
import requests
import logging
from market_maker.utils import constants, errors
from market_maker.ws.gateio_ws_thread import GateioWebsocket


class GateIo(object):

    """GateIo API Connector."""

    def __init__(self, base_url=None, symbol=None,  timeout=7):
        """Init connector."""
        self.logger = logging.getLogger('root')
        self.base_url = base_url
        self.symbol = symbol


        self.retries = 0  # initialize counter


        # Create websocket for streaming data
        self.ws = GateioWebsocket()
        self.ws.connect(base_url, symbol)

        self.timeout = timeout

    def __del__(self):
        self.exit()

    def exit(self):
        pass

    #
    # Public methods
    #
    def ticker_data(self):
        """Get ticker data."""

        return self.ws.get_ticker()









