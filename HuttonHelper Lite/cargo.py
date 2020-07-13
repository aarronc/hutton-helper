"""
Cargo Submission for Mission Helper
"""

import sys
import zlib
import time
import json

import data
import plugin
import xmit


class CargoPlugin(plugin.HuttonHelperPlugin):
    "Forwards cargo data to the Helper back end."

    hidden = True  # invisible
    ready = True  # always

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        # if entry['event'] == 'MarketBuy' or entry['event'] == 'MarketSell' or entry['event'] == 'MissionCompleted' :  # requires specific events
        if entry['event'] == 'Cargo':
            # time.sleep(2.5)
            dump_path = data.get_journal_path('Cargo.json')
            # sys.stderr.write("Reading market data from: {}\r\n".format(dump_path))
            with open(dump_path, 'r') as dump:
                dump = dump.read()
                dump = json.loads(dump)
                dump['commandername'] = cmdr
                dump = json.dumps(dump)
                cargo_data = zlib.compress(dump)
                # sys.stderr.write("Posting it...\r\n")
                xmit.post('/missioncargo', cargo_data, headers=xmit.COMPRESSED_OCTET_STREAM)
                # self.helper.status("Market data posted.")
        else:
            return
