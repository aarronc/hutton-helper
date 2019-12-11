"""
Update mechanism.
"""

from version import HH_VERSION

try:
    # for Python2
    import Tkinter as tk
    import urlparse
    import ConfigParser
    import StringIO
except ImportError:
    # for python 3
    import tkinter as tk
    import urllib.parse as urlparse
    import configparser
    from io import StringIO
import collections
import hashlib
import json
import os
import sys
import zipfile

import xmit
import pack
import plugin

import myNotebook as nb
from ttkHyperlinkLabel import HyperlinkLabel

HH_TEXT_UPDATE_AVAILABLE = "UPDATE AVAILABLE to version {remote_version}"
HH_TEXT_UPDATED = "UPDATED. Please restart EDMC."
HH_TEXT_VERSION_CHECK_FAILED = "Check for upgrade failed."
HH_VERSION_URL = 'http://hot.forthemug.com/live_plugin_version.json'

HH_PLUGIN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
HH_CONFIG_FILE = os.path.join(HH_PLUGIN_DIRECTORY, 'hutton.ini')

if os.path.exists(HH_CONFIG_FILE):
    HH_CONFIG = configparser.SafeConfigParser()
    HH_CONFIG.read(HH_CONFIG_FILE)
    if HH_CONFIG.has_option('updates', 'version_url'):
        HH_VERSION_URL = HH_CONFIG.get('updates', 'version_url')

CFG_AUTO_UPDATE = 'AutoUpdate'

INCLUDE_EXTENSIONS = set([
    '.py'
])


class Version(collections.namedtuple('Version', ['major', 'minor', 'patch'])):
    "A semantic version."

    def __new__(cls, *args):
        "Create a new ``Version`` from a version string or three integers."

        if len(args) == 1:
            args = [int(arg) for arg in args[0].strip().split('.')]

        assert len(args) == 3
        for arg in args:
            assert isinstance(arg, int)

        return super(Version, cls).__new__(cls, *args)

    def __gt__(self, other):
        "Compare one ``Version`` to another."

        if isinstance(other, str):
            return self > Version(other)
        assert isinstance(other, Version)

        if self.major > other.major:
            return True

        if self.major == other.major:
            if self.minor > other.minor:
                return True

            if self.minor == other.minor:
                if self.patch > other.patch:
                    return True

        return False

    def __str__(self):
        "Represent the ``Version`` as a string."
        return '{}.{}.{}'.format(*self)


def get_version_info():
    "Get the information on the latest version."

    info = xmit.get(HH_VERSION_URL)
    if info is None:
        return None

    version = info['version']
    location = info['location']
    digest = info['digest']

    zipfile_url = urlparse.urljoin(HH_VERSION_URL, location)

    return Version(version), zipfile_url, digest


def delete_current_version(here=HH_PLUGIN_DIRECTORY):
    "SCARY."

    for filename in sorted(os.listdir(here)):
        if os.path.splitext(filename)[1] in INCLUDE_EXTENSIONS:
            sys.stderr.write("Deleting {}...\r\n".format(filename))
            os.remove(os.path.join(here, filename))


def unzip_new_version(z, here=HH_PLUGIN_DIRECTORY):
    "Slightly less scary."

    with z:
        for filename in sorted(z.namelist()):
            sys.stderr.write("Extracting {}...\r\n".format(filename))
            z.extract(filename, path=here)


def update(zipfile_url, digest):
    "Update using the ZIP file at ``zipfile_url`` if the ``digest`` checks out."

    s = xmit.get(zipfile_url, parse=False)
    z = pack.read_distro_string(s, digest)
    delete_current_version()
    unzip_new_version(z)


class UpdatePlugin(plugin.HuttonHelperPlugin):
    "An update plugin."

    def __init__(self, helper):
        "Initialise the ``UpdatePlugin``."

        plugin.HuttonHelperPlugin.__init__(self, helper)

        self.remote_version = None
        self.zipfile_url = None
        self.digest = None
        self.updated = False

    @property
    def cfg_auto(self):
        "Get our automatic upgrade preference (0 or 1)"

        return 1 if self.helper.prefs.setdefault(CFG_AUTO_UPDATE, True) else 0

    @cfg_auto.setter
    def cfg_auto(self, value):
        "Set our automatic upgrade preference (0 or 1)."

        self.helper.prefs[CFG_AUTO_UPDATE] = bool(value)

    def plugin_app(self, parent):
        "Called once to get the plugin widget. Return a ``tk.Frame``."

        self.helper.status("Version {} OK".format(HH_VERSION))
        parent.after(250, self.__fetch_version_info)

    def __fetch_version_info(self):
        "Fetch the remote info."

        info = get_version_info()
        if info is not None:
            self.remote_version, self.zipfile_url, self.digest = info
            if self.remote_version > HH_VERSION:
                text = HH_TEXT_UPDATE_AVAILABLE.format(remote_version=self.remote_version)
                if self.cfg_auto:
                    self.__upgrade_action()
                else:
                    self.helper.status(text)

    def plugin_prefs(self, parent, cmdr, is_beta):
        "Called to get a tk Frame for the settings dialog."

        frame = nb.Frame(parent)
        return self.__populate_plugin_prefs_frame(frame)

    def __populate_plugin_prefs_frame(self, frame):
        "Populate the frame for ``plugin_prefs``."

        for widget in frame.winfo_children(): # In case we're called again
            widget.destroy()

        frame.columnconfigure(0, weight=1)

        topline = nb.Frame(frame)
        topline.grid(row=0, sticky=tk.W)

        HyperlinkLabel(
            topline,
            text="Hutton Helper",
            background=nb.Label().cget('background'),
            url='https://hot.forthemug.com/',
            underline=True
        ).grid(row=0, column=0)
        nb.Label(topline, text="version {}".format(HH_VERSION)).grid(row=0, column=1)
        self.automatic_intvar = tk.IntVar(value=self.cfg_auto)
        nb.Checkbutton(frame, text="Update automatically", variable=self.automatic_intvar).grid(row=1, sticky=tk.W)

        if self.updated:
            nb.Label(frame, text=HH_TEXT_UPDATED).grid(row=2, sticky=tk.W) # str(self) == self.__str__()

        elif self.remote_version is None:
            nb.Label(frame, text=HH_TEXT_VERSION_CHECK_FAILED, fg='dark red').grid(row=2, sticky=tk.W)
            button = nb.Button(frame, text="Check Again", command=lambda: self.__again_callback(frame, button))
            button.grid(row=3, sticky=tk.W)

        elif self.remote_version > HH_VERSION:
            text = HH_TEXT_UPDATE_AVAILABLE.format(remote_version=self.remote_version)
            nb.Label(frame, text=text, fg='dark green').grid(row=2, sticky=tk.W)
            button = nb.Button(frame, text="UPDATE", command=lambda: self.__upgrade_callback(frame, button))
            button.grid(row=3, sticky=tk.W)

        else:
            nb.Label(frame, text="You're up to date. Fly safe!").grid(row=2, sticky=tk.W)

        return frame

    def prefs_changed(self, _cmdr, _is_beta):
        "Called when the user clicks OK on the settings dialog."

        self.cfg_auto = self.automatic_intvar.get()

    def __again_callback(self, frame, button):
        "Handle the user's request to check again."

        button['state'] = tk.DISABLED
        button['text'] = 'Checking...'
        frame.after_idle(lambda: self.__again_action(frame))

    def __again_action(self, frame):
        "Check again."

        try:
            self.__fetch_version_info()

        finally:
            self.__populate_plugin_prefs_frame(frame)

    def __upgrade_callback(self, frame, button):
        "Handle the user's upgrade request."

        button['state'] = tk.DISABLED
        button['text'] = 'Updating...'
        frame.after_idle(lambda: self.__upgrade_action(frame))

    def __upgrade_action(self, frame=None):
        "Check again."

        try:
            self.helper.status("Updating...")
            update(self.zipfile_url, self.digest)
            self.helper.status(HH_TEXT_UPDATED)
            self.updated = True

        finally:
            if frame:
                self.__populate_plugin_prefs_frame(frame)
