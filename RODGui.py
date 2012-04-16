#-------------------------------------------------------------------------------
# Name:	Reliving on demand GUI
# Purpose:
#
# Author:      PSDUKES
#
# Created:     10/04/2012
# Copyright:   (c) PSDUKES 2012
#-------------------------------------------------------------------------------

import sys
import wx
import os
from buzhug import Base
from wx.lib.buttons import GenBitmapButton, GenBitmapToggleButton

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

#size of display frame, in pixels:
DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 1000


class DisplayFrame(wx.Frame):
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
		self.toolbar.Realize()


		#Create our tabbed pane
		self.selectorTabs = wx.Notebook(self, -1, style=0)
		self.peopleTab = wx.ScrolledWindow(self.selectorTabs, -1,style=wx.VSCROLL)
		self.placesTab = wx.Panel(self.selectorTabs, -1)
		self.eventsTab = wx.Panel(self.selectorTabs, -1)

		#create the display
		self.topPanel = wx.Panel(self, -1)
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


		self.topPanel.Bind(wx.EVT_SIZE, self.onSize)


		# Install our own method to handle closing the window.  This allows us
		# to ask the user if he/she wants to save before closing the window, as
		# well as keeping track of which windows are currently open.

		self.Bind(wx.EVT_CLOSE, self.doClose)

		# Install our own method for handling keystrokes.  We use this to let
		# the user control the show with arrow keys.

		self.Bind(wx.EVT_CHAR_HOOK, self.onKeyEvent)

		# ====================
		# == Set properties ==
		# ====================
		self.SetTitle("Reliving on Demand 2.0")
		self.SetSize((900,800))
		self.peopleTab.SetScrollRate(0,10)
		self.dirty = False

		# ===============
		# == Do Layout ==
		# ===============
		topSizer = wx.BoxSizer(wx.HORIZONTAL)

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

		topSizer.Add(self.selectorTabs, 1,wx.EXPAND,0)
		topSizer.Add(self.topPanel, 4, wx.EXPAND, 0)

		self.SetAutoLayout(True)
		self.SetSizer(topSizer)
		self.Layout()
		self.Centre()

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
		self.Destroy()


	def doSave(self,event):
		"""writes library to file"""
	pass

	def doSaveAs(self,event):
		"""writes library to a different file"""
	pass

	def doExit(self,event):
		"""exits program prompts to save"""
	pass

	def doPlay(self,event):
		"""toggles playbool"""
	pass

	def doStop(self,event):
		"""stops playback"""
	pass

	def doRewind(self,event):
		"""goes backwards"""
	pass

	def doFastForward(self,event):
		"""goes fowards"""
	pass

	def doShowAbout(self,event):
		"""shows about information"""
	pass

	# =========================
	# == Reordering commands ==
	# =========================
	def getPeople(self):
		"""gets all the faces and populates the people pane"""
		facesDB=Base(os.getcwd() +"\\Databases\\faces.db")
		peopleDB=Base(os.getcwd()+"\\Databases\\people.db")
		try:
			facesDB.open()
			peopleDB.open()
			for human in peopleDB.select(None).sort_by("+__id__"):
				print " humans name is ", human.name
				thumb = facesDB.select(['thumbnail'],pid=human.__id__)[0].thumbnail
				self.People.append(os.getcwd()+"\\Images\\thumbnails\\" + thumb)
				self.FaceButtons.append(wx.BitmapButton(self.peopleTab, -1, wx.Bitmap(os.getcwd()+"\\Images\\thumbnails\\" + thumb, wx.BITMAP_TYPE_ANY),style=wx.BU_AUTODRAW,name=str(human.__id__)))
				self.FaceButtons[human.__id__].Bind(wx.EVT_BUTTON,self.selectPerson)
				name_button = str(human.name)
				if name_button == str(human.__id__):
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


	def getEvents(self):
		"""gets all the events and populates the event pane"""
	pass

	def getPlaces(self):
		"""gets all the places and populates the event pane"""
	pass
	# ====================
	# == Event handlers ==
	# ====================
	def onKeyEvent(self, event):
		pass

	def onSize(self, event):
		print self.peopleSizer.GetSize()
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
		frame = DisplayFrame(None,-1,"Reliving On Demand v2")
		frame.Centre()
		frame.Show()

		return True

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
