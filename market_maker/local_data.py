"""GateIo API Connector."""
from __future__ import absolute_import
import requests
import logging
from market_maker.utils import constants, errors
from market_maker.local_http.local_http_thread import LocalHttpDataServer


class LocalData(object):

    """GateIo API Connector."""

    def __init__(self, base_url=None, symbol=None):
        """Init connector."""
        self.logger = logging.getLogger('root')
        self.base_url = base_url
        self.symbol = symbol
        self.local_data=LocalHttpDataServer(url=self.base_url)



    def __del__(self):
        self.exit()

    def exit(self):
        self.local_data.exit()

    #
    # Public methods

    def ticker_data(self):
        """Get ticker data."""

        return self.local_data.get_ticker()











