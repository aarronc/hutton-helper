"""
Provides base classes for Hutton Helper plugins.

Each is almost an EDMC plugin in its own right.
"""

import json
import sys
try:
    # for python 2
    import UserDict
    is2 = True # used to check if is python2
except ImportError:
    # for python 3
    from collections import UserDict
    from collections import MutableMapping as DictMixin
    from collections import MutableMapping
    import collections
    is2 = False # used to check if is python2


def add_config_prefix(key):
    "Transform ``key`` for the EDMC ``config``."

    return 'HuttonHelper{}'.format(key)


class HuttonHelperPreferences(UserDict.DictMixin if is2 else collections.MutableMapping):
    """
    Stores Hutton Helper preferences in EDMC config.

    This class pretends to be a normal Python ``dict``. That kind of trick
    makes this class a little harder to maintain, but makes code that uses
    it easier to maintain.

    The awful doc-strings come straight from Python.

    Treats ``None`` as equivalent to deletion.
    """

    old_int_prefs_to_delete = [
        'ShowExploProgress',
        'ShowCargoProgress',
        'ShowMissionProgress',
        'ShowCombatProgress',
        'ShowExploValue',
    ]

    def __init__(self, config):
        "Initialise the ``HuttonHelperPreferences``."

        self.__config = config
        self.__prefs = set()
        #for key in self.old_int_prefs_to_delete:    #This broke in v5 deleting old keys not there
            #self.__config.delete(key)

    def __getitem__(self, pref):
        "Get a preference."

        value = self.__config.get_str(add_config_prefix(pref))
        if value is None:
            raise KeyError(pref)
        else:
            self.__prefs.add(pref)  # Surprise!
        return json.loads(value)

    def __setitem__(self, pref, value):
        "Set a preference to a JSON serialisable value."

        if value is None:
            del self[pref]
        else:
            self.__config.set(add_config_prefix(pref), json.dumps(value))
            self.__prefs.add(pref)

    def __delitem__(self, pref):
        "Delete a preference."

        self.__prefs.remove(pref)
        self.__config.delete(add_config_prefix(pref))

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)

    def keys(self):
        "Return a set of all currently known preferences."

        return self.__prefs.copy()


class HuttonHelperHelper(object):
    "A support object for a Hutton Helper plugin."

    def __init__(self, config, refresh, status):
        "Initialise the ``HuttonHelperHelper``."

        self.prefs = HuttonHelperPreferences(config)
        self.refresh = refresh
        self.status = status


class HuttonHelperPlugin(object):
    "A Hutton Helper plugin. Looks and smells pretty much like an EDMC plugin."

    # Call self.helper.refresh() when you change either of:

    hidden = False   # set True if you're disabled
    ready = True     # set False if you're not ready yet

    def __init__(self, helper):
        "Initialise the ``HuttonHelperPlugin``."
        assert isinstance(helper, HuttonHelperHelper)
        self.helper = helper

    def plugin_start(self):
        "Called once at startup. Try to keep it short..."
        pass

    def plugin_stop(self):
        "Called once at shutdown."
        pass

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Called each time the user opens EDMC settings. Return an ``nb.Frame``."
        pass

    def prefs_changed(self, cmdr, is_beta):
        "Called when the user clicks OK on the settings dialog."
        pass

    def plugin_app(self, parent):
        "Called once to get the plugin widget. Return a ``tk.Frame``."
        pass

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."
        pass

    def dashboard_entry(self, cmdr, is_beta, entry):
        "Called anywhere up to once a second with flight telemetry."
        pass

    def cmdr_data(self, data, is_beta):
        "Called shortly after startup with a dump of information from Frontier."
        pass

    # TODO prefs_cmdr_changed
    # TODO system_changed

    def __hash__(self):
        "Return our ``id`` as our hash so we can be used as a dict key."
        return id(self)

    def __eq__(self, other):
        "Compare us to another ``HuttonHelperPlugin`` so we can be used as a dict key."
        return other is self

    def __str__(self):
        "Convert us into a string."
        return self.__class__.__name__

    def refresh(self):
        "Refresh our display based on our ``hidden`` and ``enabled`` properties."
        self.helper.refresh()

    @property
    def config(self):
        "Return our configuration object."
        return self.helper.config
