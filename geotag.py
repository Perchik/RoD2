#haversine distance based on
# http://code.activestate.com/recipes/576779-calculating-distance-between-two-geographic-points/

import urllib
import xml.dom.minidom
from xml.dom.minidom import Node
import math

def findlocation(location):
	url = "http://where.yahooapis.com/geocode?location="+location+"&appid=dj0yJmk9YjBqbWRNaHJCejM4JmQ9WVdrOWIyeFhlblppTjJFbWNHbzlOemd6T0RZeU1qWXkmcz1jb25zdW1lcnNlY3JldCZ4PTEz"
	data = urllib.urlopen(url).read()
	
	#parse xml to get lat long
	lat = 0
	long = 0
	possibilities = []
	doc = xml.dom.minidom.parseString(data)
	nodes = doc.getElementsByTagName("Result")
	for node in nodes:
		newnode = {}
		try:
			newnode["lat"] = node.getElementsByTagName("latitude")[0].childNodes[0].nodeValue
			newnode["long"]  = node.getElementsByTagName("longitude")[0].childNodes[0].nodeValue
		except:
			newnode["lat"] = ""
			newnode["long"] = ""
			
		try:
			newnode["address"] = node.getElementsByTagName("line1")[0].childNodes[0].nodeValue
		except:
			newnode["address"] = ""
		
		try:
			newnode["city"]  = node.getElementsByTagName("city")[0].childNodes[0].nodeValue
		except:
			newnode["city"] = ""
		
		try:
			newnode["state"] = node.getElementsByTagName("state")[0].childNodes[0].nodeValue
		except:
			newnode["state"] = ""
		try:
			newnode["country"] = node.getElementsByTagName("country")[0].childNodes[0].nodeValue
		except:
			newnode["country"] = ""
			
		try:
			newnode["quality"] = node.getElementsByTagName("quality")[0].childNodes[0].nodeValue
		except:
			newnode["quality"] = ""
		possibilities.append(newnode)
	
	#if there's just one possibility return it
	if len(possibilities) == 1:
		return location, possibilities[0]["lat"], possibilities[0]["long"]
		
	#otherwise disambiguate
	else:
		#if there were no results, ask the user if they'd like to try another name
		#if len(possibilities) == 0:
		#ask the user which they meant (TO DO)
		return location, possibilities[0]["lat"], possibilities[0]["long"]
		
	
def finddistance(loc1,loc2):
	print loc1
	print loc2
	start_long = math.radians(float(loc1[0]))
	start_latt = math.radians(float(loc1[1]))
	end_long = math.radians(float(loc2[0]))
	end_latt = math.radians(float(loc2[1]))
	d_latt = end_latt - start_latt
	d_long = end_long - start_long
	a = math.sin(d_latt/2)**2 + math.cos(start_latt) * math.cos(end_latt) * math.sin(d_long/2)**2
	c = 2 * math.atan2(math.sqrt(a),  math.sqrt(1-a))
	return 6371 * c *  0.621371192


# name1, lat1, long1 = findlocation("Blacksburg, VA")
# name2, lat2, long2 = findlocation("Washington, DC")

# print name1, lat1, long1
# print name2, lat2, long2
# print finddistance((lat1, long1),(lat2,long2))