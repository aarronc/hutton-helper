"""Settings for the Hutton Helper data server."""

try:
    # for Python2
    import Tkinter as tk
    import ttk
    import tkMessageBox
except ImportError:
    # for Python3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.messagebox as tkMessageBox

import myNotebook as nb
import plugin
import xmit

CFG_SERVER_URL = 'ServerUrl'
SERVER_URL_OPTIONS = (
    xmit.XMIT_URL,
    'http://localhost:4567',
)


class ServerOptionsPlugin(plugin.HuttonHelperPlugin):
    "Lets users choose the Hutton Helper API server."

    def __init__(self, helper):
        plugin.HuttonHelperPlugin.__init__(self, helper)
        self.server_url_var = None

    def plugin_start(self):
        "Load the saved server URL before other plugins make requests."
        saved_url = self.helper.prefs.setdefault(CFG_SERVER_URL, xmit.XMIT_URL)
        try:
            normalized_url = xmit.set_base_url(saved_url)
        except ValueError:
            normalized_url = xmit.set_base_url(xmit.XMIT_URL)
            self.helper.prefs[CFG_SERVER_URL] = normalized_url

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Return the server address setting."
        prefs_frame = nb.Frame(parent)
        nb.Label(prefs_frame, text="Server Options :-").grid(row=0, column=0, sticky=tk.W)
        nb.Label(prefs_frame, text="Hutton Helper data server URL:").grid(row=1, column=0, sticky=tk.W)
        self.server_url_var = tk.StringVar(value=xmit.get_base_url())
        ttk.Combobox(
            prefs_frame,
            textvariable=self.server_url_var,
            values=SERVER_URL_OPTIONS,
            width=45,
            state='normal',
        ).grid(
            row=1, column=1, sticky=tk.W
        )
        nb.Label(
            prefs_frame,
            text=(
                "Choose localhost or type a custom host/port (for example, "
                "http://localhost:8000). Canonn submissions and plugin updates "
                "are unaffected."
            ),
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W)
        return prefs_frame

    def prefs_changed(self, cmdr, is_beta):
        "Validate and save the selected server address."
        if self.server_url_var is None:
            return
        try:
            server_url = xmit.set_base_url(self.server_url_var.get())
        except ValueError as error:
            self.server_url_var.set(xmit.get_base_url())
            tkMessageBox.showerror(
                "Invalid server URL",
                str(error),
            )
            return
        self.server_url_var.set(server_url)
        self.helper.prefs[CFG_SERVER_URL] = server_url
