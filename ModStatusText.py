import TermUI as tui 

class StatusText(tui.GenElement):
	def __init__(self):
		self.text=tui.Text("")
		self.vanishing=""
		self.lingering=""
		self.showing=0

	def _updateText(self):
		if self.lingering and self.vanishing:
			self.text.text=self.lingering+", "+self.vanishing
		else:
			self.text.text=self.lingering+self.vanishing

	def queueText(self,text,frames,seconds=3):
		self.vanishing=text
		self._updateText()
		self.showing+=1
		frames.schedule(0,tui.sched.framesLater)
		frames.schedule(seconds,tui.sched.secondsLater,callback=self.clear)

	def setLingering(self,text,frames):
		self.lingering=text
		self._updateText()
		frames.schedule(0,tui.sched.framesLater)

	def clear(self,frames):
		self.showing-=1
		if self.showing==0:
			self.vanishing=""
			self._updateText()

	def size(self):
		return self.text.size()

	def render(self,cnv,x,y,ph,pw):
		self.text.render(cnv,x,y,ph,pw)

def setLingering(text):
	statusText.setLingering(text,frames)

def clear():
	statusText.clear(frames)

def queueText(text,seconds=3):
	statusText.queueText(text,frames,seconds=seconds)

statusText=StatusText()
shown=statusText.align(alignV="bottom")
frames=None
def modInit(modules,config,lock):
	modules.ui.addElem(shown)
	global frames
	frames=modules.ui.root.frames