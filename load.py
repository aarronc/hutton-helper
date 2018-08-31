import sys
import os
import ttk
import Tkinter as tk
import tkMessageBox
from ttkHyperlinkLabel import HyperlinkLabel
from config import applongname, appversion
from config import config
import myNotebook as nb
import json
import requests
import zlib
import re
import webbrowser
import textwrap
import time

this = sys.modules[__name__]
this.msg = ""

RADIO_URL = "https://radio.forthemug.com/"
STATS_URL = "https://hot.forthemug.com/stats.php"


HH_VERSION="1.8.4"
REMOTE_VERSION_URL="http://hot.forthemug.com/beta_plugin_version.txt"
REMOTE_PLUGIN_FILE_URL="http://hot.forthemug.com/beta_hutton_helper.py"

this.remote_version = None
this.upgrade_required = None # None for unknown, True for required, False for not
this.network_error_str = "" # Contains human readable network error log
this.upgrade_applied = False

def plugin_start():
    """
    Invoked when EDMC has just loaded the plug-in
    :return: Plug-in name
    """
    # sys.stderr.write("plugin_start\n")	# appears in %TMP%/EDMarketConnector.log in packaged Windows app
    fetch_remote_version() # Fetch remote version information early
    return 'Hutton Helper'

def plugin_prefs(parent):
    """
    Invoked whenever a user opens the preferences pane
    Must return a TK Frame for adding to the EDMC settings dialog.
    """
    this.ShowExploVal = tk.IntVar(value=config.getint("ShowExploValue"))
    # sys.stderr.write("plugin_prefs\n")
    PADX = 10 # formatting

    # We need to make another check, as we failed in plugin_start()
    if this.upgrade_required is None:
        fetch_remote_version()

    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    HyperlinkLabel(frame, text='Hutton Helper website', background=nb.Label().cget('background'), url='https://hot.forthemug.com/', underline=True).grid(columnspan=2, padx=PADX, sticky=tk.W)	# Don't translate

    nb.Label(frame, text="Hutton Helper Plug-in - Public Version {VER}".format(VER=HH_VERSION)).grid(columnspan=2, padx=PADX, sticky=tk.W)
    nb.Label(frame).grid()	# spacer
    if this.upgrade_required is None:
        nb.Label(frame, text="Attempt to query for a new plug-in version failed:").grid(columnspan=2, padx=PADX, sticky=tk.W)
        nb.Label(frame, text=this.network_error_str, fg="red").grid(columnspan=2, padx=PADX, sticky=tk.W)
    elif this.upgrade_required:
        nb.Label(frame, text="Upgrade required! Hit the button below and restart EDMC").grid(columnspan=2, padx=PADX, sticky=tk.W)
        nb.Label(frame).grid()	# spacer
        nb.Button(frame, text="UPGRADE", command=upgrade_callback).grid(columnspan=2, padx=PADX, sticky=tk.W)
    else:
        nb.Label(frame, text="Fly Safe!").grid(columnspan=2, padx=PADX, sticky=tk.W)
        nb.Label(frame).grid() # Spacer
        nb.Label(frame, text="Exploration Options :-").grid(columnspan=2, padx=PADX, sticky=tk.W)
        nb.Checkbutton(frame, text="Show Exploration Credits on Hutton Helper Display", variable=this.ShowExploVal).grid(columnspan=2, padx=PADX, sticky=tk.W)

    return frame

def prefs_changed(cmdr, is_beta):
    """
    Save settings.
    """
    config.set('ShowExploValue', this.ShowExploVal.get())
    display_update()

def fetch_remote_version():
    try:
        response = requests.get(REMOTE_VERSION_URL, timeout=0.5)
        sys.stderr.write("response.status_code:%d\n" % response.status_code)
        sys.stderr.write("response.text:%s\n" % response.text)
        if response.status_code == 200:
            clean_response = response.text.rstrip()
            if len(versiontuple(clean_response)) != 3:
                # Bad format. We need a version number formatted as 1.2.3
                this.network_error_str = "Bad version format reply from server"
                return

            # Store for later
            this.remote_version = clean_response

            sys.stderr.write("comparing remote version '{REMOTE}' to local version '{LOCAL}'\n".format(REMOTE=this.remote_version, LOCAL=HH_VERSION))
            if HH_VERSION == this.remote_version:
                this.upgrade_required = False
            else:
                this.upgrade_required = True
        else:
            this.network_error_str = "Bad response code {HTTP_RESP_CODE} from server".format(HTTP_RESP_CODE=response.status_code)
    except requests.exceptions.Timeout:
        # sys.stderr.write("requests.exceptions.Timeout\n")
        this.network_error_str = "Request to upgrade URL timed out while finding current version"
    except:
        # sys.stderr.write("generic exception\n")
        this.network_error_str = "Unknown network problem finding current version"


def upgrade_callback():
    # sys.stderr.write("You pushed the upgrade button\n")

    # Catch upgrade already done once
    if this.upgrade_applied:
        msginfo = ['Upgrade already applied', 'Please close and restart EDMC']
        tkMessageBox.showinfo("Upgrade status", "\n".join(msginfo))
        return

    this_fullpath = os.path.realpath(__file__)
    this_filepath, _ext = os.path.splitext(this_fullpath)
    corrected_fullpath = this_filepath + ".py" # Somehow we might need this to stop it hitting the pyo file?

    # sys.stderr.write("path is %s\n" % this_filepath)
    try:
        response = requests.get(REMOTE_PLUGIN_FILE_URL)
        if (response.status_code == 200):

            # Check our required version number is in the response, otherwise
            # it's probably not our file and should not be trusted
            expected_version_substr="HH_VERSION=\"{REMOTE_VER}\"".format(REMOTE_VER=this.remote_version)
            if expected_version_substr in response.text:
                with open(corrected_fullpath, "wb") as f:
                    f.seek(0)
                    f.write(response.content)
                    f.truncate()
                    f.flush()
                    os.fsync(f.fileno())
                    this.upgrade_applied = True # Latch on upgrade successful
                    msginfo = ['Upgrade has completed sucessfully.', 'Please close and restart EDMC']
                    tkMessageBox.showinfo("Upgrade status", "\n".join(msginfo))

                sys.stderr.write("Finished plugin upgrade!\n")
            else:
                msginfo = ['Upgrade failed. Did not contain the correct version', 'Please try again']
                tkMessageBox.showinfo("Upgrade status", "\n".join(msginfo))
        else:
            msginfo = ['Upgrade failed. Bad server response', 'Please try again']
            tkMessageBox.showinfo("Upgrade status", "\n".join(msginfo))
    except:
        sys.stderr.write("Upgrade problem when fetching the remote data: {E}\n".format(E=sys.exc_info()[0]))
        msginfo = ['Upgrade encountered a problem.', 'Please try again, and restart if problems persist']
        tkMessageBox.showinfo("Upgrade status", "\n".join(msginfo))


def plugin_status_text():
    if this.upgrade_required is None:
        return "Hutton Helper {VER} OK (upgrade status unknown)".format(VER=HH_VERSION)
    elif this.upgrade_required:
        return "Hutton Helper {VER} OLD (Open Settings->HH to upgrade)".format(VER=HH_VERSION)
    else:
        return "Hutton Helper {VER} OK (up-to-date)".format(VER=HH_VERSION)


def versiontuple(v):
    return tuple(map(int, (v.split("."))))

def OpenUrl(UrlToOpen):
    webbrowser.open_new(UrlToOpen)

def news_update():
    this.parent.after(300000,news_update)
    try:
        url = "http://hot.forthemug.com:4567/news.json/"
        response = requests.get(url)
        news_data = response.json()
        #sys.stderr.write("got news!'{HDLN}' and link '{LNK}'\n".format(HDLN=news_data['headline'], LNK=news_data['link']))
        if (response.status_code == 200):
            if len(news_data['headline']) > 30:
                this.news_headline['text'] = textwrap.fill(news_data['headline'], 30)
            else:
                this.news_headline['text'] = news_data['headline']

            this.news_headline['url'] = news_data['link']
        else:
            this.news_headline['text'] = "News refresh Failed"
    except:
        this.news_headline['text'] = "Could not update news from HH server"

def influence_data_call():
    try:
        url = "http://hot.forthemug.com:4567/msgbox_influence.json"
        response = requests.get(url)
        influence_data = response.json()
        #sys.stderr.write("got news!'{HDLN}' and link '{LNK}'\n".format(HDLN=news_data['headline'], LNK=news_data['link']))
        if (response.status_code == 200):
            tkMessageBox.showinfo("Hutton Influence Data", "\n".join(influence_data))
        else:
            tkMessageBox.showinfo("Hutton Influence Data", "Could not get Influence Data")
    except:
        tkMessageBox.showinfo("Hutton Influence Data", "Did not Receive response from HH Server")

def daily_info_call():
    try:
        url = "http://hot.forthemug.com:4567/msgbox_daily_update.json"
        response = requests.get(url)
        daily_data = response.json()
        #sys.stderr.write("got news!'{HDLN}' and link '{LNK}'\n".format(HDLN=news_data['headline'], LNK=news_data['link']))
        if (response.status_code == 200):
            tkMessageBox.showinfo("Hutton Daily update", "\n".join(daily_data))
        else:
            tkMessageBox.showinfo("Hutton Daily update", "Could not get Daily Update Data")
    except:
        tkMessageBox.showinfo("Hutton Daily update", "Did not Receive response from HH Server")

def display_update():
    if config.getint("ShowExploValue") == 0:
        this.exploration_label.grid_forget()
        this.exploration_status.grid_forget()
    else:
        this.exploration_status['text'] = "<Scan object to update>"
        this.exploration_label.grid(row = 2,column = 0, sticky = tk.W)
        this.exploration_status.grid(row = 2,column = 1, columnspan= 3,sticky = tk.W)

def explo_credits(cmdr):
    credit_url = "http://forthemug.com:4567/explocredit.json/{}".format(cmdr)
    response = requests.get(credit_url)
    json_data = response.json()
    this.exploration_status['text'] = "{:,.0f} credits".format(float(json_data['ExploCredits']))

def plugin_app(parent):
    this.parent = parent
    this.frame = tk.Frame(parent)
    this.inside_frame = tk.Frame(this.frame)
    this.exploration_frame = tk.Frame(this.frame)
    this.inside_frame.columnconfigure(4, weight=1)
    this.exploration_frame.columnconfigure(2, weight=1)
    label_string = plugin_status_text()


    this.frame.columnconfigure(2, weight=1)
    this.label = HyperlinkLabel(this.frame, text='Helper:', url='https://hot.forthemug.com/', underline=False)
    this.status = tk.Label(this.frame, anchor=tk.W, text=label_string)
    this.news_label = tk.Label(this.frame, anchor=tk.W, text="News:")
    this.news_headline = HyperlinkLabel(this.frame, text="", url="", underline=True)
    this.daily_button = tk.Button(this.inside_frame, text="Daily Update", command=daily_info_call)
    this.influence_button = tk.Button(this.inside_frame, text="Influence", command=influence_data_call)
    this.stats_button = tk.Button(this.inside_frame, text="Stats", command=lambda: OpenUrl(STATS_URL))
    this.radio_button = tk.Button(this.inside_frame, text="Radio", command=lambda: OpenUrl(RADIO_URL))
    this.exploration_label = tk.Label(this.inside_frame, text="Explo Credits:")
    this.exploration_status = tk.Label(this.inside_frame, text = "")
    this.spacer = tk.Label(this.frame)
    this.label.grid(row = 0, column = 0, sticky=tk.W)
    this.status.grid(row = 0, column = 1, sticky=tk.W)
    this.news_label.grid(row = 1, column = 0, sticky=tk.W)
    this.news_headline.grid(row = 1, column = 1, sticky=tk.W)
    this.inside_frame.grid(row = 3,column = 0, columnspan= 2,sticky=tk.W)
    #this.spacer.grid(row = 2, column = 0,sticky=tk.W)
    this.daily_button.grid(row = 3, column = 0, sticky =tk.W)
    this.influence_button.grid(row = 3 , column = 1, sticky =tk.W, padx = 5,pady= 10)
    this.stats_button.grid(row = 3, column = 2, sticky =tk.W)
    this.radio_button.grid(row = 3, column = 3, sticky =tk.W,padx = 5)
    this.exploration_label.grid(row = 2,column = 0, sticky = tk.W)
    this.exploration_status.grid(row = 2,column = 1,columnspan= 2, sticky = tk.W)
    news_update()
    display_update()

    return this.frame

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
    entry['commandername'] = cmdr
    entry['hhstationname'] = station
    entry['hhsystemname'] = system
    entry['huttonappversion'] = HH_VERSION

    compress_json = json.dumps(entry)
    transmit_json = zlib.compress(compress_json)
    # transmit_json = json.dumps(entry)
    if is_beta:
        pass

    elif entry['event'] == 'StartUp':
        explo_credits(cmdr)

    elif entry['event'] == 'FSDJump':
        url_jump = 'http://forthemug.com:4567/fsdjump'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_jump, data=transmit_json, headers=headers, timeout=7)
        this.status['text'] = "Jumped into {} system".format(entry['StarSystem'])
        if 'StarPos' in entry:
            sys.stderr.write("Arrived at {} ({},{},{})\n".format(entry['StarSystem'], *tuple(entry['StarPos'])))
        else:
            sys.stderr.write("Arrived at {}\n".format(entry['StarSystem']))

    elif entry['event'] == 'MarketBuy':
        url_buy = 'http://forthemug.com:4567/buy'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_buy, data=transmit_json, headers=headers, timeout=7)
        this.status['text'] = "{:,.0f} {} bought".format(float(entry['Count']),entry['Type'])
        sys.stderr.write("{} CMDR {} has bought {} {} from {} in the {} system costing {} credits\n".format(entry['timestamp'],cmdr,entry['Count'],entry['Type'],station,system,entry['TotalCost']))
        sys.stderr.write("{}".format(response))

    elif entry['event'] == 'Rank':
        url_rank = 'http://forthemug.com:4567/rank'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_rank, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'MarketSell':
        url_sell = 'http://forthemug.com:4567/sell'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_sell, data=transmit_json, headers=headers, timeout=7)
        this.status['text'] = "{:,.0f} {} sold".format(float(entry['Count']),entry['Type'])
        sys.stderr.write("{} CMDR {} has sold {} {} in {} in the {} system for {} credits\n".format(entry['timestamp'],cmdr,entry['Count'],entry['Type'],station,system,entry['TotalSale']))

    elif entry['event'] == 'DockingGranted':
        this.status['text'] = "Docking request granted"

    elif entry['event'] == 'DockingCancelled':
        this.status['text'] = "Docking Canceled"

    elif entry['event'] == 'DockingDenied':
        this.status['text'] = "Docking Denied"

    elif entry['event'] == 'DockingTimeout':
        this.status['text'] = "Docking Timed out"

    elif entry['event'] == 'Liftoff':
        this.status['text'] = "We have Liftoff!"

    elif entry['event'] == 'Touchdown':
        this.status['text'] = "Touchdown!"

    elif entry['event'] == 'LeaveBody':
        this.status['text'] = "Leaving Gravitational Well"

    elif entry['event'] == 'CommunityGoal':
        this.status['text'] = "Community Goal Data Received"
        url_transmit_cg = 'http://forthemug.com:4567/communitygoal'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        print ('CG updating')
        for goal in entry['CurrentGoals']:

            if not goal['IsComplete']: #v0.2Collect Active CG only
                """
                First Extract CG Data
                """
                communitygoalID = goal['CGID']
                communitygoalName = goal['Title']
                contributionsTotal= goal['CurrentTotal']
                contributorsNum = goal['NumContributors']
                contribution = goal['PlayerContribution']
                percentileBand = goal['PlayerPercentileBand']
                #print ('CG Variables Calculated')
                """
                Build the Data Set to Submit, based on the Entry field number from the form.
                """
                form_data = {
                    'entry.1465819909' : communitygoalID,
                    'entry.2023048714' : communitygoalName,
                    'entry.617265888' : contributionsTotal,
                    'entry.1469183421' : contributorsNum,
                    'entry.2011125544' : contribution,
                    'entry.1759162752' : percentileBand
                    }
                url = "https://docs.google.com/forms/d/e/1FAIpQLScJHvd9MNKMMNGpjZtlcT74u6Wnhcgesqz38a8JWBC94Se2Dg/formResponse"
                """
                Request URl as a POST with the Form URL plus send the Form Data to each entry.
                """
                try:
                    r = requests.post(url, data=form_data)
                    if r.status_code == 200:
                        #print ('URL Success')
                        this.msg = 'CG Post Success'
                    else:
                        #print ('URL Fail' + str(r.status_code))
                        this.msg = 'CG Post Failed'
                except:
                    this.msg = 'CG Post Exception'

        response = requests.post(url_transmit_cg, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'CargoDepot':
        this.status['text'] = "Wing Mission Info updated"
        url_transmit_cargo = 'http://forthemug.com:4567/cargodepot'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_cargo, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'Docked':
        this.status['text'] = "Docked"
        url_transmit_dockinf = 'http://forthemug.com:4567/dockedinfoupdate'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_dockinf, data=transmit_json, headers=headers, timeout=7)
        sys.stderr.write("{} CMDR {} has docked at {} in the {} system \n".format(entry['timestamp'],cmdr,station,system,))

    elif entry['event'] == 'Undocked':
        this.status['text'] = "Undocked"
        url_transmit_undockinf = 'http://forthemug.com:4567/undockedinfoupdate'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_undockinf, data=transmit_json, headers=headers, timeout=7)
        sys.stderr.write("{} CMDR {} has undocked from {} in the {} system \n".format(entry['timestamp'],cmdr,station,system,))

    elif entry['event'] == 'Loadout':
        url_transmit_loadout = 'http://forthemug.com:4567/loadout'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_loadout, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'SupercruiseEntry':
        this.status['text'] = "Entered Supercruise"
        url_transmit_supercruiseentry = 'http://forthemug.com:4567/supercruiseentry'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_supercruiseentry, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'SupercruiseExit':
        this.status['text'] = "Exited Supercruise"
        url_transmit_supercruiseexit = 'http://forthemug.com:4567/supercruiseexit'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_supercruiseexit, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'NpcCrewPaidWage':
        url_transmit_npc_paid_wage = 'http://forthemug.com:4567/npccrewpaidwage'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_npc_paid_wage, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'LoadGame':
        url_transmit_loadgame = 'http://forthemug.com:4567/loadgame'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_loadgame, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'MissionAccepted':
        url_278024 = 'http://forthemug.com:4567/missiontake'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_278024, data=transmit_json, headers=headers, timeout=7)
        this.status['text'] = "Mission Accepted"
        sys.stderr.write("{} CMDR {} has accepted a mission of type {} for {} in the {} system. Mission ID {} \n".format(entry['timestamp'],cmdr,entry['Name'],entry['Faction'],system,entry['MissionID']))
        #sys.stderr.write("{} MissionID {} Required {} {} needed at {} before {} \n".format(entry['timestamp'],entry['MissionID'],entry['Count'],entry['Commodity_Localised'],entry['DestinationStation'],entry['Expiry']))

    elif entry['event'] == 'MissionCompleted':
        this.status['text'] = "Mission Completed"
        sys.stderr.write("{} CMDR {} has completed the mission with MissionID {} good job! \n".format(entry['timestamp'],cmdr,entry['MissionID']))
        url_278025 = 'http://forthemug.com:4567/missioncomplete'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_278025, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'MissionAbandoned':
        this.status['text'] = "Mission Abandoned"
        sys.stderr.write("{} CMDR {} has abandoned the mission with MissionID {} :( \n".format(entry['timestamp'],cmdr,entry['MissionID']))
        url_278026 = 'http://forthemug.com:4567/missioncomplete'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_278026, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'MissionFailed':
        this.status['text'] = "Mission Failed"
        sys.stderr.write("{} CMDR {} has failed the mission with MissionID {} :( \n".format(entry['timestamp'],cmdr,entry['MissionID']))
        url_278027 = 'http://forthemug.com:4567/missioncomplete'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_278027, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'FactionKillBond':
        this.status['text'] = "Kill Bond Earned for {:,.0f} credits".format(float(entry['Reward']))
        sys.stderr.write("{} CMDR {} has earned a bond of {} fighting in the {} system fighting against the {} :) \n".format(entry['timestamp'],cmdr,entry['Reward'],system,entry['VictimFaction']))
        url_transmit_bond = 'http://forthemug.com:4567/factionkillbond'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_bond, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'Bounty':
        this.status['text'] = "Bounty Earned for {:,.0f} credits".format(float(entry['TotalReward']))
        sys.stderr.write("{} CMDR {} has earned {} by killing a {} fighting in the {} system fighting against the {} :) \n".format(entry['timestamp'],cmdr,entry['TotalReward'],entry['Target'],system,entry['VictimFaction']))
        url_transmit_bounty = 'http://forthemug.com:4567/bounty'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_bounty, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'RedeemVoucher':
        if entry['Type'] == 'CombatBond':
            this.status['text'] = "Combat Bond cashed in for {:,.0f} credits".format(float(entry['Amount']))
            sys.stderr.write("{} CMDR {} has earned {} by killing combatants in the {} combat zone :) \n".format(entry['timestamp'],cmdr,entry['Amount'],system))
            url_transmit_voucher = 'http://forthemug.com:4567/redeemvoucher'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_voucher, data=transmit_json, headers=headers, timeout=7)

        if entry['Type'] == 'bounty':
            this.status['text'] = "Bounty Voucher cashed in for {:,.0f} credits".format(float(entry['Amount']))
            sys.stderr.write("{} CMDR {} has earned {} by killing a pirates in the {} system :) \n".format(entry['timestamp'],cmdr,entry['Amount'],system))
            url_transmit_voucher = 'http://forthemug.com:4567/redeemvoucher'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_voucher, data=transmit_json, headers=headers, timeout=7)

        if entry['Type'] == 'settlement':
            this.status['text'] = "{:,.0f} credits paid to settle fines".format(float(entry['Amount']))
            sys.stderr.write("{} CMDR {} has paid {} to settle fines in and around the {} system :) \n".format(entry['timestamp'],cmdr,entry['Amount'],system))
            url_transmit_voucher = 'http://forthemug.com:4567/redeemvoucher'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_voucher, data=transmit_json, headers=headers, timeout=7)

        if entry['Type'] == 'trade':
            this.status['text'] = "{:,.0f} credits earned from trade voucher".format(float(entry['Amount']))
            sys.stderr.write("{} CMDR {} has earned {} credits handing in trade vouchers in the {} system :) \n".format(entry['timestamp'],cmdr,entry['Amount'],system))
            url_transmit_voucher = 'http://forthemug.com:4567/redeemvoucher'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_voucher, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'SellExplorationData':
        baseval = entry['BaseValue']
        bonusval = entry['Bonus']
        totalvalue = baseval + bonusval
        this.status['text'] = "Sold ExplorationData for {:,.0f} credits".format(float(totalvalue))
        sys.stderr.write("{} CMDR {} has sold {} credits of exploration data \n".format(entry['timestamp'],cmdr,totalvalue))
        url_transmit_voucher = 'http://forthemug.com:4567/explorationdata'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_voucher, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'Statistics':
        url_transmit_stats = 'http://forthemug.com:4567/stats'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_stats, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'Died':
        this.status['text'] = "Oops.... you died :( :( :("
        sys.stderr.write("{} CMDR {} died \n".format(entry['timestamp'],cmdr))
        url_transmit_death = 'http://forthemug.com:4567/death'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_death, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'Scan':
        this.status['text'] = "Scan Data stored for Cartographics"
        url_transmit_scan = 'http://forthemug.com:4567/scan'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_scan, data=transmit_json, headers=headers, timeout=7)
        #sleep(0.2)
        explo_credits(cmdr)

    elif entry['event'] == 'MissionRedirected':
        this.status['text'] = "Mission Update Received"
        url_transmit_missionupdate = 'http://forthemug.com:4567/missionupdate'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_missionupdate, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'CollectCargo':
        this.status['text'] = "Cargo scooped into cargo bay"
        url_transmit_scooped = 'http://forthemug.com:4567/cargocollection'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_scooped, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'Promotion':
        this.status['text'] = "Congratulations on your promotion commander"
        url_transmit_promo = 'http://forthemug.com:4567/cmdrpromotion'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_promo, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'Cargo':
        url_transmit_cargo = 'http://forthemug.com:4567/cargo'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        response = requests.post(url_transmit_cargo, data=transmit_json, headers=headers, timeout=7)

    elif entry['event'] == 'HeatWarning':
        this.status['text'] = "Its getting warm in here"

    elif entry['event'] == 'Scanned':
        this.status['text'] = "You have been scanned"

    elif entry['event'] == 'SendText':
        if "mission close" in entry['Message']:
            this.status['text'] = "Sending Mission close Command"
            url_transmit_mr = 'http://forthemug.com:4567/missionreset'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_mr, data=transmit_json, headers=headers, timeout=7)

        if "tick update" in entry['Message']:
            this.status['text'] = "Sending tick update Command"
            url_transmit_tu = 'http://forthemug.com:4567/tickupdate'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_tu, data=transmit_json, headers=headers, timeout=7)

        if "TLDR" in entry['Message']:
            this.status['text'] = "Sending TLDR update Command"
            url_transmit_tldr = 'http://forthemug.com:4567/tldr'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_tldr, data=transmit_json, headers=headers, timeout=7)

        if "COLBRIEF" in entry['Message']:
            this.status['text'] = "Sending TLDR update Colonia Command"
            url_transmit_tldrcol = 'http://forthemug.com:4567/tldrcol'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_tldrcol, data=transmit_json, headers=headers, timeout=7)

        if "stateupdate" in entry['Message']:
            this.status['text'] = "Sending state update Command"
            url_transmit_state = 'http://forthemug.com:4567/state'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_state, data=transmit_json, headers=headers, timeout=7)

        if "recheck system" in entry['Message']:
            this.status['text'] = "Forcing System Re-check of {} on next jump in".format(system)
            url_transmit_fr = 'http://forthemug.com:4567/recheckinfluence'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_fr, data=transmit_json, headers=headers, timeout=7)

        if "generalupdate" in entry['Message']:
            this.status['text'] = "Sending General update Command"
            url_transmit_gen_state = 'http://forthemug.com:4567/dailygeneral'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_gen_state, data=transmit_json, headers=headers, timeout=7)

        if "coloniaupdate" in entry['Message']:
            this.status['text'] = "Sending state update Command"
            url_transmit_col_state = 'http://forthemug.com:4567/colstate'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_col_state, data=transmit_json, headers=headers, timeout=7)

        if "race start" in entry['Message']:
            this.status['text'] = "Sending Race START info"
            url_transmit_tu = 'http://forthemug.com:4567/racestart'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_tu, data=transmit_json, headers=headers, timeout=7)

        if "race end" in entry['Message']:
            this.status['text'] = "Sending Race END info"
            url_transmit_tu = 'http://forthemug.com:4567/raceend'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_tu, data=transmit_json, headers=headers, timeout=7)

        if "exploration start" in entry['Message']:
            this.status['text'] = "Sending Exploration Start command"
            url_transmit_explo_start = 'http://forthemug.com:4567/explostart'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_explo_start, data=transmit_json, headers=headers, timeout=7)

        if "reset exploration data" in entry['Message']:
            this.status['text'] = "Resetting your Exploration 2.0 Data"
            url_transmit_explo_reset = 'http://forthemug.com:4567/exploreset'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_explo_reset, data=transmit_json, headers=headers, timeout=7)
            explo_credits(cmdr)

        if "inf reload" in entry['Message']:
            this.status['text'] = "Developer Mode : inf reload command sent"
            url_transmit_dev_inf_reload = 'http://forthemug.com:4567/devinfreload'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_dev_inf_reload, data=transmit_json, headers=headers, timeout=7)

        if "allow list reload" in entry['Message']:
            this.status['text'] = "Developer Mode : allow list reload command sent"
            url_transmit_dev_allow_reload = 'http://forthemug.com:4567/devallowreload'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_dev_allow_reload, data=transmit_json, headers=headers, timeout=7)

        if "black ops add" in entry['Message']:
            this.status['text'] = "Admin Mode : Black Ops Faction Added"
            url_transmit_dev_blops_add = 'http://forthemug.com:4567/blopsadd'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_dev_blops_add, data=transmit_json, headers=headers, timeout=7)

        if "black ops active" in entry['Message']:
            this.status['text'] = "Black ops Mode : Enjoy Being Naughty Commander"
            blops_add = 'http://forthemug.com:4567/silentrunning'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(blops_add, data=transmit_json, headers=headers, timeout=7)

        if "black ops reset" in entry['Message']:
            this.status['text'] = "Black ops Mode : Welcome back Commander"
            blops_remove = 'http://forthemug.com:4567/normalrunning'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(blops_remove, data=transmit_json, headers=headers, timeout=7)

        if "auth list reload" in entry['Message']:
            this.status['text'] = "Admin Mode : Reloading Auth List"
            url_transmit_dev_auth_reload = 'http://forthemug.com:4567/authlistreload'
            headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
            response = requests.post(url_transmit_dev_auth_reload, data=transmit_json, headers=headers, timeout=7)

        if "explo system" in entry['Message']:
            url = "http://forthemug.com:4567/explosystem.json/{}/{}".format(cmdr,system)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You Have sold {:,.0f} credits in {} today".format(json_data['ExplorationSystemTotal'],system)

        if "explo today" in entry['Message']:
            url = "http://forthemug.com:4567/explotoday.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You Have sold {:,.0f} credits in total so far today".format(json_data['ExplorationTodayTotal'])

        if "explo week" in entry['Message']:
            url = "http://forthemug.com:4567/exploweek.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You Have sold {:,.0f} credits in total so far this week".format(float(json_data['ExplorationWeekTotal']))

        if "explo total" in entry['Message']:
            url = "http://forthemug.com:4567/explototal.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            test = str("{:,.0f}".format(json_data['ExplorationTotal']))
            this.status['text'] = "You Have sold {:,.0f} credits in Exploration Data so far".format(float(test))

        if "missions today" in entry['Message']:
            url = "http://forthemug.com:4567/missionday.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You Have earned {:,.0f} mission points today".format(float(json_data['MissionDayTotal']))

        if "missions week" in entry['Message']:
            url = "http://forthemug.com:4567/missionweek.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You Have earned {:,.0f} mission points this week".format(float(json_data['MissionWeekTotal']))

        if "missions total" in entry['Message']:
            url = "http://forthemug.com:4567/missiontotal.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You Have earned {:,.0f} mission points in total so far".format(float(json_data['MissionTotal']))

        if "cargo buy today" in entry['Message']:
            url = "http://forthemug.com:4567/cargoboughttoday.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have bought {:,.0f} units of cargo today".format(float(json_data['CargoBuyToday']))

        if "cargo buy week" in entry['Message']:
            url = "http://forthemug.com:4567/cargoboughtweek.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have bought {:,.0f} units of cargo this week".format(float(json_data['CargoBuyWeek']))

        if "cargo buy total" in entry['Message']:
            url = "http://forthemug.com:4567/cargoboughttotal.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have bought {:,.0f} units of cargo in total".format(float(json_data['CargoBuyTotal']))

        if "cargo sell today" in entry['Message']:
            url = "http://forthemug.com:4567/cargosoldtoday.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have sold {:,.0f} units of cargo today".format(float(json_data['CargoSellToday']))

        if "cargo sell week" in entry['Message']:
            url = "http://forthemug.com:4567/cargosoldweek.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have sold {:,.0f} units of cargo this week".format(float(json_data['CargoSellWeek']))

        if "cargo sell total" in entry['Message']:
            url = "http://forthemug.com:4567/cargosoldtotal.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have sold {:,.0f} units of cargo in total".format(float(json_data['CargoSellTotal']))

        if "combat today" in entry['Message']:
            url = "http://forthemug.com:4567/combatbondstoday.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have redeemed {:,.0f} credits today".format(float(json_data['CombatBondsToday']))

        if "combat week" in entry['Message']:
            url = "http://forthemug.com:4567/combatbondsweek.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have redeemed {:,.0f} credits this week".format(float(json_data['CombatBondsWeek']))

        if "combat total" in entry['Message']:
            url = "http://forthemug.com:4567/combatbondstotal.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have redeemed {:,.0f} credits in total".format(float(json_data['CombatBondsTotal']))

        if "bounty today" in entry['Message']:
            url = "http://forthemug.com:4567/bountytoday.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have redeemed {:,.0f} credits today".format(float(json_data['BountyToday']))

        if "bounty week" in entry['Message']:
            url = "http://forthemug.com:4567/bountyweek.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have redeemed {:,.0f} credits this week".format(float(json_data['BountyWeek']))

        if "bounty total" in entry['Message']:
            url = "http://forthemug.com:4567/bountytotal.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have redeemed {:,.0f} credits in total".format(float(json_data['BountyTotal']))

        if "jumps today" in entry['Message']:
            url = "http://forthemug.com:4567/jumpstoday.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have jumped {:,.0f} times today".format(float(json_data['JumpsToday']))

        if "jumps week" in entry['Message']:
            url = "http://forthemug.com:4567/jumpsweek.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have jumped {:,.0f} times this week".format(float(json_data['JumpsWeek']))

        if "jumps total" in entry['Message']:
            url = "http://forthemug.com:4567/jumpstotal.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have jumped {:,.0f} times in total".format(float(json_data['JumpsTotal']))

        if "ly today" in entry['Message']:
            url = "http://forthemug.com:4567/lytoday.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have jumped {:,.2f} Light Years today".format(float(json_data['LYToday']))

        if "ly week" in entry['Message']:
            url = "http://forthemug.com:4567/lyweek.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have jumped {:,.2f} Light Years this week".format(float(json_data['LYWeek']))

        if "ly total" in entry['Message']:
            url = "http://forthemug.com:4567/lytotal.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have jumped {:,.2f} Light Years in total".format(float(json_data['LYTotal']))

        if "scan today" in entry['Message']:
            url = "http://forthemug.com:4567/scantoday.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have scanned {:,.0f} objects today".format(float(json_data['ScanToday']))

        if "scan week" in entry['Message']:
            url = "http://forthemug.com:4567/scanweek.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have scanned {:,.0f} objects this week".format(float(json_data['ScanWeek']))

        if "scan total" in entry['Message']:
            url = "http://forthemug.com:4567/scantotal.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "You have scanned {:,.0f} objects in total".format(float(json_data['ScanTotal']))

        if "my hutton run" in entry['Message']:
            url = "http://forthemug.com:4567/myhuttonrun.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            if json_data['SecondCount'] == "0" :
                this.status['text'] = "You have not completed a Hutton Run"
            else:
                this.status['text'] = "Your best Hutton Run is {}".format(json_data['TravelTime'])

        if "best hutton run" in entry['Message']:
            url = "http://forthemug.com:4567/besthuttonrun.json/{}".format(cmdr)
            response = requests.get(url)
            json_data = response.json()
            this.status['text'] = "BEST Hutton Run is CMDR {} in {}".format(json_data['commandername'],json_data['TravelTime'])

        if "!shoutout" in entry['Message']:
            url = "http://forthemug.com:4567/shoutout.json/"
            response = requests.get(url)
            json_data = response.json()
            if json_data['online'] == "true":
                this.status['text'] = "Shoutout sent to the LIVE DJ"
                url_transmit_shoutout = 'http://forthemug.com:4567/shoutout'
                headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
                response = requests.post(url_transmit_shoutout, data=transmit_json, headers=headers, timeout=7)
            if json_data['online'] == "false":
                this.status['text'] = "There is no LIVE DJ at the moment... please try again later"

    if entry['event'] == 'CommunityGoal':
        #print ('CG updating')
        for goal in entry['CurrentGoals']:

            if not goal['IsComplete']: #v0.2Collect Active CG only
                """
                First Extract CG Data
                """
                communitygoalID = goal['CGID']
                communitygoalName = goal['Title']
                contributionsTotal= goal['CurrentTotal']
                contributorsNum = goal['NumContributors']
                contribution = goal['PlayerContribution']
                percentileBand = goal['PlayerPercentileBand']
                #print ('CG Variables Calculated')
                """
                Build the Data Set to Submit, based on the Entry field number from the form.
                """
                form_data = {
                    'entry.1465819909' : communitygoalID,
                    'entry.2023048714' : communitygoalName,
                    'entry.617265888' : contributionsTotal,
                    'entry.1469183421' : contributorsNum,
                    'entry.2011125544' : contribution,
                    'entry.1759162752' : percentileBand
                    }
                url = "https://docs.google.com/forms/d/e/1FAIpQLScJHvd9MNKMMNGpjZtlcT74u6Wnhcgesqz38a8JWBC94Se2Dg/formResponse"
                """
                Request URl as a POST with the Form URL plus send the Form Data to each entry.
                """
                try:
                    r = requests.post(url, data=form_data)
                    if r.status_code == 200:
                        #print ('URL Success')
                        this.msg = 'CG Post Success'
                    else:
                        #print ('URL Fail' + str(r.status_code))
                        this.msg = 'CG Post Failed'
                except:
                    this.msg = 'CG Post Exception'

def cmdr_data(data, is_beta):
    """
    Obtained new data from Frontier about our commander, location and ships
    :param data:
    :return:
    """
    explo_credits(data.get('commander').get('name'))
    if not is_beta:
        cmdr_data.last = data
        #this.status['text'] = "Got new data ({} chars)".format(len(str(data)))
        sys.stderr.write("Got new data ({} chars)\n".format(len(str(data))))
        data2 = json.dumps(data)
        transmit_json = zlib.compress(data2)
        url_transmit_dock = 'http://forthemug.com:4567/docked'
        headers = {'content-type': 'application/octet-stream','content-encoding': 'zlib'}
        _response = requests.post(url_transmit_dock, data=transmit_json, headers=headers, timeout=7)
        cmdr_data.last = None

def plugin_stop():
    print "Farewell cruel world!"
