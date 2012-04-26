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
from collections import namedtuple
import time
import Bases as DB


## {{{ http://code.activestate.com/recipes/576555/ (r1)
__all__ = ['recordtype']

import sys
from textwrap import dedent
from keyword import iskeyword


def recordtype(typename, field_names, verbose=False, **default_kwds):
    '''Returns a new class with named fields.

    @keyword field_defaults: A mapping from (a subset of) field names to default
        values.
    @keyword default: If provided, the default value for all fields without an
        explicit default in `field_defaults`.

    >>> Point = recordtype('Point', 'x y', default=0)
    >>> Point.__doc__           # docstring for the new class
    'Point(x, y)'
    >>> Point()                 # instantiate with defaults
    Point(x=0, y=0)
    >>> p = Point(11, y=22)     # instantiate with positional args or keywords
    >>> p[0] + p.y              # accessible by name and index
    33
    >>> p.x = 100; p[1] =200    # modifiable by name and index
    >>> p
    Point(x=100, y=200)
    >>> x, y = p               # unpack
    >>> x, y
    (100, 200)
    >>> d = p.todict()         # convert to a dictionary
    >>> d['x']
    100
    >>> Point(**d) == p        # convert from a dictionary
    True
    '''
    # Parse and validate the field names.  Validation serves two purposes,
    # generating informative error messages and preventing template injection attacks.
    if isinstance(field_names, basestring):
        # names separated by whitespace and/or commas
        field_names = field_names.replace(',', ' ').split()
    field_names = tuple(map(str, field_names))
    if not field_names:
        raise ValueError('Records must have at least one field')
    for name in (typename,) + field_names:
        if not min(c.isalnum() or c=='_' for c in name):
            raise ValueError('Type names and field names can only contain '
                             'alphanumeric characters and underscores: %r' % name)
        if iskeyword(name):
            raise ValueError('Type names and field names cannot be a keyword: %r'
                             % name)
        if name[0].isdigit():
            raise ValueError('Type names and field names cannot start with a '
                             'number: %r' % name)
    seen_names = set()
    for name in field_names:
        if name.startswith('_'):
            raise ValueError('Field names cannot start with an underscore: %r'
                             % name)
        if name in seen_names:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen_names.add(name)
    # determine the func_defaults of __init__
    field_defaults = default_kwds.pop('field_defaults', {})
    if 'default' in default_kwds:
        default = default_kwds.pop('default')
        init_defaults = tuple(field_defaults.get(f,default) for f in field_names)
    elif not field_defaults:
        init_defaults = None
    else:
        default_fields = field_names[-len(field_defaults):]
        if set(default_fields) != set(field_defaults):
            raise ValueError('Missing default parameter values')
        init_defaults = tuple(field_defaults[f] for f in default_fields)
    if default_kwds:
        raise ValueError('Invalid keyword arguments: %s' % default_kwds)
    # Create and fill-in the class template
    numfields = len(field_names)
    argtxt = ', '.join(field_names)
    reprtxt = ', '.join('%s=%%r' % f for f in field_names)
    dicttxt = ', '.join('%r: self.%s' % (f,f) for f in field_names)
    tupletxt = repr(tuple('self.%s' % f for f in field_names)).replace("'",'')
    inittxt = '; '.join('self.%s=%s' % (f,f) for f in field_names)
    itertxt = '; '.join('yield self.%s' % f for f in field_names)
    eqtxt   = ' and '.join('self.%s==other.%s' % (f,f) for f in field_names)
    template = dedent('''
        class %(typename)s(object):
            '%(typename)s(%(argtxt)s)'

            __slots__  = %(field_names)r

            def __init__(self, %(argtxt)s):
                %(inittxt)s

            def __len__(self):
                return %(numfields)d

            def __iter__(self):
                %(itertxt)s

            def __getitem__(self, index):
                return getattr(self, self.__slots__[index])

            def __setitem__(self, index, value):
                return setattr(self, self.__slots__[index], value)

            def todict(self):
                'Return a new dict which maps field names to their values'
                return {%(dicttxt)s}

            def __repr__(self):
                return '%(typename)s(%(reprtxt)s)' %% %(tupletxt)s

            def __eq__(self, other):
                return isinstance(other, self.__class__) and %(eqtxt)s

            def __ne__(self, other):
                return not self==other

            def __getstate__(self):
                return %(tupletxt)s

            def __setstate__(self, state):
                %(tupletxt)s = state
    ''') % locals()
    # Execute the template string in a temporary namespace
    namespace = {}
    try:
        exec template in namespace
        if verbose: print template
    except SyntaxError, e:
        raise SyntaxError(e.message + ':\n' + template)
    cls = namespace[typename]
    cls.__init__.im_func.func_defaults = init_defaults
    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in enviroments where
    # sys._getframe is not defined (Jython for example).
    if hasattr(sys, '_getframe') and sys.platform != 'cli':
        cls.__module__ = sys._getframe(1).f_globals['__name__']
    return cls

## end of http://code.activestate.com/recipes/576555/ }}}


#-------------------------------------------------------------------------------
#		   System Constants
#-------------------------------------------------------------------------------

#Menu item IDs:
menu_PLAY	= wx.NewId() #Show menu items
menu_STOP	= wx.NewId()
menu_RW	  = wx.NewId()
menu_FF	  = wx.NewId()
menu_SKIP = wx.NewId()
menu_BACK  = wx.NewId()


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

Criteria = namedtuple('Criteria','kind value')
ShowEvent = recordtype('ShowEvent', 'event startpos endpos')


class Speed:
	FAST = .5
	NORMAL =3
#-------------------------------------------------------------------------------
class Direction:
	FORWARD=1
	BACKWARD=-1
#-------------------------------------------------------------------------------
class SlideShow:
	def __init__(self):
		self.isPaused = True
		self.playSpeed = Speed.NORMAL
		self.playlist =[]
		self.eventList = []
		self.currPos =0 
		self.currEvt_index=0 #position in the event list. NOT THE EVENT ID
		self.direction = Direction.FORWARD
	def Back(self):
		if self.currEvt_index>0:
			self.currEvt_index-=1
			self.currPos = self.eventList[self.currEvt_index].startpos
	def Skip(self):
		if self.currEvt_index < len(self.eventList)-1:
			self.currEvt_index+=1
			self.currPos = self.eventList[self.currEvt_index].startpos	

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
		print "Initializing display frame"
		wx.Frame.__init__(self, parent, id, title,style = wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("Reliving on Demand 2.0")
		self.SetSize((900,735))
	
		# ================
		# == Class vars ==
		# ================
		self.dirty = False #library has been modified
		self.currCriteria = [] #currently selected criteria
		self.slideShow = SlideShow()
		
		self.PlaceTable={} 
		#Setup our menu bar.
		menuBar = wx.MenuBar()

##		self.fileMenu = wx.Menu()
##		self.fileMenu.Append(wx.ID_NEW,    "New\tCtrl-N", "Create a new photo library")
##		self.fileMenu.Append(wx.ID_OPEN,   "Open...\tCtrl-O", "Open an existing photo library")
##		self.fileMenu.Append(wx.ID_CLOSE,  "Close\tCtrl-W")
##		self.fileMenu.AppendSeparator()
##		self.fileMenu.Append(wx.ID_SAVE,   "Save\tCtrl-S")
##		self.fileMenu.Append(wx.ID_SAVEAS, "Save As...")
##		self.fileMenu.AppendSeparator()
##		self.fileMenu.Append(wx.ID_EXIT,    "Quit\tCtrl-Q")
##
##		menuBar.Append(self.fileMenu, "File")

		self.showMenu = wx.Menu()
		self.showMenu.Append(menu_PLAY,     "Play\\Pause")
		self.showMenu.Append(menu_FF,       "Fast Forward")
		self.showMenu.Append(menu_SKIP,		"Next Event")
		self.showMenu.Append(menu_RW,       "Rewind")
		self.showMenu.Append(menu_BACK,		"Previous Event")

		menuBar.Append(self.showMenu, "Show")
##
##		self.helpMenu = wx.Menu()
##		self.helpMenu.Append(menu_ABOUT, "About Reliving on Demand...")
##
##		menuBar.Append(self.helpMenu, "Help")

		self.SetMenuBar(menuBar)
		#Menu Bar end

		#Create our statusbar
		self.statusBar = self.CreateStatusBar(1,0)
		self.statusBar.SetStatusWidths([-1])
		self.statusBar.SetStatusText("Welcome to RoD 2.0")
		
##
##		#Create a toolbar
##		tsize = (15,15)
##		self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
##
##		artBmp = wx.ArtProvider.GetBitmap
##		self.toolbar.AddSimpleTool(
##		    wx.ID_OPEN, artBmp(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize), "Open Library")
##		self.toolbar.AddSimpleTool(
##		    wx.ID_SAVE, artBmp(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, tsize), "Save Library")
##		self.toolbar.AddSimpleTool(
##		    wx.ID_SAVEAS, artBmp(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR, tsize),
##		    "Save Library As...")

		#Create our tabbed pane
		self.selectorTabs = wx.Notebook(self, -1, style=0)
		self.peopleTab = wx.ScrolledWindow(self.selectorTabs, -1,style=wx.VSCROLL)
		self.placesTab = wx.ScrolledWindow(self.selectorTabs, -1,style=wx.VSCROLL)
		self.eventsTab = wx.ScrolledWindow(self.selectorTabs, -1,style=wx.VSCROLL)
		
		self.peopleTab.SetScrollRate(0,10)
		self.placesTab.SetScrollRate(0,10)

		#create picture displays
		self.picture1 = PictureWindow(self,-1)
		self.picture2 = PictureWindow(self,-1)
		self.picture3 = PictureWindow(self,-1)
		self.picture4 = PictureWindow(self,-1)
		
		self.playTimer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.loadNextImage, self.playTimer)
		
		self.pictureControls = [self.picture1,self.picture2,self.picture3,self.picture4]
		
		# =====================
		# == Control Buttons ==
		# =====================
		
		#back button, goes to previous event
		self.backBtn= wx.BitmapButton(self,back_btn, wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\back.png",wx.BITMAP_TYPE_PNG), style=wx.NO_BORDER)
		self.backBtn.SetBitmapHover(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\back_hover.png",wx.BITMAP_TYPE_PNG))
		self.backBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\back_disabled.png",wx.BITMAP_TYPE_PNG))
		self.backBtn.SetBitmapSelected(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\back_down.png",wx.BITMAP_TYPE_PNG))

		#rewind, moves quickly backwards through show
		self.rewindIcon = wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\rw.png",wx.BITMAP_TYPE_PNG)
		self.rewindIcon_hover =wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\rw_hover.png",wx.BITMAP_TYPE_PNG)
		self.rewindIcon_down =wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\rw_down.png",wx.BITMAP_TYPE_PNG)
		
		self.rwBtn= wx.BitmapButton(self, rw_btn, self.rewindIcon, style=wx.NO_BORDER)
		self.rwBtn.SetBitmapHover(self.rewindIcon_hover)
		self.rwBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\rw_disabled.png",wx.BITMAP_TYPE_PNG))
		self.rwBtn.SetBitmapSelected(self.rewindIcon_down)
		
		#play/pause, toggles between two states, starts and resumes show
		self.playIcon =wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\play.png",wx.BITMAP_TYPE_PNG)
		self.playIcon_hover =wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\play_hover.png",wx.BITMAP_TYPE_PNG)
		self.playIcon_down = wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\play_down.png",wx.BITMAP_TYPE_PNG)
		
		self.pauseIcon =wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\pause.png",wx.BITMAP_TYPE_PNG)
		self.pauseIcon_hover =wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\pause_hover.png",wx.BITMAP_TYPE_PNG)
		self.pauseIcon_down =wx.Bitmap(os.getcwd() + "\\Images\\Buttons\\pause_down.png",wx.BITMAP_TYPE_PNG)
		
		self.playBtn=wx.BitmapButton(self,play_btn,self.playIcon, style=wx.NO_BORDER)
		self.playBtn.SetBitmapHover(self.playIcon_hover)
		self.playBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\play_disabled.png",wx.BITMAP_TYPE_PNG))
		self.playBtn.SetBitmapSelected(self.playIcon_down)

		#fast foward, moves quickly foward through show
		self.fastforwardIcon = wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\ff.png",wx.BITMAP_TYPE_PNG)
		self.fastforwardIcon_down = wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\ff_down.png",wx.BITMAP_TYPE_PNG)
		self.fastforwardIcon_hover = wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\ff_hover.png",wx.BITMAP_TYPE_PNG) 
		
		self.ffBtn= wx.BitmapButton(self,ff_btn,self.fastforwardIcon, style=wx.NO_BORDER)
		self.ffBtn.SetBitmapHover(self.fastforwardIcon_hover)
		self.ffBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\ff_disabled.png",wx.BITMAP_TYPE_PNG))
		self.ffBtn.SetBitmapSelected(self.fastforwardIcon_down)
		
		#next button, moves to next event		
		self.nextBtn= wx.BitmapButton(self,next_btn, wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\next.png",wx.BITMAP_TYPE_PNG), style=wx.NO_BORDER)
		self.nextBtn.SetBitmapHover(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\next_hover.png",wx.BITMAP_TYPE_PNG))
		self.nextBtn.SetBitmapDisabled(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\next_disabled.png",wx.BITMAP_TYPE_PNG))
		self.nextBtn.SetBitmapSelected(wx.Bitmap(os.getcwd()+"\\Images\\Buttons\\next_down.png",wx.BITMAP_TYPE_PNG))
		
		
		# Associate menu/toolbar items with their handlers.
		menuHandlers = [
		(menu_PLAY,    self.doPlay),
		(menu_RW,      self.doRewind),
		(menu_FF,      self.doFastForward),
		(menu_SKIP,      self.doNext),
		(menu_BACK,      self.doBack)]
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
		self.EventButtons = []
		self.PlaceButtons =[]
		
		
		#layout tabs
		self.getPeople()
		for i in range(len(self.FaceButtons)):
			self.FaceButtons[i].SetSize(self.FaceButtons[i].GetBestSize())
		self.peopleSizer = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(self.FaceButtons)):
			self.peopleSizer.Add(self.FaceButtons[i],1,wx.TOP|wx.RIGHT|wx.LEFT|wx.Bottom|wx.ALIGN_CENTER|wx.EXPAND|wx.SHAPED,10)
			self.peopleSizer.Add(self.NameButtons[i],0,wx.ALIGN_CENTER|wx.Bottom|wx.NO_BORDER,5)
			self.peopleSizer.AddSpacer(0,20)

		self.peopleTab.SetSizer(self.peopleSizer)
		self.peopleSizer.Fit(self.peopleTab)

		self.getEvents()
		self.eventSizer = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(self.EventButtons)):
			self.eventSizer.Add(self.EventButtons[i],0, wx.ALL|wx.ALIGN_CENTRE,10)
			self.eventSizer.AddSpacer(0,20)
		self.eventsTab.SetSizer(self.eventSizer)
		self.eventSizer.Fit(self.eventsTab)
		
		self.getPlaces()
		self.placeSizer = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(self.PlaceButtons)):
			self.placeSizer.Add(self.PlaceButtons[i],0, wx.ALIGN_CENTRE|wx.ALL, 10)
			self.placeSizer.AddSpacer(0,20)
		self.placesTab.SetSizer(self.placeSizer)
		self.placeSizer.Fit(self.placesTab)
		
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
		
		
		self.startShow()
    # ==========================
    # == Menu Command Methods ==
    # ==========================

##	def doNew(self,event):
##		"""Creates a library"""
##		pass
##
##	def doOpen(self,event):
##		"""Opens a library"""
##		pass
##
##	def doClose(self,event):
##		"""closes this library. Prompts to save"""
##		pass
##
##
##	def doSave(self,event):
##		"""writes library to file"""
##		pass
##
##	def doSaveAs(self,event):
##		"""writes library to a different file"""
##		pass

	def doExit(self,event):
		"""exits program prompts to save"""
		DB.close()
		self.Destroy()

	def doPlay(self,event):
		if(self.slideShow.isPaused):
			print "Playing"
			self.playBtn.SetBitmapLabel(self.pauseIcon)
			self.playBtn.SetBitmapHover(self.pauseIcon_hover)
			self.playBtn.SetBitmapSelected(self.pauseIcon_down)
			self.whichPic=0
			for i in range(4):
				self.loadNextImage(None)
			
			self.playTimer.Start(self.slideShow.playSpeed*1000)
		else:
			print "Paused"
			#set buttons
			self.playBtn.SetBitmapLabel(self.playIcon)
			self.playBtn.SetBitmapHover(self.playIcon_hover)
			self.playBtn.SetBitmapSelected(self.playIcon_down)
			self.rwBtn.SetBitmapLabel(self.rewindIcon)
			self.rwBtn.SetBitmapHover(self.rewindIcon_hover)
			self.ffBtn.SetBitmapLabel(self.fastforwardIcon)
			self.ffBtn.SetBitmapHover(self.fastforwardIcon_hover)
			self.playTimer.Stop()
		self.slideShow.isPaused = not self.slideShow.isPaused
	

	def doRewind(self,event):
		"""goes backwards"""
		print "RW"
		if(self.slideShow.direction != Direction.BACKWARD):#if we're not rewinding
			self.rwBtn.SetBitmapLabel(self.rewindIcon_down)
			self.rwBtn.SetBitmapHover(self.rewindIcon_down)
			self.ffBtn.SetBitmapLabel(self.fastforwardIcon)
			self.ffBtn.SetBitmapHover(self.fastforwardIcon_hover)
			self.slideShow.direction=Direction.BACKWARD
			self.slideShow.playSpeed=Speed.FAST
		else:	
			self.rwBtn.SetBitmapLabel(self.rewindIcon)
			self.slideShow.direction=Direction.FORWARD
			self.slideShow.playSpeed=Speed.NORMAL
		self.playTimer.Start(self.slideShow.playSpeed*1000)

	def doFastForward(self,event):
		"""goes foward quickly"""
		print "FF"
		if not(self.slideShow.direction==Direction.FORWARD and self.slideShow.playSpeed==Speed.FAST):
			#if we're not fast forwarding, start fastfowarding
			self.ffBtn.SetBitmapLabel(self.fastforwardIcon_down)
			self.ffBtn.SetBitmapHover(self.fastforwardIcon_down)
			self.rwBtn.SetBitmapLabel(self.rewindIcon)
			self.rwBtn.SetBitmapHover(self.rewindIcon_hover)
			self.slideShow.direction=Direction.FORWARD
			self.slideShow.playSpeed= Speed.FAST
		else:
			self.ffBtn.SetBitmapLabel(self.fastforwardIcon)
			self.slideShow.playSpeed=Speed.NORMAL
		self.playTimer.Start(self.slideShow.playSpeed*1000)


	def doBack(self,event):
		"""goes one event back"""
		print "Back"
		self.slideShow.Back()
	
	def doNext(self,event):
		"""goes fowards"""
		print "Next"
		self.slideShow.Skip()

##	def doShowAbout(self,event):
##		"""shows about information"""
##		pass

	# ==================
	# == ROD commands ==
	# ==================
	def getPeople(self):
		print "Getting people"
		"""gets all the faces and populates the people pane"""

		for human in DB.people.select(None).sort_by("+__id__"):
			thumb = DB.faces.select(['thumbnail'],personid=human.__id__)[0].thumbnail

			self.People.append(os.getcwd()+"\\Images\\thumbnails\\" + thumb)

			self.FaceButtons.append(GenBitmapToggleButton(self.peopleTab, -1, wx.Bitmap(os.getcwd()+"\\Images\\thumbnails\\" + thumb, wx.BITMAP_TYPE_ANY),size=(120,120),name=str(human.__id__)))
			self.FaceButtons[human.__id__].Bind(wx.EVT_BUTTON,self.selectPerson)
			name_button = str(human.name).strip()
		
			if str(name_button) == str(human.__id__):
				name_button ="(unnamed)"
			self.NameButtons.append(wx.StaticText(self.peopleTab,-1, name_button, name=str(human.__id__),style=wx.TE_CENTRE))
		
			if name_button=="(unnamed)":
				self.NameButtons[human.__id__].SetToolTip(wx.ToolTip("Click on name to change"))
			self.NameButtons[human.__id__].Bind(wx.EVT_LEFT_DOWN,self.changeName)
		
	def getEvents(self):
		print "Getting Events"
		for event in DB.events.select().sort_by("+firsttime"):
			eventTime =event.firsttime
			eventTime = time.strptime(eventTime, "%Y:%m:%d %H:%M:%S")
			eventTime = time.strftime("%b %d, %Y",eventTime)
			self.EventButtons.append(wx.ToggleButton(self.eventsTab,-1, str(eventTime), name=str(event.__id__)))
			self.EventButtons[event.__id__].SetToolTip(wx.ToolTip(event.name))
			self.EventButtons[event.__id__].Bind(wx.EVT_TOGGLEBUTTON, self.selectEvent)
					
	def getPlaces(self):
		print "Getting Locations"
		for place in DB.places:
			self.PlaceButtons.append(wx.ToggleButton(self.placesTab,-1,str(place.name), name=str(place.__id__)))
			self.PlaceButtons[place.__id__].Bind(wx.EVT_TOGGLEBUTTON,self.selectPlace)
			self.PlaceTable[place.__id__]=(place.lat,place.lon)
	
	def selectPerson(self,  event):
		print "Selecting Person"
		button = event.GetEventObject()
		personNo= int(button.GetName())
		button.SetBackgroundColour(wx.Colour(255,255,0))
		print "person num",personNo
		self.selectCriteria(Criteria('person',personNo))
		
	def selectEvent(self, event):
		print "Selecting Event"
		button = event.GetEventObject()	
		eventNo = int(button.GetName())
		print "event is ",eventNo
		button.SetBackgroundColour(wx.Colour(255,255,0))
		self.selectCriteria(Criteria('event',eventNo))	
		
	def selectPlace(self, event):
		print "Selecting Place"
		button = event.GetEventObject()	
		placeNo = int(button.GetName())
		print "place is",placeNo
		button.SetBackgroundColour(wx.Colour(255,255,0))
		self.selectCriteria(Criteria('location',placeNo))	
		
	def selectCriteria(self,criteria):
		addFlag = True
		if len(self.currCriteria)!=0:
			if not (self.currCriteria[0].kind=='person' and criteria.kind== 'person'):
				for criterion in self.currCriteria:
					#unselect everything
					if criterion.kind == 'person':
						self.FaceButtons[criterion.value].SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
						self.FaceButtons[criterion.value].SetValue(False)
					elif criterion.kind == 'event':
						self.EventButtons[criterion.value].SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
						self.EventButtons[criterion.value].SetValue(False)
					elif criterion.kind == 'location':
						self.PlaceButtons[criterion.value].SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
						self.PlaceButtons[criterion.value].SetValue(False)	
				self.currCriteria=[]
			elif criteria in self.currCriteria:
				self.FaceButtons[criteria.value].SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
				self.FaceButtons[criteria.value].SetValue(False)
				self.currCriteria.remove(criteria)
			
				addFlag=False
		
		if addFlag:self.currCriteria.append(criteria)
						
		self.reorderShow()
			

	def loadNextImage(self,event): #event is dummy param so it can be caleld from a button event...
##		print "curr pos is ", self.slideShow.currPos," event index is ",self.slideShow.currEvt_index
		try:
##			print "loading next image"
			widget = self.pictureControls[self.whichPic]
			self.whichPic= (self.whichPic+1)%4
			
			if self.slideShow.currPos >=0 and self.slideShow.currPos < len(self.slideShow.playlist):
				picID = self.slideShow.playlist[self.slideShow.currPos]
				if(self.slideShow.currPos > self.slideShow.eventList[self.slideShow.currEvt_index].endpos):
					self.slideShow.currEvt_index+=1
				self.slideShow.currPos+= self.slideShow.direction
			
			else:
				raise StopIteration

			#Load picture
			wdgtSize = widget.GetSize()
			croppedImg = scaleCropImage(DB.photos[picID].path,*wdgtSize)
			loadedImg = wx.EmptyImage(*wdgtSize)
			loadedImg.SetData(croppedImg.convert("RGB").tostring())
			widget.SetBitmap(wx.BitmapFromImage(loadedImg))
			
		except StopIteration:
			self.playTimer.Stop() 
			self.slideShow.isPaused = False
			self.slideShow.playSpeed = Speed.NORMAL
			self.doPlay(wx.EVT_BUTTON) #pauses it
			self.slideShow.currEvt_index=0
			self.slideShow.currPos=self.slideShow.eventList[self.slideShow.currEvt_index].startpos
			
		except IOError:
			print "Error loading database from LoadNextImage"	
	
	def reorderShow(self):
		
		if len(self.currCriteria)>0:
			pos = self.slideShow.currPos
			self.slideShow.playlist=self.slideShow.playlist[:pos]
			if self.currCriteria[0].kind=='person':
				print "reordering on person"
				people=[]
				for criterion in self.currCriteria:
					people.append(criterion.value)
				eventOrder = OE.orderEvents("people",people)
				for evtID in eventOrder:
					self.slideShow.eventList.append( ShowEvent(evtID,pos,-1) )
					photoOrder = PS.photoSuitability(evtID,"people",people)
					for photo in photoOrder:
						self.slideShow.playlist.append(photo)
						pos+=1
					self.slideShow.eventList[-1].endpos = pos	
					
			elif self.currCriteria[0].kind=='event':
				print "reordering on event"
				eventOrder = OE.orderEvents("time",DB.events[self.currCriteria[0].value].firsttime)
				for evtID in eventOrder:
					self.slideShow.eventList.append( ShowEvent(evtID,pos,-1) )
					photoOrder = PS.photoSuitability(evtID,"time",self.currCriteria[0].value)
					for photo in photoOrder:
						self.slideShow.playlist.append(photo)
						pos+=1
					self.slideShow.eventList[-1].endpos = pos
				
			elif self.currCriteria[0].kind=='location':
				print "reordering on location"
				eventOrder = OE.orderEvents("location",self.PlaceTable[self.currCriteria[0].value])
				
				for evtID in eventOrder:
					self.slideShow.eventList.append( ShowEvent(evtID,pos,-1) )
					photoOrder = PS.photoSuitability(evtID,"location", self.PlaceTable[self.currCriteria[0].value] )
					for photo in photoOrder:
						self.slideShow.playlist.append(photo)
						pos+=1
					self.slideShow.eventList[-1].endpos = pos
			else:
				print "GET TO THE CHOPPA!"
			
		else:
			eventOrder = OE.orderEvents("time","1970:01:01 0:0:0")
		pos=0
		for evtID in eventOrder:
			self.slideShow.eventList.append( ShowEvent(evtID,pos,-1) )
			photoOrder = PS.photoSuitability(evtID,"time","1970:01:01 0:0:0")
			for photo in photoOrder:
				self.slideShow.playlist.append(photo)
				pos+=1
			self.slideShow.eventList[-1].endpos = pos
		print "Event order is ", eventOrder
			
			
	def startShow(self):
		print "Starting Show"
		self.reorderShow()
		self.slideShow.isPaused=True
		self.slideShow.currPos=0
		self.slideShow.direction=Direction.FORWARD

	def changeName(self,  event):
		"""changes the associated persons name"""
		button = event.GetEventObject()

		rec = DB.people[int(button.GetName())]
		
		newname = button.GetLabel()
		dialog = wx.TextEntryDialog(None, "What is this person's name?","Change Name", button.GetLabel(), style=wx.OK|wx.CANCEL)
		if dialog.ShowModal() == wx.ID_OK:
			 newname = dialog.GetValue()
		dialog.Destroy()
		
		if len(newname)>1 and newname!="(unnamed)":
			rec.update(name=str(newname))
			button.SetLabel(newname)
			button.CenterOnParent(wx.HORIZONTAL)

	# ====================
	# == Event handlers ==
	# ====================
	def onKeyEvent(self, event):
		pass
		
	def onSize(self, event):
		pass
#------------------------------------------------------------------------------
class RodApp(wx.App):

	"""The main Reliving on Demand applicaiton"""
	def OnInit(self):
		"""Initialize the application"""
		print "Starting RodApp"
		frame = MainFrame(None,-1,"Reliving On Demand v2")
		frame.Centre()
		frame.Show()

		return True


#-------------------------------------------------------------------------------	
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


def main():
	print "in main"
	
	DB.init()
	DB.open()
	global _app
	#create and start the ROD application
	_app = RodApp(0)
	_app.MainLoop()

	
	
if __name__ == '__main__':
	main()
