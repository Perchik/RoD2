# Lauren Cairco
# Spring 2012
# CPSC 863
# detectfaces.py


# Adapted from the following website:
# https://iss.jottit.com/python_opencv
# Notable changes include:
# - Updating to work with the new version of opencv
# - Changing the minimum face size to 100x100 for improved accuracy and performance

from ctypes import byref
import cv2
import cv2.cv as cv
#import pylab
import numpy
from scipy.spatial.distance import euclidean
from sklearn.decomposition import PCA
from sklearn.cluster import MiniBatchKMeans, KMeans
import os
import mahotas.features

def detectFaceInImage(imagename):
	#use the frontal face haar cascade
	cascade_name = "lib/haarcascades/haarcascade_frontalface_alt.xml"
	cascade = cv.Load(cascade_name);

	#load the image
	image = cv.LoadImage(imagename, cv.CV_LOAD_IMAGE_COLOR)

	#we're going to say that the minimum face size is 1/8 of the little image's width and height
	#I realize this will cut out some faces but it should get the most salient ones
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
	returnfaceregions = [imagename]
	if faces:
		for r in faces:
			returnfaceregions.append((int(r[0][0]*image_scale), int(r[0][1]*image_scale),int((r[0][2])*image_scale), int((r[0][3])*image_scale)))

	return returnfaceregions

def faceLBP(faces):
	#build an array where every row represents a face
	facesamples = []
	faceimages = []
	imglist = []
	fitted = []

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

			tinyimg = cv.CreateImage((100,100),cv.IPL_DEPTH_32F, 3)
			cv.ConvertScale(thumbnail, tinyimg, 1/255.0)
			#cv.Resize(subimage, tinyimg, cv.CV_INTER_LINEAR)

			#reserve memory for a grayscale image
			gray = cv.CreateImage((subimage.width, subimage.height), 8, 1)
			#reserve memory for the scaled down image, we choose 300x300
			smallimage = cv.CreateImage((200,200), 8, 1 )

			#convert original image to grayscale and then scale down
			cv.CvtColor(subimage,gray,cv.CV_BGR2GRAY)
			cv.Resize(gray, smallimage, cv.CV_INTER_LINEAR)

			#local binary pattern each little section of it and then append together for the feature
			patchsize = 25
			wIterator = 0
			hIterator = 0
			feature = []
			for wIterator in range(8):
				for hIterator in range(8):
					section = cv.GetSubRect(smallimage,(wIterator * patchsize, hIterator * patchsize, patchsize, patchsize))
					img = numpy.asarray(smallimage[:,:])
					#print img
					lbpvector = mahotas.features.lbp(img,1,8)
					feature.extend(lbpvector)
					print wIterator, hIterator
			fitted.append(feature)

			# img = numpy.asarray(smallimage)
			# lbpvector = mahotas.features.lbp(numpy.asarray(subimage),1,8)
			# facesamples.append(lbpvector)
			# print lbpvector
			# fitted.append(lbpvector)


	return faceimages, fitted, imglist



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

		#print facesamples

	#subtract the mean face from each row
	avgvector = facesamples[0]
	for i in range (1,len(facesamples)):
		avgvector = numpy.asarray(avgvector) + numpy.asarray(facesamples[i])

	for field in avgvector:
		field = field / (len(facesamples) * 1.0)

	for face in facesamples:
		face = numpy.asarray(face) - numpy.asarray(avgvector)

	#facesamples = numpy.asarray(facesamples).transpose()

	#now we have all the face samples in a gigantic array
	#do PCA on them
	pca = PCA(n_components = 0.90)
	pca.fit(facesamples)
	fitted = pca.transform(facesamples)

	return faceimages, fitted, imglist

def gMeansCluster(samples):
	clusters = []

	nclusters = 0
	threshold = 0.001
	highvariance = 0
	totalvariance = 0
	highvariancepercent = 0

	clusters = {}
	oldpercent = 0
	delta = 1

	while (delta > threshold and nclusters < len(samples)):
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
			distance = euclidean(centers[labels[i]],samples[i])
			variance[labels[i]] = variance[labels[i]] + distance * distance

		print("nclusters is " + str(nclusters))
		highvariance = 0
		for i in range(nclusters):
			variance[i] = variance[i] / (1.0 * pointcount[i])
			#print (str(variance[i]) + " ",)
			if variance[i] > highvariance:
				highvariance = variance[i]
			if nclusters == 1:
				totalvariance = highvariance

		highvariancepercent = highvariance / totalvariance
		delta = numpy.abs(oldpercent-highvariancepercent)
		oldpercent = highvariancepercent
		print delta
		print highvariancepercent
		print labels

	return labels, nclusters

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