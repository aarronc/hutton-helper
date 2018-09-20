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

    status_formats = {
        # OPTIONAL unless there's no matching xmit_paths entry above
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

    def __init__(self, helper):
        "Initialise the ``CommandPlugin``."

        self.commands = set(self.xmit_paths.keys()) | set(self.status_formats.keys())

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        if entry['event'] != 'SendText':
            return

        compress_json = json.dumps(entry)
        transmit_json = zlib.compress(compress_json)

        for command in self.commands:
            if command in entry['Message']:
                # Get the status format:
                command_status_format = self.status_formats.get(command)
                if not command_status_format:
                    command_status_format = 'Sent {command} Command'

                # Send the event if required, getting json_data back:
                json_data = None
                command_xmit_path = self.xmit_paths.get(command)
                if command_xmit_path:
                    command_xmit_path = command_xmit_path.format(cmdr=cmdr, system=system)
                    if '{cmdr}' in command_xmit_path: # FILTHY hack to figure out if it's a 'get'
                        json_data = xmit.get(command_xmit_path)
                    else:
                        json_data = xmit.post(command_xmit_path, data=transmit_json, headers=xmit.COMPRESSED_OCTET_STREAM)

                if not json_data:
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

        if "!shoutout" in entry['Message']:
            json_data = xmit.get('/shoutout.json')

            if not json_data:
                self.helper.status("Could not shout, shout, or let it all out.")

            elif json_data['online'] == "true":
                self.helper.status("Shoutout sent to the LIVE DJ")
                xmit_event('/shoutout')

            if json_data['online'] == "false":
                self.helper.status("There is no LIVE DJ at the moment... please try again later")
