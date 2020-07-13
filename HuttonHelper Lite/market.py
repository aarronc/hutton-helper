"""
Tracks the market.
"""

import sys
import zlib

import data
import plugin
import xmit


class MarketPlugin(plugin.HuttonHelperPlugin):
    "Forwards market data to the Helper back end. Might, later, keep track locally."

    hidden = True  # invisible
    ready = True  # always

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        if entry['event'] != 'Market':  # requires accessing the commodity market in station
            return

        dump_path = data.get_journal_path('Market.json')
        # sys.stderr.write("Reading market data from: {}\r\n".format(dump_path))
        with open(dump_path, 'rb') as dump:
            market_data = zlib.compress(dump.read())
            # sys.stderr.write("Posting it...\r\n")
            xmit.post('/market', market_data, headers=xmit.COMPRESSED_OCTET_STREAM)
            # self.helper.status("Market data posted.")
