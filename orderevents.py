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
 		placedb = Base(os.getcwd() + "\\Databases\\locations.db")
		photosdb = Base(os.getcwd() + "\\Databases\\photos.db")


		eventdb.open()
		peopledb.open()
		placedb.open()
		photosdb.open()

	except IOError:
		print "error"
		return evtOrder

	if criteria == "people":
		pass


	elif criteria == "location":
		pass
	elif criteria == "time":
		temp = []
		lastTimestamp = 0
		for evt in eventdb:
			#select the first photo in the event and get its start time
			photos = photosdb.select(eventid=evt.__id__).sort_by("+timestamp")
			firstTimestamp = photos[0].timestamp
			temp.append((firstTimestamp, evt.__id__))
			if minuteConvert(firstTimestamp) > lastTimestamp:
				lastTimestamp = firstTimestamp

		#calculate w1s for the events and append the scores with the event ids
		scored = []
		for item in temp:
			print lastTimestamp
			print item[0]
			if minuteConvert(item[0]) - minuteConvert(value) < 0:
				print "neg"
				w1 = -1
			else:
				w1 = 1 - (minuteConvert(item[0]) - minuteConvert(value)) / (1.0 * minuteConvert(lastTimestamp) - minuteConvert(value))
			scored.append((w1,item[1]))
		scored.sort()

		for item in scored:
			evtOrder.append(item[1])
	print evtOrder
	return evtOrder

def main():
	orderEvents("time", "1987:5:13 12:00:00")
	pass

if __name__ == '__main__':
    main()