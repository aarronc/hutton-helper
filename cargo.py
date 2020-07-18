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

cargodump = {}

class CargoPlugin(plugin.HuttonHelperPlugin):
    "Forwards cargo data to the Helper back end and other plugins within the helper"

    hidden = True  # invisible
    ready = True  # always

    def __init__(self, helper):
        "Initialise the ``CargoPlugin``."

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        if entry['event'] == 'Cargo':
            dump_path = data.get_journal_path('Cargo.json')
            # sys.stderr.write("Reading cargo data from: {}\r\n".format(dump_path))
            with open(dump_path, 'r') as dump:
                dump = dump.read()
                dump = json.loads(dump)
                cargodump = dump
                dump['commandername'] = cmdr
                compress_json = json.dumps(dump)
                cargo_data = zlib.compress(compress_json.encode('utf-8'))
                # sys.stderr.write("Posting it...\r\n")
                xmit.post('/missioncargo', cargo_data, headers=xmit.COMPRESSED_OCTET_STREAM)
                # self.helper.status("Market data posted.")
        else:
            return
