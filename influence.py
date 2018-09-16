"""
You'd better stock up on land mines for that trip, Commander.
"""

import json
import sys
import time
import Tkinter as tk
import ttk

import plugin

import myNotebook as nb


CFG_SHOW_INFLUENCE = 'ShowInfluence'
STALE_AFTER_SECONDS = 5
FACTIONS = set([
    'HOTCOL',
    'Hutton Orbital Truckers Co-Operative'
])


class InfluencePlugin(plugin.HuttonHelperPlugin):
    "Tracks mission shopping lists."

    def __init__(self, config):
        "Initialise the ``InfluencePlugin``."

        plugin.HuttonHelperPlugin.__init__(self, config)
        self.label = None
        self.in_faction_space = False

    def plugin_app(self, parent):
        "Called once to get the plugin widget. Return a ``tk.Frame``."

        frame = tk.Frame(parent)
        frame.columnconfigure(0, weight=1)  # system name
        frame.columnconfigure(1, weight=1)  # system state

        tk.Frame(frame, highlightthickness=1).grid(pady=5, columnspan=4, sticky=tk.EW)  # divider

        self.system_label = ttk.Label(frame, text="SYSTEM", anchor=tk.NW)
        self.state_label = ttk.Label(frame, text="STATE", anchor=tk.NW)
        self.influence_label = ttk.Label(frame, text="23.0%", anchor=tk.NE)
        self.margin_label = ttk.Label(frame, text="(+2%)", anchor=tk.NE)

        self.system_label.grid(row=1, column=0, sticky=tk.EW)
        self.state_label.grid(row=1, column=1, sticky=tk.EW)
        self.influence_label.grid(row=1, column=2, sticky=tk.EW)
        self.margin_label.grid(row=1, column=3, sticky=tk.EW)

        enabled = self.helper.prefs.setdefault(CFG_SHOW_INFLUENCE, True)
        self.enabled_intvar = tk.IntVar(value=1 if enabled else 0)
        self.__update_hidden()

        # frame.after(5000, self.fake_an_entry)

        return frame

    def fake_an_entry(self):
        "Fake an entry for testing purposes."

        sys.stderr.write("Faking an entry...\r\n")
        entry = {
            'event': 'FSDJump',
            'StarSystem': 'Ross 671',
            'SystemAddress': 13864825529769,
            'StarPos': [-17.53125, -13.84375, 0.62500],
            'Factions': [{
                'Name': 'Social Ross 671 for Equality',
                'FactionState': 'Boom',
                'Influence': 0.176647,
            }, {
                'Name': 'Hutton Orbital Truckers Co-Operative',
                'FactionState': 'None',
                'Influence': 0.323353,
            }],
            'SystemFaction': 'Social Ross 671 for Equality'
        }
        self.journal_entry(None, False, None, None, entry, None)

    def journal_entry(self, cmdr, _is_beta, _system, _station, entry, _state):
        "Act like a tiny EDMC plugin."

        if entry['event'] == 'FSDJump':
            influence_them = float('-inf')
            influence_us = float('-inf')
            state_us = ""

            for faction in entry['Factions']:
                if faction['Name'] in FACTIONS:
                    influence_us = faction['Influence']
                    state_us = faction['FactionState']
                else:
                    influence_them = max([influence_them, faction['Influence']])

            self.system_label['text'] = entry['StarSystem']
            self.in_faction_space = not (influence_us < 0)

            if self.in_faction_space:
                self.state_label['text'] = state_us
                self.influence_label['text'] = '{:.1f}%'.format(100 * influence_us)
                self.margin_label['text'] = '(by {:.1f}%)'.format(100 * (influence_us - influence_them))

            else:
                self.state_label['text'] = 'N/A'
                self.influence_label['text'] = 'N/A'
                self.margin_label['text'] = 'N/A'

            self.__update_hidden()

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Called each time the user opens EDMC settings. Return an ``nb.Frame``."

        prefs_frame = nb.Frame(parent)
        prefs_frame.columnconfigure(0, weight=1)

        nb.Label(prefs_frame, text="Background Simulator Fan Options :-").grid(row=0, column=0, sticky=tk.W)
        nb.Checkbutton(
            prefs_frame,
            text="Show influence in Hutton space",
            variable=self.enabled_intvar
        ).grid(row=1, column=0, sticky=tk.W)

        return prefs_frame

    def prefs_changed(self, cmdr, is_beta):
        "Called when the user clicks OK on the settings dialog."

        self.helper.prefs[CFG_SHOW_INFLUENCE] = bool(self.enabled_intvar.get())
        self.__update_hidden()

    def __update_hidden(self):
        "Update whether we're hidden."

        self.hidden = not (self.in_faction_space and self.enabled_intvar.get())
