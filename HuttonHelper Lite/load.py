"The Hutton Helper. For the Mug!"

try:
    # for Python2
    import Tkinter as tk
    import ttk
    import tkFont
    import tkMessageBox
    is2 = True # used to check if python2
except ImportError:
    # for python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as tkFont
    import tkinter.messagebox as tkMessageBox
    import logging
    is2 = False  # used to check if is python2

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
from config import config, applongname, appversion, appname
import myNotebook as nb

import requests # still here for CG code

try:
    HERE = os.path.dirname(__file__)
    sys.path.insert(0, HERE)

    # We import the rest of the Hutton Helper together in this block while
    # we've altered sys.path so we don't inhale files from EDMC "package"
    # plugins by accident. https://git.io/fAQkf#python-package-plugins

    import forward
    import local
    import news
    # import pwpevents
    import plugin as plugin_module
    import updater
    import widgets
    import xmit
    import market
    import cargo

    from version import HH_VERSION

finally:
    del sys.path[0]

this = sys.modules[__name__]  # pylint: disable=C0103
this.msg = ""

FRONT_COVER_DELAY = 10  # seconds
UUID = str(uuid.uuid4())

if is2 == False:
    plugin_name = os.path.basename(os.path.dirname(__file__))
    logger = logging.getLogger("{}.{}".format(appname,plugin_name))
    if not logger.hasHandlers():
        level = logging.ERROR  # So logger.error(...) is equivalent to sys.stderr.write()
        logger.setLevel(level)
        logger_channel = logging.StreamHandler()
        logger_channel.setLevel(level)
        logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
        logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
        logger_formatter.default_msec_format = '%s.%03d'
        logger_channel.setFormatter(logger_formatter)
        logger.addHandler(logger_channel)

def PANIC(description=None):
    "Handle failure."

    if is2:
        sys.stderr.write("ERROR: {}\r\n".format(description or ''))
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
    else:
        logger.error("ERROR: {}".format(description or ''))
        logger.error("{}".format("\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback))))

    errorreport = {}
    errorreport['cmdr'] = news.commander
    errorreport['huttonappversion'] = HH_VERSION
    errorreport['edmcversion'] = str(appversion)
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

    return 'Hutton Helper Lite'

def plugin_start(plugin_dir):
    "Initialise the Hutton Helper plugin."

    this.helper = plugin_module.HuttonHelperHelper(config, _refresh, _status)
    this.plugins = [
        # A list of plugins to which we pass events.
        updater.UpdatePlugin(this.helper),
        forward.ForTheMugPlugin(this.helper),
        local.CommandPlugin(this.helper),
        market.MarketPlugin(this.helper),
        cargo.CargoPlugin(this.helper),
        # pwpevents.PwpEventsPlugin(this.helper),
    ]

    for plugin in plugins:
        try:
            plugin.plugin_start()
        except:
            PANIC("{}.plugin_start".format(plugin))

    return 'Hutton Helper Lite'

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
    this.status = widgets.SelfWrappingLabel(table, anchor=anchor, text="For the Mug!", wraplength=50)
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
    _show_front_cover(False)

    # Arrange for the front cover to be shown for at least a few seconds
    this.front_cover_until = time.time() + FRONT_COVER_DELAY
    frame.after(1000 * FRONT_COVER_DELAY, _refresh)
    frame.after_idle(_refresh)
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


def _show_front_cover(show=False):
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
                any_ready = False
                plugin_frame.grid(row=plugin_row, sticky=tk.EW)

    _show_front_cover(not any_ready)


def _status(text=''):
    "Set the status text."

    this.status['text'] = text


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
    'CargoDepot': "Wing Mission Info updated",
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

ITEM_LOOKUP = {
    "advancedcatalysers" : "Advanced Catalysers",
    "advancedmedicines" : "Advanced Medicines",
    "agriculturalmedicines" : "Agri-Medicines",
    "agronomictreatment" : "Agronomic Treatment",
    "airelics" : "AI Relics",
    "alexandrite" : "Alexandrite",
    "algae" : "Algae",
    "aluminium" : "Aluminium",
    "ancientcasket" : "Ancient Casket",
    "ancientkey" : "Ancient Key",
    "ancientorb" : "Ancient Orb",
    "ancientrelic" : "Ancient Relic",
    "ancienttablet" : "Ancient Tablet",
    "ancienttotem" : "Ancient Totem",
    "ancienturn" : "Ancient Urn",
    "animalmeat" : "Animal Meat",
    "animalmonitors" : "Animal Monitors",
    "antimattercontainmentunit" : "Antimatter Containment Unit",
    "antiquejewellery" : "Antique Jewellery",
    "antiquities" : "Antiquities",
    "aquaponicsystems" : "Aquaponic Systems",
    "articulationmotors" : "Articulation Motors",
    "assaultplans" : "Assault Plans",
    "atmosphericextractors" : "Atmospheric Processors",
    "autofabricators" : "Auto-Fabricators",
    "basicmedicines" : "Basic Medicines",
    "basicnarcotics" : "Narcotics",
    "battleweapons" : "Battle Weapons",
    "bauxite" : "Bauxite",
    "beer" : "Beer",
    "benitoite" : "Benitoite",
    "bertrandite" : "Bertrandite",
    "beryllium" : "Beryllium",
    "bioreducinglichen" : "Bioreducing Lichen",
    "biowaste" : "Biowaste",
    "bismuth" : "Bismuth",
    "bootlegliquor" : "Bootleg Liquor",
    "bromellite" : "Bromellite",
    "buildingfabricators" : "Building Fabricators",
    "ceramiccomposites" : "Ceramic Composites",
    "chemicalwaste" : "Chemical Waste",
    "clothing" : "Clothing",
    "cmmcomposite" : "CMM Composite",
    "cobalt" : "Cobalt",
    "coffee" : "Coffee",
    "coltan" : "Coltan",
    "combatstabilisers" : "Combat Stabilisers",
    "comercialsamples" : "Commercial Samples",
    "computercomponents" : "Computer Components",
    "conductivefabrics" : "Conductive Fabrics",
    "consumertechnology" : "Consumer Technology",
    "coolinghoses" : "Micro-weave Cooling Hoses",
    "copper" : "Copper",
    "cropharvesters" : "Crop Harvesters",
    "cryolite" : "Cryolite",
    "damagedescapepod" : "Damaged Escape Pod",
    "datacore" : "Data Core",
    "diagnosticsensor" : "Hardware Diagnostic Sensor",
    "diplomaticbag" : "Diplomatic Bag",
    "domesticappliances" : "Domestic Appliances",
    "drones" : "Limpets",
    "duradrives" : "Duradrives",
    "earthrelics" : "Earth Relics",
    "emergencypowercells" : "Emergency Power Cells",
    "encripteddatastorage" : "Encrypted Data Storage",
    "encryptedcorrespondence" : "Encrypted Correspondence",
    "evacuationshelter" : "Evacuation Shelter",
    "exhaustmanifold" : "Exhaust Manifold",
    "explosives" : "Explosives",
    "fish" : "Fish",
    "foodcartridges" : "Food Cartridges",
    "fossilremnants" : "Fossil Remnants",
    "fruitandvegetables" : "Fruit and Vegetables",
    "gallite" : "Gallite",
    "gallium" : "Gallium",
    "genebank" : "Gene Bank",
    "geologicalequipment" : "Geological Equipment",
    "geologicalsamples" : "Geological Samples",
    "gold" : "Gold",
    "goslarite" : "Goslarite",
    "grain" : "Grain",
    "grandidierite" : "Grandidierite",
    "hafnium178" : "Hafnium 178",
    "hazardousenvironmentsuits" : "H.E. Suits",
    "heatsinkinterlink" : "Heatsink Interlink",
    "heliostaticfurnaces" : "Microbial Furnaces",
    "hnshockmount" : "HN Shock Mount",
    "hostage" : "Hostages",
    "hydrogenfuel" : "Hydrogen Fuel",
    "hydrogenperoxide" : "Hydrogen Peroxide",
    "imperialslaves" : "Imperial Slaves",
    "indite" : "Indite",
    "indium" : "Indium",
    "insulatingmembrane" : "Insulating Membrane",
    "iondistributor" : "Ion Distributor",
    "jadeite" : "Jadeite",
    "landmines" : "Landmines",
    "lanthanum" : "Lanthanum",
    "largeexplorationdatacash" : "Large Survey Data Cache",
    "leather" : "Leather",
    "lepidolite" : "Lepidolite",
    "liquidoxygen" : "Liquid oxygen",
    "liquor" : "Liquor",
    "lithium" : "Lithium",
    "lithiumhydroxide" : "Lithium Hydroxide",
    "lowtemperaturediamond" : "Low Temperature Diamonds",
    "magneticemittercoil" : "Magnetic Emitter Coil",
    "marinesupplies" : "Marine Equipment",
    "medicaldiagnosticequipment" : "Medical Diagnostic Equipment",
    "metaalloys" : "Meta-Alloys",
    "methaneclathrate" : "Methane Clathrate",
    "methanolmonohydratecrystals" : "Methanol Monohydrate Crystals",
    "microcontrollers" : "Micro Controllers",
    "militarygradefabrics" : "Military Grade Fabrics",
    "militaryintelligence" : "Military Intelligence",
    "mineralextractors" : "Mineral Extractors",
    "mineraloil" : "Mineral Oil",
    "modularterminals" : "Modular Terminals",
    "moissanite" : "Moissanite",
    "monazite" : "Monazite",
    "musgravite" : "Musgravite",
    "mutomimager" : "Muon Imager",
    "mysteriousidol" : "Mysterious Idol",
    "nanobreakers" : "Nanobreakers",
    "nanomedicines" : "Nanomedicines",
    "naturalfabrics" : "Natural Fabrics",
    "neofabricinsulation" : "Neofabric Insulation",
    "nerveagents" : "Nerve Agents",
    "nonlethalweapons" : "Non-Lethal Weapons",
    "occupiedcryopod" : "Occupied Escape Pod",
    "opal" : "Void Opal",
    "osmium" : "Osmium",
    "painite" : "Painite",
    "palladium" : "Palladium",
    "performanceenhancers" : "Performance Enhancers",
    "personaleffects" : "Personal Effects",
    "personalweapons" : "Personal Weapons",
    "pesticides" : "Pesticides",
    "platinum" : "Platinum",
    "politicalprisoner" : "Political Prisoners",
    "polymers" : "Polymers",
    "powerconverter" : "Power Converter",
    "powergenerators" : "Power Generators",
    "powergridassembly" : "Energy Grid Assembly",
    "powertransferconduits" : "Power Transfer Bus",
    "praseodymium" : "Praseodymium",
    "preciousgems" : "Precious Gems",
    "progenitorcells" : "Progenitor Cells",
    "prohibitedresearchmaterials" : "Prohibited Research Materials",
    "pyrophyllite" : "Pyrophyllite",
    "radiationbaffle" : "Radiation Baffle",
    "reactivearmour" : "Reactive Armour",
    "reinforcedmountingplate" : "Reinforced Mounting Plate",
    "resonatingseparators" : "Resonating Separators",
    "rhodplumsite" : "Rhodplumsite",
    "robotics" : "Robotics",
    "rockforthfertiliser" : "Rockforth Fertiliser",
    "rutile" : "Rutile",
    "samarium" : "Samarium",
    "sap8corecontainer" : "SAP 8 Core Container",
    "scientificresearch" : "Scientific Research",
    "scientificsamples" : "Scientific Samples",
    "scrap" : "Scrap",
    "semiconductors" : "Semiconductors",
    "serendibite" : "Serendibite",
    "silver" : "Silver",
    "skimercomponents" : "Skimmer Components",
    "slaves" : "Slaves",
    "smallexplorationdatacash" : "Small Survey Data Cache",
    "spacepioneerrelics" : "Space Pioneer Relics",
    "structuralregulators" : "Structural Regulators",
    "superconductors" : "Superconductors",
    "surfacestabilisers" : "Surface Stabilisers",
    "survivalequipment" : "Survival Equipment",
    "syntheticfabrics" : "Synthetic Fabrics",
    "syntheticmeat" : "Synthetic Meat",
    "syntheticreagents" : "Synthetic Reagents",
    "taaffeite" : "Taaffeite",
    "tacticaldata" : "Tactical Data",
    "tantalum" : "Tantalum",
    "tea" : "Tea",
    "telemetrysuite" : "Telemetry Suite",
    "terrainenrichmentsystems" : "Land Enrichment Systems",
    "thallium" : "Thallium",
    "thargoidheart" : "Thargoid Heart",
    "thargoidscouttissuesample" : "Thargoid Scout Tissue Sample",
    "thargoidtissuesampletype1" : "Thargoid Cyclops Tissue Sample",
    "thargoidtissuesampletype2" : "Thargoid Basilisk Tissue Sample",
    "thargoidtissuesampletype3" : "Thargoid Medusa Tissue Sample",
    "thargoidtissuesampletype4" : "Thargoid Hydra Tissue Sample",
    "thermalcoolingunits" : "Thermal Cooling Units",
    "thorium" : "Thorium",
    "timecapsule" : "Time Capsule",
    "titanium" : "Titanium",
    "tobacco" : "Tobacco",
    "toxicwaste" : "Toxic Waste",
    "trinketsoffortune" : "Trinkets of Hidden Fortune",
    "unknownartifact" : "Thargoid Sensor",
    "unknownartifact2" : "Thargoid Probe",
    "unknownartifact3" : "Thargoid Link",
    "unknownbiologicalmatter" : "Thargoid Biological Matter",
    "unknownresin" : "Thargoid Resin",
    "unknowntechnologysamples" : "Thargoid Technology Samples",
    "unstabledatacore" : "Unstable Data Core",
    "uraninite" : "Uraninite",
    "uranium" : "Uranium",
    "usscargoancientartefact" : "Ancient Artefact",
    "usscargoblackbox" : "Black Box",
    "usscargoexperimentalchemicals" : "Experimental Chemicals",
    "usscargomilitaryplans" : "Military Plans",
    "usscargoprototypetech" : "Prototype Tech",
    "usscargorareartwork" : "Rare Artwork",
    "usscargorebeltransmissions" : "Rebel Transmissions",
    "usscargotechnicalblueprints" : "Technical Blueprints",
    "usscargotradedata" : "Trade Data",
    "water" : "Water",
    "waterpurifiers" : "Water Purifiers",
    "wine" : "Wine",
    "wreckagecomponents" : "Wreckage Components"
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
    entry['gameversion'] = state['GameVersion']
    
    if isinstance(appversion, str):
        entry['edmcversion'] = appversion
    else:
        entry['edmcversion'] = str(appversion())

    entry['uuid'] = UUID

    compress_json = json.dumps(entry)
    compress_json = compress_json.encode('utf-8')
    transmit_json = zlib.compress(compress_json)

    event = entry['event']
    #sys.stderr.write('event: {}\r\n'.format(event)) #Very Chatty

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
        this.status['text'] = "{:,.0f} {} bought".format(float(entry['Count']), ITEM_LOOKUP.get(entry['Type'], entry['Type']))

    elif event == 'MarketSell':
        this.status['text'] = "{:,.0f} {} sold".format(float(entry['Count']), ITEM_LOOKUP.get(entry['Type'], entry['Type']))

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
        compress_json = json.dumps(dict(data))
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
