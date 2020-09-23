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
rucio-admin rse add PIC-DET
rucio-admin rse add --non-deterministic PIC-NON-DET
#rucio-admin rse add PIC-NON-DET

# Add the protocol definitions for the storage servers

# https://dcdoor01-dev.pic.es:8452/
#rucio-admin rse set-attribute --rse PIC-NON-DET --key type --value HTTPS
#rucio-admin rse add-protocol --hostname dcdoor01-dev.pic.es --scheme https --prefix //rucio --port 8452 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' PIC-NON-DET

# https://dcdoor01-dev.pic.es:1094/
#rucio-admin rse set-attribute --rse PIC-NON-DET --key lfn2pfn_algorithm --value identity

#rucio-admin rse add-protocol --hostname dcdoor01-dev.pic.es --scheme root --prefix //pnfs/pic.es/data/escape2 --port 1094 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' PIC-NON-DET
rucio-admin rse add-protocol --hostname dcdoor01-dev.pic.es --scheme https --prefix //escape2 --port 8453 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' PIC-NON-DET


# root://dcdoor01-dev.pic.es:1094/
#rucio-admin rse set-attribute --rse PIC-DET --key lfn2pfn_algorithm --value hash

# rucio-admin rse add-protocol --hostname dcdoor01-dev.pic.es --scheme root --prefix //pnfs/pic.es/data/escape/rucio --port 1094 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' PIC-DET
rucio-admin rse add-protocol --hostname dcdoor01-dev.pic.es --scheme https --prefix //rucio --port 8452 --impl rucio.rse.protocols.gfal.Default --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' PIC-DET

rucio-admin rse delete-attribute --rse PIC-DET --key fts --value https://fts01.pic.es:8446
rucio-admin rse delete-attribute --rse PIC-NON-DET --key fts --value https://fts01.pic.es:8446
rucio-admin rse delete-attribute --rse PIC-DET --key fts_testing --value https://fts01.pic.es:8446
rucio-admin rse delete-attribute --rse PIC-NON-DET --key fts_testing --value https://fts01.pic.es:8446

# Enable FTS
rucio-admin rse set-attribute --rse PIC-DET --key fts --value https://fts01.pic.es:8446 
rucio-admin rse set-attribute --rse PIC-NON-DET --key fts --value https://fts01.pic.es:8446 
rucio-admin rse set-attribute --rse PIC-DET --key fts_testing --value https://fts01.pic.es:8446
rucio-admin rse set-attribute --rse PIC-NON-DET --key fts_testing --value https://fts01.pic.es:8446

# Fake a full mesh network
rucio-admin rse add-distance --distance 1 --ranking 1 PIC-DET PIC-NON-DET
rucio-admin rse add-distance --distance 1 --ranking 1 PIC-NON-DET PIC-DET

# Indefinite limits for root
rucio-admin account set-limits root PIC-DET -1
rucio-admin account set-limits root PIC-NON-DET -1
rucio-admin account set-limits abruzzese PIC-DET -1
rucio-admin account set-limits abruzzese PIC-NON-DET -1

# Create a default scope for testing
rucio-admin scope add --account root --scope test-root
rucio-admin scope add --account abruzzese --scope test-abruzzese

# Delegate credentials to FTS
#fts-rest-delegate -vf -s https://fts:8446 -H 9999
fts-rest-delegate -vf -s https://fts01.pic.es:8446 -H 9999
 
# Create initial transfer testing data
dd if=/dev/urandom of=file11 bs=10M count=1
dd if=/dev/urandom of=file21 bs=10M count=1

rucio upload --rse PIC-DET --scope test-root file11
# rucio upload --rse PIC-NON-DET --scope test-root file2
# rucio -v upload --rse PIC-NON-DET --pfn root://dcdoor01-dev.pic.es:1094//pnfs/pic.es/data/escape/rucio/test-root/file21 --scope test-root file21 
# rucio -v upload --rse PIC-NON-DET --pfn https://dcdoor01-dev.pic.es:8452//rucio/test-root/file21 --scope test-root file21 
# rucio -v upload --rse PIC-NON-DET --pfn root://dcdoor01-dev.pic.es:1094//pnfs/pic.es/data/escape2/test-root/file21 --scope test-root file21
rucio -v upload --rse PIC-NON-DET --pfn https://dcdoor01-dev.pic.es:8453//escape2/test-root/file21 --scope test-root file21

rucio-admin rse set-attribute --key greedyDeletion --value True --rse PIC-NON-DET
rucio-admin rse set-attribute --key greedyDeletion --value True --rse PIC-DET
