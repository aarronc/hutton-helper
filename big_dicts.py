"""
big_dicts

just a place to store large lookup tables etc
"""

import csv

def csv_to_dict(filename):
    """Import CSV as string-to-string dictionary"""
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return {row['key']: row['value'] for row in reader}
    except FileNotFoundError:
        print(f"File {filename} not found")
        return {}

# Needs extra work new landable events etc
# maybe should make this look up from a CSV easier to edit ?
# removed 'FSDJump': "Jumped into {StarSystem} system in the {StarRegion} Region",
# to allow BGS Driectives to use the message space
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
    'USSDrop' : "Dropped into {USSType_Localised} Threat : {USSThreat}",
    'Disembark' : "Get out of the chair and have some fun commander!",
    'Embark' : "Welcome Back, hows the weather out there?"
    
}

REDEEM_TYPE_STATUS_FORMATS = {
    'CombatBond': "Combat Bond cashed in for {:,.0f} credits",
    'bounty': "Bounty Voucher cashed in for {:,.0f} credits",
    'settlement': "{:,.0f} credits paid to settle fines",
    'trade': "{:,.0f} credits earned from trade voucher",
}

# Events and reportable path on website
EVENT_PATHS = {
  "ApproachSettlement": "/approachsettlement",
  "BackpackChange": "/backpackchange",
  "Bounty": "/bounty",
  "BuyMicroResources": "/buymicroresources",
  "Cargo": "/cargo",
  "CargoDepot": "/cargodepot",
  "CargoTransfer": "/cargotransfer",
  "CarrierDepositFuel": "/carrierdepositfuel",
  "CarrierStats": "/carrierstats",
  "CarrierTradeOrder":"/carriertradeorder",
  "CarrierJump": "/carrierjump",
  "CollectCargo": "/collectcargo",
  "CollectItems": "/collectitems",
  "ColonisationConstructionDepot" : "/colonisationconstructiondepot",
  "ColonisationContribution" : "/colonisationcontribution",
  "CommitCrime": "/commitcrime",
  "CommunityGoal": "/communitygoal",
  "Died": "/died",
  "Disembark": "/disembark",
  "Docked": "/docked",
  "DockingRequested": "/dockingrequested",
  "DockingGranted": "/dockinggranted",
  "EjectCargo": "/ejectcargo",
  "Embark": "/embark",
  "EscapeInterdiction": "/escapeinterdiction",
  "FactionKillBond": "/factionkillbond",
  "Friends": "/friends",
  "FSDJump": "/fsdjump",
  "FSSAllBodiesFound": "/fssallbodiesfound",
  "FSSSignalDiscovered": "/fsssignaldiscovered",
  "Interdicted": "/interdicted",
  "Interdiction": "/interdiction",
  "LaunchDrone": "/launchdrone",
  "LoadGame": "/loadgame",
  "Loadout": "/loadout",
  "Location": "/location",
  "MarketBuy": "/marketbuy",
  "MarketSell": "/marketsell",
  "MiningRefined": "/miningrefined",
  "MissionAbandoned": "/missionabandoned",
  "MissionAccepted": "/missionaccepted",
  "MissionCompleted": "/missioncompleted",
  "MissionFailed": "/missionfailed",
  "MissionRedirected": "/missionredirected",
  "MultiSellExplorationData": "/multisellexplorationdata",
  "NpcCrewPaidWage": "/npccrewpaidwage",
  "Promotion": "/promotion",
  "ProspectedAsteroid": "/prospectedasteroid",
  "Rank": "/rank",
  "ReceiveText": "/receivetext",
  "RedeemVoucher": "/redeemvoucher",
  "SAAScanComplete": "/saascancomplete",
  "SAASignalsFound": "/saasignalsfound",
  "Scan": "/scan",
  "SearchAndRescue": "/searchandrescue",
  "SellExplorationData": "/sellexplorationdata",
  "SellMicroResources": "/sellmicroresources",
  "SendText": "/sendtext",
  "ShipTargeted": "/shiptargeted",
  "ShipLocker": "/shiplocker",
  "SquadronStartup": "/squadronstartup",
  "StartJump": "/startjump",
  "Statistics": "/statistics",
  "SupercruiseEntry": "/supercruiseentry",
  "SupercruiseExit": "/supercruiseexit",
  "Undocked": "/undocked",
  "USSDrop": "/ussdrop"
}


ITEM_LOOKUP = csv_to_dict('item_lookup.csv')
