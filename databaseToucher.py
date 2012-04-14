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
	path = os.getcwd() +"\\Databases\\people.db"
	print path + "\n"
	db=Base(path)
	try:
		db.open()


		for field in db.fields:
			print field,db.fields[field]

		for record in db:
			print record
	except IOError:
		print "no database there.."

if __name__ == '__main__':
    main()
