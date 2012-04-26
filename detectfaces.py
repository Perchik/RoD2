# Lauren Cairco
# Spring 2012
# CPSC 863
# detectfaces.py
# Face detection and clustering for replication of Reliving on Demand paper

# Given a list of photos, detects all the faces in them and attempts to cluster
# the faces so that the faces of each individual end up in their own cluster.
# Several functions are currently unused but left in for historical purposes
# to show the various methods we tried.

from ctypes import byref
import cv2
import cv2.cv as cv
import numpy
from scipy.spatial.distance import *
from scipy.cluster.vq import kmeans2
from scipy.stats import anderson
from scipy.stats import zscore
from scipy.stats import tmean, tstd
from scipy.stats import norm, f
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn import preprocessing
import os
import mahotas.features
import random
from math import ceil, pow, log, log10, pi, sqrt

#Detects faces in the image using Haar cascades through OpenCV.
# Partially adapted from the following website:
# https://iss.jottit.com/python_opencv
def detectFaceInImage(imagename):
	#use the frontal face haar cascade
	cascade_name = "lib/haarcascades/haarcascade_frontalface_alt.xml"
	cascade = cv.Load(cascade_name);

	#load the image
	image = cv.LoadImage(imagename, cv.CV_LOAD_IMAGE_COLOR)

	#set parameters for the Haar cascade, most notably, a minimum face size
	image_scale = 0.5
	min_size = ( cv.Round(image_scale * image.height * 0.05), cv.Round(image_scale * image.width* 0.25) )
	haar_scale = 1.2
	min_neighbors = 3
	haar_flags = 0

	#reserve memory for a grayscale image
	gray = cv.CreateImage((image.width, image.height), 8, 1)

	#reserve memory for the scaled down image
	small_img = cv.CreateImage(( cv.Round (image.width/image_scale), cv.Round (image.height/image_scale)), 8, 1 )

	#convert original image to grayscale
	cv.CvtColor(image,gray,cv.CV_BGR2GRAY)

	#scale down the image
	cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

	#normalize the histogram
	cv.EqualizeHist(small_img,small_img)

	#reserve memory storage
	storage = cv.CreateMemStorage(0)

	#detect the faces in the image
	faces = cv.HaarDetectObjects(small_img, cascade, storage, haar_scale, min_neighbors, haar_flags, min_size)

	#the first item in the returned face regions will be the filename
	#the second item will be the x,y,w,h of the face within the image
	returnfaceregions = [imagename]
	if faces:
		for r in faces:
			returnfaceregions.append((int(r[0][0]*image_scale), int(r[0][1]*image_scale),int((r[0][2])*image_scale), int((r[0][3])*image_scale)))

	#return the list of files/faces
	return returnfaceregions

# use local binary patterns to reduce our faces into a one-dimensional feature vector for clustering
# also create thumbnails while we're at it
def faceLBP(faces):
	faceimages = []
	imglist = []
	fitted = []

	thumb = 0

	minFaces = []
	for faceset in faces:
		#load in an image--its name is held in the first array position
		bigimage = cv.LoadImage(faceset[0], cv.CV_LOAD_IMAGE_COLOR)
		#the rest of the array is all face rectangles
		faceset = faceset[1:]

		#get all the face subimages
		append = False
		if len(faceset) > len(minFaces):
			print 'hi',len(faceset)
			minFaces = []
			append = True
			
		for faceregion in faceset:
			#get the subrectangle
			subimage = cv.GetSubRect(bigimage, faceregion)
			#save a thumbnail
			thumbnail = cv.CreateImage((100,100), cv.IPL_DEPTH_8U,3)
			cv.Resize(subimage, thumbnail, cv.CV_INTER_LINEAR)
			cv.SaveImage(os.getcwd()+"//Images//thumbnails//th" + str(thumb) + ".jpg", thumbnail)
			imglist.append("th" + str(thumb) + ".jpg")
			thumb = thumb + 1
			faceimages.append(subimage)

			#reserve memory for a grayscale image
			gray = cv.CreateImage((subimage.width, subimage.height), 8, 1)
			#reserve memory for the scaled down image
			smallimage = cv.CreateImage((200,200), 8, 1 )

			#convert original image to grayscale and then scale down
			cv.CvtColor(subimage,gray,cv.CV_BGR2GRAY)
			cv.Resize(gray, smallimage, cv.CV_INTER_LINEAR)

			#local binary pattern each little section of it and then append together for the feature
			patchsize = 20
			wIterator = 0
			hIterator = 0
			feature = []

			for wIterator in range(10):
				for hIterator in range(10):
					section = cv.GetSubRect(smallimage,(wIterator * patchsize, hIterator * patchsize, patchsize, patchsize))
					img = numpy.asarray(section[:,:])
					#use a library for local binary pattern
					lbpvector = mahotas.features.lbp(img,1,8)
					#append this section's histogram onto all the others
					feature.extend(lbpvector)
			#fitted is the array of all the feature vectors
			fitted.append(feature)
			if append:
				minFaces.append(feature)


	#print minFaces
	#print len(minFaces)
	#print numpy.asarray(minFaces)
	return faceimages, fitted, imglist, minFaces

#projects a onto b, returning the scalar quantity
#used as a part of g-means clustering
def vectorProject(a,b):
	abdot = numpy.vdot(a,b)
	blensq =pow(numpy.linalg.norm(b), 2)
	return float(abdot)/float(blensq)

# g-means clustering
def gMeansCluster(samples, minFaces):
	clusters = []

	nclusters = len(minFaces)
	print "len",len(minFaces)
	testFails = True
	centers = []
	labels = []

	#run kmeans clustering
	while testFails:
		if nclusters == len(minFaces):
			clusterer = KMeans(k=len(minFaces),init=numpy.asarray(minFaces),n_init=1)
			#centers, labels = kmeans2(numpy.asarray(samples),k=1)
		else:
			clusterer = KMeans(k=len(centers),init=numpy.asarray(centers),n_init=1)
			#centers, labels = kmeans2(numpy.asarray(samples),k=nclusters,minit=numpy.asarray(centers))

		clusterer.fit(samples)
		labels = clusterer.labels_
		centers = clusterer.cluster_centers_

		newcenters = []

		#initialize two centers
		for i in range(len(centers)):
			center = centers[i]
			subsamples = []
			for j in range(len(labels)):
				if labels[j] == i:
					subsamples.append(samples[j])

			if len(subsamples) > 1:
				#cluster data
				#first find eigenvalue/eigenvector
				u,s,v = numpy.linalg.svd(numpy.asmatrix(subsamples))
				eigen = s[0]
				vector = v[:,0]

				trialcenters = []
				diff = vector * sqrt(2*eigen / pi)
				j = 0
				temp = []
				for j in range(len(diff[:,0])):
					temp.append(diff[j,0])

				trialcenters.append((center+temp))
				trialcenters.append((center-temp))

				newclusterer = KMeans(k=2, init=numpy.asarray(trialcenters),n_init=1)
				newclusterer.fit(subsamples)
				labels = clusterer.labels_
				centers = clusterer.cluster_centers_

				v = trialcenters[1]-trialcenters[0]
				onedim = []
				#project the samples onto v
				for x in subsamples:
					onedim.append(vectorProject(x,v))

				#perform statistical test
				a2, critical, sig = anderson(onedim)
				#print critical, sig
				n = len(onedim)
				corrected = a2 * (1+ 4.0/n  - 25.0 / (pow(n,2)))
				#print "a2 corr'",str(corrected)
				#print critical

				#if we're above the critical value keep the new centers
				if corrected > critical[-2]:
					newcenters.extend(trialcenters)
				#otherwise keep the old center
				else:
					newcenters.append(center)
			else:
				newcenters.append(center)

		centers = newcenters

		if nclusters == len(newcenters) or nclusters == len(samples):
			testFails = False
		else:
			nclusters = len(newcenters)
		print nclusters

	return labels, nclusters


#################################
#   alternate implementations   #
#################################

# use the eigenfaces approach to make a feature vector to classify faces
def facePCA(faces):
	#build an array where every row represents a face
	facesamples = []
	faceimages = []
	imglist = []

	thumb = 0

	for faceset in faces:
		#load in an image--its name is held in the first array position
		bigimage = cv.LoadImage(faceset[0], cv.CV_LOAD_IMAGE_COLOR)
		#the rest of the array is all face rectangles
		faceset = faceset[1:]
		for face in faceset:
			print face

		#get all the face subimages
		for faceregion in faceset:
			#get the subrectangle
			subimage = cv.GetSubRect(bigimage, faceregion)
			#save a thumbnail
			thumbnail = cv.CreateImage((100,100), cv.IPL_DEPTH_8U,3)
			cv.Resize(subimage, thumbnail, cv.CV_INTER_LINEAR)
			cv.SaveImage(os.getcwd()+"//Images//thumbnails//th" + str(thumb) + ".jpg", thumbnail)
			imglist.append("th" + str(thumb) + ".jpg")
			thumb = thumb + 1
			faceimages.append(subimage)

			#reserve memory for a grayscale image
			gray = cv.CreateImage((subimage.width, subimage.height), 8, 1)
			#reserve memory for the scaled down image, we choose 300x300
			smallimage = cv.CreateImage((100,100), 8, 1 )

			#convert original image to grayscale and then scale down
			cv.CvtColor(subimage,gray,cv.CV_BGR2GRAY)
			cv.Resize(gray, smallimage, cv.CV_INTER_LINEAR)

			#flatten the image into a vector
			A = cv.GetMat(smallimage)
			vector = []
			for i in range(smallimage.height):
				for j in range(smallimage.width):
					vector.append(A[i,j])
			facesamples.append(vector)

	#subtract the mean face from each row
	avgvector = facesamples[0]
	for i in range (1,len(facesamples)):
		avgvector = numpy.asarray(avgvector) + numpy.asarray(facesamples[i])

	for field in avgvector:
		field = field / (len(facesamples) * 1.0)

	for face in facesamples:
		face = numpy.asarray(face) - numpy.asarray(avgvector)

	#now we have all the face samples in a gigantic array
	#do PCA on them
	pca = PCA(n_components = 0.90)
	pca.fit(facesamples)
	fitted = pca.transform(facesamples)

	return faceimages, fitted, imglist

# a simplified, purely variance based thresholding process to determine
# how many clusters to used. replaced by gMeansCluster
def varianceMeansCluster(samples):
	clusters = []

	nclusters = 0
	threshold = 0.01
	highvariance = 0
	totalvariance = 0
	highvariancepercent = 1
	percentthreshold = .20

	clusters = {}
	oldpercent = 0
	delta = 1

	nclusters = 0
	while delta > threshold  and nclusters < len(samples):
		nclusters = nclusters + 1

		#cluster
		clusterer = KMeans(k=nclusters)
		clusterer.fit(samples)
		labels = clusterer.labels_
		centers = clusterer.cluster_centers_

		#find the variance within each cluster
		variance = [0 for x in range(nclusters)]
		pointcount = [0 for x in range(nclusters)]
		for i in range(len(labels)):
			pointcount[labels[i]] = pointcount[labels[i]] + 1

			distance = sqeuclidean(centers[labels[i]],samples[i])
			variance[labels[i]] = variance[labels[i]] + distance * distance

		#print("nclusters is " + str(nclusters))
		highvariance = 0
		for i in range(nclusters):
			variance[i] = variance[i] / (1.0 * pointcount[i])
			if variance[i] > highvariance:
				highvariance = variance[i]
			if nclusters == 1:
				totalvariance = highvariance

		highvariancepercent = 1.0 * highvariance / totalvariance
		delta = numpy.abs(oldpercent-highvariancepercent)
		oldpercent = highvariancepercent
		print delta
		print highvariancepercent
		print labels

	return labels, nclusters

# shows the faces in the clusters--used to check our work
def visualizeResults(samples,labels,nclusters):
	clusters = [[] for x in range(nclusters)]
	for i in range(len(labels)):
		#print samples[i]
		clusters[labels[i]].append(samples[i])

	for i in range(nclusters):
		print "cluster" + str(i)
		for picture in clusters[i]:
			cv.ShowImage("cluster" + str(i),picture)
			cv.WaitKey()