"""
Treats LOCAL as if it's a command line.
"""

from version import HH_VERSION

import json
import zlib

import plugin
import xmit


class CommandPlugin(plugin.HuttonHelperPlugin):
    "Sends commands to the server."

    xmit_paths = {
        'are we there yet': '/huttontimer.json/{cmdr}', # Calls a commanders current Hutton Run Time
        'allow list reload': '/devallowreload',
        'auth list reload': '/authlistreload',
        'best hutton run': '/besthuttonrun.json/{cmdr}',  # safe for testing
        'black ops add': '/blopsadd',
        'black ops active': '/silentrunning',
        'black ops reset': '/normalrunning',
        'COLBRIEF': '/tldrcol',
        'coloniaupdate': '/colstate',
        'exploration start': '/explostart',
        'explo system': '/explosystem.json/{cmdr}/{system}',
        'generalupdate': '/dailygeneral',
        'inf reload': '/devinfreload',
        'mission close': '/missionreset',
        'mugify' : '/verify',
        'Mugify' : '/verify',
        'race start': '/racestart',
        'race end': '/raceend',
        'recheck system': '/recheckinfluence',
        'recruit': '/squadronrecruit',
        'reset exploration data': '/exploreset',  # vaguely safe for testing
        'stateupdate': '/state',
        'tick update': '/tickupdate',
        'TLDR': '/tldr'
    }

    status_formats = {
        # OPTIONAL unless there's no matching xmit_paths entry above
        'allow list reload': "Developer Mode : allow list reload command sent",
        'are we there yet': '{info}',
        'auth list reload': "Admin Mode : Reloaded Auth List",
        'best hutton run': "BEST Hutton Run is CMDR {commandername} in {TravelTime}",
        'black ops add': "Admin Mode : Black Ops Faction Added",
        'black ops active': "Black ops Mode : Enjoy Being Naughty Commander",
        'black ops reset': "Black ops Mode : Welcome back Commander",
        'COLBRIEF': "Sent TLDR update Colonia Command",
        'explo system': "You Have sold {ExplorationSystemTotal:,.0f} credits in {system} today",
        'inf reload': "Developer Mode : inf reload command sent",
        'race start': "Sent Race START info",
        'race end': "Sent Race END info",
        'recheck system': "Forced System Re-check of {system} on next jump in",
        'recruit': 'Sent request for squadron review',
        'reset exploration data': "Reset your Exploration 2.0 Data",
        'TLDR': "Sent TLDR update Command",
    }

    def __init__(self, helper):
        "Initialise the ``CommandPlugin``."

        plugin.HuttonHelperPlugin.__init__(self, helper)
        self.commands = set(self.xmit_paths.keys()) | set(self.status_formats.keys())

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        if entry['event'] != 'SendText':
            return

        compress_json = json.dumps(entry)
        transmit_json = zlib.compress(compress_json.encode('utf-8'))

        for command in self.commands:
            if command in entry['Message']:
                # Get the status format:
                command_status_format = self.status_formats.get(command)
                if not command_status_format:
                    command_status_format = 'Sent {command} Command'

                # Send the event if required, getting json_data back:
                json_data = None
                command_xmit_path_format = self.xmit_paths.get(command)
                if command_xmit_path_format:
                    command_xmit_path = command_xmit_path_format.format(cmdr=cmdr, system=system)
                    if '{cmdr}' in command_xmit_path_format: # FILTHY hack to figure out if it's a 'get'
                        json_data = xmit.get(command_xmit_path)
                    else:
                        json_data = xmit.post(command_xmit_path, data=transmit_json, headers=xmit.COMPRESSED_OCTET_STREAM)

                if xmit.FAILED:  # naughty global
                    command_status_format = 'Failed to Send {command} Command'

                # Format and display the status text:
                self.helper.status(command_status_format.format(
                    # Add variables here that you'd like to use in your status text:
                    command=command,
                    system=system,
                    # We also supply the server's reply:
                    **(json_data or {})
                ))

        # VERY special handling, with NONE of the automatic stuff above:

        if "my hutton run" in entry['Message']:
            json_data = xmit.get('/myhuttonrun.json/{}'.format(cmdr))

            if not json_data:
                self.helper.status("Failed to get Hutton Run data.")

            elif json_data['SecondCount'] == "0":
                self.helper.status("You have not completed a Hutton Run")

            else:
                self.helper.status("Your best Hutton Run is {}".format(json_data['TravelTime']))
