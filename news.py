
"""
Module to provide the news.
"""

import tkinter as tk
import uuid
from widgets import SelfWrappingHyperlinkLabel
import xmit

REFRESH_MINUTES = 3
DEFAULT_NEWS_URL = 'http://hot.forthemug.com/dailyupdate/index.php'
WRAP_LENGTH = 200
uptime_stats = uuid.uuid4()


class HuttonNews(SelfWrappingHyperlinkLabel):
    "A label to display the headline and link to the news. Not a plugin because it doesn't have preferences or watch the pilot."

    def __init__(self, parent):
        "Initialise the ``HuttonNews``."

        SelfWrappingHyperlinkLabel.__init__(
            self,
            parent,
            text="Fetching...",
            url=DEFAULT_NEWS_URL,
            wraplength=50,  # updated in __configure_event below
            anchor=tk.NW
        )
        self.after(250, self.news_update)

    def news_update(self):
        "Update the news."

        self.after(REFRESH_MINUTES * 60 * 1000, self.news_update)

        news_data = xmit.get('/news.json/{}'.format(uptime_stats))
        if news_data:
            self['url'] = news_data['link']
            self['text'] = news_data['headline']

        else:
            self['text'] = "News refresh failed"
