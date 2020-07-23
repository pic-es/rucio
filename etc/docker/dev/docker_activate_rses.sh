#!/bin/bash
# Copyright 2019 CERN for the benefit of the ATLAS collaboration.
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
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019

# First, create the RSEs
rucio-admin rse add XRD1-DET
rucio-admin rse add --non-deterministic XRD2-NON-DET
rucio-admin rse add XRD3-NON-AUTH
rucio-admin rse add --non-deterministic PIC-INJECT2

# Add the protocol definitions for the storage servers
rucio-admin rse add-protocol --hostname xrd1 --scheme root --prefix //rucio --port 1094 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' XRD1-DET

rucio-admin rse add-protocol --hostname xrd2 --scheme root --prefix //rucio --port 1095 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' XRD2-NON-DET

rucio-admin rse add-protocol --hostname xrd3 --scheme root --prefix //rucio --port 1099 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' XRD3-NON-AUTH

rucio-admin rse add-protocol --hostname xrd3 --scheme root --prefix //rucio --port 1099 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' XRD3-NON-AUTH

rucio-admin rse add-protocol --hostname dcdoor01-dev.pic.es --scheme root --prefix //rucio --port 1094 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' PIC-INJECT2


# Enable FTS
rucio-admin rse set-attribute --rse XRD1-DET --key fts --value https://fts:8446
rucio-admin rse set-attribute --rse XRD2-NON-DET --key fts --value https://fts:8446
rucio-admin rse set-attribute --rse XRD3-NON-AUTH --key fts --value https://fts:8446
rucio-admin rse set-attribute --rse PIC-INJECT2 --key fts --value https://fts:8446

# Fake a full mesh network
rucio-admin rse add-distance --distance 1 --ranking 1 XRD1-DET XRD2-NON-DET
rucio-admin rse add-distance --distance 1 --ranking 1 XRD2-NON-DET XRD1-DET
rucio-admin rse add-distance --distance 1 --ranking 1 XRD1-DET XRD3-NON-AUTH
rucio-admin rse add-distance --distance 1 --ranking 1 XRD2-NON-DET XRD3-NON-AUTH
rucio-admin rse add-distance --distance 1 --ranking 1 PIC-INJECT2 XRD1-DET
rucio-admin rse add-distance --distance 1 --ranking 1 PIC-INJECT2 XRD2-NON-DET
rucio-admin rse add-distance --distance 1 --ranking 1 PIC-INJECT2 XRD3-NON-AUTH
rucio-admin rse add-distance --distance 1 --ranking 1 XRD3-NON-AUTH PIC-INJECT2
rucio-admin rse add-distance --distance 1 --ranking 1 XRD2-NON-DET PIC-INJECT2
rucio-admin rse add-distance --distance 1 --ranking 1 XRD1-DET PIC-INJECT2

# Indefinite limits for root
rucio-admin account set-limits root XRD1-DET -1
rucio-admin account set-limits root XRD2-NON-DET -1
rucio-admin account set-limits root XRD3-NON-AUTH -1
rucio-admin account set-limits root PIC-INJECT2 -1

# Create a default scope for testing
rucio-admin scope add --account root --scope test

# Delegate credentials to FTS
fts-rest-delegate -vf -s https://fts:8446 -H 9999

# Create initial transfer testing data
dd if=/dev/urandom of=file1 bs=10M count=1
dd if=/dev/urandom of=file2 bs=10M count=1
dd if=/dev/urandom of=file3 bs=10M count=1

rucio -v upload --rse XRD1-DET --scope test file1
rucio -v upload --rse XRD2-NON-DET --pfn root://xrd2:1095//rucio/test/file2 --scope test file2 
rucio -v upload --rse PIC-INJECT2 --pfn root://dcdoor01-dev.pic.es:1094/ --scope test file3
