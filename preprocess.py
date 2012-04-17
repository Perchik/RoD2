# Lauren Cairco
# CPSC 863
# Spring 2012
# preprocess.py
# Preprocessing for replication of Reliving on Demand paper
#
# For all the files in a directory tree, do the following to preprocess for a digital albuming system:
# - Cluster into events based on the timestamp
# - Geotag based on the lowermost directory name
# - Detect faces
# - Cluster faces
# - Store in a Buzhug database for retrieval

import detectfaces
import geotag
import timecluster2 as timecluster
from buzhug import Base
import os
import exif
from PIL import Image

def main():
	#Make the database. We need tables for events, locations, photos, people, and faces
	events = Base(os.getcwd()+"\\Databases\\events.db")
	events.create(('name',str),mode="override")

	locations = Base(os.getcwd()+"\\Databases\\locations.db")
	locations.create(('lat',float),('long',float),('name',str),mode="override")

	photos = Base(os.getcwd()+"\\Databases\\photos.db")
	photos.create(('path',str),('timestamp',str),('aestheticscore',int),('locationid',int), ('eventid',int), ("width", int), ("height", int),mode="override")

	people = Base(os.getcwd()+"\\Databases\\people.db")
	people.create(('name',str),('age',int),mode="override")

	faces = Base(os.getcwd()+"\\Databases\\faces.db")
	faces.create(('photoid',int),('thumbnail',str),('personid',int),('x',int),('y',int),('w',int),('h',int),mode="override")

	# Walk through all the directories, making a list of photos, geotagging the lowest level subdirectories, and making
	# a master list of the photos and geotags

	photolist = []
	geotaglist = []
	for dirname, dirnames, filenames in os.walk(os.getcwd()+"\\Images\\photos"):
		#geocode all the subdirectory names
		for subdirname in dirnames:
			n,lat,long =  geotag.findlocation(subdirname)

			#if we have a problem geotagging, prompt the user for a different location name
			while n == "NONE":
				newname = raw_input("We couldn't find the location '" + subdirname + "'. Type in another place name to try.")
				n, lat, long = geotag.findlocation(subdirname)

			#once we have a valid location, insert it if it's not already in the database
			if not locations(name=n):
				locations.insert(float(lat), float(long), n)

		#add all the files to a file list, and go ahead and make a parallel geotags
		for filename in filenames:
			#print "filename is ",filename
			if filename[-3:] == "jpg" or filename[-3:] == "JPG":
				#find the id for that subdirname in the database so we can geotag it
				locname = dirname[dirname.rfind('\\') + 1:]
				#location = locations(name=dirname)
				photolist.append(os.path.join(dirname,filename))
				geotaglist.append((os.path.join(dirname,filename),locname))

	#make a list to identify which event each photo is in

	#print photolist
	eventLabels, uniqueEvents = timecluster.eventCluster(photolist)
	#print "events: "
	#print eventLabels
	print uniqueEvents

	#insert the events into the event database
	for label in uniqueEvents:
		events.insert(label)

	#the events are already sorted according to photo names
	#now sort the geotags and photolist according to photo names as well, so we'll have parallel lists
	geotaglist.sort()
	photolist.sort()

	#now we can finally insert each photo, with a name, event, and geotag
	for i in range(len(photolist)):
		width, height = Image.open(photolist[i]).size
		photos.insert(photolist[i],eventLabels[i][1], 0,locations(name=geotaglist[i][1])[0].__id__,events(name=eventLabels[i][0])[0].__id__, int(width), int(height))

	#for all the images we just gathered, find the people and faces, and insert them into the database
	facelist = []
	for file in photolist:
		facelist.append(detectfaces.detectFaceInImage(file))

	faceimages, projections, imgs = detectfaces.faceLBP(facelist)#detectfaces.facePCA(facelist)
	labels, nclusters = detectfaces.gMeansCluster(projections)
	#detectfaces.visualizeResults(faceimages, labels, nclusters)

	#add the individuals we found in the photos into the people database
	i = 0
	for i in range(0,nclusters):
		people.insert(str(i),0)

	#add the faces, linking them to the individuals
	faceindex = 0
	photoindex = 0
	for listing in facelist:
		facerects = listing[1:]
		for entry in facerects:
			faces.insert(photoindex,imgs[faceindex],people[labels[faceindex]].__id__,entry[0],entry[1],entry[2],entry[3])
			faceindex = faceindex + 1
		photoindex = photoindex + 1

if __name__ == '__main__':
	main()
