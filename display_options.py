"""Display preferences for the Hutton Helper panel."""

try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk

import myNotebook as nb
import plugin

CFG_LITE_MODE = 'LiteMode'
CFG_HIDE_NEWS = 'HideNews'


class DisplayOptionsPlugin(plugin.HuttonHelperPlugin):
    "Controls optional content in the main Helper panel."

    def __init__(self, helper):
        plugin.HuttonHelperPlugin.__init__(self, helper)
        self.lite_mode_var = None
        self.hide_news_var = None

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Return the Lite Mode and news visibility settings."
        prefs_frame = nb.Frame(parent)
        nb.Label(prefs_frame, text="Lite Mode :-").grid(row=0, column=0, sticky=tk.W)

        self.lite_mode_var = tk.IntVar(
            value=1 if self.helper.prefs.setdefault(CFG_LITE_MODE, False) else 0
        )
        nb.Checkbutton(
            prefs_frame,
            text="Enable Lite Mode (hide buttons, DON'T PANIC, and other panels)",
            variable=self.lite_mode_var,
        ).grid(row=1, column=0, sticky=tk.W)

        self.hide_news_var = tk.IntVar(
            value=1 if self.helper.prefs.setdefault(CFG_HIDE_NEWS, False) else 0
        )
        nb.Checkbutton(
            prefs_frame,
            text="Hide the news section",
            variable=self.hide_news_var,
        ).grid(row=2, column=0, sticky=tk.W)
        return prefs_frame

    def prefs_changed(self, cmdr, is_beta):
        "Save the display settings and refresh the panel."
        if self.lite_mode_var is None or self.hide_news_var is None:
            return
        self.helper.prefs[CFG_LITE_MODE] = bool(self.lite_mode_var.get())
        self.helper.prefs[CFG_HIDE_NEWS] = bool(self.hide_news_var.get())
        self.helper.refresh()

    def lite_mode_enabled(self):
        "Whether optional panels and controls should be hidden."
        return bool(self.helper.prefs.setdefault(CFG_LITE_MODE, False))

    def news_hidden(self):
        "Whether the news label and headline should be hidden."
        return bool(self.helper.prefs.setdefault(CFG_HIDE_NEWS, False))
