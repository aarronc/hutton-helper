"""
Looks after our data.
"""

import os, sys

from config import config  # EDMC

import xmit

# For compatibility with pre-5.0.0
if not hasattr(config, 'get_str'):
    config.get_str = config.get

HH_PLUGIN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def get_data_path(*args):
    "Get the path to our data directory, or to a subdirectory or filename in it."

    data_path = os.path.join(HH_PLUGIN_DIRECTORY, 'data')

    if os.path.exists(data_path):
        assert os.path.isdir(data_path)
    else:
        os.mkdir(data_path, 755)

    return os.path.join(data_path, *args)


def get_journal_path(*args):
    "Get the path to the journal directory, or to a subdirectory or filename in it."

    logdir = config.get_str('journaldir') or config.default_journal_dir
    return os.path.join(logdir, *args)
