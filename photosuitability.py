#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Lauren
#
# Created:     16/04/2012
# Copyright:   (c) Lauren 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from buzhug import Base
import os
from scipy.spatial.distance import euclidean
import Bases as DB

def photoSuitability(eventID, criteria, value):
	order = []
##	try:
##		eventsDB = Base(os.getcwd() + "\\Databases\\events.db")
##		peopleDB = Base(os.getcwd() + "\\Databases\\people.db")
##			 = Base(os.getcwd() + "\\Databases\\locations.db")
##			 = Base(os.getcwd() + "\\Databases\\photos.db")
##		facesDB = Base(os.getcwd() + "\\Databases\\faces.db")
##
##		eventsDB.open()
##		peopleDB.open()
##		placesDB.open()
##		photosDB.open()
##		facesDB.open()
##
##	except IOError as e:
##		print "Error opening database", e 
##		return order


	if criteria == "time" or criteria == "location":
		photos = DB.photos.select(eventid=eventID).sort_by("+aestheticscore")
		for photo in photos:
			order.append(photo.__id__)
		order.reverse()

	elif criteria == "people":
		#print 'hi'
		photos = DB.photos.select(eventid=eventID)
		scores = []
		for photo in photos:
			#calculate r1 through r5
			presentInImage = 0
			faceSize = 0
			faceCentroid = 100

			aesthetic = photo.aestheticscore
			faces = DB.faces.select(photoid=photo.__id__)
			faceRatio = (1.0 * len(value)) / len(faces)
			for face in faces:
				for pid in value:
					if face.personid == pid:
						presentInImage = 1
						if face.w * face.h > faceSize:
							faceSize = face.w * face.h

						facecenter = (face.x + face.w / 2, face.y + face.h / 2)
						imgcentroid = (photo.width / 2, photo.height/2)
						if abs(euclidean(facecenter,imgcentroid)) < faceCentroid:
							faceCentroid = abs(euclidean(facecenter,imgcentroid))
			#print presentInImage, faceSize, faceCentroid, faceRatio, aesthetic
			scores.append(([presentInImage, faceSize, faceCentroid, faceRatio, aesthetic], photo.__id__))

		highscores = [0.01,0.01,0.01,0.01]
		for score in scores:
			for i in range(1,len(score[0])):
				if highscores[i-1] < score[0][i]:
					highscores[i-1] = score[0][i]

		composites = []
		for score in scores:
			for i in range(1,len(score[0])):
				score[0][i] = (1.0 * score[0][i]) / (highscores[i-1])
			compositescore = score[0][0] * (score[0][1] + -score[0][2] + score[0][3] + score[0][4])
			composites.append((compositescore, score[1]))

		composites.sort()
		composites.reverse()
		print composites
		for score in composites:
			order.append(score[1])
		
	return order



def main():
    print photoSuitability(3, "people", [3])

if __name__ == '__main__':
    main()
