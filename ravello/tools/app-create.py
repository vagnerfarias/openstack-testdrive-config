#!/usr/bin/env python
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
import json
from argparse import ArgumentParser
from common import *

log = logging.getLogger('main')

def mkparser():
	parser = ArgumentParser()
	parser.add_argument("-b", dest="bp_name",default=None,help='blueprint name the application is created from')
	parser.add_argument("-i", dest="bp_id",default=0,help='blueprint name the application is created from')
	parser.add_argument("-n", dest="app_prefix",default=None,help='application name prefix')
	parser.add_argument("-d", dest="app_desc",default=None,help='application description')
	parser.add_argument("-p", dest="publish",default=False,action="store_true",help='publish application')
	parser.add_argument("-r", dest="region",default=None,help='preferred region')
	parser.add_argument("-o", dest="optimization",help='optimization level: COST_OPTIMIZED or PERFORMANCE_OPTIMIZED, when using COST_OPTIMIZED optimization level leave region empty')
	parser.add_argument("-s", dest="start",default=False,action="store_true",help='start VMs')
	parser.add_argument("-t", dest="exp_time",default=False,type=int,help='application expiration time in minutes, use in combination with -s')
	parser.add_argument("-u", dest="username",default=None,help='Ravello user account name')
	parser.add_argument("-l", dest="log_file", default='ravello.log',help='logfile name')
	parser.add_argument("-c", dest="app_count", default='1',help='number of applications to create')

	return parser

def validate_param(args):
	if not args.bp_name and not args.bp_id: # Blue print name or ID must be provided 
		log.error("Invalid parameters, either blueprint name or blueprint ID must be provided")
		print("Error: Invalid parameters, either blueprint name or blueprint ID must be provided")
		return False

	if not args.app_prefix:
		log.error("Invalid parameters, application name must be provided")
		print("Error: Invalid parameters, application name must be provided")
		return False

	if args.region:
		args.region = args.region.lower().capitalize()

	return True

def get_bp_data(bp_id,bp_name,client):
        found_pb = None
        if bp_id == 0:                 # If blueprint ID is unknown find the blueprint by name
                for bp in client.get_blueprints():
                        if bp['name'].lower() == bp_name.lower():
                                found_pb = bp
                                break
        else:
                for bp in client.get_blueprints():
                        if bp['id'] == bp_id:
                                found_bp = bp
                                break
        return found_pb

def create_app(app_name,app_desc,bp_id,client):	
	new_app=None
	if (app_name and bp_id!=0):
		app={'name':app_name,'description':app_desc,'baseBlueprintId':bp_id}
		log.info("Creating a new application {}".format(app_name))
		print("Creating a new application", app_name)
		print(app)
		new_app = client.create_application(app)
	return new_app

def publish_app(app,region,optimization_level,start,exp_time,client):
	if app:
		if region:
			if optimization_level=='COST_OPTIMIZED':
				log.warning('Region is specified. Changing optimization level to PERFORMANCE_OPTIMIZED')
				print('Region is specified. Changing optimization level to PERFORMANCE_OPTIMIZED')
			optimization_level = 'PERFORMANCE_OPTIMIZED'
		
		elif not optimization_level:	
			optimization_level = 'COST_OPTIMIZED'
			
			
		param = {'preferredRegion':region, 'optimizationLevel':optimization_level, 'startAllVms':start}

		log.info("Publishing application {0}".format(app['name']))
		print("Publishing application {0}".format(app['name']))
		log.info(param)
		print(param)

		client.publish_application(app,param)

		if start and exp_time: # Set the application expiration time
			log.info("Setting the application expiration time to {0} min".format(exp_time))
			print("Setting the application expiration time to {0} min".format(exp_time))
			exp = {'expirationFromNowSeconds': 60*exp_time}
			client.set_application_expiration(app['id'], exp)

def validate_region(app_id,region,client):

	cloud_locations = client.get_application_publish_locations(app_id)
	available_regions = []
	found = False
	for loc in cloud_locations:
		if loc['regionName'] == region or not region:
			found = True
			break
		cloud_location = loc['regionName']
		available_regions.append(cloud_location)
	
	if found:		#The app can be published in the specified cloud location
		return True
	elif len(available_regions)>0: #preffered region was not specified but there are cloud locations the app can be published
		return True
	else:			#There is no avalable cloud locations where the app can be published
		log.error("Invalid region {0}".format(region))
		log.info("Available region locations: {}".format(", ".join(available_regions)))
		print("Error: Invalid region {0}".format(region))
		print("Available region locations:")
		print (", ".join(available_regions))
		return False

def delete_app_if_exists(app_name,client,prompt_user):

	app_id = get_app_id(app_name,client)

	if app_id > 0:	#Application found
		resp = raw_input("Application {0} already exists, do you want to delete it [yes/no]:".format(app_name))
		if resp.lower() == "yes":
			log.info("Deleting application {}".format(app_name))
			print("Deleting application",app_name)
			client.delete_application(app_id)
			return True
		else:
			log.info("Application {} already exists, exiting...".format(app_name))
			print("Application {} already exists, exiting...".format(app_name))
			return False
	#Application not found
	return True
	
def display_app(app_id,client):
	if app_id:
		app = client.get_application(app_id)
		print()
		print ("name: ",app['name'])
		print ("id: ",app['id'])
		print ("owner: ",app['owner'])

# Check if this is a published app
		app_state = application_state(app)		
		if app_state != None:					#Published app
			print ("publishOptimization: ",app['deployment']['publishOptimization'])
			print ("regionName: ",app['deployment']['regionId'])
			print ("totalActiveVms: ",app['deployment']['totalActiveVms'])
			print ("totalErrorVms: ",app['deployment']['totalErrorVms'])
			print ("Application state: ", app_state)
		else:
			print("Application {0} is not published".format(app['name']))
def main():
	parser = mkparser()
	args = parser.parse_args()

	if not validate_param(args):
		parser.print_help()
		exit(1)

	initlog(args.log_file)

	#Get user credentials
	username, password  = get_user_credentials(args.username)
	if not username or not password:
		exit(1)

	#Connect to Ravello
	client = connect(username, password)
	if not client:
		exit (1)

        #Main loop
        for i in range(1, int(args.app_count)+1):
            app_name = args.app_prefix + '-' + str(i).zfill(2)

            #Check if application with this name already exists and delete it
            if not delete_app_if_exists(app_name,client,True):
            	exit(0) #Cancelled by user
            
            #Get Blue Print ID
            bp = get_bp_data(args.bp_id,args.bp_name,client)
            
            if bp:
            	#Create application
            	new_app = create_app(app_name,args.app_desc,bp['id'],client)
            
            	if new_app and args.publish:		 #Validate region and publish application
            		if validate_region(new_app['id'],args.region,client):
            			publish_app(new_app,args.region,args.optimization,args.start,args.exp_time,client)
            	if new_app:
            		display_app(new_app['id'],client)
            
            else:
            	log.error("Blueprint {} not found".format(args.bp_name))
            	print("Error: Blueprint {} not found".format(args.bp_name))
            	exit(1)
	

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        sys.stderr.write('Error: {!s}\n'.format(e))
