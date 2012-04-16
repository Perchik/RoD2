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

#haversine distance based on
# http://code.activestate.com/recipes/576779-calculating-distance-between-two-geographic-points/
def finddistance(loc1,loc2):
	start_long = math.radians(float(loc1[0]))
	start_latt = math.radians(float(loc1[1]))
	end_long = math.radians(float(loc2[0]))
	end_latt = math.radians(float(loc2[1]))
	d_latt = end_latt - start_latt
	d_long = end_long - start_long
	a = math.sin(d_latt/2)**2 + math.cos(start_latt) * math.cos(end_latt) * math.sin(d_long/2)**2
	c = 2 * math.atan2(math.sqrt(a),  math.sqrt(1-a))
	return 6371 * c *  0.621371192


#Roughly convert the timestamps to minutes
def minuteConvert(time):
	time = datetime.strptime(time, "%Y:%m:%d %H:%M:%S")
	minutes = 60 * (24 * (365 *  time.year + 30 * ( time.month - 1) + ( time.day - 1)) +  time.hour) +  time.minute
	return minutes

def orderEvents(criteria, value):
	evtOrder = []
	try:
		eventdb = Base(os.getcwd() + "\\Databases\\events.db")
		peopledb = Base(os.getcwd() + "\\Databases\\people.db")
 		locationdb = Base(os.getcwd() + "\\Databases\\locations.db")
		photosdb = Base(os.getcwd() + "\\Databases\\photos.db")
		facedb = Base(os.getcwd() + "\\Databases\\faces.db")


		eventdb.open()
		peopledb.open()
		locationdb.open()
		photosdb.open()
		facedb.open()

	except IOError:
		print "error"
		return evtOrder

	#for people, use a ratio based approach
	if criteria == "people":
		temp = []
		maxevtphotos = 0
		for event in eventdb:
			photos = photosdb.select(eventid=event.__id__)
			numPhotos = len(photos)
			if maxevtphotos < numPhotos:
				maxevtphotos = numPhotos

		i = 0
		for event in eventdb:
			photos = photosdb.select(eventid=event.__id__)
			#figure out how many photos our people are in
			personct = 0
			numPhotos = len(photos)
			for photo in photos:
				faces = facedb.select(photoid=photo.__id__)
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
		photos = photosdb.select().sort_by("eventid")
		for photo in photos:
			evtID = photo.eventid
			lat = locationdb[photo.locationid].lat
			long = locationdb[photo.locationid].long
			if evtID == len(temp):
				temp.append([(lat,long)])
			else:
				temp[evtID].append((lat,long))

		#calculate the distance between the desired value and each event
		i = 0
		difflist = []
		for event in temp:
			latsum = 0
			longsum = 0
			for item in event:
				latsum = item[0] + latsum
				longsum = item[1] + longsum
			latavg = (1.0 * latsum) / len(item)
			longavg = (1.0 * longsum) / len(item)

			#now calculate the distance between our desired point and this point
			diff = finddistance(value, (latavg,longavg))
			difflist.append((diff, i))
			i = i + 1


		#order them on that basis
		difflist.sort()
		evtOrder = []
		for diff in difflist:
			evtOrder.append(diff[1])


	#for time, calculate the weights according to the time ordering
	elif criteria == "time":
		temp = []
		lastTimestamp = 0
		for evt in eventdb:
			#print evt
			#select the first photo in the event and get its start time
			photos = photosdb.select(eventid=evt.__id__).sort_by("+timestamp")
			firstTimestamp = photos[0].timestamp
			temp.append((firstTimestamp, evt.__id__))
			if minuteConvert(firstTimestamp) > lastTimestamp:
				lastTimestamp = firstTimestamp

		#calculate w1s for the events and append the scores with the event ids
		scored = []
		for item in temp:
			if minuteConvert(item[0]) - minuteConvert(value) < 0:
				w1 = -10000
			else:
				w1 = 1 - (minuteConvert(item[0]) - minuteConvert(value)) / (1.0 * minuteConvert(lastTimestamp) - minuteConvert(value))
			scored.append((w1,item[1]))
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