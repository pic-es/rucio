from __future__ import absolute_import, division, print_function

import sys,os,os.path

# Set Rucio virtual environment configuration 

os.environ['RUCIO_HOME']=os.path.expanduser('~/Rucio-v2/rucio')

# Import Rucio libraries

from rucio.client.client import Client

from pprint import pprint

from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
import rucio.rse.rsemanager as rsemgr
from rucio.client import RuleClient
import uuid 
from rucio.client.uploadclient import UploadClient
from rucio.common.exception import (AccountNotFound, Duplicate, RucioException, DuplicateRule, InvalidObject, DataIdentifierAlreadyExists, FileAlreadyExists, RucioException,
                                    AccessDenied)


#from rucio.common.utils import adler32, generate_uuid, md5
from rucio.common.utils import adler32, detect_client_location, execute, generate_uuid, md5, send_trace, GLOBALLY_SUPPORTED_CHECKSUMS
import json
import math
import re
import time
import os
import sys
import numpy as np 
#import hashlib

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

account='mario'
auth_type='x509_proxy'

# account=account, auth_type=auth_type
CLIENT = Client(account=account)
didc = DIDClient(account=account)
repc = ReplicaClient(account=account)
rulesClient = RuleClient(account=account)
client = Client(account=account)
uploadClient=UploadClient()

print(client.whoami())
print(client.ping())

sys.path.append("/usr/lib64/python3.6/site-packages/")
import gfal2
from gfal2 import Gfal2Context, GError

gfal = Gfal2Context()

# Global variables definition : 

DEFAULT_ORIGIN_RSE = 'XRD1-DET'
DEFAULT_SCOPE = 'test-mario'

# Generate a random file : 

def generate_random_file(filename, size, copies = 1):
    """
    generate big binary file with the specified size in bytes
    :param filename: the filename
    :param size: the size in bytes
    :param copies: number of output files to generate
    
    """
    n_files = []
    n_files = np.array(n_files, dtype = np.float32)   
    for i in range(copies):
        file = filename + '-' + str(uuid.uuid4())
        if os.path.exists(file) : 
            print ("File %s already exist" %file)

        else:
            print ("File %s not exist" %file)    
            try : 
                newfile = open(file, "wb")
                newfile.seek(size)
                newfile.write(b"\0")
                newfile.close ()
                os.stat(file).st_size
                print('random file with size %f generated ok'%size)
                n_files = np.append(n_files, file)
            except :
                print('could not be generate file %s'%file)

    return(n_files)

list_files = generate_random_file('deletion', 10)     


if list_files :
    for n in range(0, len(list_files)) :
        client=Client()
        rulesClient=RuleClient()
        uploadClient=UploadClient()

        name_file = list_files[n]
    filePath="./"+name_file
    file = {'path': filePath, 'rse': DEFAULT_ORIGIN_RSE, 'did_scope': DEFAULT_SCOPE}

    # perform upload
    uploadClient.upload([file])

