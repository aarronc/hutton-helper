"""
Broadcasts to the Hutton Helper web site.
"""

from __init__ import __version__ as HH_VERSION

import plugin
import xmit


class ForTheMugPlugin(plugin.HuttonHelperPlugin):
    "Forwards data to the CGThreshCalc team."

    event_paths = {
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

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        event = entry['event']
        event_path = self.event_paths.get(event)

        if event_path:
            xmit.post(xmit_path, data=data, parse=False, headers=xmit.COMPRESSED_OCTET_STREAM)
