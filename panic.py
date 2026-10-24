"""
Module to suppress the DON'T PANIC message for commanders who like it tidy.
"""

try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for python 3
    import tkinter as tk

import myNotebook as nb  # EDMC

import plugin  # Hutton


CFG_PANIC = 'SuppressBigFriendlyLetters'
CFG_PANIC_POPUP = 'EnablePanicPopup'


class PanicPlugin(plugin.HuttonHelperPlugin):
    "Prevents the DON'T PANIC message when nothing else is ready and visible."

    def __init__(self, helper):
        "Initialise the ``PanicPlugin``."

        plugin.HuttonHelperPlugin.__init__(self, helper)
        self.popup_enabled_intvar = None

    def plugin_app(self, parent):
        "Called once to get the plugin widget. Return a ``tk.Frame``."

        self.__initialise_preferences()
        self.__update_hidden()

        return tk.Frame(parent)  # EMPTY

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Called each time the user opens EDMC settings. Return an ``nb.Frame``."

        self.__initialise_preferences()
        prefs_frame = nb.Frame(parent)
        prefs_frame.columnconfigure(0, weight=1)

        nb.Label(prefs_frame, text="Big Friendly Letters Control :-").grid(row=0, column=0, sticky=tk.W)
        nb.Checkbutton(prefs_frame, text="PANIC", variable=self.enabled_intvar).grid(row=1, column=0, sticky=tk.W)
        nb.Checkbutton(
            prefs_frame,
            text="Enable a popup when DON'T PANIC! is clicked",
            variable=self.popup_enabled_intvar,
        ).grid(row=2, column=0, sticky=tk.W)

        self.prefs_changed(cmdr, is_beta)
        return prefs_frame

    def prefs_changed(self, cmdr, is_beta):
        "Called when the user clicks OK on the settings dialog."

        self.helper.prefs[CFG_PANIC] = bool(self.enabled_intvar.get())
        self.helper.prefs[CFG_PANIC_POPUP] = bool(self.popup_enabled_intvar.get())
        self.__update_hidden()

    def __initialise_preferences(self):
        "Create our controls using the saved preferences." 

        if self.popup_enabled_intvar is not None:
            return

        enabled = self.helper.prefs.setdefault(CFG_PANIC, False)
        popup_enabled = self.helper.prefs.setdefault(CFG_PANIC_POPUP, False)
        self.enabled_intvar = tk.IntVar(value=1 if enabled else 0)
        self.popup_enabled_intvar = tk.IntVar(value=1 if popup_enabled else 0)

    def popup_enabled(self):
        "Whether clicking the front cover should open its popup." 

        return bool(self.popup_enabled_intvar and self.popup_enabled_intvar.get())

    def __update_hidden(self):
        "Update our ``hidden`` flag."

        self.hidden = not self.enabled_intvar.get()
