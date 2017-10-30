#!/usr/bin/env python
# A Ravello SDK example showing all applications in a user account in format: 
# Application name, ID, Creation Time, Owner, If published, Region
#
# Copyright 2011-2016 Ravello Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import ravello_sdk
import sys
import os
import datetime
import json
import re
import ConfigParser
from argparse import ArgumentParser
from ravello_sdk import *
from common import *

def mkparser():
        parser = ArgumentParser()
        parser.add_argument("-u", dest="username",default=None,help='Ravello user account name')
        parser.add_argument("-o", dest="out_file",default=None,help='output file')
        return parser


def get_vms(app_id, client):
        vms = client.get_vms(app_id,level='deployment')
        return vms

def print_vms(vms,out_file):
        if vms:
                for vm in vms:
                    #if vm['platform']:
                    if re.search('^controller|director',vm['name'].encode('utf-8')) is not None:
                        print('Name: {0:<40} ID: {1:<20} State: {2} FQDN: {3}'.format(vm['name'].encode('utf-8'),vm['id'], vm['state'], vm['externalFqdn']))
                    else:
                        print('Name: {0:<40} ID: {1:<20} State: {2} FQDN: N/A'.format(vm['name'].encode('utf-8'),vm['id'], vm['state']))

#               print (json.dumps(vms, indent=5))

                if out_file:
                        with open(out_file,'w') as f:
                                for vm in vms:
                                        f.write(json.dumps(vms,indent=5))

def build_inventory(apps,app_filter,client):
        group = {}
        for app in apps:
            if re.search('^'+app_filter,app['name'].encode('utf-8')) is not None and app['published']:
                    group[app['name']] = []
                    group[app['name']].append('controller-'+app['name']+' nodeIp=172.16.1.27')
                    group[app['name']].append('compute1-'+app['name']+' nodeIp=172.16.1.25')
                    group[app['name']].append('compute2-'+app['name']+' nodeIp=172.16.1.23')
                    vms = get_vms(app['id'],client)
                    for vm in vms:
                        if re.search('^controller',vm['name'].encode('utf-8')) is not None:
                            group[app['name']].append('controllerFqdn=' +vm['externalFqdn'])
                        elif re.search('director',vm['name'].encode('utf-8')) is not None:
                            group[app['name']].append('ansible_ssh_common_args=\'-o ProxyCommand=\"ssh -W {{ nodeIp }}:%p -q cloud-user@' + vm['externalFqdn'] + '\"\'')



        return group
                    


		
def main():
	parser = mkparser()
	args = parser.parse_args()

        #Set user credentials
	username, password  = get_user_credentials(args.username)
	if not username or not password:
		exit(1)

	#Connect to Ravello
	client = connect(username, password)
	if not client:
		exit (1)

	#Get List of application
	apps = client.get_applications()

        # FIXME: testing filter
        app_filter='LATAM-SME-OSP'

        x = build_inventory(apps, app_filter, client)

        print x

#        for app in apps:
#            creation_time = datetime.datetime.fromtimestamp(app['creationTime']/1000).strftime('%Y-%m-%d %H:%M')
#            if re.search('^LATAM-SME-OSP',app['name'].encode('utf-8')) is not None and app['published']:
#                print('Application name: {0:<50} ID: {1:<10} Creation Date: {2:<20} Owner: {3:<25} Published: yes    Region: {4:<10}'.format(app['name'].encode('utf-8'),app['id'],creation_time,app['ownerDetails']['name'],app['deployment']['cloudRegion']['name']))
#                vms = get_vms(app['id'],client)
#                print_vms(vms,args.out_file)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        sys.stderr.write('Error: {!s}\n'.format(e))
