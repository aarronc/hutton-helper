"""
Broadcasts to the Community Goal Reward Thresholds Calculator.
"""

import plugin
import xmit

CGT_TARGET_URL = 'https://docs.google.com/forms/d/e/1FAIpQLScJHvd9MNKMMNGpjZtlcT74u6Wnhcgesqz38a8JWBC94Se2Dg/formResponse'


class CommunityGoalWatcher(plugin.HuttonHelperPlugin):
    "Forwards data to the CGThreshCalc team."

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        "Called when Elite Dangerous writes to the commander's journal."

        if entry['event'] == 'CommunityGoal':
            for goal in entry['CurrentGoals']:
                if not goal['IsComplete']: # v0.2Collect Active CG only
                    data = {
                        'entry.1465819909': goal['CGID'],
                        'entry.2023048714': goal['Title'],
                        'entry.617265888': goal['CurrentTotal'],
                        'entry.1469183421': goal['NumContributors'],
                        'entry.2011125544': goal['PlayerContribution'],
                        'entry.1759162752': goal['PlayerPercentileBand']
                    }

                    xmit.post(CGT_TARGET_URL, data=data)
