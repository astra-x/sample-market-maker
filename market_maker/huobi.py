"""Huobi API Connector."""
from __future__ import absolute_import
import logging
from market_maker.ws.huobi_ws_thread import  HuobiWebsocket


class Huobi(object):

    """GateIo API Connector."""

    def __init__(self, base_url=None):
        """Init connector."""
        self.logger = logging.getLogger('root')
        self.base_url = base_url
        # Create websocket for streaming data
        self.ws = HuobiWebsocket()
        self.ws.connect(base_url)

    def __del__(self):
        self.exit()

    def exit(self):
        self.ws.exit()

    # Public methods

    def get_depath(self):

        return self.ws.get_depath()
