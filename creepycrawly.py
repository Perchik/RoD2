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
#try:
#	imagesDB.open()
#except IOError:
	#imagesDB.create(('title',str),("url",str),("score",float),("file",str ))
imagesDB.create(('title',str),("url",str),("score",float),("fileloc",str ), mode="override")

for i in range(1,100):#pages on the website
	print "ripping page " + str(i)
	page = urllib2.urlopen("<http://www.dpchallenge.com/challenge_results.php?CHALLENGE_ID=1005&page="+str(i)+">")
	rawHtml = page.read()
	anchors = SoupStrainer("a", {'class':'i'})
	soup = BeautifulSoup(rawHtml, parse_only=anchors)
	for a in soup:
		url ="http://www.dpchallenge.com"+str(a['href'])
		title=unicodedata.normalize('NFKD',a.string).encode('ascii','ignore')
		imagesDB.insert(title, str(url), 0.0, "")



imgNum=0
records = imagesDB()
for record in imagesDB():
	print "working on img" + str(imgNum)
	try:
		imagePage = urllib2.urlopen(str(record.url)).read()
		img_soup=BeautifulSoup(imagePage)


		for child in img_soup.find(id="img_container").contents:
				if child.has_key('alt'):
					imagesDB.update(record,url=str(child['src']))

		tag = img_soup.find(text=re.compile("commenters"))
		record.update(score=float(tag.next_element))

		img_url = record.url
		img_req = Request(img_url)
		ext=os.path.splitext(img_url)[1]
		try:
				f = urlopen(img_req)
				imgFile='%0*d' % (6,imgNum)
				imgFile=os.getcwd()+"\\Images\\training\\" + imgFile + ext
				local_file = open(imgFile,"wb")
				local_file.write(f.read())
				local_file.close()
				record.update(fileloc=imgFile)

		except HTTPError, e:
				print "HTTP Error:",e.code , url
		except URLError, e:
				print "URL Error:",e.reason , url

		records = imagesDB().sort_by("+__id__")
	except:
		pass
	imgNum+=1

errorLog = open("errLog.txt","w")
badRecords = imagesDB(score=0.0)
for rec in badRecords:
	f.write(rec)

print "Done"
