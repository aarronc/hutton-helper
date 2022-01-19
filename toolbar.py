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

import xmit

RADIO_URL = "https://radio.forthemug.com/"
STATS_URL = "https://hot.forthemug.com/stats"
BASE_URL = "https://hot.forthemug.com/"
INF_URL = "https://hot.forthemug.com/factions/349"


def open_trucker_browser(url):
    "Open the trucker's browser."
    webbrowser.open_new(url)


class HuttonToolbar(tk.Frame):
    "The main toolbar. Not a plugin because it doesn't have preferences or watch the pilot."

    def __init__(self, parent):
        "Initialise the ``Toolbar``."

        tk.Frame.__init__(self, parent)

        BUTTONS = [
            ("Website", lambda: open_trucker_browser(BASE_URL)),
            ("Influence", lambda: open_trucker_browser(INF_URL)),
            ("Stats", lambda: open_trucker_browser(STATS_URL)),
            ("Radio", lambda: open_trucker_browser(RADIO_URL))
        ]

        for column, (text, command) in enumerate(BUTTONS):
            self.columnconfigure(column, weight=1)
            tk.Button(self, text=text, command=command).grid(row=0, column=column, padx=5)

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
