#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Lauren
#
# Created:     14/04/2012
# Copyright:   (c) Lauren 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from buzhug import Base
import os
from datetime import datetime, timedelta, date
import math
import Bases as DB

#haversine distance based on
# http://code.activestate.com/recipes/576779-calculating-distance-between-two-geographic-points/
def finddistance(loc1,loc2):
	R = 6371 #km
	dlat =math.radians(float(loc2[0]-loc1[0] ))
	dlon =math.radians(float(loc2[1]-loc1[1] ))
	lat1 = math.radians(loc1[0])
	lat2 = math.radians(loc2[0])
	
	a = math.sin(dlat/2) * math.sin(dlat/2) +  math.sin(dlon/2) * math.sin(dlon/2) * math.cos(lat1)*math.cos(lat2)
 	c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
 	d= R*c

	return d

#Roughly convert the timestamps to minutes
def minuteConvert(time):

	time = datetime.strptime(time, "%Y:%m:%d %H:%M:%S")
	minutes = 60 * (24 * (365 *  time.year + 30 * ( time.month - 1) + ( time.day - 1)) +  time.hour) +  time.minute
	return minutes

def orderEvents(criteria, value):
	evtOrder = []
##	try:
##		eventsDB = Base(os.getcwd() + "\\Databases\\events.db")
##		peopleDB = Base(os.getcwd() + "\\Databases\\people.db")
## 		placesDB = Base(os.getcwd() + "\\Databases\\locations.db")
##		photosDB = Base(os.getcwd() + "\\Databases\\photos.db")
##		facesDB = Base(os.getcwd() + "\\Databases\\faces.db")
##
##
##		eventsDB.open()
##		peopleDB.open()
##		placesDB.open()
##		photosDB.open()
##		facesDB.open()
##
##	except IOError as e:
##		print "Error opening database in OrderEvents",e
##		return evtOrder

	#for people, use a ratio based approach
	if criteria == "people":
		temp = []
		maxevtphotos = 0
		for event in DB.events:
			photos = DB.photos.select(eventid=event.__id__)
			numPhotos = len(photos)
			if maxevtphotos < numPhotos:
				maxevtphotos = numPhotos

		i = 0
		for event in DB.events:
			photos = DB.photos.select(eventid=event.__id__)
			#figure out how many photos our people are in
			personct = 0
			numPhotos = len(photos)
			for photo in photos:
				faces = DB.faces.select(photoid=photo.__id__)
				for face in faces:
					for pid in value:
						if face.personid == pid:
							personct = personct + 1

			#calculate the score
			score = 0.5 * (1.0 * personct) / numPhotos + 0.5 * (1.0 * numPhotos) / maxevtphotos
			temp.append((score,i))
			i = i + 1

		temp.sort()
		for item in temp:
			evtOrder.append(item[1])

	#for location calculate which events to show based on their lat/long distance
	elif criteria == "location":
		temp = []
		#average the lat/long of the photos in each event
		photos = DB.photos.select().sort_by("eventid")
		for photo in photos:
			evtID = photo.eventid
			print "event id",evtID
			lat = DB.places[photo.locationid].lat
			lon = DB.places[photo.locationid].lon
			if evtID == len(temp):
				temp.append([(lat,lon)])
			else:
				temp[evtID].append((lat,lon))

		#calculate the distance between the desired value and each event
		i = 0
		difflist = []
		for event in temp:
			latsum = 0
			longsum = 0
			for item in event:
				latsum = item[0] + latsum
				longsum = item[1] + longsum
			latavg = (1.0 * latsum) / len(event)
			longavg = (1.0 * longsum) / len(event)

			#now calculate the distance between our desired point and this point
			diff = finddistance(value, (latavg,longavg))
			difflist.append((diff, i))
			i = i + 1


		#order them on that basis
		difflist.sort()
		print "difflist",difflist
		evtOrder = []
		for diff in difflist:
			evtOrder.append(diff[1])


	#for time, calculate the weights according to the time ordering
	elif criteria == "time":
		scored=[]
		
		for evt in DB.events:
			if minuteConvert(evt.firsttime) - minuteConvert(value) < 0:
				w1 = -10000
			else:
				w1 = 1 - (minuteConvert(evt.firsttime) - minuteConvert(value)) / (1.0 * minuteConvert(evt.lasttime) - minuteConvert(value))
			scored.append((w1,evt.__id__))
			
		scored.sort()
		scored.reverse()

		for item in scored:
			evtOrder.append(item[1])
			
	return evtOrder

def main():
	print orderEvents("people",[0])
	pass

if __name__ == '__main__':
    main()