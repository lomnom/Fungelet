import Befunge as bfg
import Funge as fng

funge=None
pointers=set()

focused=None
cursor=None
mvmtCallbacks=[]
def pointerMoved(pointer):
	if pointer is focused:
		cursor.cursor=pointer.pos
		cursor.cursorDelta=pointer.delta

	for cb in mvmtCallbacks:
		cb(pointer)

def cursorMoved(c,d):
	if focused:
		focused.pos=c
		focused.delta=d

class BfPointerN(bfg.BfPointer):
	@property
	def pos(self):
		return self._pos

	@pos.setter
	def posSetter(self,value):
		self._pos=value
		pointerMoved(self)

def newPointer():
	pointers.add((p:=
		bfg.BfPointer(funge,fng.Vect2d(0,0),fng.Vect2d(1,0),[],[],fng.Vect2d(0,0))
	))
	return p

def removePointer(p):
	pointers.remove(p)

def addPointer(p):
	pointers.add(p)

def display():
	def mod(char):
		char.flags|={'s','b','r'}
	for pointer in pointers:
		yield (pointer.pos.x,pointer.pos.y,mod) 

def modInit(modules,config,lock):
	global funge,cursor
	funge=modules.load.funge
	cursor=modules.cursor

	cursor.addCallback(cursorMoved)

	screen=modules.fungescreen.display
	screen.markers.append(display)

	