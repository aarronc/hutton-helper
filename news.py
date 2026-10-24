
"""
Module to provide the news.
"""
try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for python 3
    import tkinter as tk

from widgets import SelfWrappingHyperlinkLabel
import xmit
import plugin
import myNotebook as nb

DEFAULT_REFRESH_SECONDS = 180
MIN_REFRESH_SECONDS = 5
CFG_NEWS_REFRESH_SECONDS = 'NewsRefreshSeconds'
DEFAULT_NEWS_URL = 'http://helper.forthemug.com/dailyupdate/index.php'
WRAP_LENGTH = 200
commander = ""

class NewsPlugin(plugin.HuttonHelperPlugin):
    "Stores news display preferences."

    def __init__(self, helper):
        plugin.HuttonHelperPlugin.__init__(self, helper)
        self.refresh_seconds_var = None
        self.widget = None

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Return the news refresh interval preference."
        prefs_frame = nb.Frame(parent)
        nb.Label(prefs_frame, text="News Options :-").grid(row=0, column=0, columnspan=3, sticky=tk.W)
        nb.Label(prefs_frame, text="Check for news every").grid(row=1, column=0, sticky=tk.W)
        self.refresh_seconds_var = tk.StringVar(
            value=str(self._get_refresh_seconds())
        )
        # myNotebook does not expose Entry consistently across EDMC versions.
        tk.Entry(prefs_frame, textvariable=self.refresh_seconds_var, width=8).grid(
            row=1, column=1, sticky=tk.W
        )
        nb.Label(prefs_frame, text="seconds (minimum 5)").grid(row=1, column=2, sticky=tk.W)
        return prefs_frame

    def prefs_changed(self, cmdr, is_beta):
        "Save the refresh interval and apply it to the live widget."
        if self.refresh_seconds_var is None:
            return
        try:
            seconds = int(self.refresh_seconds_var.get())
        except (TypeError, ValueError):
            seconds = DEFAULT_REFRESH_SECONDS
        seconds = max(MIN_REFRESH_SECONDS, seconds)
        self.refresh_seconds_var.set(str(seconds))
        self.helper.prefs[CFG_NEWS_REFRESH_SECONDS] = seconds
        if self.widget is not None:
            self.widget.reschedule()

    def _get_refresh_seconds(self):
        "Return the configured refresh interval, enforcing the minimum."
        try:
            seconds = int(self.helper.prefs.setdefault(
                CFG_NEWS_REFRESH_SECONDS, DEFAULT_REFRESH_SECONDS
            ))
        except (TypeError, ValueError):
            seconds = DEFAULT_REFRESH_SECONDS
        return max(MIN_REFRESH_SECONDS, seconds)


class HuttonNews(SelfWrappingHyperlinkLabel):
    "A label to display the headline and link to the news."

    def __init__(self, parent, news_plugin):
        "Initialise the ``HuttonNews``."

        SelfWrappingHyperlinkLabel.__init__(
            self,
            parent,
            text="Fetching...",
            url=DEFAULT_NEWS_URL,
            wraplength=50,  # updated in __configure_event below
            anchor=tk.NW
        )
        self.news_plugin = news_plugin
        self.refresh_after_id = None
        news_plugin.widget = self
        self._schedule_refresh(250)

    def _schedule_refresh(self, delay_ms):
        "Schedule the next news update, replacing any pending timer."
        if self.refresh_after_id is not None:
            try:
                self.after_cancel(self.refresh_after_id)
            except tk.TclError:
                pass
        self.refresh_after_id = self.after(delay_ms, self.news_update)

    def reschedule(self):
        "Apply the latest configured interval to the pending refresh."
        self._schedule_refresh(self.news_plugin._get_refresh_seconds() * 1000)

    def pause(self):
        "Stop news requests while the news section is hidden."
        if self.refresh_after_id is not None:
            try:
                self.after_cancel(self.refresh_after_id)
            except tk.TclError:
                pass
            self.refresh_after_id = None

    def resume(self):
        "Restart news requests when the news section is shown."
        if self.refresh_after_id is None:
            self._schedule_refresh(250)

    def news_update(self):
        "Update the news."

        self.refresh_after_id = None
        try:
            if commander: # if we have commander name ask for specific news
                news_data = xmit.get('/news.json/{}'.format(commander))
                if news_data:
                    self['url'] = news_data['link']
                    self['text'] = news_data['headline']

                else:
                    self['text'] = "News refresh failed"

            else: # Get normal news
                news_data = xmit.get('/news.json/{}')
                if news_data:
                    self['url'] = news_data['link']
                    self['text'] = news_data['headline']

                else:
                    self['text'] = "News refresh failed"
        finally:
            # Wait the full configured interval after each request completes so a
            # slow response cannot cause back-to-back requests.
            self._schedule_refresh(self.news_plugin._get_refresh_seconds() * 1000)
