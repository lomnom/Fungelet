import TermUI as tui
import TermCanvas as tc
import Terminal as trm
import TermIntr as ti
from threading import Lock as lock

import FungeUI as fui

import Funge as f3e
import Befunge as b5e

#### making the funge
def loadBf(text,plane,sx,sy):
	for row,line in enumerate(text.split("\n")):
		for x,char in enumerate(line):
			if char!=' ':
				plane[f3e.Vect2d(x+sx,row+sy)]=ord(char)

funge=f3e.Funge([],f3e.Space2d(),b5e.befunge2d)
pointer=b5e.BfPointer(funge,f3e.Vect2d(0,0),f3e.Vect2d(1,0),[],[],f3e.Vect2d(0,0))
funge.pointers.append(pointer)

loadBf(open("Tester.b98",'r').read(),funge.plane,-5,-3)

def showFunge(funge,pointer):
	topleft,size=funge.plane.limits()
	print(
		funge.plane.stringify(topleft.x-1,topleft.y-1,size.y+2,size.x+2,pointers=[pointer])
		     .replace(' ',trm.dim+'⋅'+trm.reset)
		)
	print(pointer.stack)
	print([chr(char) for char in pointer.stack])
	if pointer.mode==0:
		print((instr:=funge.instrs[funge.plane[pointer.pos]]).name,">",instr.description)
	else:
		print("In stringMode, push to stack")

showFunge(funge,pointer)

### cursor & movement stuff
plane=funge.plane
instrs=b5e.befunge2d

cursor=f3e.Vect2d(0,0)
cursorDelta=f3e.Vect2d(1,0)
def canvasWhere(x,y,ph,pw):
	return (cursor.x-(pw//2),cursor.y-(ph//2))

movement=ti.Listener()

def updateInfo(delta,coords,plane,instrs):
	statusText.setLingering(f"At ({coords.x},{coords.y}), moving ({delta.x},{delta.y})",root.frames)
	try:
		statusText.queueText(instrs[plane[coords]].description,root.frames)
	except KeyError:
		statusText.clear(root.frames)

@movement.handle
def key(key):
	global cursor,cursorDelta
	root.frames.schedule(
		1,tui.sched.framesLater
	)
	if key=='\n':
		try:
			cursorDelta,cursor=f3e.nextPlaces(cursor,cursorDelta,instrs,plane)[0]
		except:
			pass
		updateInfo(cursorDelta,cursor,plane,instrs)
		return
	elif key=="up":
		cursorDelta=f3e.Vect2d(0,-1)
	elif key=="down":
		cursorDelta=f3e.Vect2d(0,1)
	elif key=="left":
		cursorDelta=f3e.Vect2d(-1,0)
	elif key=="right":
		cursorDelta=f3e.Vect2d(1,0)
	else:
		return
	cursor+=cursorDelta
	updateInfo(cursorDelta,cursor,plane,instrs)

#markers
class Cell:
	def __init__(self,depth,pos,delta,prev=None,after=None):
		self.prev=prev
		self.after=after if after else []
		self.depth=depth
		self.pos=pos
		self.delta=delta

	def __repr__(self):
		return f"Cell({self.depth},{self.delta},{repr(self.pos)},after={repr(self.after)})" # prev is omitted

	def __eq__(self,other):
		return self.delta==other.delta and self.pos==other.pos

	def __hash__(self):
		return hash((self.delta,self.pos))

def shallowize(root,rootDepth,visited=None):
	if visited==None:
		visited={root}
	if root in visited:
		return
	for after in root.after:
		after.depth=rootDepth+1
		shallowize(after,rootDepth+1,visited)

def _generatePathTree(pos,delta,plane,traversed,instrs,depthLimit,depth=0) -> Cell:
	here=Cell(depth,pos,delta)
	if pos in traversed: #traversed is {pos:{delta:[depth,cell], ...}}
		cells=traversed[pos]
		if delta in cells:
			tdepth,tcell=cells[delta]
			if tdepth<=depth:
				return tcell
			else:
				shallowize(tcell,depth)
		else:
			cells[delta]=[depth,here]
	else:
		traversed[pos]={}
		traversed[pos][delta]=[depth,here]

	if depth==depthLimit:
		return Cell(depth,pos,delta)
	else:
		currentChar=plane[pos]
		if currentChar in instrs:
			instruction=instrs[currentChar]
		else:
			instruction=instrs[plane.defaultValue]
		for tdelta,tpos in instruction.transforms(delta,pos,plane):
			paths=_generatePathTree(tpos,tdelta,plane,traversed,instrs,depthLimit,depth=depth+1)
			here.after.append(paths)
			paths.prev=here
		return here

def generatePathTree(pos,delta,plane,instrs,depthLimit):
	traversed={}
	root=_generatePathTree(pos,delta,plane,traversed,instrs,depthLimit)
	return (root,traversed)

def fromTo(start,end,step=1): #inclusive range
	start,end=(start,end) if end>=start else (end,start)
	yield from range(start,end+1,step)

pathDepth=24
def markers():
	def cursorMod(char):
		char.flags|={'r'}

	def path(depth):
		color=244-round((depth/pathDepth)*12)+1
		if color==256:
			color=231
		color=str(color)
		def pathMod(char):
			char.bcolor=color
		return pathMod

	root,traversed=generatePathTree(cursor,cursorDelta,plane,instrs,pathDepth)
	for pos in traversed:
		cells=traversed[pos]
		smallestDepth,cell=min(cells.values(),key=lambda value: value[0])
		yield (pos.x,pos.y,path(smallestDepth))
		if cell.prev:
			change=(cell.prev.pos-cell.pos)
			if abs(change.x)>1 or abs(change.y)>1: #if pointer moved more than one space in a tick.
				for x in fromTo(cell.prev.pos.x,cell.pos.x):
					yield (x,cell.prev.pos.y,path(smallestDepth-1))
				for y in fromTo(cell.prev.pos.y,cell.pos.y):
					yield (cell.pos.x,y,path(smallestDepth-1))
	yield (cursor.x,cursor.y,cursorMod)

## status text
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

	def queueText(self,text,frames):
		self.vanishing=text
		self._updateText()
		self.showing+=1
		frames.schedule(0,tui.sched.framesLater)
		frames.schedule(3,tui.sched.secondsLater,callback=self.clear)

	def setLingering(self,text,frames):
		self.lingering=text
		self._updateText()
		frames.schedule(0,tui.sched.framesLater)

	def clear(self,frames):
		if self.showing==0:
			self.vanishing=""
			self._updateText()
		else:
			self.showing-=1

	def size(self):
		return self.text.size()

	def render(self,cnv,x,y,ph,pw):
		self.text.render(cnv,x,y,ph,pw)

@tc.canvasApp # wrapper that initialises the terminal and passes the canvas to you
def main(cnv):
	global root,statusText
	quitlock=lock()
	quitlock.acquire()
	quitButton=ti.Button("quit","ctrl w")
	statusText=StatusText()
	@quitButton.onToggle
	def onPress(*_):
		quitlock.release()

	root=tui.Root(
		cnv,
		tui.ZStack(
			fui.BfSpaceDisplay(funge.plane,where=canvasWhere,markers=markers),
			statusText.align(alignV="bottom")
		)
	)

	intrRoot=ti.IntrRoot(
		root.frames,
		ti.Group(
			quitButton,
			movement
		)
	)
	statusText.setLingering("Press `ctrl w` to quit",root.frames)
	root.frames.schedule(0,tui.sched.framesLater)

	quitlock.acquire()