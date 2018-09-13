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


CFG_SHOW_SHOPPING = 'ShowShoppingList'
STALE_AFTER_SECONDS = 5


class ShoppingListPlugin(plugin.HuttonHelperPlugin):
    "Tracks mission shopping lists."

    def __init__(self, config):
        "Initialise the ``ShoppingListPlugin``."

        plugin.HuttonHelperPlugin.__init__(self, config)
        self.table_frame = None
        self.items = []
        self.visible_count = 0

    def plugin_app(self, parent):
        "Called once to get the plugin widget. Return a ``tk.Frame``."

        frame = tk.Frame(parent)
        frame.columnconfigure(0, weight=1)

        tk.Frame(frame, highlightthickness=1).grid(pady=5, sticky=tk.EW)
        self.heading = ttk.Label(frame, text="[SHOPPING LIST]", anchor=tk.NW)
        self.heading.grid(sticky=tk.EW)

        self.table_frame = tk.Frame(frame)
        self.table_frame.grid(sticky=tk.EW)

        enabled = self.helper.prefs.setdefault(CFG_SHOW_SHOPPING, True)
        self.enabled_intvar = tk.IntVar(value=1 if enabled else 0)
        self.__update_hidden()

        # frame.after(5000, self.fake_an_entry)

        return frame

    def fake_an_entry(self):
        "Fake an entry for testing purposes."
        entry = {
            'event': 'MissionAccepted',
            'Commodity_Localised': 'Consumer Technology',
            'Count': 2,
        }
        self.journal_entry(None, False, None, None, entry, None)

    def journal_entry(self, cmdr, _is_beta, _system, _station, entry, _state):
        "Act like a tiny EDMC plugin."

        if entry['event'] != 'MissionAccepted':
            return

        text = entry.get('Commodity_Localised')
        count = entry.get('Count')

        if not text and count:
            return

        intvar = tk.IntVar(value=0)
        intvar.trace('w', lambda _x, _y, _z: self.refresh())

        checkbutton = ttk.Checkbutton(
            self.table_frame,
            text='{}X {}'.format(count, text),
            variable=intvar,
            style='HH.TCheckbutton'
        )
        self.items.append(dict(
            text=text,
            count=count,
            intvar=intvar,
            checkbutton=checkbutton,
        ))
        self.refresh()

    def refresh(self):
        "Refresh our display."

        self.visible_count = 0
        for row, entry in enumerate(self.items):
            hidden = False

            if entry['intvar'].get():
                if 'checked_when' in entry:
                    if time.time() > entry['checked_when'] + STALE_AFTER_SECONDS:
                        hidden = True

                else:
                    entry['checked_when'] = time.time()
                    self.table_frame.after(500 + STALE_AFTER_SECONDS * 1000, self.refresh)

            else:
                if 'checked_when' in entry:
                    del entry['checked_when']

            if hidden:
                entry['checkbutton'].grid_forget()

            else:
                self.visible_count = self.visible_count + 1
                entry['checkbutton'].grid(row=row, column=0, sticky=tk.EW)

        if self.visible_count == 1:
            self.heading['text'] = "Stock up for that mission, Commander!"
        else:
            self.heading['text'] = "Stock up for those missions, Commander!"

        self.__update_hidden()
        plugin.HuttonHelperPlugin.refresh(self)

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Called each time the user opens EDMC settings. Return an ``nb.Frame``."

        prefs_frame = nb.Frame(parent)
        prefs_frame.columnconfigure(0, weight=1)

        nb.Label(prefs_frame, text="Shopping List Options :-").grid(row=0, column=0, sticky=tk.W)
        nb.Checkbutton(
            prefs_frame,
            text="Pop Up Shopping List When Appropriate",
            variable=self.enabled_intvar
        ).grid(row=1, column=0, sticky=tk.W)

        return prefs_frame

    def prefs_changed(self, cmdr, is_beta):
        "Called when the user clicks OK on the settings dialog."

        self.helper.prefs[CFG_SHOW_SHOPPING] = bool(self.enabled_intvar.get())
        self.__update_hidden()

    def __update_hidden(self):
        "Update whether we're hidden."

        self.hidden = not (self.visible_count and self.enabled_intvar.get())
