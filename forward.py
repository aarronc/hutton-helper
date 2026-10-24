"""
Broadcasts to the Hutton Helper web site.
"""

from hutton_helper_version import HH_VERSION

import json
import re
from threading import Thread
import zlib

import plugin
import xmit

ADDITIONAL_PATHS_URL = '/event_paths.json'
EVENT_NAME_PATTERN = re.compile(r'[A-Z][A-Za-z0-9]*')
HANDLER_PATH_PATTERN = re.compile(r'/[a-z]+')
logger = xmit.logger
SENDTEXT_ALLOWED_RECIPIENTS = frozenset({'local', 'starsystem', 'squadron'})
RECEIVETEXT_REQUIRED_WORD = re.compile(r'\bmug\b', re.IGNORECASE)

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
        Thread(
            target=self._load_additional_paths,
            name='HuttonHelperEventPaths',
            daemon=True,
        ).start()

    def _load_additional_paths(self):
        extra_paths = xmit.get(ADDITIONAL_PATHS_URL)

        if isinstance(extra_paths, dict):
            valid_paths = {}
            rejected_count = 0

            for event, handler in extra_paths.items():
                if (
                    isinstance(event, str)
                    and EVENT_NAME_PATTERN.fullmatch(event)
                    and isinstance(handler, str)
                    and HANDLER_PATH_PATTERN.fullmatch(handler)
                ):
                    valid_paths[event] = handler
                else:
                    rejected_count += 1

            if rejected_count:
                logger.warning(
                    "Rejected %d invalid event path entr%s",
                    rejected_count,
                    'y' if rejected_count == 1 else 'ies',
                )

            self.event_paths = merge_dicts(self.event_paths, valid_paths)
        elif extra_paths is not None:
            logger.warning("Ignoring invalid event paths response: expected a JSON object")


    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        event = entry['event']
        
        # Filter out unwanted SendText events
        if event == 'SendText':
            send_to = entry.get('To', '').casefold()
            if send_to not in SENDTEXT_ALLOWED_RECIPIENTS:
                return  # Drop it and exit the function
        elif event == 'ReceiveText':
            message = entry.get('Message', '')
            if not isinstance(message, str) or not RECEIVETEXT_REQUIRED_WORD.search(message):
                return

        event_path = self.event_paths.get(event)
        if not event_path:
            return

        compress_json = json.dumps(entry)
        transmit_json = zlib.compress(compress_json.encode('utf-8'))
        logger.debug("Sending journal event %s to %s", event, event_path)
        xmit.post(event_path, data=transmit_json, parse=False, headers=xmit.COMPRESSED_OCTET_STREAM)
