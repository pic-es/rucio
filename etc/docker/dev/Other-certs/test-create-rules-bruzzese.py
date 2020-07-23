#!/usr/bin/env python
# coding: utf-8

# In[1]:


from __future__ import absolute_import, division, print_function

__author__ = "Agustin Bruzzese"
__copyright__ = "Copyright (C) 2020 Agustin Bruzzese"

__revision__ = "$Id$"
__version__ = "0.2"

import sys
sys.path.append("/usr/lib64/python3.6/site-packages/")

import gfal2
import io
import json
import linecache
import logging
import numpy as np 
import os
import os.path
import random
import re
import time
import uuid
import zipfile
import string
import pathlib
import time 
import pytz
from urllib.parse import urlunsplit
import graphyte, socket
from dateutil import parser
from datetime import (
    datetime,
    tzinfo,
    timedelta,
    timezone,
)
from gfal2 import (
    Gfal2Context,
    GError,
)
from io import StringIO

# Set Rucio virtual environment configuration 
os.environ['RUCIO_HOME']=os.path.expanduser('~/Rucio-v2/rucio')
from rucio.rse import rsemanager as rsemgr
from rucio.client.client import Client
from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
import rucio.rse.rsemanager as rsemgr
from rucio.client import RuleClient

from rucio.common.exception import (AccountNotFound, Duplicate, RucioException, DuplicateRule, InvalidObject, DataIdentifierAlreadyExists, FileAlreadyExists, RucioException,
                                    AccessDenied, InsufficientAccountLimit, RuleNotFound, AccessDenied, InvalidRSEExpression,
                                    InvalidReplicationRule, RucioException, DataIdentifierNotFound, InsufficientTargetRSEs,
                                    ReplicationRuleCreationTemporaryFailed, InvalidRuleWeight, StagingAreaRuleRequiresLifetime)

from rucio.common.utils import adler32, detect_client_location, execute, generate_uuid, md5, send_trace, GLOBALLY_SUPPORTED_CHECKSUMS

gfal2.set_verbose(gfal2.verbose_level.debug)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Magic naming 
from lfn2pfn import *


# In[2]:


class Rucio :
    def __init__(self, myscope, orgRse, destRse, account='bruzzese', working_folder=None):
        
        self.myscope = myscope
        self.orgRse = orgRse 
        self.destRse = destRse
        self.working_folder = working_folder
        
        self.gfal = Gfal2Context()

        self.didc = DIDClient()
        self.repc = ReplicaClient()
        self.rulesClient = RuleClient()
        
        # Configuration
        self.account = account

        # account=account
        self.client = Client(account=self.account)
        
        # Get list of all RSEs 
    def rses(self) :
        rses_lists = list()
        for single_rse in list(self.client.list_rses()) :
            rses_lists.append(single_rse['rse'])
        return(rses_lists)
    
    def usage(self,s_rse) :
        return(list(self.client.get_local_account_usage(account=self.account,rse=s_rse))[0])
        
    def rules(self) :
        return(list(self.client.list_account_rules(account=self.account)))
    
    def myfunc(self):
        print("Hello your setting are account=%s, scope=%s, origin RSE =%s and destination RSE =%s" %(self.account, self.myscope, self.orgRse, self.destRse))

    def file_exists(self, pfn) :
        try :
            self.gfal.stat(pfn).st_size
            return(True)
        except : 
            return(False)
        
        
    def get_rse_url(self):
        """
        Return the base path of the rucio url
        """
        rse_settings = rsemgr.get_rse_info(self.orgRse)
        protocol = rse_settings['protocols'][0]
        
        schema = protocol['scheme']
        prefix = protocol['prefix']
        port = protocol['port']
        rucioserver = protocol['hostname']
        
        rse_url = list()
        if None not in (schema,str(rucioserver+':'+str(port)),prefix): 
            rse_url.extend([schema,rucioserver+':'+str(port),prefix,'',''])
            if self.working_folder != None :
                # Check if our test folder exists
                path = os.path.join(urlunsplit(rse_url), self.working_folder)
                self.gfal.mkdir_rec(path, 775)
                return(path)
            else :
                return(urlunsplit(rse_url))
        else :
            return('Wrong url parameters')    

    def check_replica(self, lfn, dest_rse=None):
        """
        Check if a replica of the given file at the site already exists.
        """
        if lfn : 
            replicas = list(
                self.client.list_replicas([{
                    'scope': self.myscope,
                    'name': lfn
                }], rse_expression=dest_rse))

            if replicas:
                for replica in replicas:
                    if isinstance(replica,dict) :
                        if dest_rse in replica['rses']:
                            path = replica['rses'][dest_rse][0]
                            return(path)
            return(False)
        
    ############################

    ## Create Metadata for DIDs

    ############################    
    def getFileMetaData(self, p_file, origenrse=None):
        """
        Get the size and checksum for every file in the run from defined path
        """ 
        '''
        generate the registration of the file in a RSE :
        :param rse: the RSE name.
        :param scope: The scope of the file.
        :param name: The name of the file.
        :param bytes: The size in bytes.
        :param adler32: adler32 checksum.
        :param pfn: PFN of the file for non deterministic RSE  
        :param dsn: is the dataset name.
        '''
        name = os.path.basename(p_file)
        name = name.replace('/','')

        replica = {
        'scope': self.myscope,
        'name': name.replace('+','_'),
        'adler32': self.gfal.checksum(p_file, 'adler32'),
        'bytes': self.gfal.stat(p_file).st_size,
        'pfn': p_file,
        "meta": {"guid": str(generate_uuid())}
        }

        Data = dict();
        Data['replica'] = replica
        Data['scope'] = self.myscope

        return(Data) 

    ############################

    ## Create Groups of DIDs

    ############################
    def createDataset(self, new_dataset) :         
        logger.debug("|  -  - Checking if a provided dataset exists: %s for a scope %s" % (new_dataset, self.myscope))
        try:
            self.client.add_dataset(scope=self.myscope, name=new_dataset)
            return(True)
        except DataIdentifierAlreadyExists:
            return(False)
        except Duplicate as error:
            return generate_http_error_flask(409, 'Duplicate', error.args[0])
        except AccountNotFound as error:
            return generate_http_error_flask(404, 'AccountNotFound', error.args[0])
        except RucioException as error:
            exc_type, exc_obj, tb = sys.exc_info()
            logger.debug(exc_obj)

    def createcontainer(self, name_container):
        '''
        registration of the dataset into a container :
        :param name_container: the container's name
        :param info_dataset : contains, 
            the scope: The scope of the file.
            the name: The dataset name.
        '''
        logger.debug("|  -  -  - registering container %s" % name_container)

        try:
            self.client.add_container(scope=self.myscope, name=name_container)
        except DataIdentifierAlreadyExists:
            logger.debug("|  -  -  - Container %s already exists" % name_container)       
        except Duplicate as error:
            return generate_http_error_flask(409, 'Duplicate', error.args[0])
        except AccountNotFound as error:
            return generate_http_error_flask(404, 'AccountNotFound', error.args[0])
        except RucioException as error:
            exc_type, exc_obj, tb = sys.exc_info()
            logger.debug(exc_obj)
    
    ############################

    ## General funciotn for registering a did into a GROUP of DID (CONTAINER/DATASET)

    ############################
    def registerIntoGroup(self,n_file, new_dataset):
        """
        Attaching a DID to a GROUP
        """
        type_1 = self.client.get_did(scope=self.myscope, name=new_dataset)
        type_2 = self.client.get_did(scope=self.myscope, name=n_file)

        try:
            self.client.attach_dids(scope=self.myscope, name=new_dataset, dids=[{'scope':self.myscope, 'name':n_file}])
        except RucioException:
            logger.debug("| - - - %s already attached to %s" %(type_2['type'],type_1['type']))    

    ############################

    ## MAGIC functions 

    ############################
    def create_groups(self, organization) :

        # 2.1) Create the dataset and containers for the file 
        self.createDataset(organization['dataset_1']) 
        # 2.1.1) Attach the dataset and containers for the file 
        self.registerIntoGroup(organization['replica'], organization['dataset_1'])        

        # 2.2) Create the dataset and containers for the file 
        self.createcontainer(organization['container_1']) 
        # 2.2.1) Attach the dataset and containers for the file 
        self.registerIntoGroup(organization['dataset_1'], organization['container_1'])        

        # 2.3) Create the dataset and containers for the file 
        self.createcontainer(organization['container_2']) 
        # 2.3.1) Attach the dataset and containers for the file 
        self.registerIntoGroup(organization['container_1'], organization['container_2'])        

        # 2.4) Create the dataset and containers for the file 
        self.createcontainer(organization['container_3']) 
        # 2.4.1) Attach the dataset and containers for the file             
        self.registerIntoGroup(organization['container_2'], organization['container_3'])   

    
    ############################

    ## Create Rule for DIDs

    ############################            
    def addReplicaRule(self, destRSE, group):
        """
        Create a replication rule for one dataset at a destination RSE
        """

        type_1 = self.client.get_did(scope=self.myscope, name=group)
        logger.debug("| - - - Creating replica rule for %s %s at rse: %s" % (type_1['type'], group, destRSE))
        if destRSE:
            try:
                rule = self.rulesClient.add_replication_rule([{"scope":self.myscope,"name":group}],copies=1, rse_expression=destRSE, grouping='ALL', account=self.account, purge_replicas=True)
                logger.debug("| - - - - Rule succesfully replicated at %s" % destRSE)
                logger.debug("| - - - - - The %s has the following id %s" % (rule, destRSE))
                return(rule[0])
            except DuplicateRule:
                exc_type, exc_obj, tb = sys.exc_info()
                rules = list(self.client.list_account_rules(account=self.account))
                if rules : 
                    for rule in rules :
                        if rule['rse_expression'] == destRSE and rule['scope'] == self.myscope and rule['name'] == group:
                            logger.debug('| - - - - Rule already exists %s which contains the following DID %s:%s %s' % (rule['id'],self.myscope, group, str(exc_obj)))
            except ReplicationRuleCreationTemporaryFailed:    
                exc_type, exc_obj, tb = sys.exc_info()
                rules = list(self.client.list_account_rules(account=self.account))
                if rules : 
                    for rule in rules :
                        if rule['rse_expression'] == destRSE and rule['scope'] == self.myscope and rule['name'] == group:
                            print('| - - - - Rule already exists %s which contains the following DID %s:%s %s' % (rule['id'],self.myscope, group, str(exc_obj)))                
                
                
    ############################

    ## Create Rules for not registered DIDs

    ############################  
    def outdated_register_replica(self, filemds, dest_RSE, org_RSE):
        """
        Register file replica.
        """
        carrier_dataset = 'outdated_replication_dataset' + '-' + str(uuid.uuid4())

        creation = self.createDataset(carrier_dataset)

        # Make sure your dataset is ephemeral

        self.client.set_metadata(scope=self.myscope, name=carrier_dataset, key='lifetime', value=86400) # 86400 in seconds = 1 day       

        # Create a completly new create the RULE: 
        for filemd in filemds :
            outdated = filemd['replica']['name']
            self.registerIntoGroup(outdated, carrier_dataset)
            
        # Add dummy dataset for replicating at Destination RSE
        rule_child = self.addReplicaRule(dest_RSE, group=carrier_dataset)

        # Add dummy dataset for replicating Origin RSE
        rule_parent = self.addReplicaRule(org_RSE, group=carrier_dataset)
        
        # Create a relation rule between origin and destiny RSE, so that the source data can be deleted 
        rule = self.client.update_replication_rule(rule_id=rule_parent, options={'lifetime': 10, 'child_rule_id':rule_child, 'purge_replicas':True})
        logger.debug('| - - - - Creating relationship between parent %s and child %s : %s' % (rule_parent, rule_child, rule))

        # Create a relation rule between the destinity rule RSE with itself, to delete the dummy rule, whiles keeping the destiny files    
        rule = self.client.update_replication_rule(rule_id=rule_child, options={'lifetime': 10, 'child_rule_id':rule_child})
        logger.debug('| - - - - Creating relationship between parent %s and child %s : %s' % (rule_parent, rule_child, rule))                          
                        
    ############################

    ## Create Dictionary for Grafana

    ############################              
    def stats_rules(self, rules) :
        '''
        Gather general information about 
        total number of rules, and stats.
        '''
        RUCIO = dict()
        if rules : 
            for rule in rules :
                if 'outdated_replication_dataset' not in rule['name'] :
                    if 'Rules' not in RUCIO :
                        RUCIO['Rules'] = {
                            'total_stuck' : 0, 
                            'total_replicating' : 0,
                            'total_ok' : 0,
                            'total_rules': 0 
                        }

                        RUCIO['Rules']['total_rules'] += 1
                        if rule['state'] == 'REPLICATING' : 
                            RUCIO['Rules']['total_replicating'] += 1
                        elif rule['state'] == 'STUCK' :
                            RUCIO['Rules']['total_stuck'] += 1
                        elif rule['state'] == 'OK' :
                            RUCIO['Rules']['total_ok'] += 1

                    else :     
                        RUCIO['Rules']['total_rules'] += 1
                        if rule['state'] == 'REPLICATING' : 
                            RUCIO['Rules']['total_replicating'] += 1
                        elif rule['state'] == 'STUCK' :
                            RUCIO['Rules']['total_stuck'] += 1
                        elif rule['state'] == 'OK' :
                            RUCIO['Rules']['total_ok'] += 1

                if 'AllRules' not in RUCIO : 
                    RUCIO['AllRules'] = {
                        'total_stuck' : 0, 
                        'total_replicating' : 0,
                        'total_ok' : 0,
                        'total_rules': 0 
                    }

                    RUCIO['AllRules']['total_rules'] += 1
                    if rule['state'] == 'REPLICATING' : 
                        RUCIO['AllRules']['total_replicating'] += 1
                    elif rule['state'] == 'STUCK' :
                        RUCIO['AllRules']['total_stuck'] += 1
                    elif rule['state'] == 'OK' :
                        RUCIO['AllRules']['total_ok'] += 1

                else :     
                    RUCIO['AllRules']['total_rules'] += 1
                    if rule['state'] == 'REPLICATING' : 
                        RUCIO['AllRules']['total_replicating'] += 1
                    elif rule['state'] == 'STUCK' :
                        RUCIO['AllRules']['total_stuck'] += 1
                    elif rule['state'] == 'OK' :
                        RUCIO['AllRules']['total_ok'] += 1 

                ##################
                if 'Grouping' not in RUCIO : 
                    RUCIO['Grouping'] = {
                        'file' : 0, 
                        'dataset' : 0,
                        'container' : 0 
                    }

                    if rule['did_type'] == 'CONTAINER' : 
                        RUCIO['Grouping']['container'] += 1
                    elif rule['did_type'] == 'DATASET' :
                        RUCIO['Grouping']['dataset'] += 1
                    elif rule['did_type'] == 'FILE' :
                        RUCIO['Grouping']['file'] += 1

                else :     
                    if rule['did_type'] == 'CONTAINER' : 
                        RUCIO['Grouping']['container'] += 1
                    elif rule['did_type'] == 'DATASET' :
                        RUCIO['Grouping']['dataset'] += 1
                    elif rule['did_type'] == 'FILE' :
                        RUCIO['Grouping']['file'] += 1 
            return(RUCIO)

    def stats_replica_rules(self, rules) :

        '''
        Gather specific information about 
        state and number of replicas.
        '''
        REPLICAS = dict()
        REPLICAS['RSE'] = {}
        if rules : 
            # Creates a key for all the RSEs that we have replicas
            for rule in rules :
                # if the RSE is not in the dictionary
                #print(rule['rse_expression'], REPLICAS['RSE'])
                if rule['rse_expression'] not in REPLICAS['RSE'] : 
                    #print(REPLICAS)
                    REPLICAS['RSE'][rule['rse_expression']] = { 
                        'total_replica_stuck' : rule['locks_stuck_cnt'], 
                        'total_replica_replicating' : rule['locks_replicating_cnt'],
                        'total_replica_ok' : rule['locks_ok_cnt']
                    } 
                # else if it  is, update replica numbers
                else :
                    REPLICAS['RSE'][rule['rse_expression']]['total_replica_stuck'] += rule['locks_stuck_cnt']
                    REPLICAS['RSE'][rule['rse_expression']]['total_replica_replicating'] += rule['locks_replicating_cnt']
                    REPLICAS['RSE'][rule['rse_expression']]['total_replica_ok'] += rule['locks_ok_cnt']
            return(REPLICAS)

    def stats_usage_rules(self, all_rses) :    
        STORAGE = dict()
        STORAGE['USAGE'] = {}
        for x_rse in all_rses :
            rses = self.usage(x_rse)
            if rses['bytes'] != 0 :
                if rses['rse'] not in STORAGE['USAGE'] : 
                    STORAGE['USAGE'][rses['rse']] = { 
                        'total_bytes_used' : rses['bytes']
                    } 
                # else if it  is, update replica numbers
                else :
                    STORAGE['USAGE'][rses['rse']]['total_bytes_used'] += rses['bytes']
        return(STORAGE)


# In[3]:


class Look_for_Files :
    def __init__(self) :

        self.gfal = Gfal2Context()
        
    def check_directory(self, path):
        try :
            full_path = self.gfal.listdir(str(path))
            is_dir_or_not = True        
        except:
            is_dir_or_not = False

        return(is_dir_or_not)

    def scrap_through_files(self, path) : 

        all_files = []

        # Itinerate over all the entries  
        listFiles = self.gfal.listdir(str(self.path))
        for file in listFiles :
            # Create full Path 
            fullPath = os.path.join(self.path, file)
            is_dir = self.check_directory(fullPath) 
            # If entry is a directory then get the list of files in
            if is_dir == True :
                pass
            else :
                all_files.append(fullPath) 
        return(all_files)

    def scrap_through_dir(self, path) : 
        
        logger.debug("*-Listin files from url : %s" % path)
        all_files = []

        # Itinerate over all the entries  
        listFiles = self.gfal.listdir(str(path))
        for file in listFiles :
            # Create full Path 
            fullPath = os.path.join(path, file)
            is_dir = self.check_directory(fullPath)
            # If entry is a directory then get the list of files in
            if is_dir == True :
                logger.debug('|--- ' + fullPath + ' its a directory ')
                all_files = all_files + self.scrap_through_dir(fullPath)

            else :
                logger.debug('|--- '+ fullPath + ' its a file')
                all_files.append(fullPath)
                
        return(all_files)


# In[4]:


############################

# Check existence of json File

############################

def json_write(data, filename='Rucio-bkp.json'): 
    with io.open(filename, 'w') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)
        
def json_check(json_file_name='Rucio-bkp.json') :
    # checks if file exists
    if not os.path.isfile(json_file_name) : 
        logger.debug("Either file is missing or is not readable, creating file...")
        return(False)
    
    elif os.stat(json_file_name).st_size == 0 :
        os.remove(json_file_name)
        return(False)
    
    elif os.path.isfile(json_file_name) and os.access(json_file_name, os.R_OK) :
        logger.debug("File exists in JSON and is readable")
        return(True)


# In[5]:


def register_rucio() : 
        
    # Look for files in the orgRse
    l1 = Look_for_Files()
    listOfFiles = l1.scrap_through_dir(r1.get_rse_url())

    if listOfFiles :
        # Create a dictionary with the properties for writing a json 
        result_dict = dict();
        for dest in r1.destRse :
            # Create an array for those files that has not been replicated 
            n_unreplicated = []
            for n in range(0,len(listOfFiles)):
            # for n in range(0,20):
                name = str(listOfFiles[n])
                logger.debug('|  -  ' + str(n) + ' - ' + str(len(listOfFiles)) + ' name : ' + name)
                
                # Break down the file path
                f_name = base=os.path.basename(name)

                # Check if file is already is registered at a particular destination RSE
                check = r1.check_replica(lfn=f_name.replace('+','_'), dest_rse=dest)
                
                # If it is registered, skip add replica 
                if check != False : ## needs to be changed to False
                    logger.debug('| - - The FILE %s already have a replica at RSE %s : %s' % (f_name, dest, check))

                # Else, if the files has no replica at destination RSE
                else :

                    # 1) Get the file metadata
                    metaData = r1.getFileMetaData(name, r1.orgRse)
                    r1.client.add_replicas(rse=r1.orgRse, files=[metaData['replica']])

                    # 2) Look for create and attach groups 

                    # look at script lfn2pfn.py
                    group = groups(name)
                    
                    # functions : groups and create_groups
                    r1.create_groups(group)

                    # 3) Add information to Json file :
                    
                    temp_dict = dict()
                    temp_dict[f_name] = {}
                    temp_dict[f_name]['Properties'] = {**metaData['replica'], **{'updated': datetime.utcnow().replace(tzinfo=pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}} 
                    temp_dict[f_name]['Organization'] = group
                    temp_dict[f_name]['Replicated'] = {dest : {**{'state': 'REPLICATING'}, **{'registered': datetime.utcnow().replace(tzinfo=pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}}}

                    # 4) Contruct a dictionary 
                    if f_name in result_dict :   
                        result_dict[f_name]['Replicated'].update(temp_dict[f_name]['Replicated'])
                        
                    # if its is the first entry, add the RSE where it was found : 
                    elif f_name not in result_dict :
                        origin = { r1.orgRse : {
                        'path': name,
                        'registered': datetime.utcnow().replace(tzinfo=pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'state': 'ALIVE',
                        }}
                        
                        temp_dict[f_name]['Replicated'].update(origin)
                
                        result_dict[f_name] = temp_dict[f_name]                                          
                        
                    # 5) Create the Main Replication Rule at Destination RSE
                    main_rule = r1.addReplicaRule(dest, group['container_3'])
                    logger.debug("| - - - - Getting parameters for rse %s" % dest)

                    # 6 ) Create the json array 

                    # Finally, add them to a general list 
                    n_unreplicated.append(metaData)
                    
            logger.debug('Your are going to replicate %s files' % str(len(n_unreplicated)))   
            print('Your are going to replicate %s files' % str(len(n_unreplicated)))
            ## Now, create Dummy rules between the ORIGIN and DESTINATION RSEs  
            if len(n_unreplicated) > 0 :
                r1.outdated_register_replica(n_unreplicated, dest, r1.orgRse)

        # Finally return the information of the replicas as a dictionary
        return(result_dict)


# In[6]:


def stateCheck(json_file='Rucio-bkp.json'):
      
    with open(json_file) as f : 
        data_keys  = json.load(f)
        for file in data_keys :
            for ele in data_keys[file].values():
                if isinstance(ele,dict):
                    for key, value in ele.items():
                        if key in r1.rses() :
                            
                            if 'path' in value:
                                if value['state'] == 'ALIVE' :
                                    # Check for deleted files
                                    try :
                                        existence = r1.file_exists(value['path'])
                                        
                                    # If gfal fails, it means that the file still exists  
                                    except :
                                        print('failed')
                                        dead_state = dict()
                                        dead_state = {'state': 'DEAD',
                                                    'deleted': datetime.utcnow().replace(tzinfo=pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                                                        }

                                        data_keys[file]['Replicated'][key].update(dead_state) 

                            elif 'state' in value :
                                # Check completed transference files
                                if value['state'] == 'REPLICATING' :
                                    #check = check_replica(DEFAULT_SCOPE, file.strip('+').replace('+','_'), dest_rse=info[0])
                                    
                                    check = r1.check_replica(lfn=file.replace('+','_'), dest_rse=key)
                                    
                                    #if there's no replica at destiny RSE
                                    if check != False : 
                                        
                                        replication_state = dict()
                                        replication_state = {'path': check,
                                                             'copied': datetime.utcnow().replace(tzinfo=pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                             'state': 'ALIVE'}
                                        # Update the dictionary with the file properties
                                        data_keys[file]['Replicated'][key].update(replication_state) 
        return(data_keys)

        


# In[7]:


class Grafana : 
    def __init__(self) :
        self.gr_prefix = [line for line in open('/etc/collectd.d/write_graphite-config.conf', 'r').readlines() if "Prefix" in line][0].strip().split()[1].strip('"')

    ## Prepare data for plots replicas 
    def prepare_grafana(self, dictionary, string='RUCIO.') :
        metric_list = []
        for key in dictionary.keys() :
            if isinstance(dictionary[key],int):
                metric_list.append((str(string+key),dictionary[key]) )

            elif isinstance(dictionary[key],dict):
                metric_list.extend(self.prepare_grafana(dictionary[key], str(string+key+'.')))       
        return(metric_list)
    
    def send_to_graf(self, dictionary, myport=2013, myprotocol='udp') : 
        for key in self.prepare_grafana(dictionary):
            if (key[0], key[1]) is not None : 
                #print(key[0].lower(),key[1])
                graphyte.Sender('graphite01.pic.es', port=myport, protocol=myprotocol, prefix=self.gr_prefix + socket.gethostname().replace(".","_")).send(key[0].lower(), key[1])
                graphyte.Sender('graphite02.pic.es', port=myport, protocol=myprotocol, prefix=self.gr_prefix + socket.gethostname().replace(".","_")).send(key[0].lower(), key[1])
    


# In[8]:


if __name__ == '__main__':
    
    # Initialize Rucio class and functions

    r1 = Rucio(myscope='test-bruzzese', orgRse='XRD2-NON-DET', 
               destRse=['XRD1-DET'], 
               account='bruzzese', working_folder='Server-test')

    r1.myfunc() 

    # It creates the main rule for replication at Destinatio RSE (see rses_catch)
    replication_dict = register_rucio()

    if json_check() == True :
        check_dict = stateCheck()
        # if both results resulted ok
        if isinstance(replication_dict,dict) & isinstance(check_dict,dict):
            replication_dict.update(check_dict)
        elif not check_dict : 
            replication_dict = replication_dict
        elif not replication_dict: 
            replication_dict = check_dict

    # creates a resulting dictionary with the files found with their respective 
    # RSEs where they have been replicated

    json_write(replication_dict)

    '''# Load grafana module
    g1 = Grafana()

    # 1) Plot general state of rules 
    g1.send_to_graf(r1.stats_rules(r1.rules()))

    # 2) Plot state of replicas per RSE
    g1.send_to_graf(r1.stats_replica_rules(r1.rules()))

    # 3) Plot RSE usage 
    g1.send_to_graf(r1.stats_usage_rules(r1.rses()))'''

