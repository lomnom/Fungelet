import Befunge as bfg
import Funge as fng
import TermIntr as ti
import TermUI as tui

funge=None
pointers=None # 0 has highest priority

focused=None
cursor=None
mvmtCallbacks=[]
def pointerMoved(pointer):
	if pointer is focused:
		cursor.cursor=pointer.pos
		cursor.cursorDelta=pointer.delta

	for cb in mvmtCallbacks:
		cb(pointer)

def focus(pointer):
	focused=pointer

def cursorMoved(c,d):
	if focused:
		focused.pos=c
		focused.delta=d

class BfPointerN(bfg.BfPointer):
	@property
	def pos(self):
		return self._pos

	@pos.setter
	def pos(self,value):
		self._pos=value
		pointerMoved(self)

def pointer():
	return BfPointerN(funge,fng.Vect2d(0,0),fng.Vect2d(1,0),[],[],fng.Vect2d(0,0))

def newPointer():
	p=pointer()
	pointers.append(p)
	return p

def removePointer(p):
	if focused is p:
		unpossess()
	if p in pointers:
		pointers.remove(p)

def reorderPointer(p,i):
	pointers.remove(p)
	pointers.insert(i,p)

def display():
	def mod(char):
		char.flags|={'s','b','r'}
	for pointer in pointers:
		yield (pointer.pos.x,pointer.pos.y,mod) 

possessCb=[]
def possess(pointer):
	global focused
	focused=pointer
	focused.pos=cursor.cursor
	focused.delta=cursor.cursorDelta
	for cb in possessCb:
		cb(pointer)

def unpossess():
	global focused
	focused=None
	for cb in possessCb:
		cb(None)

def pointersAt(pos):
	results=[] #left has highest priority
	for pointer in pointers:
		if pointer.pos==pos:
			results.append(pointer)
	return results

spawnButton=ti.Button("spawn a pointer","S")
@spawnButton.onPress
def spawn(*_):
	new=newPointer()
	possess(new)
	statusText(f"Spawned pointer #{pointers.index(new)}")

possessCounter=0 #so every possess gives a diff pointer if multiple on same tile
possessButton=ti.Button("un/possess a pointer\nbelow the cursor","P")
@possessButton.onPress
def cursorPossess(*_):
	global focused,possessCounter
	if focused:
		unpossess()
		statusText("Unpossessed pointer")
		return
	found=pointersAt(cursor.cursor)
	possessCounter+=1
	if found:
		focused=found[possessCounter%len(found)]
		statusText(f"Possessed pointer #{pointers.index(focused)}")
		possess(focused)
	else:
		statusText("No pointer to possess")

homeIntr=ti.Group(
	spawnButton,
	possessButton
)

homeGroup=tui.VStack(
	spawnButton,
	possessButton
)

class Stack(tui.GenElement): #todo: have a less crude thread safety solution (stack is one render behind)
	def __init__(self,pointer):
		self.pointer=pointer
		self.stack=pointer.stack

	def innards(self):
		stack=self.stack
		numberString=""
		for n in range(len(stack)):
			numberString+=f"#{n+1}\n"
		numberText=tui.Text(numberString[:-1])

		characterString=""
		if stack:
			for item in stack:
				if 32<=item<=126: #ascii normal character
					characterString+="\\"+chr(item)
				elif item==10:
					characterString+="↩" #newline
				else:
					characterString+="`-`"
				characterString+="\n"
		else:
			characterString="Empty stack "
		characterText=tui.Text(characterString[:-1])

		valString=""
		for item in stack:
			valString+=f"{item}\n"
		valText=tui.Text(valString)

		sep=tui.Seperator("vertical",tui.lines.thin.v,style="`").pad(left=1,right=1)
		return tui.HStack(
			numberText,
			sep,
			characterText,
			sep,
			valText
		)

	def render(self,cnv,x,y,ph,pw):
		self.innards().render(cnv,x,y,ph,pw)
		self.stack=self.pointer.stack[:]

class Inspector(tui.GenElement):
	def __init__(self,pointer,collection):
		self.pointer=pointer
		self.collection=collection
		self.stack=Stack(pointer)

	def innards(self):
		alive=self.pointer in self.collection
		if alive:
			header=tui.Text(f"*Pointer #{self.collection.index(self.pointer)}*")
		else:
			header=tui.Text("*Dead pointer*")
		possessed=(tui.Text("(Possessed)") if focused is self.pointer else tui.Nothing())
		physical=tui.Text("At "+str(self.pointer.pos)+", moving "+str(self.pointer.delta))
		stack=tui.VStack(
			tui.Text("*Stack*").align(alignH="middle"),
			self.stack.align(alignH="middle")
		)
		return tui.VStack(
			header,
			possessed,
			physical.pad(bottom=1),
			stack
		)

possessedView=None
def mkInspector(pointer):
	global possessedView
	if pointer==None:
		possessedView=None
	else:
		possessedView=Inspector(pointer,pointers)
possessCb.append(mkInspector)

class InspectorView(tui.GenElement):
	def __init__(self):
		pass

	def innards(self):
		showing=bool(focused)
		if showing:
			return possessedView
		else:
			return tui.Text("Possess a cursor to view\n(In pointers screen)")

killButton=ti.Button("kill possessed",'K')
@killButton.onPress
def kill(*_):
	if focused:
		statusText(f"Pointer killed.")
		removePointer(focused)
	else:
		statusText(f"No pointer possessed!")

def modInit(modules,config,lock):
	global funge,cursor,pointers,statusText
	funge=modules.load.funge
	pointers=funge.pointers
	cursor=modules.cursor
	sidebar=modules.sidebar
	statusText=modules.statustext.queueText

	cursor.addCallback(cursorMoved)

	screen=modules.fungescreen.display
	screen.markers.append(display)

	spawnBar=sidebar.Sidebar("Pointers",homeGroup,homeIntr)
	sidebar.addSidebar(spawnBar)

	# p=newPointer()
	# p.stack=list(bytes("hello world!".encode("ascii")))+[1,2,4,8,16,8,4,2,1]
	inspectorBar=sidebar.Sidebar(
		"Possessed",
		tui.VStack(
			killButton,
			tui.Text("Press w and s to scroll `(w,s)`"),
			(scrollView:=tui.ScrollBox(
				tui.VStack(
					InspectorView(),
					tui.Nothing(height=10)
				),
				style=[False,False,False,True],
				axes=[True,False]
			),100)
		)
		,ti.Group(
			killButton,
			ti.scrollerInput(scrollView.scroller,modules.ui.root.frames,inputs=["w","s",None,None])
		)
	)
	sidebar.addSidebar(inspectorBar)