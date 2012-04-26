# Lauren Cairco
# CPSC 863
# Spring 2012
# timecluster2.py
# Time clustering for Reliving on Demand replication
# Follows the time clustering techniques presented in A. Loui & A. Savakis, Automated Event Clustering and Quality Screening
# of Consumer Pictures for Digital Albuming, IEEE Transactions on Multimedia, 2003.
#
# We don't do quality filtering because the aesthetic scoring should take care of that.
# We also don't do color histogram techniques for event refinement yet.

import os
import pyexiv2
import time
from datetime import datetime, timedelta, date
import numpy
import copy
import scipy.cluster.vq
import math
import re

#Roughly convert the timestamps to minutes
def minuteConvert(time):
	time = datetime.strptime(time, "%Y:%m:%d %H:%M:%S")
	minutes = 60 * (24 * (365 *  time.year + 30 * ( time.month - 1) + ( time.day - 1)) +  time.hour) +  time.minute
	return minutes

def convertToMinutes(timestamps):
	minuteTimestamps = []
	for picture in timestamps:
		#get the deltas in minutes
		timedelta = minuteConvert(picture[0])
		minuteTimestamps.append((timedelta, picture[1]))
	return minuteTimestamps

def timeDifferenceHistogram(minuteTimestamps):
	#calculate time differences
	timedeltas = [(0,minuteTimestamps[0][1])]
	for i in range(1, len(minuteTimestamps)):
		timedeltas.append((minuteTimestamps[i][0] - minuteTimestamps[i-1][0],minuteTimestamps[i][1]))

	#sort
	timedeltas.sort()
	return timedeltas

def scaleTimestamp(minutes):
	#if it's less than 1/4 of a day
	if minutes < .25 * (24 * 60):
		return minutes
	#if less than one day
	elif minutes < (24 * 60):
		return math.sqrt(360 * (minutes - 270)) + 180
	#if less than one week
	elif minutes < (24 * 60) * 7:
		return math.pow(1440 * (minutes - 1078) + 588, (5.0/12.0))
	#if less than one month
	elif minutes < (24 * 60) * 30:
		return math.pow(10080 * (minutes - 7880) + 1197, (1.0/3.0))
	#if greater than one month
	else:
		return math.pow(43200 * (minutes - 38815) + 1788, (1.0/4.0))

def twoMeansCluster(deltas):
	#first we have to transform the data
	transformedDeltas = []
	for item in deltas:
		transformedDeltas.append(scaleTimestamp(item[0]))

	#then we 2-means cluster it
	initCenters = numpy.array((0, transformedDeltas[-1]))
	centroids, labels = scipy.cluster.vq.kmeans2(numpy.array(transformedDeltas), initCenters, minit='matrix')

	#return the dividing line
	return labels.tolist().index(1)


def eventCluster(filelist):
	filelist.sort()

	#put all the timestamps into a list
	timestamps = []
	orderedtimestamps = []
	i = 0
	for file in filelist:
		try:
			metadata=pyexiv2.ImageMetadata(file)
			metadata.read()
			timestamp = metadata['Exif.Image.DateTime'].value.strftime('%Y:%m:%d %H:%M:%S')
		except:
			timestamp = time.strftime('%Y:%m:%d %H:%M:%S', time.gmtime(os.path.getctime(file)))
		timestamps.append((timestamp,file))
		orderedtimestamps.append((file, timestamp))
		i = i + 1

	#sort according to timestamp
	timestamps.sort()
	#print timestamps
	orderedtimestamps.sort()

	#make the timedifference histogram and cluster to find the beginning deltas
	minuteTimestamps = convertToMinutes(timestamps)
	timedeltas = timeDifferenceHistogram(minuteTimestamps)
	boundary = twoMeansCluster(timedeltas)

	stoplist = []
	i = 0
	for i in range(boundary, len(timedeltas)):
		stoplist.append(timedeltas[i][1])

	stoplist.sort()

	#tag the photos based on their event id and their location
	i = 0
	matchobj = re.match(r'^(.*\\)*(.*)\\(.*)\.((jpg)|(JPG))$', filelist[0])
	textlabel = matchobj.group(2)
	unique = []
	labels = []
	j = 0

	for j in range(len(filelist)):
		if i < len(stoplist) and filelist[j] == stoplist[i]:
			matchobj = re.match(r'^(.*\\)*(.*)\\(.*)\.((jpg)|(JPG))$',filelist[j])
			textlabel = matchobj.group(2)
			evtLabel = (i,textlabel)
			unique.append(evtLabel)
			i = i + 1
		labels.append((evtLabel[0], orderedtimestamps[j][1]))

	return labels, unique



