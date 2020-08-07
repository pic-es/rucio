#!/usr/bin/env python

from rucio.client import Client
from rucio.common.exception import Duplicate
from rucio.core.account import add_account_attribute
from rucio.common.types import InternalAccount


if __name__ == '__main__':
    c = Client()
    try:
        c.add_account('abruzzese', 'SERVICE', 'bruzzese@pic.es')
	add_account_attribute(account=InternalAccount('abruzzese'), key='admin', value=True)
    except Duplicate:
        print('Account abruzzese already added' % locals())
    try:
        add_account_attribute(account=InternalAccount('root'), key='admin', value=True)  # bypass client as schema validation fails at API level
    except Exception as error:
        print(error)
    try:
        c.add_identity(account='abruzzese', identity='bruzzese_user', authtype='userpass', password='pwd123', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')
    try:
        c.add_identity(account='abruzzese', identity='/DC=org/DC=terena/DC=tcs/C=ES/O=Port dInformacio Cientifica/CN=Agustin Bruzzese bruzzese@pic.es', authtype='x509', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')


    # add your accounts here, if you test against CERN authed nodes
    additional_test_accounts = [('/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=mlassnig/CN=663551/CN=Mario Lassnig', 'x509', 'mario.lassnig@cern.ch'),
                                ('/DC=org/DC=terena/DC=tcs/C=ES/O=Port dInformacio Cientifica/CN=Agustin Bruzzese bruzzese@pic.es', 'x509', 'bruzzese@pic.es')
				]

    for i in additional_test_accounts:
        try:
            c.add_identity(account='root', identity=i[0], authtype=i[1], email=i[2])
        except Exception:
            print('Already added: ', i)
