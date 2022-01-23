"""
Module to provide the main toolbar.
"""

try:
    # for Python2
    import Tkinter as tk
    import tkMessageBox
except ImportError:
    # for python 3
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox

import webbrowser
import os
import xmit

HOT_URL = "https://hot.forthemug.com/"
INF_URL = "https://hot.forthemug.com/factions/349"
STATS_URL = "https://hot.forthemug.com/stats"
RADIO_URL = "https://radio.forthemug.com/"
PATREON_URL = "https://www.patreon.com/entarius"

HOT_IMAGE = tk.PhotoImage(file=os.path.dirname(os.path.realpath(__file__))+"\images\icon_hot.gif")
INF_IMAGE = tk.PhotoImage(file=os.path.dirname(os.path.realpath(__file__))+"\images\icon_inf.gif")
STATS_IMAGE = tk.PhotoImage(file=os.path.dirname(os.path.realpath(__file__))+"\images\icon_stats.gif")
RADIO_IMAGE = tk.PhotoImage(file=os.path.dirname(os.path.realpath(__file__))+"\images\icon_radio.gif")
PATREON_IMAGE = tk.PhotoImage(file=os.path.dirname(os.path.realpath(__file__))+"\images\icon_patreon.gif")


def open_trucker_browser(url):
    "Open the trucker's browser."
    webbrowser.open_new(url)


class HuttonToolbar(tk.Frame):
    "The main toolbar. Not a plugin because it doesn't have preferences or watch the pilot."

    def __init__(self, parent):
        "Initialise the ``Toolbar``."
        tk.Frame.__init__(self, parent)
        
        BUTTONS = [
            (HOT_IMAGE, lambda: open_trucker_browser(HOT_URL)),
            (INF_IMAGE, lambda: open_trucker_browser(INF_URL)),
            (STATS_IMAGE, lambda: open_trucker_browser(STATS_URL)),
            (RADIO_IMAGE, lambda: open_trucker_browser(RADIO_URL)),
            (PATREON_IMAGE, lambda: open_trucker_browser(PATREON_URL))
        ]

        for column, (image, command) in enumerate(BUTTONS):
            self.columnconfigure(column, weight=1)
            tk.Button(self, image=image, height=35, width=35, command=command).grid(row=0, column=column, padx=0)

    def daily_info_call(self):
        "Get and display the daily update."
        daily_data = xmit.get('/msgbox_daily_update.json')
        if daily_data:
            tkMessageBox.showinfo("Hutton Daily update", "\n".join(daily_data))
        else:
            tkMessageBox.showinfo("Hutton Daily update", "Could not get Daily Update Data")

    def influence_data_call(self):
        "Get and display Hutton influence data."
        influence_data = xmit.get('/msgbox_influence.json')
        if influence_data:
            tkMessageBox.showinfo("Hutton Influence Data", "\n".join(influence_data))
        else:
            tkMessageBox.showinfo("Hutton Influence Data", "Could not get Influence Data")
