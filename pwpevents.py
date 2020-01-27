"""
Module to provide pwp events info to the player.
"""
try:
    # for python 2
    import Tkinter as tk
    import ttk
except ImportError:
    # for python 3
    import tkinter as tk
    import tkinter.ttk as ttk

from ttkHyperlinkLabel import HyperlinkLabel

import json
import sys
import zlib

import plugin
import xmit

import myNotebook as nb


CFG_SHOW_PWPEVENTS = 'ShowPwpEvents'
MAX_FAILS = 2


class PwpEventsPlugin(plugin.HuttonHelperPlugin):
    "Tracks exploration data gathering."

    def __init__(self, helper):
        "Initialise the ``ExplorationPlugin``."

        plugin.HuttonHelperPlugin.__init__(self, helper)
        self.frame = None
        self.cmdr = None
        self.pwpnews = None
        self.hyperlink = None
        self.checking = False
        self.distance = None
        self.fails = 0

    def __reset(self, cmdr=None):
        "Reset the ``ExplorationPlugin``."

        if cmdr != self.cmdr:
            self.pwpnews = None
            self.cmdr = cmdr
            return True

        return False

    @property
    def ready(self):
        "Are we ready?"

        return self.pwpnews is not None

    def plugin_app(self, parent):
        "Called once to get the plugin widget. Return a ``tk.Frame``."

        # An additional internal frame that we can grid_forget if disabled:
        frame = self.frame = tk.Frame(parent)
        frame.columnconfigure(1, weight=1)

        self.textvariable = tk.StringVar()
        self.textvariable.set("(Waiting...)")
        ttk.Label(frame, text="HOT-MESS Nearest System:",name='desc', anchor=tk.NW).grid(row=0, column=0, sticky=tk.NW)
        #self.hyperlinkobj = ttk.Label(frame, textvariable=self.textvariable, anchor=tk.NE).grid(row=0, column=1, sticky=tk.NE)
        HyperlinkLabel(frame, textvariable=self.textvariable, url='https://hot.forthemug.com/hot-mess/', name='pwplink', anchor=tk.NE).grid(row=0, column=1, sticky=tk.NE)

        enabled = self.helper.prefs.setdefault(CFG_SHOW_PWPEVENTS, False)
        self.enabled_intvar = tk.IntVar(value=1 if enabled else 0)
        self.__update_hidden()

        return self.frame

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Called each time the user opens EDMC settings. Return an ``nb.Frame``."

        prefs_frame = nb.Frame(parent)
        prefs_frame.columnconfigure(0, weight=1)

        nb.Label(prefs_frame, text="PWP Event Info :-").grid(row=0, column=0, sticky=tk.W)
        nb.Checkbutton(
            prefs_frame,
            text="Show Commander relevent PWP Event info",
            variable=self.enabled_intvar
        ).grid(row=1, column=0, sticky=tk.W)

        self.prefs_changed(cmdr, is_beta)
        return prefs_frame

    def prefs_changed(self, cmdr, is_beta):
        "Called when the user clicks OK on the settings dialog."

        self.helper.prefs[CFG_SHOW_PWPEVENTS] = bool(self.enabled_intvar.get())
        self.__update_hidden()

    def __update_hidden(self):
        "Update our ``hidden`` flag."

        self.hidden = not self.enabled_intvar.get()

    def journal_entry(self, cmdr, _is_beta, _system, _station, entry, _state):
        "Act like a tiny EDMC plugin."

        if entry['event'] == 'FSDJump':
            self.__check_again()

        if self.__reset(cmdr=cmdr) or not self.ready:
            self.__check_again()

    def cmdr_data(self, data, is_beta):
        "Act like a tiny EDMC plugin."

        if self.__reset(cmdr=data.get('commander').get('name')):
            self.__check_again()

    def __check_again(self):
        "Called when we need to check again."

        if self.frame:
            self.frame.after_idle(self.__check_again_action)
        else:
            self.__check_again_action()

    def __check_again_action(self):
        "Get and display exploration credits."

        if self.checking:
            return

        if self.fails > MAX_FAILS:
            self.__fail_safe()  # again in case self.textvariable was None last time
            return

        try:
            self.checking = True
            path = 'http://hot.forthemug.com:4570/closest_mug_system.json/{}'.format(self.cmdr)
            json_data = xmit.get(path)

            self.pwpnews = str(json_data['hhtext'])
            self.distance = float(json_data['distance'])
            self.hyperlink = str(json_data['hhlink'])

            if self.textvariable and self.hyperlink:
                self.textvariable.set(self.pwpnews + " ({:,.2f}lys)".format(self.distance))

                for w in self.frame.winfo_children():
                    if "pwplink" in str(w):
                        w['url'] = self.hyperlink

            self.fails = 0
            self.refresh()

        except:
            self.fails = self.fails + 1
            print('FAIL', self.fails)
            if self.fails > MAX_FAILS:
               self.__fail_safe()

        finally:
            self.checking = False

    def __fail_safe(self):
        "Fail."

        self.credits = 'DISABLED'
        if self.textvariable:
            self.textvariable.set("Disabled (#62)")
        self.refresh()
