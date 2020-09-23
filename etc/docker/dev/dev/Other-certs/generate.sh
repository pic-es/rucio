#!/bin/bash
export PASSPHRASE=123456

# User certificate
openssl req -new -newkey rsa:2048 -nodes -keyout ruciouser.key.pem -subj "/CN=Rucio User" > ruciouser.csr
openssl x509 -req -days 9999 -CAcreateserial -extfile <(printf "keyUsage=critical") -in ruciouser.csr -CA rucio_ca.pem -CAkey rucio_ca.key.pem -out ruciouser.pem

# User certificate
openssl req -new -newkey rsa:2048 -nodes -keyout agususer.key.pem -subj "/CN=Agustin Bruzzese" > agususer.csr
openssl x509 -req -days 9999 -CAcreateserial -in agususer.csr -CA rucio_ca.pem -CAkey rucio_ca.key.pem -out agususer.pem

openssl req -new -newkey rsa:2048 -nodes -keyout gonzalouser.key.pem -subj "/CN=Gonzalo Merino" > gonzalouser.csr
openssl x509 -req -days 9999 -CAcreateserial -in gonzalouser.csr -CA rucio_ca.pem -CAkey rucio_ca.key.pem -out gonzalouser.pem

openssl req -new -newkey rsa:2048 -nodes -keyout pauuser.key.pem -subj "/CN=Pau Tallada" > pauuser.csr
openssl x509 -req -days 9999 -CAcreateserial -in pauuser.csr -CA rucio_ca.pem -CAkey rucio_ca.key.pem -out pauuser.pem

openssl req -new -newkey rsa:2048 -nodes -keyout elenauser.key.pem -subj "/CN=Elena Planas" > elenauser.csr
openssl x509 -req -days 9999 -CAcreateserial -in elenauser.csr -CA rucio_ca.pem -CAkey rucio_ca.key.pem -out elenauser.pem

openssl req -new -newkey rsa:2048 -nodes -keyout mariouser.key.pem -subj "/CN=Mario Lassnig" > mariouser.csr
openssl x509 -req -days 9999 -CAcreateserial -in mariouser.csr -CA rucio_ca.pem -CAkey rucio_ca.key.pem -out mariouser.pem

chmod 0400 *key*

echo
