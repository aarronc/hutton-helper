"""
Provides base classes for Hutton Helper plugins.

Each is almost an EDMC plugin in its own right.
"""


class HuttonHelperHelper(object):
    "A support object for a Hutton Helper plugin."

    def __init__(self, config, refresh, status):
        "Initialise the ``HuttonHelperHelper``."

        self.config = config
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

    @property
    def get_status(self):
        "Get the status via the helper."
        return self.helper.status['text']

    @get_status.setter
    def set_status(self, text):
        "Set the status via the helper."
        self.helper.status['text'] = text
