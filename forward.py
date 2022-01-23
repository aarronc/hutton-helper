"""
Broadcasts to the Hutton Helper web site.
"""

from version import HH_VERSION

import json
import zlib

import plugin
import xmit

ADDITIONAL_PATHS_URL = 'http://hot.forthemug.com/event_paths.json'

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

class ForTheMugPlugin(plugin.HuttonHelperPlugin):
    "Forwards data to the Hutton Helper Server."

    from big_dicts import EVENT_PATHS as event_paths

    def plugin_start(self):
        "Called once at startup. Try to keep it short..."
        extra_paths = xmit.get(ADDITIONAL_PATHS_URL)

        if extra_paths is not None:
            self.event_paths = merge_dicts(self.event_paths, extra_paths)


    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        event = entry['event']
        event_path = self.event_paths.get(event)

        compress_json = json.dumps(entry)
        transmit_json = zlib.compress(compress_json.encode('utf-8'))

        if event_path:
            xmit.post(event_path, data=transmit_json, parse=False, headers=xmit.COMPRESSED_OCTET_STREAM)
