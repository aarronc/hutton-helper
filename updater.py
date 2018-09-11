"""
Update mechanism.
"""

from __init__ import __version__ as HH_VERSION

import collections
import ConfigParser
import hashlib
import json
import os
import StringIO
import sys
import Tkinter as tk
import urlparse
import zipfile

import xmit
import pack
import plugin

import myNotebook as nb
from ttkHyperlinkLabel import HyperlinkLabel

HH_PLUGIN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
HH_CONFIG_FILE = os.path.join(HH_PLUGIN_DIRECTORY, 'hutton.ini')
HH_VERSION_URL = 'http://hot.forthemug.com/live_plugin_version.json'

if os.path.exists(HH_CONFIG_FILE):
    HH_CONFIG = ConfigParser.SafeConfigParser()
    HH_CONFIG.read(HH_CONFIG_FILE)
    if HH_CONFIG.has_option('updates', 'version_url'):
        HH_VERSION_URL = HH_CONFIG.get('updates', 'version_url')

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

    version = info['version'].encode('ascii')
    location = info['location'].encode('ascii')
    digest = info['digest'].encode('ascii')

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

    def __init__(self, config):
        "Initialise the ``UpdatePlugin``."

        plugin.HuttonHelperPlugin.__init__(self, config)

        self.remote_version = None
        self.zipfile_url = None
        self.digest = None
        self.updated = False

    def plugin_start(self):
        "Called once at startup. Try to keep it short..."

        self.__fetch_version_info()

    def __fetch_version_info(self):
        "Fetch the remote info."

        info = get_version_info()
        if info is not None:
            self.remote_version, self.zipfile_url, self.digest = info

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

        if self.updated:
            nb.Label(frame, text=str(self)).grid(row=1, sticky=tk.W) # str(self) == self.__str__()

        elif self.remote_version is None:
            nb.Label(frame, text="Check for upgrade failed.", fg='dark red').grid(row=1, sticky=tk.W)
            button = nb.Button(frame, text="Check Again", command=lambda: self.__again_callback(frame, button))
            button.grid(row=2, sticky=tk.W)

        elif self.remote_version > HH_VERSION:
            nb.Label(frame, text=str(self), fg='dark green').grid(row=1, sticky=tk.W)
            button = nb.Button(frame, text="UPGRADE", command=lambda: self.__upgrade_callback(frame, button))
            button.grid(row=2, sticky=tk.W)

        else:
            nb.Label(frame, text="You're up to date. Fly safe!").grid(row=1, sticky=tk.W)

        return frame

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
        button['text'] = 'Upgrading...'
        frame.after_idle(lambda: self.__upgrade_action(frame))

    def __upgrade_action(self, frame):
        "Check again."

        try:
            update(self.zipfile_url, self.digest)
            self.updated = True

        finally:
            self.__populate_plugin_prefs_frame(frame)

    def __str__(self):
        "Represent the ``UpdatePlugin`` as a string."

        if self.updated:
            return "UPDATED. Please restart EDMC."

        elif self.remote_version and self.remote_version > HH_VERSION:
            return "New version {} available!".format(self.remote_version)

        else:
            return "Hutton Helper version {}".format(HH_VERSION)
