"The Hutton Helper. For the Mug!"

try:
    # for Python2
    import Tkinter as tk
    import ttk
    import tkFont
    import tkMessageBox
except ImportError:
    # for python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as tkFont
    import tkinter.messagebox as tkMessageBox

import json
import os
import sys
import textwrap
import time
import traceback
import uuid
import zlib
from canonnevents import whiteList

from ttkHyperlinkLabel import HyperlinkLabel
from config import config, applongname, appversion
import myNotebook as nb

import requests # still here for CG code

try:
    HERE = os.path.dirname(__file__)
    sys.path.insert(0, HERE)

    # We import the rest of the Hutton Helper together in this block while
    # we've altered sys.path so we don't inhale files from EDMC "package"
    # plugins by accident. https://git.io/fAQkf#python-package-plugins

    import exploration
    import forward
    import influence
    import local
    import news
    # import pwpevents
    import plugin as plugin_module
    import progress
    import shopping
    import toolbar
    import updater
    import widgets
    import xmit
    import market
    # import cargo
    import panic
    import data

    from version import HH_VERSION

finally:
    del sys.path[0]

this = sys.modules[__name__]  # pylint: disable=C0103
this.msg = ""
this.cargodump = {}


FRONT_COVER_DELAY = 10  # seconds
UUID = str(uuid.uuid4())

def PANIC(description=None):
    "Handle failure."

    sys.stderr.write("PANIC: {}\r\n".format(description or ''))
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

    errorreport = {}
    errorreport['cmdr'] = news.commander
    errorreport['huttonappversion'] = HH_VERSION
    errorreport['edmcversion'] = appversion
    errorreport['modulecall'] = description or ''
    errorreport['traceback'] = traceback.format_exception(exc_type, exc_value, exc_traceback)
    compress_json = json.dumps(errorreport)
    error_data = zlib.compress(compress_json.encode('utf-8'))
    #sys.stderr.write("Posting it...{}\r\n".format(compress_json.encode('utf-8')))
    xmit.post('/errorreport', error_data, headers=xmit.COMPRESSED_OCTET_STREAM)

def plugin_start3(plugin_dir):
    ""
    "Initialise the Hutton Helper plugin."

    plugin_start(plugin_dir)

    return 'Hutton Helper'

def plugin_start(plugin_dir):
    "Initialise the Hutton Helper plugin."

    this.helper = plugin_module.HuttonHelperHelper(config, _refresh, _status)
    this.plugins = [
        # A list of plugins to which we pass events.
        updater.UpdatePlugin(this.helper),
        forward.ForTheMugPlugin(this.helper),
        local.CommandPlugin(this.helper),
        shopping.ShoppingListPlugin(this.helper),
        influence.InfluencePlugin(this.helper),
        progress.ProgressPlugin(this.helper),
        exploration.ExplorationPlugin(this.helper),
        market.MarketPlugin(this.helper),
        # cargo.CargoPlugin(this.helper),
        # pwpevents.PwpEventsPlugin(this.helper),
        panic.PanicPlugin(this.helper),
    ]

    for plugin in plugins:
        try:
            plugin.plugin_start()
        except:
            PANIC("{}.plugin_start".format(plugin))

    return 'Hutton Helper'

def plugin_app(parent):
    "Called once to get the plugin widget. Return a ``tk.Frame``."

    padx, pady = 10, 5  # formatting
    sticky = tk.EW + tk.N  # full width, stuck to the top
    anchor = tk.NW

    # we declare a whitelist object so we can run a timer to fetch the event whitelist from Canonn
    # This is so that we can find out what events to transmit There is no UI associated
    Canonn=whiteList(parent)
    Canonn.fetchData()

    frame = this.frame = tk.Frame(parent)
    frame.columnconfigure(0, weight=1)

    table = tk.Frame(frame)
    table.columnconfigure(1, weight=1)
    table.grid(sticky=sticky)

    HyperlinkLabel(
        table,
        text='Helper:',
        url='https://hot.forthemug.com/',
        anchor=anchor,
    ).grid(row=0, column=0, sticky=sticky)
    this.status = widgets.SelfWrappingLabel(table, anchor=anchor, text="For the Mug!")
    this.status.grid(row=0, column=1, sticky=sticky)

    widgets.StyleCaptureLabel(table, anchor=anchor, text="News:").grid(row=1, column=0, sticky=sticky)
    news.HuttonNews(table).grid(row=1, column=1, sticky=sticky)

    this.plugin_rows = {}
    this.plugin_frames = {}
    row = 1 # because the table is first

    # Add the plugins' widgets
    for plugin in this.plugins:
        try:
            plugin_frame = plugin.plugin_app(frame)
        except:
            PANIC("{}.plugin_app".format(plugin))
            continue

        if plugin_frame:
            this.plugin_rows[plugin] = row
            this.plugin_frames[plugin] = plugin_frame
            row = row + 1

    # Add the front cover
    this.front_cover_row = row
    this.front_cover = widgets.FrontCover(frame)
    _show_front_cover(True)

    # Arrange for the front cover to be shown for at least a few seconds
    this.front_cover_until = time.time() + FRONT_COVER_DELAY
    frame.after(1000 * FRONT_COVER_DELAY, _refresh)
    frame.after_idle(_refresh)

    # Add the toolbar
    toolbar.HuttonToolbar(frame).grid(row=row + 1, pady=pady, sticky=sticky)

    # Uncomment the next line to thrash the status line shortly after startup:
    # frame.after(5000, _thrash, EVENT_STATUS_FORMATS.values())

    return frame


def _thrash(remain):
    "Thrash through a list of status messages for layout troubleshooting."

    if remain:
        remain = remain[:]
        text = remain.pop()
        _status(text)
        this.frame.after(500, _thrash, remain)


def _show_front_cover(show=True):
    "Show the front cover."

    if show:
        this.front_cover.grid(
            row=this.front_cover_row,
            column=0,
            sticky=tk.EW,
            padx=10,
            pady=10
        )

    else:
        this.front_cover.grid_forget()


def _refresh():
    "Hide or unhide plugins based on their ``hidden`` flag."

    if time.time() < this.front_cover_until:
        return

    any_ready = False

    # First, the plugins:
    for plugin in this.plugins:
        plugin_frame = this.plugin_frames.get(plugin)
        plugin_row = this.plugin_rows.get(plugin)

        if plugin_frame and plugin_row:
            if plugin.hidden or not plugin.ready:
                plugin_frame.grid_forget()

            else:
                any_ready = True
                plugin_frame.grid(row=plugin_row, sticky=tk.EW)

    _show_front_cover(not any_ready)


def _status(text=''):
    "Set the status text."

    this.status['text'] = text


def _cargo_refresh(cmdr):
    dump_path = data.get_journal_path('Cargo.json')
    # sys.stderr.write("Reading cargo data from: {}\r\n".format(dump_path))
    with open(dump_path, 'r') as dump:
        dump = dump.read()
        dump = json.loads(dump)
        this.cargodump = dump
        dump['commandername'] = cmdr
        compress_json = json.dumps(dump)
        cargo_data = zlib.compress(compress_json.encode('utf-8'))
        # sys.stderr.write("Posting it...\r\n")
        xmit.post('/missioncargo', cargo_data, headers=xmit.COMPRESSED_OCTET_STREAM)
        # self.helper.status("Market data posted.")


def plugin_prefs(parent, cmdr, is_beta):
    "Called each time the user opens EDMC settings. Return an ``nb.Frame``."

    padx, pady = 10, 5  # formatting

    frame = nb.Frame(parent)
    frame.columnconfigure(0, weight=1)

    row = 0
    for plugin in plugins:
        try:
            plugin_prefs_frame = plugin.plugin_prefs(frame, cmdr, is_beta)
            if plugin_prefs_frame:
                plugin_prefs_frame.grid(row=row, column=0, padx=padx, pady=pady, sticky=tk.W)
                row = row + 1

        except:
            PANIC("{}.plugin_prefs".format(plugin))
            continue

    return frame


def prefs_changed(cmdr, is_beta):
    "Called when the user clicks OK on the settings dialog."

    for plugin in this.plugins:
        try:
            plugin.prefs_changed(cmdr, is_beta)
        except:
            PANIC("{}.prefs_changed".format(plugin))

    _refresh()


EVENT_STATUS_FORMATS = {
    'ApproachBody': "Approached {Body}",
    'ApproachSettlement': "Approached {Name}",
    'CargoDepot': "Delivery Mission Info updated",
    'CollectCargo': "Cargo scooped into cargo bay",
    'CommunityGoal': "Community Goal Data Received",
    'Died': "Oops.... you died :( :( :(",
    'Docked': "Docked",
    'DockingCancelled': "Docking Canceled",
    'DockingDenied': "Docking Denied",
    'DockingGranted': "Docking request granted",
    'DockingTimeout': "Docking Timed out",
    'EscapeInterdiction': "Phew!, that was close {Interdictor} almost got you!",
    'FSDJump': "Jumped into {StarSystem} system",
    'HeatWarning': "Its getting warm in here",
    'LeaveBody': "Leaving Gravitational Well",
    'Liftoff': "We have Liftoff!",
    'MissionAbandoned': "Mission Abandoned",
    'MissionAccepted': "Mission Accepted",
    'MissionCompleted': "Mission Completed",
    'MissionFailed': "Mission Failed",
    'MissionRedirected': "Mission Update Received",
    'Promotion': "Congratulations on your promotion commander",
    'Scan': "Scan Data stored for Cartographics",
    'Scanned': "You have been scanned",
    'SupercruiseEntry': "Entered Supercruise",
    'SupercruiseExit': "Dropped out within range of {Body}",
    'Touchdown': "Touchdown!",
    'Undocked': "Undocked",
    'USSDrop' : "Dropped into {USSType_Localised} Threat : {USSThreat}"
}

REDEEM_TYPE_STATUS_FORMATS = {
    'CombatBond': "Combat Bond cashed in for {:,.0f} credits",
    'bounty': "Bounty Voucher cashed in for {:,.0f} credits",
    'settlement': "{:,.0f} credits paid to settle fines",
    'trade': "{:,.0f} credits earned from trade voucher",
}


def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    E:D client made a journal entry
    :param cmdr: The Cmdr name, or None if not yet known
    :param system: The current system, or None if not yet known
    :param station: The current station, or None if not docked or not yet known
    :param entry: The journal entry as a dictionary
    :param state: A dictionary containing info about the Cmdr, current ship and cargo
    :return:
    """

    #we are going to send events to Canonn, The whitelist tells us which ones
    try:
        whiteList.journal_entry(cmdr, is_beta, system, station, entry, state,"Hutton-Helper-{}".format(HH_VERSION))
    except:
        print("Canonn failed, but don't let that stop you")

    if is_beta:
        this.status['text'] = 'Disabled due to beta'
        return

    entry['commandername'] = cmdr
    news.commander = cmdr
    entry['hhstationname'] = station
    entry['hhsystemname'] = system
    entry['huttonappversion'] = HH_VERSION
    entry['edmcversion'] = appversion
    entry['uuid'] = UUID

    compress_json = json.dumps(entry)
    compress_json = compress_json.encode('utf-8')
    transmit_json = zlib.compress(compress_json)

    event = entry['event']
    # sys.stderr.write('event: {}\r\n'.format(event)) #Very Chatty

    # Declare a function to make it easy to send the event to the server and get the response.
    # We've smuggled the transmit_json variable from journal_entry into xmit_event using a
    # keyword argument because Python 2.x doesn't have 'nonlocal'. Also, cmdr and system:
    def xmit_event(path, transmit_json=transmit_json, cmdr=cmdr, system=system):
        "Transmit the event to our server at ``path.format(cmdr=cmdr, system=system)``."
        path = path.format(cmdr=cmdr, system=system)
        return xmit.post(path, data=transmit_json, headers=xmit.COMPRESSED_OCTET_STREAM)

    # If we can find an entry in STATUS_FORMATS, fill in the string and display it to the user:
    status_format = EVENT_STATUS_FORMATS.get(event)
    if status_format:
        this.status['text'] = status_format.format(**entry)

    # Update and Send cargo to server first then update plugins
    if event == 'Cargo':
        this._cargo_refresh(cmdr)
        shopping.cargodump = this.cargodump


    # Update the plugins
    for plugin in this.plugins:
        try:
            plugin.journal_entry(cmdr, is_beta, system, station, entry, state)
        except:
            PANIC("{}.journal_entry".format(plugin))

    # Special event handling, which happens IN ADDITION TO the automatic transmission and
    # status message handling above:

    if event == 'MarketBuy':
        # For some events, we need our status to be based on translations of the event that
        # string.format can't do without a scary custom formatter:
        this.status['text'] = "{:,.0f} {} bought".format(float(entry['Count']), entry['Type'])

    elif event == 'MarketSell':
        this.status['text'] = "{:,.0f} {} sold".format(float(entry['Count']), entry['Type'])

    elif event == 'FactionKillBond':
        this.status['text'] = "Kill Bond Earned for {:,.0f} credits".format(float(entry['Reward']))

    elif event == 'Bounty':
        this.status['text'] = "Bounty Earned for {:,.0f} credits".format(float(entry['TotalReward']))

    elif event == 'RedeemVoucher':
        # For some events, we need to check another lookup table. There are ways to make the original lookup table
        # do this heavy lifting, too, but it'd make the code above more complicated than a trucker who'd only just
        # learned Python could be expected to maintain.

        redeem_status_format = REDEEM_TYPE_STATUS_FORMATS.get(entry['Type'])
        if redeem_status_format:
            this.status['text'] = redeem_status_format.format(float(entry['Amount']))
            xmit_event('/redeemvoucher')

    elif event == 'SellExplorationData':
        baseval = entry['BaseValue']
        bonusval = entry['Bonus']
        totalvalue = entry['TotalEarnings']
        this.status['text'] = "Sold ExplorationData for {:,.0f} credits".format(float(totalvalue))

    elif event == 'MultiSellExplorationData':
        baseval = entry['BaseValue']
        bonusval = entry['Bonus']
        totalvalue = entry['TotalEarnings']
        this.status['text'] = "Sold ExplorationData for {:,.0f} credits".format(float(totalvalue))


def cmdr_data(data, is_beta):
    "Called shortly after startup with a dump of information from Frontier."

    if not is_beta:
        compress_json = json.dumps(data)
        transmit_json = zlib.compress(compress_json.encode('utf-8'))
        xmit.post('/docked', parse=False, data=transmit_json, headers=xmit.COMPRESSED_OCTET_STREAM)

    for plugin in this.plugins:
        try:
            plugin.cmdr_data(data, is_beta)
        except:
            PANIC("{}.cmdr_data".format(plugin))


def plugin_stop():
    "Called once at shutdown."

    print("Farewell cruel world!")
    for plugin in this.plugins:
        try:
            plugin.plugin_stop()
        except:
            PANIC("{}.plugin_stop".format(plugin))


def dashboard_entry(cmdr, is_beta, entry):
    "Called anywhere up to once a second with flight telemetry."

    for plugin in this.plugins:
        try:
            plugin.dashboard_entry(cmdr, is_beta, entry)
        except:
            PANIC("{}.dashboard_entry".format(plugin))
