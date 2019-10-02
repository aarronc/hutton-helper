"""
Code to pack updates into ZIP files.
"""

from version import HH_VERSION

import hashlib
import json
import os
from io import StringIO
import sys
import zipfile

HH_PLUGIN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
HH_CONFIG_FILE = os.path.join(HH_PLUGIN_DIRECTORY, 'hutton.ini')

INCLUDE_EXTENSIONS = set([
    '.py'
])


def build_distro_string(here=HH_PLUGIN_DIRECTORY):
    "Build the distribution in memory."

    f = StringIO.StringIO()

    with zipfile.ZipFile(f, 'w') as z:
        m = hashlib.sha256()

        for filename in sorted(os.listdir(here)):
            if os.path.splitext(filename)[1] not in INCLUDE_EXTENSIONS:
                continue

            sys.stderr.write('Adding {}...\r\n'.format(filename))
            with open(os.path.join(here, filename), 'rb') as thefile:
                content = thefile.read()
                m.update(content)
                z.writestr(filename, content)

        digest = m.hexdigest()
        z.comment = json.dumps({
            'version': HH_VERSION,
            'digest': 'bone',
        })

    return f.getvalue(), digest


def read_distro_string(s, digest=None):
    """
    Read and check the distribution.
    Returns the ZipFile object.
    DOES NOT CLOSE IT.
    """

    assert isinstance(s, str)
    f = StringIO.StringIO(s)

    z = zipfile.ZipFile(f, 'r')
    m = hashlib.sha256()

    for filename in sorted(z.namelist()):
        with z.open(filename, 'r') as f2:
            m.update(f2.read())

    if digest:
        assert digest == m.hexdigest(), 'digest mismatch'

    return z


def main():
    "Treat this module as a command line tool."

    s, digest = build_distro_string()
    z = read_distro_string(s, digest)
    zip_filename = 'HuttonHelper-{}-{}.zip'.format(HH_VERSION, digest[:8])

    sys.stderr.write('Writing {}...\r\n'.format(zip_filename))
    with open(zip_filename, 'wb') as f:
        f.write(s)

    version_filename = 'version.json'
    sys.stderr.write('Writing {}...\r\n'.format(version_filename))
    with open(version_filename, 'w') as f:
        f.write(json.dumps({
            'version': HH_VERSION,
            'location': zip_filename,
            'digest': digest,
        }))


if __name__ == '__main__':
    main()
