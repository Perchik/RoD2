import sys
import os
sys.path.append(os.getcwd()+"\\lib")

from bs4 import BeautifulSoup, SoupStrainer
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from buzhug import Base
import re
import unicodedata

num_imgs=0

imagesDB = Base(os.getcwd()+"\\Databases\\training_images.db")
try:
	imagesDB.open()
except IOError:
	print "creaitng imabegase"
	imagesDB.create(('title',str),("url",str),("score",float),("fileloc",str ))
##imagesDB.create(('title',str),("url",str),("score",float),("fileloc",str ), mode="override")

challenges = {(1005,110),(1154,44),(430,82),(296,52), (1412,11),(980,52),(616,70),(536,67),(707,64),(431,61),(565,61)}
##challenges = {(430,1),(1154,1)}
for challenge in challenges:
	print "challenge #",challenge[0]
	for i in range(1,challenge[1]+1):#pages on the website
		print "ripping page " + str(i)
		page = urllib2.urlopen("<http://www.dpchallenge.com/challenge_results.php?CHALLENGE_ID="+str(challenge[0])+"&page="+str(i)+">")
		rawHtml = page.read()
		anchors = SoupStrainer("a", {'class':'i'})
		soup = BeautifulSoup(rawHtml, parse_only=anchors)
		for a in soup:
			url ="http://www.dpchallenge.com"+str(a['href'])
			if(a.string != None):
				title=unicodedata.normalize('NFKD',a.string).encode('ascii','ignore')
				imagesDB.insert(title, str(url), 0.0, "")

	records = imagesDB().sort_by("+__id__")
	for record in imagesDB():
		print "working on image ",record.__id__
		try:
			imagePage = urllib2.urlopen(str(record.url)).read()
			img_soup=BeautifulSoup(imagePage)
	
			for child in img_soup.find(id="img_container").contents:
					if child.has_key('alt') and child['alt']==record.title: 
						imagesDB.update(record,url=str(child['src']))
						break
	
			tag = img_soup.find(text=re.compile("all users"))
			record.update(score=float(tag.next_element))
	
			img_url = record.url
			img_req = Request(img_url)
			ext=os.path.splitext(img_url)[1]
			try:
					f = urlopen(img_req)
					imgFile='%0*d' % (6,record.__id__)
					imgFile=os.getcwd()+"\\Images\\training\\" + imgFile + ext
	
					local_file = open(imgFile,"wb")
					local_file.write(f.read())
					local_file.close()
					record.update(fileloc=imgFile)	
			except HTTPError, e:
					print "HTTP Error:",e.code , url
			except URLError, e:
					print "URL Error:",e.reason , url
				
			##records = imagesDB().sort_by("+__id__")
		except:
			pass
for rec in imagesDB().sort_by("+__id__"):
	print rec
imagesDB.close()
print "Done"
