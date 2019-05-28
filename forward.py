"""
Broadcasts to the Hutton Helper web site.
"""

from version import HH_VERSION

import json
import zlib

import plugin
import xmit


class ForTheMugPlugin(plugin.HuttonHelperPlugin):
    "Forwards data to the CGThreshCalc team."

    event_paths = {
        'Bounty': '/bounty',
        'Cargo': '/cargo',
        'CargoDepot': '/cargodepot',
        'CollectCargo': '/cargocollection',
        'CommitCrime': '/commitcrime',
        'CommunityGoal': '/communitygoal',
        'Died': '/death',
        'Docked': '/dockedinfoupdate',
        'EjectCargo': '/ejectcargo',
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
        'ReceiveText': '/receivetext',
        'Scan': '/scan',
        'SellExplorationData': '/explorationdata',
        'MultiSellExplorationData': '/multisellexplorationdata',
        'Statistics': '/stats',
        'SupercruiseEntry': '/supercruiseentry',
        'SupercruiseExit': '/supercruiseexit',
        'Undocked': '/undockedinfoupdate',
        'FSSSignalDiscovered': '/fsssignaldiscovered',
        'SAAScanComplete': '/saascancomplete',
        'ProspectedAsteroid': '/prospectedasteroid',
        'MiningRefined': '/miningrefined',
        'SquadronStartup': '/squadronstartup',
        'USSDrop' : '/ussdrop'
        }

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        event = entry['event']
        event_path = self.event_paths.get(event)

        compress_json = json.dumps(entry)
        transmit_json = zlib.compress(compress_json)

        if event_path:
            xmit.post(event_path, data=transmit_json, parse=False, headers=xmit.COMPRESSED_OCTET_STREAM)
