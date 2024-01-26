import TermUI as tui
import TermIntr as ti
import TermCanvas as tc
import Befunge as bfg
import Funge as fng

cursor=fng.Vect2d(0,0)
cursorDelta=fng.Vect2d(1,0)
instrs=bfg.befunge2d

def updateInfo(delta,coords):
	statusText.setLingering(f"At ({coords.x},{coords.y}) = {plane[coords]}, moving ({delta.x},{delta.y})")
	try:
		statusText.queueText("\033"+instrs[plane[coords]].description+"\033")
	except KeyError:
		statusText.clear()

def goto(c,d):
	global cursorDelta, cursor
	cursorDelta=d
	cursor=c
	updateInfo(cursorDelta,cursor)
	for callback in callbacks:
		callback(c,d)

def step(certain=False):
	places=list(instrs[plane[cursor]].transforms(cursorDelta.copy(),cursor.copy(),plane))
	if len(places)==0:
		return True
	if len(places)>1 and certain:
		return True
	d,c=places[0]
	moved=c!=cursor
	goto(c,d)
	return moved

movement=ti.Listener()
@movement.handle
def key(key):
	global cursor
	if key==cfg["Step"]:
		step(certain=True)
		root.frames.schedule(
			1,tui.sched.framesLater
		)
		return
	elif key==cfg["Up"]:
		d=fng.Vect2d(0,-1)
	elif key==cfg["Down"]:
		d=fng.Vect2d(0,1)
	elif key==cfg["Left"]:
		d=fng.Vect2d(-1,0)
	elif key==cfg["Right"]:
		d=fng.Vect2d(1,0)
	else:
		return
	root.frames.schedule(
		1,tui.sched.framesLater
	)
	c=d+cursor
	goto(c,d)

callbacks=[]
def addCallback(cb):
	global callbacks
	callbacks.append(cb)

def removeCallback(cb):
	callbacks.remove(cb)

def cursorCenter(x,y,ph,pw): #align canvas so cursor is in middle
	return (cursor.x-(pw//2),cursor.y-(ph//2))

def cursorMarker():
	def cursorMod(char):
		char.flags|={'r'}
	yield (cursor.x,cursor.y,cursorMod)

def modInit(m,config,lock):
	global modules,statusText,plane,cfg,root
	root=m.ui.root
	cfg=config
	modules=m
	plane=modules.load.funge.plane
	statusText=modules.statustext

	modules.fungescreen.display.where=cursorCenter
	modules.fungescreen.display.markers.append(cursorMarker)

	modules.ui.addIntr(movement)