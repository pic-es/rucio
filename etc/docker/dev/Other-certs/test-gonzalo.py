# Immport libraries 

from __future__ import absolute_import, division, print_function

import sys,os,os.path,json,io,math,re,datetime,time

# Set Rucio virtual environment configuration 

os.environ['RUCIO_HOME']=os.path.expanduser('~/Rucio-v2/rucio')

# Import Rucio libraries

from rucio.client.client import Client

from pprint import pprint

from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
import rucio.rse.rsemanager as rsemgr
from rucio.client import RuleClient

from rucio.common.exception import (AccountNotFound, Duplicate, RucioException, DuplicateRule, InvalidObject, DataIdentifierAlreadyExists, FileAlreadyExists, RucioException,
                                    AccessDenied)


#from rucio.common.utils import adler32, generate_uuid, md5
from rucio.common.utils import adler32, detect_client_location, execute, generate_uuid, md5, send_trace, GLOBALLY_SUPPORTED_CHECKSUMS

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#import hashlib
import uuid 

from itertools import islice
from subprocess import PIPE, Popen
import requests
from requests.exceptions import ReadTimeout

from rucio.common.utils import generate_http_error_flask, render_json, APIEncoder

try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3
import linecache

# Rucio settings 
rulesClient = RuleClient()

account='gonzalo'
auth_type='x509_proxy'

# account=account, auth_type=auth_type
CLIENT = Client(account=account)
didc = DIDClient(account=account)
repc = ReplicaClient(account=account)
rulesClient = RuleClient(account=account)
client = Client(account=account)
print(client.whoami())
print(client.ping())
