import collections
from .client import Client
from .lock import Lock
from .election import LeaderElection
from base import *  # NOQA

# Attempt to enable urllib3's SNI support, if possible
# Blatantly copied from requests.
try:
    from urllib3.contrib import pyopenssl
    pyopenssl.inject_into_urllib3()
except ImportError:
    pass
