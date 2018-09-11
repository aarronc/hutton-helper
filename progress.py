"""
Track the trucker's progress.
"""

import collections
import time
import Tkinter as tk

import plugin
import xmit

import myNotebook as nb

COLUMNS = ['today', 'week'] # 'total' also works

ROW_CONFIGURATION = [
    ("Jumps", 'Jumps', 'ShowExploProgress'),
    ("Light Years", 'LY', 'ShowExploProgress'),
    ("Scanned Objects", 'ScannedObjects', 'ShowExploProgress'),
    ("Data Sold (CR)", 'Exploration', 'ShowExploProgress'),

    ("Cargo Bought (t)", 'CargoBought', 'ShowCargoProgress'),
    ("Cargo Sold (t)", 'CargoSold', 'ShowCargoProgress'),
    ("Cargo Smuggled (t)", 'SmuggledCargo', 'ShowCargoProgress'),

    ("Missions (points)", 'Mission', 'ShowMissionProgress'),
    ("Passengers (count)", "PassengersTransported", "ShowMissionProgress"),

    ("Bounties (CR)", 'Bounty', 'ShowCombatProgress'),
    ("Combat Bonds (CR)", 'CombatBonds', 'ShowCombatProgress'),
    ("Thargoids (count)", 'ThargoidsKilled', 'ShowCombatProgress'),
]


def capitalise(word):
    "Capitalise the ``word``."
    return word[:1].upper() + word[1:]


def render(value):
    "Render a ``value`` for display."

    if isinstance(value, float):
        return '{:,.0f}'.format(value)

    elif value is None:
        return '-'

    else:
        return str(value)


def varname(varbase, when):
    "Determine a variable name for the JSON."

    if when is 'today':
        when = 'day'

    return '{}{}'.format(varbase, capitalise(when))


class ProgressDisplay(tk.Frame):
    "Displays progress."

    def __init__(self, parent, helper=None, **kwargs):
        "Initialise the ``ProgressDisplay``."

        tk.Frame.__init__(self, parent, relief=tk.SUNKEN, **kwargs)
        self.columnconfigure(0, weight=1)

        self.helper = helper
        self.cmdr = None
        self.textvariables = {}

        self.heading_labels = list(self.__create_headings())
        self.row_labels = list(self.__create_rows())
        self.footer_label = self.__create_footer()

        self.data = None
        self.update()

    def __create_headings(self):
        "Create labels for the headings."

        yield tk.Label(self, text="Progress:", anchor=tk.W)
        for when in COLUMNS:
            yield tk.Label(self, text=capitalise(when), anchor=tk.E)

    def __create_rows(self):
        "Create labels for each row."

        for title, varbase, _configvar in ROW_CONFIGURATION:
            yield list(self.__create_row_cells(title, varbase))

    def __create_row_cells(self, title, varbase):
        "Create labels for one row."

        yield tk.Label(self, text=title, anchor=tk.W)
        for when in COLUMNS:
            key = varname(varbase, when)
            textvariable = self.textvariables[key] = tk.StringVar(value='-')
            yield tk.Label(self, textvariable=textvariable, anchor=tk.E)

    def __create_footer(self):
        "Create our footer."

        return tk.Label(self, text="Progress display not ready.", anchor=tk.W)

        self.data = None

    def update(self, data=None):
        "Update our display based on the config."

        # This wasn't this complicated until I decided I wanted to show
        # truckers each line only if there was data AND they'd made some
        # progress AND they were interested in seeing it.

        if data:
            self.data = data

        any_enabled_has_progress = False
        sticky = tk.EW

        for idx, (_title, varbase, configvar) in enumerate(ROW_CONFIGURATION):
            enabled = self.helper.config.getint(configvar)
            row_visible = False

            for column, when in enumerate(COLUMNS, start=1):
                key = varname(varbase, when)

                if self.data and key in self.data:
                    value = float(self.data[key])
                    has_progress = not not value

                else:
                    value = None
                    has_progress = False

                self.textvariables[key].set(render(value))

                if enabled:
                    any_enabled_has_progress = any_enabled_has_progress or has_progress

                    if has_progress:
                        row_visible = True

            for column, label in enumerate(self.row_labels[idx]):
                if row_visible:
                    label.grid(row=idx + 1, column=column, sticky=sticky)
                else:
                    label.grid_forget()

        self.__display_header_and_footer(any_enabled_has_progress)

        return not not self.data

    def __display_header_and_footer(self, any_has_progress):
        "Display the header and footer."

        footer_row = len(ROW_CONFIGURATION) + 1

        if any_has_progress:
            self.footer_label.grid_forget()
            for column, label in enumerate(self.heading_labels):
                label.grid(row=0, column=column, sticky=tk.EW)

        else:
            for label in self.heading_labels:
                label.grid_forget()

            if self.data:
                self.footer_label['text'] = "No progress this week. Get truckin'!"

            else:
                self.footer_label['text'] = "Progress display not ready."  # not shown because ``not ready```

            self.footer_label.grid(row=footer_row, column=0, columnspan=1 + len(COLUMNS), sticky=tk.EW)


class ProgressPlugin(plugin.HuttonHelperPlugin):
    "Provides progress updates."

    fetch_events = set([
        'FSDJump',
        'MarketBuy',
        'MarketSell',
        'MissionCompleted',
        'RedeemVoucher',
        'Scan',
        'SellExplorationData',
    ])

    config_intvars = [
        # I wanted this to be a dictionary, but couldn't preserve the order without stunt coding
        ('ShowExploProgress', "Show Exploration Progress"),
        ('ShowCargoProgress', "Show Cargo Hauling Progress"),
        ('ShowMissionProgress', "Show Mission Progress"),
        ('ShowCombatProgress', "Show Combat Progress")
    ]

    def __init__(self, helper):
        "Initialise the ``ProgressPlugin``."

        plugin.HuttonHelperPlugin.__init__(self, helper)

        self.display = None
        self.data = None
        self.cmdr = None

    def __reset(self, cmdr=None):
        "Reset our numbers to switch commander."

        self.cmdr = cmdr
        self.data = None

    def journal_entry(self, cmdr, _is_beta, _system, _station, entry, _state):
        "Act like a tiny EDMC plugin. Forward events to our ``TRACKERS``."

        if self.cmdr != cmdr or entry['event'] == 'ShutDown':
            self.__reset(cmdr=cmdr)

        if self.data is None or entry['event'] in self.fetch_events:
            self.display.after(250, self.__fetch)

    def __fetch(self):
        "Fetch the data again."

        if not self.cmdr:
            return

        self.data = xmit.get('/day-week-stats.json/{}'.format(self.cmdr))
        if self.display:
            self.ready = self.display.update(self.data)
            self.refresh()

    def plugin_app(self, parent):
        "Called once to get the plugin widget. Return a ``tk.Frame``."

        self.display = ProgressDisplay(parent, helper=self.helper)
        self.ready = self.display.update()
        self.__initialise_prefs()
        return self.display

    def __initialise_prefs(self):
        "Initialise the preference system."

        self.prefs_vars = {}
        all_disabled = True

        for key, text in self.config_intvars:
            enabled = self.config.getint(key)
            all_disabled = all_disabled and not enabled
            self.prefs_vars[key] = variable = tk.IntVar(value=enabled)

        self.hidden = all_disabled

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Called each time the user opens EDMC settings. Return an ``nb.Frame``."

        frame = nb.Frame(parent)
        frame.columnconfigure(0, weight=1)
        nb.Label(frame, text="Progress Display Options :-").grid(sticky=tk.W)

        for key, text in self.config_intvars:
            variable = self.prefs_vars[key]
            nb.Checkbutton(frame, text=text, variable=variable).grid(sticky=tk.W)

        return frame

    def prefs_changed(self, _cmdr, _is_beta):
        "Called when the user clicks OK on the settings dialog."

        all_disabled = True
        for key, _text in self.config_intvars:
            enabled = self.prefs_vars[key].get()
            all_disabled = all_disabled and not enabled
            self.config.set(key, enabled)

        self.hidden = all_disabled
        self.ready = self.display.update()
