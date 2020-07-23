#!/usr/bin/env python

from rucio.client import Client
from rucio.common.exception import Duplicate
from rucio.core.account import add_account_attribute
from rucio.common.types import InternalAccount


if __name__ == '__main__':
    c = Client()
    try:
        c.add_account('bruzzese', 'SERVICE', 'bruzzese@pic.es')
	add_account_attribute(account=InternalAccount('bruzzese'), key='admin', value=True)
    except Duplicate:
        print('Account bruzzese already added' % locals())
    try:
        add_account_attribute(account=InternalAccount('root'), key='admin', value=True)  # bypass client as schema validation fails at API level
    except Exception as error:
        print(error)
    try:
        c.add_identity(account='bruzzese', identity='bruzzese_user', authtype='userpass', password='pwd123', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')
    try:
        c.add_identity(account='bruzzese', identity='/CN=Agustin Bruzzese', authtype='x509', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')

    try:
        c.add_identity(account='mario', identity='mario_user', authtype='userpass', password='pwd123', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')

    try:
        c.add_account('gonzalo', 'SERVICE', 'bruzzese@pic.es')
	add_account_attribute(account=InternalAccount('gonzalo'), key='admin', value=True)
    except Duplicate:
        print('Account bruzzese already added' % locals())
    try:
        c.add_identity(account='gonzalo', identity='/CN=Gonzalo Merino', authtype='x509', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')
    try:
        c.add_identity(account='gonzalo', identity='gonzalo_user', authtype='userpass', password='pwd123', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')

    try:
        c.add_account('elena', 'SERVICE', 'bruzzese@pic.es')
	add_account_attribute(account=InternalAccount('elena'), key='admin', value=True)
    except Duplicate:
        print('Account bruzzese already added' % locals())
    try:
        c.add_identity(account='elena', identity='/CN=Elena Planas', authtype='x509', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')
    try:
        c.add_identity(account='elena', identity='elena_user', authtype='userpass', password='pwd123', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')

    try:
        c.add_account('pau', 'SERVICE', 'bruzzese@pic.es')
	add_account_attribute(account=InternalAccount('pau'), key='admin', value=True)
    except Duplicate:
        print('Account bruzzese already added' % locals())
    try:
        c.add_identity(account='pau', identity='/CN=Pau Tallada', authtype='x509', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')
    try:
        c.add_identity(account='pau', identity='pau_user', authtype='userpass', password='pwd123', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')


    try:
        c.add_account('mario', 'SERVICE', 'bruzzese@pic.es')
	add_account_attribute(account=InternalAccount('mario'), key='admin', value=True)
    except Duplicate:
        print('Account bruzzese already added' % locals())
    try:
        c.add_identity(account='mario', identity='/CN=Mario Lassnig', authtype='x509', email='bruzzese@pic.es')
    except Exception:
        print('Already added: ')


    # add your accounts here, if you test against CERN authed nodes
    additional_test_accounts = [('/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=mlassnig/CN=663551/CN=Mario Lassnig', 'x509', 'mario.lassnig@cern.ch'),
                                ('/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=barisits/CN=692443/CN=Martin Barisits', 'x509', 'martin.barisits@cern.ch'),
                                ('/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=tbeerman/CN=722011/CN=Thomas Beermann', 'x509', 'thomas.beermann@cern.ch'),
                                ('/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ruciobuildbot/CN=692443/CN=Robot: Rucio build bot', 'x509', 'rucio.build.bot@cern.ch'),
                                ('/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=sprenner/CN=822876/CN=Stefan Prenner', 'x509', 'stefan.prenner@cern.ch'),
                                ('/CN=docker client', 'x509', 'dummy@cern.ch'),
                                ('mlassnig@CERN.CH', 'GSS', 'mario.lassnig@cern.ch')]

    for i in additional_test_accounts:
        try:
            c.add_identity(account='root', identity=i[0], authtype=i[1], email=i[2])
        except Exception:
            print('Already added: ', i)
