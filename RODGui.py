#-------------------------------------------------------------------------------
# Name:	Reliving on demand GUI
# Purpose:
#
# Author:      PSDUKES
#
# Created:     10/04/2012
# Copyright:   (c) PSDUKES 2012
#-------------------------------------------------------------------------------




#-------------------------------------------------------------------------------
#			LIBRARIES!!!!
#-------------------------------------------------------------------------------
import sys
import wx
import os
from buzhug import Base
from wx.lib.buttons import GenBitmapButton, GenBitmapToggleButton
from PIL import Image
import math
import time
import orderevents as OE
import photosuitability as PS
#-------------------------------------------------------------------------------
#		   System Constants
#-------------------------------------------------------------------------------

#Menu item IDs:
menu_PLAY	= wx.NewId() #Show menu items
menu_STOP	= wx.NewId()
menu_RW	  = wx.NewId()
menu_FF	  = wx.NewId()

menu_ABOUT       = wx.NewId() #help menu item

#Button IDs:
play_btn = wx.NewId()
back_btn = wx.NewId()
rw_btn = wx.NewId()
ff_btn = wx.NewId()
next_btn = wx.NewId()

#size of display frame, in pixels:
DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 1000

USE_BUFFERED_DC = True

#databases
eventsDB = Base(os.getcwd()+"\\Databases\\events.db")
locationsDB = Base(os.getcwd()+"\\Databases\\locations.db")
photosDB = Base(os.getcwd()+"\\Databases\\photos.db")
peopleDB = Base(os.getcwd()+"\\Databases\\people.db")
facesDB = Base(os.getcwd()+"\\Databases\\faces.db")

class BufferedWindow(wx.Window):
	
	"""
	
	A Buffered window class.
	
	To use it, subclass it and define a Draw(DC) method that takes a DC
	to draw to. In that method, put the code needed to draw the picture
	you want. The window will automatically be double buffered, and the
	screen will be automatically updated when a Paint event is received.
	
	When the drawing needs to change, you app needs to call the
	UpdateDrawing() method. Since the drawing is stored in a bitmap, you
	can also save the drawing to file by calling the
	SaveToFile(self, file_name, file_type) method.
	
	"""
	def __init__(self, *args, **kwargs):
		# make sure the NO_FULL_REPAINT_ON_RESIZE style flag is set.
		kwargs['style'] = kwargs.setdefault('style', wx.NO_FULL_REPAINT_ON_RESIZE) | wx.NO_FULL_REPAINT_ON_RESIZE
		print "e"
		wx.Window.__init__(self, *args, **kwargs)
		
		wx.EVT_PAINT(self, self.OnPaint)
		wx.EVT_SIZE(self, self.OnSize)
		
		# OnSize called to make sure the buffer is initialized.
		# This might result in OnSize getting called twice on some
		# platforms at initialization, but little harm done.
		self.OnSize(None)
		self.paint_count = 0
	
	def Draw(self, dc):
		## just here as a place holder.
		## This method should be over-ridden when subclassed
		pass
		
	def OnPaint(self, event):
		# All that is needed here is to draw the buffer to screen
		if USE_BUFFERED_DC:
		    dc = wx.BufferedPaintDC(self, self._Buffer)
		else:
		    dc = wx.PaintDC(self)
		    dc.DrawBitmap(self._Buffer, 0, 0)
		
	def OnSize(self,event):
		# The Buffer init is done here, to make sure the buffer is always
		# the same size as the Window
		#Size  = self.GetClientSizeTuple()
		Size  = self.ClientSize
		
		# Make new offscreen bitmap: this bitmap will always have the
		# current drawing in it, so it can be used to save the image to
		# a file, or whatever.
		self._Buffer = wx.EmptyBitmap(*Size)
		self.UpdateDrawing()
		
	def SaveToFile(self, FileName, FileType=wx.BITMAP_TYPE_PNG):
		## This will save the contents of the buffer
		## to the specified file. See the wxWindows docs for 
		## wx.Bitmap::SaveFile for the details
		self._Buffer.SaveFile(FileName, FileType)
	
	def UpdateDrawing(self):
		"""
		This would get called if the drawing needed to change, for whatever reason.
		
		The idea here is that the drawing is based on some data generated
		elsewhere in the system. If that data changes, the drawing needs to
		be updated.
		
		This code re-draws the buffer, then calls Update, which forces a paint event.
		"""
		dc = wx.MemoryDC()
		dc.SelectObject(self._Buffer)
		self.Draw(dc)
		del dc # need to get rid of the MemoryDC before Update() is called.
		self.Refresh()
		self.Update()
#-------------------------------------------------------------------------------
class PictureWindow(BufferedWindow):
	def __init__(self, *args,**kwargs ):
		## Any data the Draw() function needs must be initialized befrore calling
		## BufferedWindow.__init__, as it will call the Draw Function
		self.bmp =wx.EmptyBitmap(0,0)
		BufferedWindow.__init__(self, *args, **kwargs)
	def Draw(self, dc):
		dc.SetBackground(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)))
		##dc.SetBackground(wx.RED_BRUSH)
		dc.Clear()
		dc.DrawBitmap(self.bmp,0,0)
				
	def SetBitmap(self,bitmap):
		self.bmp=bitmap
		self.UpdateDrawing()
#-------------------------------------------------------------------------------
class MainFrame(wx.Frame):
	""" A frame for displaying pictures """
	# ===========================================
	# ==  Initialisation and Window Management ==
	# ===========================================
	def __init__(self, parent, id, title):
		""" Standard constructor.
		'parent', 'id' and 'title' are all passed to the standard wx.Frame
		constructor."""
		print "init display frame"
		wx.Frame.__init__(self, parent, id, title,style = wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("Reliving on Demand 2.0")
		self.SetSize((900,735))
	
		# ================
		# == Class vars ==
		# ================
		self.dirty = False
		self.currSelct = None
		self.showGen = self.getShow()
		self.isPaused = False
		self.playSpeed=3 #seconds
		self.show =[]

		#Setup our menu bar.
		menuBar = wx.MenuBar()

		self.fileMenu = wx.Menu()
		self.fileMenu.Append(wx.ID_NEW,    "New\tCtrl-N", "Create a new photo library")
		self.fileMenu.Append(wx.ID_OPEN,   "Open...\tCtrl-O", "Open an existing photo library")
		self.fileMenu.Append(wx.ID_CLOSE,  "Close\tCtrl-W")
		self.fileMenu.AppendSeparator()
		self.fileMenu.Append(wx.ID_SAVE,   "Save\tCtrl-S")
		self.fileMenu.Append(wx.ID_SAVEAS, "Save As...")
		self.fileMenu.AppendSeparator()
		self.fileMenu.Append(wx.ID_EXIT,    "Quit\tCtrl-Q")

		menuBar.Append(self.fileMenu, "File")

		self.showMenu = wx.Menu()
		self.showMenu.Append(menu_PLAY,     "Play\\PauseSpacebar")
		self.showMenu.Append(menu_FF,       "Fast Forward")
		self.showMenu.Append(menu_RW,       "Rewind")
		self.showMenu.Append(menu_STOP,     "Stop")

		menuBar.Append(self.showMenu, "Show")

		self.helpMenu = wx.Menu()
		self.helpMenu.Append(menu_ABOUT, "About Reliving on Demand...")

		menuBar.Append(self.helpMenu, "Help")

		self.SetMenuBar(menuBar)
		#Menu Bar end

		#Create our statusbar
		self.statusBar = self.CreateStatusBar(1,0)
		self.statusBar.SetStatusWidths([-1])
		self.statusBar.SetStatusText("Welcome to RoD 2.0")

		#Create a toolbar
		tsize = (15,15)
		self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)

		artBmp = wx.ArtProvider.GetBitmap
		self.toolbar.AddSimpleTool(
		    wx.ID_OPEN, artBmp(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize), "Open Library")
		self.toolbar.AddSimpleTool(
		    wx.ID_SAVE, artBmp(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, tsize), "Save Library")
		self.toolbar.AddSimpleTool(
		    wx.ID_SAVEAS, artBmp(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR, tsize),
		    "Save Library As...")

		#Create our tabbed pane
		self.selectorTabs = wx.Notebook(self, -1, style=0)
		self.peopleTab = wx.ScrolledWindow(self.selectorTabs, -1,style=wx.VSCROLL)
		self.placesTab = wx.Panel(self.selectorTabs, -1)
		self.eventsTab = wx.Panel(self.selectorTabs, -1)
		
		self.peopleTab.SetScrollRate(0,10)
		#create the display
	
		#self.topPanel.Bind(wx.EVT_SIZE, self.onSize)
		

		self.picture1 = PictureWindow(self,-1)
		self.picture2 = PictureWindow(self,-1)
		self.picture3 = PictureWindow(self,-1)
		self.picture4 = PictureWindow(self,-1)
		
		self.playTimer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.loadNextImage, self.playTimer)
		
		self.pictureControls = [self.picture1,self.picture2,self.picture3,self.picture4]
		
		#create control buttons
		self.backBtn= wx.BitmapButton(self,back_btn, wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\back.png",wx.BITMAP_TYPE_PNG), style=wx.NO_BORDER)
		self.backBtn.SetBitmapHover(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\back_hover.png",wx.BITMAP_TYPE_PNG))
		self.backBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\back_disabled.png",wx.BITMAP_TYPE_PNG))

		self.rwBtn= wx.BitmapButton(self, rw_btn, wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\rw.png",wx.BITMAP_TYPE_PNG), style=wx.NO_BORDER)
		self.rwBtn.SetBitmapHover(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\rw_hover.png",wx.BITMAP_TYPE_PNG))
		self.rwBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\rw_disabled.png",wx.BITMAP_TYPE_PNG))

		self.playIcon =wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\play.png",wx.BITMAP_TYPE_PNG)
		self.playIcon_hover =wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\play_hover.png",wx.BITMAP_TYPE_PNG)
		self.pauseIcon =wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\pause.png",wx.BITMAP_TYPE_PNG)
		self.pauseIcon_hover =wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\pause_hover.png",wx.BITMAP_TYPE_PNG)
		
		self.playBtn=wx.BitmapButton(self,play_btn,self.playIcon, style=wx.NO_BORDER)
		self.playBtn.SetBitmapHover(self.playIcon_hover)
		self.playBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\play_disabled.png",wx.BITMAP_TYPE_PNG))

		self.ffBtn= wx.BitmapButton(self,ff_btn, wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\ff.png",wx.BITMAP_TYPE_PNG), style=wx.NO_BORDER)
		self.ffBtn.SetBitmapHover(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\ff_hover.png",wx.BITMAP_TYPE_PNG))
		self.ffBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\ff_disabled.png",wx.BITMAP_TYPE_PNG))

		self.nextBtn= wx.BitmapButton(self,next_btn, wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\next.png",wx.BITMAP_TYPE_PNG), style=wx.NO_BORDER)
		self.nextBtn.SetBitmapHover(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\next_hover.png",wx.BITMAP_TYPE_PNG))
		self.nextBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\next_disabled.png",wx.BITMAP_TYPE_PNG))

		# Associate menu/toolbar items with their handlers.
		menuHandlers = [
		(wx.ID_NEW,    self.doNew),
		(wx.ID_OPEN,   self.doOpen),
		(wx.ID_CLOSE,  self.doClose),
		(wx.ID_SAVE,   self.doSave),
		(wx.ID_SAVEAS, self.doSaveAs),
		(wx.ID_EXIT,   self.doExit),


		(menu_PLAY,    self.doPlay),
		(menu_STOP,    self.doStop),
		(menu_RW,      self.doRewind),
		(menu_FF,      self.doFastForward),

		(menu_ABOUT, self.doShowAbout)]
		for combo in menuHandlers:
		    cid, handler = combo[:2]
		    self.Bind(wx.EVT_MENU, handler, id = cid)
		    if len(combo)>2:
				self.Bind(wx.EVT_UPDATE_UI, combo[2], id = cid)
			
			
		#associate buttons with their handlers
		buttonHandlers = [
		(back_btn, self.doBack),
		(rw_btn, self.doRewind),
		(play_btn, self.doPlay),
		(ff_btn, self.doFastForward),
		(next_btn, self.doNext)]
		for combo in buttonHandlers:
			cid, handler = combo[:2]
			self.Bind(wx.EVT_BUTTON, handler, id = cid)
				

 		# Install our own method to handle closing the window.  This allows us
		# to ask the user if he/she wants to save before closing the window, as
		# well as keeping track of which windows are currently open.

		self.Bind(wx.EVT_CLOSE, self.doExit)

		# Install our own method for handling keystrokes.  We use this to let
		# the user control the show with arrow keys.

		self.Bind(wx.EVT_CHAR_HOOK, self.onKeyEvent)


		
		# ===============
		# == Do Layout ==
		# ===============
		self.FaceButtons = []
		self.People = []
		self.NameButtons = []
		self.getPeople()
		for i in range(len(self.FaceButtons)):
			self.FaceButtons[i].SetSize(self.FaceButtons[i].GetBestSize())

		self.peopleSizer = wx.BoxSizer(wx.VERTICAL)

		for i in range(len(self.FaceButtons)):
			self.peopleSizer.Add(self.FaceButtons[i],1,wx.TOP|wx.RIGHT|wx.LEFT|wx.Bottom|wx.ALIGN_CENTER|wx.EXPAND|wx.SHAPED,10)
			self.peopleSizer.Add(self.NameButtons[i],0,wx.ALIGN_CENTER|wx.Bottom|wx.NO_BORDER,5)
			self.peopleSizer.Add((-1,20))

		self.peopleTab.SetSizer(self.peopleSizer)
		self.peopleSizer.Fit(self.peopleTab)

		self.selectorTabs.AddPage(self.peopleTab,"People")
		self.selectorTabs.AddPage(self.placesTab,"Places")
		self.selectorTabs.AddPage(self.eventsTab,"Events")
		
		self.pictureTopSizer=wx.BoxSizer(wx.HORIZONTAL)
		self.pictureTopSizer.Add(self.picture1,16,wx.EXPAND|wx.ALL,5)
		self.pictureTopSizer.Add(self.picture2,10,wx.EXPAND|wx.ALL,5)
		
		self.pictureBtmSizer=wx.BoxSizer(wx.HORIZONTAL)
		self.pictureBtmSizer.Add(self.picture3,10,wx.EXPAND|wx.ALL,5)
		self.pictureBtmSizer.Add(self.picture4,16,wx.EXPAND|wx.ALL,5)
		
		self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.buttonSizer.Add(self.backBtn,0,0,0)
		self.buttonSizer.Add(self.rwBtn,0,0,0)
		self.buttonSizer.Add(self.playBtn,0,0,0)
		self.buttonSizer.Add(self.ffBtn,0,0,0)
		self.buttonSizer.Add(self.nextBtn ,0,0,0)
		
		self.controlSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.controlSizer.AddStretchSpacer(1)
		self.controlSizer.Add(self.buttonSizer,0)
		self.controlSizer.AddStretchSpacer(1)
	
		self.displaySizer = wx.BoxSizer(wx.VERTICAL)
 		self.displaySizer.Add(self.pictureTopSizer,1, wx.EXPAND | wx.ALL,5)
 		self.displaySizer.Add(self.pictureBtmSizer,1, wx.EXPAND | wx.LEFT |wx.RIGHT|wx.BOTTOM, 5)
 		self.displaySizer.Add(self.controlSizer,0,wx.EXPAND,0)
		
		topSizer = wx.BoxSizer(wx.HORIZONTAL)
		topSizer.Add(self.selectorTabs,1,wx.EXPAND,0)
		topSizer.Add(self.displaySizer, 4, wx.EXPAND, 0)
 		self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
		
		self.toolbar.Realize()
		self.SetAutoLayout(True)
		self.SetSizer(topSizer)
		self.Layout()
		self.Centre()
		
		
		self.setShow()
    # ==========================
    # == Menu Command Methods ==
    # ==========================

	def doNew(self,event):
		"""Creates a library"""
		pass

	def doOpen(self,event):
		"""Opens a library"""
		pass

	def doClose(self,event):
		"""closes this library. Prompts to save"""
		pass


	def doSave(self,event):
		"""writes library to file"""
		pass

	def doSaveAs(self,event):
		"""writes library to a different file"""
		pass

	def doExit(self,event):
		"""exits program prompts to save"""
		self.Destroy()

	def doPlay(self,event):
		if(not self.isPaused):
			print "not ispaused"
			self.playBtn.SetBitmapLabel(self.pauseIcon)
			self.playBtn.SetBitmapHover(self.pauseIcon_hover)
			self.whichPic=0
			for i in range(4):
				self.loadNextImage(None)
			self.playTimer.Start(self.playSpeed*1000)
			
		else:
			self.playBtn.SetBitmapLabel(self.playIcon)
			self.playBtn.SetBitmapHover(self.playIcon_hover)
			self.playTimer.Stop()
		self.isPaused = not self.isPaused
		
##		self.loadPicture(self.picture1, os.getcwd()+"\\Images\\photos\\Bramwell, WV\\DSCF3395.JPG" )
##		self.loadPicture(self.picture2, os.getcwd()+"\\Images\\photos\\Blacksburg, Va\\DSCF3788.JPG")
##		self.loadPicture(self.picture3, os.getcwd()+"\\Images\\photos\Washington, DC\\003.JPG")
##		self.loadPicture(self.picture4, os.getcwd()+"\\Images\\photos\\Washington, DC\\012.JPG")
##		

	def doStop(self,event):
		"""stops playback"""
		pass

	def doRewind(self,event):
		"""goes backwards"""
		self.currSelct=1
		print "RW"

	def doFastForward(self,event):
		"""goes fowards"""
		print "FF"
		self.pictureBtmSizer.Remove(self.picture3)
		self.picture3.Destroy()
		
		pass

	def doBack(self,event):
		"""goes fowards"""
		print "Back"
	pass

	def doNext(self,event):
		"""goes fowards"""
		print "Next"
	pass

	def doShowAbout(self,event):
		"""shows about information"""
	pass

	# ==================
	# == ROD commands ==
	# ==================
	def getPeople(self):
		print "Getting people"
		"""gets all the faces and populates the people pane"""
		facesDB=Base(os.getcwd() +"\\Databases\\faces.db")
		peopleDB=Base(os.getcwd()+"\\Databases\\people.db")
		try:
			facesDB.open()
			peopleDB.open()
			for human in peopleDB.select(None).sort_by("+__id__"):
				print human
				thumb = facesDB.select(['thumbnail'],personid=human.__id__)[0].thumbnail

				self.People.append(os.getcwd()+"\\Images\\thumbnails\\" + thumb)

				self.FaceButtons.append(wx.BitmapButton(self.peopleTab, -1, wx.Bitmap(os.getcwd()+"\\Images\\thumbnails\\" + thumb, wx.BITMAP_TYPE_ANY),style=wx.NO_BORDER,name=str(human.__id__)))
				self.FaceButtons[human.__id__].Bind(wx.EVT_BUTTON,self.selectPerson)
				name_button = str(human.name).strip()
			
				if str(name_button) == str(human.__id__):
					name_button ="(unnamed)"
				self.NameButtons.append(wx.StaticText(self.peopleTab,-1, name_button, name=str(human.__id__),style=wx.TE_CENTRE))
			
				if name_button=="(unnamed)":
					self.NameButtons[human.__id__].SetToolTip(wx.ToolTip("Click on name to change"))
				self.NameButtons[human.__id__].Bind(wx.EVT_LEFT_DOWN,self.changeName)

		except IOError:
			print "ERROR: Databases not found. (In func getPeople())"
			exit(-1)

	def selectPerson(self,  event):
		"""changes the show to select a certain person"""
		button = event.GetEventObject()
		print int(button.GetName())

	def changeName(self,  event):
		"""changes the associated persons name"""
		button = event.GetEventObject()


		dialog = wx.TextEntryDialog(None, "Whaat is this person's name?","Change Name", button.GetLabel(), style=wx.OK|wx.CANCEL)
		if dialog.ShowModal() == wx.ID_OK:
			 newname = dialog.GetValue()
		dialog.Destroy()

		peopleDB=Base(os.getcwd()+"\\Databases\\people.db")
		try:
			peopleDB.open()
			rec = peopleDB[int(button.GetName())]
			if(len(newname)>1):
				rec.update(name=str(newname))
				button.SetLabel(newname)
				button.CenterOnParent(wx.HORIZONTAL)


		except IOError:
			print "ERROR: Databases not found. (In func cahngeName())"
	
	def loadPicture(self,widget,filename):
		"""takes in a filename and a widget. 
			loads picture into that widget after cropping and scaling
		"""
	
		wdgtSize = widget.GetSize()
		croppedImg = scaleCropImage(filename,wdgtSize[0],wdgtSize[1])
		loadedImg = wx.EmptyImage(*wdgtSize)
		loadedImg.SetData(croppedImg.convert("RGB").tostring())
		
		widget.SetBitmap(wx.BitmapFromImage(loadedImg))

	def getEvents(self):
		"""gets all the events and populates the event pane"""
		pass

	def getPlaces(self):
		"""gets all the places and populates the event pane"""
		pass
	def loadNextImage(self,event):
		try:
			ctrl = self.pictureControls[self.whichPic]
			self.whichPic= (self.whichPic+1)%4
			imgLoc = self.showGen.next()
			print imgLoc
			self.loadPicture(ctrl,imgLoc)
			
		except StopIteration:
			self.playTimer.Stop() 
			self.isPaused=True
			self.doPlay(wx.EVT_BUTTON)
		
		
	def getShow(self):
		photosDB.open()
		for pic in self.show:
			yield photosDB[pic].path
		
	def setShow(self):
		self.eventOrder = OE.orderEvents("time","1970:01:01 0:0:0")
		for evtID in self.eventOrder:
			photoOrder = PS.photoSuitability(evtID,"time","1970:01:01 0:0:0")
			for photo in photoOrder:
				self.show.append(photo)
		
	# ====================
	# == Event handlers ==
	# ====================
	def onKeyEvent(self, event):
		pass
		
	def onSize(self, event):
		
		pass
#-------------------------------------------------------------------------------
class ExceptionHandler:
    """ A simple error-handling class to write exceptions to a text file.

	Under MS Windows, the standard DOS console window doesn't scroll and
	closes as soon as the application exits, making it hard to find and
	view Python exceptions.  This utility class allows you to handle Python
	exceptions in a more friendly manner.
    """

    def __init__(self):
	""" Standard constructor.
	"""
	self._buff = ""
	if os.path.exists("errors.txt"):
	    os.remove("errors.txt") # Delete previous error log, if any.


    def write(self, s):
	""" Write the given error message to a text file.

	    Note that if the error message doesn't end in a carriage return, we
	    have to buffer up the inputs until a carriage return is received.
	"""
	if (s[-1] != "\n") and (s[-1] != "\r"):
	    self._buff = self._buff + s
	    return

	try:
	    s = self._buff + s
	    self._buff = ""

	    f = open("errors.txt", "a")
	    f.write(s)
	    f.close()

	    if s[:9] == "Traceback":
		# Tell the user than an exception occurred.
		wx.MessageBox("An internal error has occurred.\nPlease " + \
			     "refer to the 'errors.txt' file for details.",
			     "Error", wx.OK | wx.CENTRE | wx.ICON_EXCLAMATION)


	except:
	    pass # Don't recursively crash on errors.



#------------------------------------------------------------------------------

class RodApp(wx.App):

	"""The main Reliving on Demand applicaiton"""
	def OnInit(self):
		"""Initialize the application"""
		print "in RodApp"
		frame = MainFrame(None,-1,"Reliving On Demand v2")
		frame.Centre()
		frame.Show()

		return True

#-------------------------------------------------------------------------------
# ===============
# == Utilities ==
# ===============
def scaleCropImage(imageLoc, boundWidth, boundHeight):
	"""scales an image to fit into the rectangle defined by boundWidth, boundHeight
		We scale it down so that one dimension fits and the other overlaps
		then we crop it to fit the window. 
		
		returns a PIL Image
			"""
	theImage = Image.open(imageLoc)
	width = theImage.size[0]
	height = theImage.size[1]
	ratioW = float(boundWidth) / width
	ratioH = float(boundHeight)/ height 
	
	newHeight = int(math.floor(ratioW*height))
	newWidth =int( math.floor( ratioH * width))
	
	#we clip just by splitting the difference on either side
	if(ratioW>ratioH):
		#width is fit, height is too big
		theImage.thumbnail((boundWidth,newHeight),Image.ANTIALIAS)
		hDel = int(math.floor( abs(newHeight - boundHeight)/2))
		cropIm = theImage.crop((0,hDel,boundWidth,hDel+boundHeight))
	else:
		#height fits, width is too big
		theImage.thumbnail((newWidth,boundHeight),Image.ANTIALIAS)
		wDel = int(math.floor( abs(newWidth-boundWidth)/2))
		cropIm = theImage.crop((wDel,0,wDel+boundWidth,boundHeight))
	cropIm.load()
	
	return cropIm
#-------------------------------------------------------------------------------
def main():
	print "in main"
	global _app

	#redirect python exceptions to a log file
	#  sys.stderr = ExceptionHandler()

	#create and start the ROD application
	_app = RodApp(0)
	_app.MainLoop()


if __name__ == '__main__':
	main()
