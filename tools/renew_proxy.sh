#!/bin/bash
#
# cred_proxy
#
# Create an x509 proxy from the host's igtf grid certificate and delegate
# against the osg fts server at https://fts01.pic.es:8446.  Run this script (as
# root) as a cronjob to maintain an FTS-delegated proxy for rucio operations.
#
## Configuration
#export PASSPHRASE=br4912862

proxytool=/usr/bin/voms-proxy-init
#hostcert=/etc/grid-security/usercert.pem
#hostkey=/etc/grid-security/userkey.pem
hostcert=/etc/grid-security/rucio02_pic_es_cert.cer
hostcert=/etc/grid-security/rucio02_pic_es_cert.key
#x509proxy=/opt/rucio/etc/web/x509up
x509proxy=/tmp/x509up_u0

## Logging info
dtstamp="`date +%F-%A-%H.%M.%S `"
echo -e "\n################ ${dtstamp} ################" 


## Create robot proxy
echo $PASSPHRASE
echo -e "${dtstamp}: ${proxytool} -cert ${hostcert} -key ${hostkey} -out ${x509proxy} "

while true
do  
  ${proxytool} -cert ${hostcert} -key ${hostkey} -out ${x509proxy} -pwstdin
  proxy_ret=$?

  echo -e "${dtstamp}: ${proxytool} return: ${proxy_ret}\n" 2>&1

  fts-rest-delegate -vf -s https://fts01.pic.es:8446 -H 9999

  sleep 43100

done

