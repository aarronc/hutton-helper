"""
You'd better stock up on land mines for that trip, Commander.
"""

try:
    # for Python2
    import Tkinter as tk
    import ttk
    import tkFont
except ImportError:
    # for python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as tkFont

import json
import data
import sys
import time

import plugin

try:
    import myNotebook as nb
except ImportError:
    pass  # trust that we're getting run as a script


CFG_SHOW_SHOPPING = 'ShowShoppingList'
STALE_AFTER_SECONDS = 5

TEST_EVENTS = [
    {
        'event': 'Cargo',
        'Inventory': [{
            'Count': 4,
            'Name_Localised': 'Uranium',
            'Name': 'uranium',
        }],
    },  # hidden
    {
        'event': 'MissionAccepted',
        'Commodity_Localised': 'Uranium',
        'Commodity': '$Uranium_Name',
        'Count': 25,
        'MissionID': 415110664,
        'Name': 'Mission_Collect',
    },  # 25, 4
    {
        'event': 'MissionAccepted',
        'Commodity_Localised': 'Uranium',
        'Commodity': '$Uranium_Name',
        'Count': 23,
        'MissionID': 415110665,
        'Name': 'Mission_Collect',
    },  # 48, 4
    {
        'event': 'MissionAccepted',
        'Commodity_Localised': 'Uranium',
        'Commodity': '$Uranium_Name',
        'Count': 22,
        'MissionID': 415110666,
        'Name': 'Mission_Collect',
    },  # 70, 4
    {
        'event': 'MissionAccepted',
        'Commodity_Localised': 'Uranium',
        'Commodity': '$Uranium_Name',
        'Count': 2,
        'MissionID': 415110667,
        'Name': 'Mission_Collect',
    },  # 72, 4
    {
        'event': 'MarketBuy',
        'Count': 27,
        'Type_Localised': 'Uranium',
        'Type': 'uranium',
    },  # 72, 31
    {
        'event': 'MarketBuy',
        'Count': 41,
        # 'Type_Localised': 'Uranium',  # sometimes, we don't get it
        'Type': 'uranium',
    },  # 72, 72
    {
        'event': 'CargoDepot',
        'Count': 25,
        'ItemsDelivered': 25,
        'MissionID': 415110664,
        'TotalItemsToDeliver': 25,
        'CargoType_Localised': 'Uranium',
        'CargoType': 'Uranium',
        'UpdateType': 'Deliver',
    },  # 47, 47
    {
        'event': 'MissionCompleted',
        'MissionID': 415110664,
    },  # 47, 47
    {
        'event': 'MarketSell',
        'Count': 1,
        'Type_Localised': 'Uranium',
        'Type': 'uranium',
    },  # 47, 46
    {
        'event': 'EjectCargo',
        'Count': 1,
        'Type_Localised': 'Uranium',
        'Type': 'uranium',
    },  # 47, 45
    {
        'event': 'MissionAbandoned',
        'MissionID': 415110667,
    },  # 45, 45
    {
        'event': 'Died'
    },  # 45, 0
    {
        'event': 'MissionFailed',
        'MissionID': 415110665,
    },  # 22, 0
    {
        'event': 'MiningRefined',
        'Type': 'Uranium' # I don't know if this actually happens, but bear with me
    },  # 22, 1
    {
        'event': 'CollectCargo',
        'Type': 'Uranium'
    },  # 22, 2
    {
        'event': 'Missions',
        'Active': [],
    },  # 0, 0
]

LOCALISATION_CACHE = {}


def _extract_commodity(entry):
    "Get the commodity type and localised description from an ``event`` entry."

    if 'Commodity' in entry:  # MissionAccepted
        commodity = entry['Commodity']
        if commodity[:1] == '$':  # $Uranium_Name;
            commodity = commodity[1:].split('_')[0]
        return commodity, entry.get('Commodity_Localised')

    if 'Type' in entry:  # MarketBuy, MarketSell, EjectCargo, MiningRefined
        return entry['Type'], entry.get('Type_Localised')

    elif 'CargoType' in entry:  # CargoDepot
        return entry['CargoType'], entry.get('CargoType_Localised')

    elif 'Name' in entry and 'event' not in entry:  # Cargo event Inventory entry
        return entry['Name'], entry.get('Name_Localised')

    sys.stderr.write("Entry: {}\r\n", entry)
    raise AssertionError("could not extract commodity details from entry")


def extract_commodity(entry):
    "Get the commodity type and localised description from an ``event`` entry, caching descriptions."

    commodity, commodity_localised = _extract_commodity(entry)

    if commodity:
        commodity = commodity.lower()

        if commodity_localised is None and commodity in LOCALISATION_CACHE:
            commodity_localised = LOCALISATION_CACHE[commodity]

        if commodity_localised is not None and commodity not in LOCALISATION_CACHE:
            LOCALISATION_CACHE[commodity] = commodity_localised

    return commodity, commodity_localised


class ShoppingListPlugin(plugin.HuttonHelperPlugin):
    "Tracks mission shopping lists."

    def __init__(self, helper):
        "Initialise the ``ShoppingListPlugin``."

        plugin.HuttonHelperPlugin.__init__(self, helper)
        self.table_frame = None
        self.missions = []
        self.cargo = {}
        self.visible_count = 0

    def plugin_app(self, parent):
        "Called once to get the plugin widget. Return a ``tk.Frame``."

        frame = tk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        tk.Frame(frame, highlightthickness=1).grid(pady=5, sticky=tk.EW)  # divider

        self.table_frame = tk.Frame(frame)
        self.table_frame.grid(sticky=tk.EW)
        self.table_frame.columnconfigure(0, weight=1)

        enabled = self.helper.prefs.setdefault(CFG_SHOW_SHOPPING, True)
        self.enabled_intvar = tk.IntVar(value=1 if enabled else 0)
        self.__update_hidden()

        # Uncomment the next line to replay TEST_EVENTS after startup:
        # frame.after(5000, self.__replay, TEST_EVENTS)

        return frame

    def __replay(self, entries):
        "Replay entries for development purposes."

        if entries:
            entries = entries[:]
            # This line below is why this method is easier to copy and paste into
            # each plugin than to make generic enough to pull to the base class:
            entry = entries.pop(0)
            print('=== replay', entry)
            self.journal_entry(None, False, None, None, entry, None)
            self.table_frame.after(500, self.__replay, entries)

    def journal_entry(self, cmdr, _is_beta, _system, _station, entry, _state):
        "Act like a tiny EDMC plugin."

        method = 'event_{}'.format(entry['event'].lower())
        if hasattr(self, method):
            getattr(self, method)(entry)
            self.refresh()

    def event_cargo(self, entry):
        "Handle ``Cargo``."

        self.cargo = {}
        cargo_path = data.get_journal_path('Cargo.json')
        # sys.stderr.write("Reading cargo data from: {}\r\n".format(dump_path))
        with open(cargo_path, 'r') as infile:
            cargodump = infile.read()
            cargodump = json.loads(cargodump)

        # TODO this is by the lowercase version FFS
        for item in cargodump['Inventory']:
            commodity, _desc = extract_commodity(item)
            count = item['Count']
            self.cargo[commodity] = count

    def event_cargodepot(self, entry):
        "Handle ``CargoDepot``."

        for mission in self.missions:
            if mission['mission_id'] == entry['MissionID']:
                mission['remaining'] = entry['TotalItemsToDeliver'] - entry['ItemsDelivered']

        self.event_cargo(entry)

        if 'Count' in entry and 'CargoType' in entry:
            # absent if a wing member dropped something off
            commodity, _desc = extract_commodity(entry)
            count = entry['Count']
            self.cargo[commodity] -= count

    def event_ejectcargo(self, entry):
        "Handle ``EjectCargo``."

        commodity, _desc = extract_commodity(entry)
        self.__remove_cargo(commodity, entry['Count'])

    def event_died(self, entry):
        "Handle ``Died``."

        self.cargo = {}

    def event_collectcargo(self, entry):
        "Handle ``CollectCargo``."

        commodity, _desc = extract_commodity(entry)
        self.__add_cargo(commodity, 1)

    def event_marketbuy(self, entry):
        "Handle ``MarketBuy``."

        commodity, _desc = extract_commodity(entry)
        self.__add_cargo(commodity, entry['Count'])

    def event_marketsell(self, entry):
        "Handle ``MarketSell``."

        commodity, _desc = extract_commodity(entry)
        self.__remove_cargo(commodity, entry['Count'])

    def event_miningrefined(self, entry):
        "Handle ``MiningRefined``."

        commodity, _desc = extract_commodity(entry)
        self.__add_cargo(commodity, 1)

    def event_missionaccepted(self, entry):
        "Handle ``MissionAccepted``."

        for prefix in ['mission_collect', 'mission_passengervip', 'mission_mining']:
            if entry['Name'].lower().startswith(prefix):
                break

        else: # nothing broke
            return

        commodity, _desc = extract_commodity(entry)
        remaining = entry['Count']
        mission_id = entry['MissionID']

        self.missions.append(dict(
            mission_id=mission_id,
            commodity=commodity,
            remaining=remaining,
        ))

    def event_missioncompleted(self, entry):
        "Handle ``MissionCompleted``."

        self.__remove_mission(entry['MissionID'])

    def event_missionfailed(self, entry):
        "Handle ``MissionFailed``."

        self.__remove_mission(entry['MissionID'])

    def event_missionabandoned(self, entry):
        "Handle ``MissionAbandoned``."

        self.__remove_mission(entry['MissionID'])

    def event_missions(self, entry):
        "Handle ``Missions``."

        known = set(mission['mission_id'] for mission in self.missions)
        active = set(mission['MissionID'] for mission in entry['Active'])

        for mission_id in known - active:
            self.__remove_mission(mission_id)

    def __add_cargo(self, commodity, count):
        "Remove some cargo."

        self.cargo[commodity] = self.cargo.get(commodity, 0) + count

    def __remove_cargo(self, commodity, count):
        "Remove some cargo."

        count = self.cargo.get(commodity, 0) - count
        if count < 0:
            count = 0
        self.cargo[commodity] = count

    def __remove_mission(self, mission_id):
        "Remove a mission."

        self.missions = [mission for mission in self.missions
                         if mission['mission_id'] != mission_id]

    def refresh(self):
        "Refresh our display."

        frame = self.table_frame

        for widget in frame.winfo_children():
            widget.destroy()

        by_com = {}
        for mission in self.missions:
            by_com.setdefault(mission['commodity'], []).append(mission)

        def gridlabel(**kw):
            "Make a grid label."
            return ttk.Label(frame, style='HH.TLabel', **kw)

        text = "Mission needs:" if len(self.missions) == 1 else "Missions need:"
        gridlabel(text=text, anchor=tk.W).grid(row=0, column=0, sticky=tk.EW)
        gridlabel(text="Remaining", anchor=tk.E).grid(row=0, column=1, sticky=tk.EW)
        gridlabel(text="In Cargo", anchor=tk.E).grid(row=0, column=2, sticky=tk.EW)

        normal = ttk.Style().configure('HH.TLabel').get('font', 'TkDefaultFont')
        if isinstance(normal, str):
            normal = tkFont.nametofont('TkDefaultFont')
        complete = normal.copy()
        complete['overstrike'] = 1

        for row, commodity in enumerate(sorted(by_com), start=1):
            description = LOCALISATION_CACHE.get(commodity, commodity.upper())
            remaining = sum(mission['remaining'] for mission in by_com[commodity])
            cargo = self.cargo.get(commodity, 0)
            font = complete if cargo >= remaining else normal

            gridlabel(text=description, anchor=tk.W, font=font).grid(row=row, column=0, sticky=tk.EW)
            gridlabel(text='{:,.0f}'.format(remaining), anchor=tk.E, font=font).grid(row=row, column=1, sticky=tk.EW)
            gridlabel(text='{:,.0f}'.format(cargo), anchor=tk.E, font=font).grid(row=row, column=2, sticky=tk.EW)

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

        self.hidden = not (self.missions and self.enabled_intvar.get())
