import TermUI as tui
import TermIntr as ti
import TermCanvas as tc
import Befunge as bfg
import Funge as fng

cursor=fng.Vect2d(0,0)
cursorDelta=fng.Vect2d(1,0)
instrs=bfg.befunge2d

def updateInfo(delta,coords,plane,instrs):
	statusText.setLingering(f"At ({coords.x},{coords.y}), moving ({delta.x},{delta.y})")
	try:
		statusText.queueText(instrs[plane[coords]].description)
	except KeyError:
		statusText.clear(root.frames)

movement=ti.Listener()
@movement.handle
def key(key):
	global cursor,cursorDelta
	root.frames.schedule(
		1,tui.sched.framesLater
	)
	if key==cfg["Step"]:
		try:
			cursorDelta,cursor=fng.nextPlaces(cursor,cursorDelta,instrs,plane)[0]
		except:
			pass
		updateInfo(cursorDelta,cursor,plane,instrs)
		return
	elif key==cfg["Up"]:
		cursorDelta=fng.Vect2d(0,-1)
	elif key==cfg["Down"]:
		cursorDelta=fng.Vect2d(0,1)
	elif key==cfg["Left"]:
		cursorDelta=fng.Vect2d(-1,0)
	elif key==cfg["Right"]:
		cursorDelta=fng.Vect2d(1,0)
	else:
		return
	cursor+=cursorDelta
	updateInfo(cursorDelta,cursor,plane,instrs)

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