# Copyright 2012-2020 CERN for the benefit of the ATLAS collaboration.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Vincent Garonne <vincent.garonne@cern.ch>, 2012-2014
# - Mario Lassnig <mario.lassnig@cern.ch>, 2013-2017
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2020

import unittest

from rucio.client.didclient import DIDClient
from rucio.client.metaclient import MetaClient
from rucio.client.rseclient import RSEClient
from rucio.client.scopeclient import ScopeClient
from rucio.common.utils import generate_uuid as uuid


class TestMetaDIDClient(unittest.TestCase):
    """
    Test the metadata DID client
    """

    def setUp(self):
        """ Setup the Test Case """
        self.did_client = DIDClient()
        self.meta_client = MetaClient()
        self.rse_client = RSEClient()
        self.scope_client = ScopeClient()

    def test_add_list_meta(self):
        """ META DID (CLIENTS):  Add metadata to a data identifier"""
        # Add a scope
        tmp_scope = 'mock'

        # Add a dataset
        tmp_dataset = 'dsn_%s' % uuid()

        self.did_client.add_dataset(scope=tmp_scope, name=tmp_dataset)

        # Add a key
        key = 'project'
        value = 'data13_hip'
        self.did_client.set_metadata(scope=tmp_scope, name=tmp_dataset, key=key, value=value)

        meta = self.did_client.get_metadata(scope=tmp_scope, name=tmp_dataset)
        assert key in meta
        assert meta[key] == value
