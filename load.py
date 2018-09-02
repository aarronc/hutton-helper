"The Hutton Helper. For the Mug!"

from __init__ import __version__ as HH_VERSION

import json
import os
import sys
import textwrap
import Tkinter as tk
import traceback
import ttk
import zlib
import tkFont

from ttkHyperlinkLabel import HyperlinkLabel
from config import config # applongname, appversion
import myNotebook as nb
import tkMessageBox

import requests # still here for CG code

# Internal plugins and utilities:
import cover
import exploration
import news
import plugin as plugin_module
import progress
import toolbar
import updater
import xmit

this = sys.modules[__name__]  # pylint: disable=C0103
this.msg = ""


def PANIC(description=None):
    "Handle failure."

    sys.stderr.write("PANIC: {}\r\n".format(description or ''))
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)


def plugin_start():
    "Initialise the Hutton Helper plugin."

    this.helper = plugin_module.HuttonHelperHelper(config, _refresh)
    this.updater = updater.UpdatePlugin(this.helper)  # get a reference only if you need one
    this.plugins = [
        # A list of plugins to which we pass events.
        this.updater,
        progress.ProgressPlugin(this.helper),
        exploration.ExplorationPlugin(this.helper)
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

    frame = this.frame = tk.Frame(parent)
    frame.columnconfigure(0, weight=1)

    table = tk.Frame(frame)
    table.columnconfigure(1, weight=1)
    table.grid(sticky=sticky)

    HyperlinkLabel(
        table,
        text='Helper:',
        url='https://hot.forthemug.com/',
        underline=False,
        anchor=anchor,
    ).grid(row=0, column=0, sticky=sticky)
    this.status = tk.Label(table, anchor=anchor, text=str(this.updater))
    this.status.grid(row=0, column=1, sticky=sticky)

    tk.Label(table, anchor=anchor, text="News:").grid(row=1, column=0, sticky=sticky)
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
    this.front_cover = cover.FrontCover(frame)
    row = row + 1

    # Configure the grid for everything above
    _refresh()

    # Add the toolbar
    toolbar.HuttonToolbar(frame).grid(row=row, pady=pady, sticky=sticky)

    return frame


def _refresh():
    "Hide or unhide plugins based on their ``hidden`` flag."

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

    # Second, the front cover we display if no plugins are enabled AND ready:
    if any_ready:
        this.front_cover.grid_forget()
    else:
        front_cover.grid(
            row=this.front_cover_row,
            column=0,
            sticky=tk.EW,
            padx=10,
            pady=10
        )


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


EVENT_XMIT_PATHS = {
    'Bounty': '/bounty',
    'Cargo': '/cargo',
    'CargoDepot': '/cargodepot',
    'CollectCargo': '/cargocollection',
    'CommunityGoal': '/communitygoal',
    'Died': '/death',
    'Docked': '/dockedinfoupdate',
    'FactionKillBond': '/factionkillbond',
    'FSDJump': '/fsdjump',
    'LoadGame': '/loadgame',
    'Loadout': '/loadout',
    'MarketBuy': '/buy',
    'MarketSell': '/sell',
    'MissionAbandoned': '/missioncomplete',
    'MissionAccepted': '/missiontake',
    'MissionCompleted': '/missioncomplete',
    'MissionFailed': '/missioncomplete',
    'MissionRedirected': '/missionupdate',
    'NpcCrewPaidWage': '/npccrewpaidwage',
    'Promotion': '/cmdrpromotion',
    'Rank': '/rank',
    'Scan': '/scan',
    'SellExplorationData': '/explorationdata',
    'Statistics': '/stats',
    'SupercruiseEntry': '/supercruiseentry',
    'SupercruiseExit': '/supercruiseexit',
    'Undocked': '/undockedinfoupdate',
}

EVENT_STATUS_FORMATS = {
    'CargoDepot': "Wing Mission Info updated",
    'CollectCargo': "Cargo scooped into cargo bay",
    'CommunityGoal': "Community Goal Data Received",
    'Died': "Oops.... you died :( :( :(",
    'Docked': "Docked",
    'DockingCancelled': "Docking Canceled",
    'DockingDenied': "Docking Denied",
    'DockingGranted': "Docking request granted",
    'DockingTimeout': "Docking Timed out",
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
    'SupercruiseExit': "Exited Supercruise",
    'Touchdown': "Touchdown!",
    'Undocked': "Undocked",
}

REDEEM_TYPE_STATUS_FORMATS = {
    'CombatBond': "Combat Bond cashed in for {:,.0f} credits",
    'bounty': "Bounty Voucher cashed in for {:,.0f} credits",
    'settlement': "{:,.0f} credits paid to settle fines",
    'trade': "{:,.0f} credits earned from trade voucher",
}

COMMAND_XMIT_PATHS = {
    'mission close': '/missionreset',
    'tick update': '/tickupdate',
    'TLDR': '/tldr',
    'COLBRIEF': '/tldrcol',
    'stateupdate': '/state',
    'recheck system': '/recheckinfluence',
    'generalupdate': '/dailygeneral',
    'coloniaupdate': '/colstate',
    'race start': '/racestart',
    'race end': '/raceend',
    'exploration start': '/explostart',
    'reset exploration data': '/exploreset',
    'inf reload': '/devinfreload',
    'allow list reload': '/devallowreload',
    'black ops add': '/blopsadd',
    'black ops active': '/silentrunning',
    'black ops reset': '/normalrunning',
    'auth list reload': '/authlistreload',
    'explo system': '/explosystem.json/{cmdr}/{system}',
    'best hutton run': '/besthuttonrun.json/{cmdr}'
}

COMMAND_STATUS_FORMATS = {
    # OPTIONAL unless there's no matching COMMAND_XMIT_PATHS entry above
    'TLDR': "Sent TLDR update Command",
    'COLBRIEF': "Sent TLDR update Colonia Command",
    'recheck system': "Forced System Re-check of {system} on next jump in",
    'race start': "Sent Race START info",
    'race end': "Sent Race END info",
    'reset exploration data': "Reset your Exploration 2.0 Data",
    'inf reload': "Developer Mode : inf reload command sent",
    'allow list reload': "Developer Mode : allow list reload command sent",
    'black ops add': "Admin Mode : Black Ops Faction Added",
    'black ops active': "Black ops Mode : Enjoy Being Naughty Commander",
    'black ops reset': "Black ops Mode : Welcome back Commander",
    'auth list reload': "Admin Mode : Reloaded Auth List",
    'explo system': "You Have sold {ExplorationSystemTotal:,.0f} credits in {system} today",
    'best hutton run': "BEST Hutton Run is CMDR {commandername} in {TravelTime}",
}

COMMANDS = set(COMMAND_XMIT_PATHS.keys()) | set(COMMAND_STATUS_FORMATS.keys())


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

    if is_beta:
        this.status['text'] = 'Disabled due to beta'
        return

    entry['commandername'] = cmdr
    entry['hhstationname'] = station
    entry['hhsystemname'] = system
    entry['huttonappversion'] = HH_VERSION

    compress_json = json.dumps(entry)
    transmit_json = zlib.compress(compress_json)

    event = entry['event']

    # Declare a function to make it easy to send the event to the server and get the response.
    # We've smuggled the transmit_json variable from journal_entry into xmit_event using a
    # keyword argument because Python 2.x doesn't have 'nonlocal'. Also, cmdr and system:
    def xmit_event(path, transmit_json=transmit_json, cmdr=cmdr, system=system):
        "Transmit the event to our server at ``path.format(cmdr=cmdr, system=system)``."
        path = path.format(cmdr=cmdr, system=system)
        return xmit.post(path, data=transmit_json, headers=xmit.COMPRESSED_OCTET_STREAM)

    # If we can find an entry in XMIT_PATHS, send the event to the server at the required path:
    xmit_path = EVENT_XMIT_PATHS.get(event)
    if xmit_path:
        xmit_event(xmit_path)

    # If we can find an entry in STATUS_FORMATS, fill in the string and display it to the user:
    status_format = EVENT_STATUS_FORMATS.get(event)
    if status_format:
        this.status['text'] = status_format.format(**entry)

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

    elif event == 'CommunityGoal':
        # For some events, we need custom transmission logic, e.g. to the Community Goal Reward Thresholds Calculator:

        for goal in entry['CurrentGoals']:

            if not goal['IsComplete']: # v0.2Collect Active CG only
                # First Extract CG Data
                cg_id = goal['CGID']
                cg_title = goal['Title']
                cg_total = goal['CurrentTotal']
                cg_contributors = goal['NumContributors']
                cg_contribution = goal['PlayerContribution']
                cg_percentile_band = goal['PlayerPercentileBand']

                # Build the Data Set to Submit, based on the Entry field number from the form.
                form_data = {
                    'entry.1465819909': cg_id,
                    'entry.2023048714': cg_title,
                    'entry.617265888': cg_total,
                    'entry.1469183421': cg_contributors,
                    'entry.2011125544': cg_contribution,
                    'entry.1759162752': cg_percentile_band
                }
                url = "https://docs.google.com/forms/d/e/1FAIpQLScJHvd9MNKMMNGpjZtlcT74u6Wnhcgesqz38a8JWBC94Se2Dg/formResponse"

                # Request URl as a POST with the Form URL plus send the Form Data to each entry.
                try:
                    response = requests.post(url, data=form_data)
                    if response.status_code == 200:
                        # print ('URL Success')
                        this.msg = 'CG Post Success'
                    else:
                        # print ('URL Fail' + str(r.status_code))
                        this.msg = 'CG Post Failed'

                except: # pylint: disable=W0702
                    this.msg = 'CG Post Exception'

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
        totalvalue = baseval + bonusval
        this.status['text'] = "Sold ExplorationData for {:,.0f} credits".format(float(totalvalue))

    elif event == 'SendText': # pylint: disable=R1702
        # Another lookup table, this time a little odder.
        for command in COMMANDS:
            if command in entry['Message']:
                # Get the status format:
                command_status_format = COMMAND_STATUS_FORMATS.get(command)
                if not command_status_format:
                    command_status_format = 'Sent {command} Command'

                # Send the event if required, getting json_data back:
                json_data = None
                command_xmit_path = COMMAND_XMIT_PATHS.get(command)
                if command_xmit_path:
                    command_xmit_path = command_xmit_path.format(cmdr=cmdr, system=system)
                    if '{cmdr}' in command_xmit_path: # FILTHY hack to figure out if it's a 'get'
                        json_data = xmit.get(command_xmit_path)
                    else:
                        json_data = xmit.post(command_xmit_path, data=transmit_json, headers=xmit.COMPRESSED_OCTET_STREAM)

                if not json_data:
                    command_status_format = 'Failed to Send {command} Command'

                # Format and display the status text:
                print "Filling in: {}".format(command_status_format)
                this.status['text'] = command_status_format.format(
                    # Add variables here that you'd like to use in your status text:
                    command=command,
                    system=system,
                    # We also supply the server's reply:
                    **(json_data or {})
                )

                # Special handling
                # ONLY performed if there's ALSO an entry in COMMAND_XMIT_PATHS or COMMAND_STATUS_FORMATS:

                if command == 'reset exploration data':
                    this.exploration_display.explo_credits(cmdr)

        # VERY special handling, with NONE of the automatic stuff above:

        if "my hutton run" in entry['Message']:
            json_data = xmit.get('/myhuttonrun.json/{}'.format(cmdr))
            if not json_data:
                this.status['text'] = "Failed to get Hutton Run data."
            elif json_data['SecondCount'] == "0":
                this.status['text'] = "You have not completed a Hutton Run"
            else:
                this.status['text'] = "Your best Hutton Run is {}".format(json_data['TravelTime'])

        if "!shoutout" in entry['Message']:
            json_data = xmit.get('/shoutout.json')
            if not json_data:
                this.status['text'] = "Could not shout, shout, or let it all out."
            elif json_data['online'] == "true":
                this.status['text'] = "Shoutout sent to the LIVE DJ"
                xmit_event('/shoutout')
            if json_data['online'] == "false":
                this.status['text'] = "There is no LIVE DJ at the moment... please try again later"


def cmdr_data(data, is_beta):
    "Called shortly after startup with a dump of information from Frontier."

    if not is_beta:
        transmit_json = zlib.compress(json.dumps(data))
        xmit.post('/docked', parse=False, data=transmit_json, headers=xmit.COMPRESSED_OCTET_STREAM)

    for plugin in this.plugins:
        try:
            plugin.cmdr_data(data, is_beta)
        except:
            PANIC("{}.cmdr_data".format(plugin))


def plugin_stop():
    "Called once at shutdown."

    print "Farewell cruel world!"
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
