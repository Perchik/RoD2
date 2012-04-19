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
from buzhug import Base

def main():
	events = Base(os.getcwd()+"\\Databases\\events.db")
	locations = Base(os.getcwd()+"\\Databases\\locations.db")
	photos = Base(os.getcwd()+"\\Databases\\photos.db")
	people = Base(os.getcwd()+"\\Databases\\people.db")
	faces = Base(os.getcwd()+"\\Databases\\faces.db")


	try:
		print "events"
		events.open()
		for field in events.fields:
			print field,events.fields[field]
		print "len",len(events),"\n"
		
		print "locations"
		locations.open()
		for field in locations.fields:
			print field,locations.fields[field]
		print "len",len(locations),"\n"
		
		print "photos"
		photos.open()
		for field in photos.fields:
			print field,photos.fields[field]
		print "len",len(photos),"\n"
		
		print "people"
		people.open()
		for field in people.fields:
			print field,people.fields[field]
		print "len",len(people),"\n"
		
		print"faces"
		faces.open()
		for field in faces.fields:
			print field,faces.fields[field]
		print "len",len(faces),"\n"
		
		
##	
##		maxscore =0
##		minscore=10
##		count=0
##		for record in db.select(None).sort_by("+__id__"):
##			if(record.score>maxscore):
##				maxscore=record.score
##				print "max",record
##			if(record.score<minscore):
##				minscore =record.score
##				print "min",record
##		print "max is ", maxscore, "min is",minscore
		
		
		print "events"
		for record in events:
			print record
		print "\n"
		
		print "location"
		for record in locations:
			print record
		print "\n"
	
		print"photos"
		for record in photos:
			print record
		print "\n"

		print"people"
		for record in people:
			print record
		print "\n"

		print"faces"
		for record in faces:
			print record
		print "\n"
		
	except IOError:
		print "no database there.."

if __name__ == '__main__':
    main()
