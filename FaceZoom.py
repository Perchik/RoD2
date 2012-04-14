#!/usr/bin/python
# -*- coding: utf-8 -*-

# facezoom.py

import wx
import math
import time
theFace = None
duration = 4. #1 second
steps = 20
class Face():
	#defines the region we care about
	def __init__(self, x,y,width,height):
		self.x=x
		self.y=y
		self.width = width
		self.height = height
		
	def fitAspectRatio(self,ratio):
		#fits the face we care about into a region the same ratio of the main image
		if(ratio==1):
			if(self.height > self.width):
				print (self.height-self.width)
				margin = math.floor((self.height-self.width)/2)
				print "sqaure margin is ", margin
				self.width=self.width + 2*margin 
				self.x = self.x-margin
			elif(self.width > self.height):
				margin = math.floor((self.width-self.height)/2)
				self.height = self.height + 2*margin
				self.y = self.y-margin
		if(self.height*ratio < self.width): #need to go wider
			print "wider margin is ",(self.height*ratio - self.width)/2
			margin = math.floor((self.height*ratio - self.width)/2)
			self.width = self.width + 2*margin
			self.x=self.x-margin
		elif(self.height*ratio > self.width): #need to get higher
			print "higher margin is " ,(self.height/ratio - self.height)/2
			margin = math.floor((self.width/ratio - self.height)/2)
			self.height = self.height + 2*margin
			self.y=self.y-margin
		#print "height:",self.height," width:",self.width, " x ", self.x, " y " , self.y
	def getRect(self):
		return wx.Rect(self.x, self.y, self.height, self.width)
		
class MainForm(wx.Frame):
	""" The main form"""
	def __init__(self, *args, **kw):
		super(MainForm, self).__init__(*args,**kw)
		self.InitUI()
	
	def InitUI(self):
		main_panel = wx.Panel(self)
		
		load_btn = wx.Button(main_panel,label="Load", pos=(20,20))
		load_btn.Bind(wx.EVT_BUTTON, self.loadImage)
	
		zoomin_btn = wx.Button(main_panel, label="Zoom In", pos=(20,60))
		zoomin_btn.Bind(wx.EVT_BUTTON, self.zoomIn)
		
		transit_btn = wx.Button(main_panel, label="Transit", pos= (20,100))
		transit_btn.Bind(wx.EVT_BUTTON, self.transit) 
		
		zoomout_btn = wx.Button(main_panel, label="Zoom Out", pos = (20, 140 ))
		zoomout_btn.Bind(wx.EVT_BUTTON, self.zoomOut)
		
		picture_pane = wx.Panel(main_panel, pos= (140,20))
		picture_pane.SetBackgroundColour("Green")
		picture_pane.SetSize((500,500))
		
		self.picture_box = wx.StaticBitmap(main_panel, pos=(140,20))
		self.picture_box.SetSize((500,500))
		
		self.SetSize((800,600))
		self.Show(True)

	def loadImage(self,e):
		#load in an image
		self.bitmap = wx.EmptyBitmap(1,1)
		self.bitmap.LoadFile("img2.png",wx.BITMAP_TYPE_ANY)
		self.img = wx.ImageFromBitmap(self.bitmap)
		self.picture_box.SetBitmap(self.bitmap)
		theFace.fitAspectRatio( self.img.GetSize()[0]/self.img.GetSize()[1])
	
	def zoomIn(self,e):
		currZoom = wx.Rect(0,0,500,500)
		newZoom = currZoom
				
		faceRect = theFace.getRect()
		leftMargin = math.fabs( (faceRect.left-currZoom.left) / steps)
		rightMargin = math.fabs( (currZoom.right - faceRect.right) / steps )
		topMargin = math.fabs( (currZoom.top - faceRect.top) / steps )
		bottomMargin = math.fabs( (faceRect.bottom-currZoom.bottom)/steps )
		#print leftMargin, rightMargin, topMargin, bottomMargin
		
		
		step=steps
		for i in range(steps):
			leftMargin = math.fabs( (faceRect.left-currZoom.left) / step)
		#	rightMargin = math.fabs( (currZoom.right - faceRect.right) / step )
		#	topMargin = math.fabs( (currZoom.top - faceRect.top) / step )
		#	bottomMargin = math.fabs( (faceRect.bottom-currZoom.bottom)/step )
			print(leftMargin)
			newZoom.x = leftMargin
		#	newZoom.y = topMargin
		#	newZoom.width = 500 - leftMargin - rightMargin
		#	newZoom.height = 500 - topMargin - bottomMargin
			newZoom.y =0
			newZoom.width =500-leftMargin
			newZoom.height=500
			
			hscale = 500.0/newZoom.width
			vscale = 500.0/newZoom.height
			self.img= self.img.GetSubImage(newZoom)
			self.img.Rescale(500,500)
			self.picture_box.SetBitmap(wx.BitmapFromImage(self.img))
			time.sleep(duration/steps)
			step-=1
	
	def transit(self,e):
		pass
	
	def zoomOut(self, e):
		pass
	

if __name__ == '__main__':
	theFace = Face(50.0,50.0,200.0,200.0)
	
	ex= wx.App()
	MainForm(None)
	ex.MainLoop()