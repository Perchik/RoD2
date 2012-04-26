#-------------------------------------------------------------------------------
# Name:        Database explorer
# Purpose:
#
# Author:      PSDUKES
#
# Created:     13/04/2012
# Copyright:   (c) PSDUKES 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os

import sys
import webbrowser
sys.path.append(os.getcwd()+"\\lib")
from bs4 import BeautifulSoup, SoupStrainer
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from buzhug import Base
import re
import unicodedata
import HTMLParser
import tidy
def main():
	events = Base(os.getcwd()+"\\Databases\\events.db")
	locations = Base(os.getcwd()+"\\Databases\\locations.db")
	photos = Base(os.getcwd()+"\\Databases\\photos.db")
	people = Base(os.getcwd()+"\\Databases\\people.db")
	faces = Base(os.getcwd()+"\\Databases\\faces.db")
	training = Base(os.getcwd()+"\\Databases\\training_images.db")
	features = Base(os.getcwd()+"\\Databases\\features.db")
	try:
		print "============ events ================"
		events.open()
		for field in events.fields:
			print field,events.fields[field]
		print "len",len(events),"\n\n"
		for record in events.select().sort_by("+firsttime"):
			print record
		
		elist =[ None for i in range(len(events))]
		print elist
			
		
		print "============ locations ================"
		locations.open()
		for field in locations.fields:
			print field,locations.fields[field]
		print "len",len(locations),"\n\n"
		#for record in locations:
		#	print record

		print "============ photos ================"
		photos.open()
		for field in photos.fields:
			print field,photos.fields[field]
		print "len",len(photos),"\n\n"
		for record in photos:
			print record
		
		print "============ people ================"
		people.open()
		for field in people.fields:
			print field,people.fields[field]
		print "len",len(people),"\n\n"
		#for record in people:
		#	print record
		
		print "=========== faces =============="
		faces.open()
		for field in faces.fields:
			print field,faces.fields[field]
		print "len",len(faces),"\n\n"
		#for record in faces:
		#	print record
		
		print "============ training ========"
		training.open()
		for field in training.fields:
			print field, training.fields[field]
		print "len",len(training),"\n\n"
	
		print "============ features ==========="
		features.open()
		for field in features.fields:
			print field, features.fields[field]
		print "len",len(features),"\n\n"
		
		
	except IOError as err:
		print "no database there:",err

if __name__ == '__main__':
    main()
