from buzhug import Base
import os

photos = None
faces=None
people = None
events=None
places=None



def init():
	global photos
	global faces
	global people
	global events
	global places
	photos = Base(os.getcwd()+ "\\Databases\\photos.db")
	faces = Base(os.getcwd() +"\\Databases\\faces.db")
	people = Base(os.getcwd()+"\\Databases\\people.db")
	events = Base(os.getcwd()+"\\Databases\\events.db")
	places = Base(os.getcwd()+"\\Databases\\locations.db")

def open():
	global photos
	global faces
	global people
	global events
	global places
	photos.open()
	faces.open()
	people.open()
	events.open()
	places.open()
	
def close():
	global photos
	global faces
	global people
	global events
	global places
	photos.close()
	faces.close()
	people.close()
	events.close()
	places.close()
