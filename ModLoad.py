import TermUI as tui 
import TermIntr as ti
import TermCanvas as tc
import Funge as fng
import Befunge as bng
import pathlib

fileIn=ti.Textbox("ctrl l")
loadButton=ti.Button("load","L")
saveButton=ti.Button("load","S")

onLoad=[]
onSave=[]

interactives=ti.Group(
	fileIn,
	loadButton,
	saveButton
)
visual=tui.VStack(
	tui.HStack(
		tui.Text("File: "),
		fileIn
	),
	loadButton,
	saveButton
)

funge=None

def loadBf(text,plane,sx,sy):
	for row,line in enumerate(text.split("\n")):
		for x,char in enumerate(line):
			if char!=' ':
				plane[fng.Vect2d(x+sx,row+sy)]=ord(char)

@loadButton.onPress
def load(*args):
	global funge
	file=fileIn.text

	funge.plane.clear()
	loadBf(open(file,'r').read(),funge.plane,0,0)

	modules.statustext.queueText(f"Loaded file *{file}*")
	for cb in onLoad:
		cb(file)

@saveButton.onPress
def save(*args):
	global funge
	tlc,size=funge.limits()[0]
	file=fileIn.text

	raise NotImplementedError
	
	for cb in onSave:
		cb(file)

def modInit(m,config,lock):
	global funge,modules
	modules=m
	here=pathlib.Path(".")
	here=list(here.glob("*.b98"))
	if len(here)==1:
		fileIn.text=str(here[0])

	funge=fng.Funge([],fng.Space2d(),bng.befunge2d)

	sidebar=m.sidebar.Sidebar("File",visual,interactives)
	m.sidebar.addSidebar(sidebar)