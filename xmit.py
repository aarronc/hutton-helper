"""
Transmit data to the back end.
"""

import sys

if sys.version_info[0] < 3:
    # for Python2
    is2 = True # used to check if is python2
else:
    # for python 3.1
    import logging
    is2 = False  # used to check if is python2

import os
import time
import traceback
import requests
try:
    # for Python2
    import urlparse
except ImportError:
    # for Python3
    import urllib.parse as urlparse

from config import applongname, appversion, appname

if is2 == False:
    plugin_name = os.path.basename(os.path.dirname(__file__))
    logger = logging.getLogger("{}.{}".format(appname,plugin_name))
    if not logger.hasHandlers():
        level = logging.INFO  # this level means we can have level info and above So logger.info(...) is equivalent to sys.stderr.write() but puts an INFO tag on it logger.error(...) is possible gives ERROR tag
        logger.setLevel(level)
        logger_channel = logging.StreamHandler()
        logger_channel.setLevel(level)
        logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
        logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
        logger_formatter.default_msec_format = '%s.%03d'
        logger_channel.setFormatter(logger_formatter)
        logger.addHandler(logger_channel)

XMIT_URL = 'https://helper.forthemug.com'
ACTIVE_XMIT_URL = XMIT_URL
DEFAULT_TIMEOUT = 7
COMPRESSED_OCTET_STREAM = {'content-type': 'application/octet-stream', 'content-encoding': 'zlib'}

FAILED = False


def normalize_base_url(base):
    "Validate and normalize the Hutton Helper API base URL."
    if not isinstance(base, str):
        raise ValueError('The server address must be a URL.')
    base = base.strip().rstrip('/')
    try:
        parsed = urlparse.urlsplit(base)
        hostname = parsed.hostname
        parsed.port  # Accessing this also validates the port, if one was supplied.
    except ValueError:
        raise ValueError('Enter a valid server URL.')
    if (
        parsed.scheme.lower() not in ('http', 'https')
        or not hostname
        or '@' in parsed.netloc
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError('Enter an http:// or https:// server URL without credentials, query, or fragment.')
    return base


def set_base_url(base):
    "Set the base URL used for relative API paths."
    global ACTIVE_XMIT_URL
    ACTIVE_XMIT_URL = normalize_base_url(base)
    return ACTIVE_XMIT_URL


def get_base_url():
    "Return the active API base URL."
    return ACTIVE_XMIT_URL


def request(path_or_url, base=None, method='get', parse=True, **kwargs):
    """
    GET or POST the JSON at ``path_or_url``.

    If ``path_or_url`` starts with ``/``, treat it as a path under ``base``.
    When ``base`` is omitted, use the configured Hutton Helper API base URL.
    Else, treat it as a full URL.

    Returns:

     * None on an exception or ``status_code`` not in [200, 204]
     * '' on 204
     * JSON-parsed text if 200 and ``parse``
     * Text if 200 and not ``parse``
    """

    assert isinstance(path_or_url, str)
    assert method in ['get', 'post']
    assert isinstance(parse, bool)

    global FAILED
    FAILED = False

    if base is None:
        base = ACTIVE_XMIT_URL
    assert isinstance(base, str)

    if path_or_url[:1] == '/':
        url = base + path_or_url
    else:
        url = path_or_url

    try:
        began = time.time()
        response = getattr(requests, method)(url, timeout=DEFAULT_TIMEOUT, **kwargs)
        delay = (time.time() - began) * 1000

        if response.status_code == 200:
            if parse:
                try:
                    return response.json()

                except ValueError:
                    FAILED = True
                    if is2:
                        sys.stderr.write('Unable to parse JSON: ')
                    else:
                        logger.error("Unable to parse JSON: ")
                    pass # fall through to stderr and None

            else:
                return response.content

        elif response.status_code == 204:
            return ''

        FAILED = True
        if is2:
            sys.stderr.write("{} {} {} ms={:.0f}\r\n".format(response.status_code, method.upper(), url, delay))
            sys.stderr.write("{}\r\n".format(repr(response.content)))
        else:
            logger.error("{} {} {} ms={:.0f}".format(response.status_code, method.upper(), url, delay))
            logger.error("{}".format(repr(response.content)))

        return None

    except Exception:
        FAILED = True
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if is2:
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
        else:
            logger.error("{}".format("\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback))))
        return None


def get(path, **kwargs):
    "Get the JSON at ``path``. See request_json for return details."
    return request(path, method='get', **kwargs)


def post(path, data, **kwargs):
    "Post ``data`` to ``path``. See request_json for return details."
    return request(path, method='post', data=data, **kwargs)
