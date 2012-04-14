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
	facesDB=Base(os.getcwd() +"\\Databases\\faces.db")
	peopleDB=Base(os.getcwd()+"\\Databases\\people.db")
	try:
		facesDB.open()
		peopleDB.open()

##  		results = facesDB.select()
##		results = results.sort_by("+person")
##		for result in results: print result.thumbnail

		for human in peopleDB:
			result = facesDB.select(['thumbnail'],pid=human.__id__)[0].thumbnail
			print result
	except IOError:
		print "no database there.."

if __name__ == '__main__':
    main()
