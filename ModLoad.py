import TermUI as tui 
import TermIntr as ti
import TermCanvas as tc
import Funge as fng
import Befunge as bng
import pathlib
from sys import argv

fileIn=ti.Textbox("ctrl l")
loadButton=ti.Button("load","L")
saveButton=ti.Button("save","S")
clearButton=ti.Button("clear","C")
killButton=ti.Button("kill","K")

onLoad=[]
onSave=[]

interactives=ti.Group(
	clearButton,
	fileIn,
	loadButton,
	saveButton,
	killButton
)
visual=tui.VStack(
	tui.HStack(
		tui.Text("File: "),
		fileIn
	),
	loadButton,
	saveButton,
	clearButton,
	killButton
)

funge=None

def loadBf(text,plane,sx,sy):
	for row,line in enumerate(text.split("\n")):
		for x,char in enumerate(line):
			if char!=' ':
				plane[fng.Vect2d(x+sx,row+sy)]=ord(char)

def dumpBf(plane):
	if not plane.matrix:
		return ""
	output=""
	corner,size=plane.limits()
	leftmost=min([min(row) for row in plane.matrix.values()])
	for y in range(corner.y,corner.y+size.y):
		prevX=leftmost-1
		row=plane.matrix.get(y)
		if row:
			for x in sorted(row.keys()):
				output+=" "*((x-prevX)-1)
				output+=chr(row[x]) if row[x]>0 else "!"
				prevX=x
		output+="\n"
	return output[:-1]

loadTries=0
@loadButton.onPress
def load(*args): #todo: spawn relative to cursor
	global funge,loadTries
	loadTries+=1
	if len(funge.plane.matrix)>0 and loadTries!=3:
		modules.statustext.queueText(f"Plane not empty! Press {3-loadTries} more times to confirm load!")
		return
	loadTries=0
	file=runpath+"/"+fileIn.text

	try:
		cont=open(file,'r').read()
	except:
		modules.statustext.queueText(f"File '*{file}*' inaccessible!")
		return

	funge.plane.clear()
	loadBf(cont,funge.plane,0,0)

	modules.statustext.queueText(f"Loaded file '*{file}*'")
	for cb in onLoad:
		cb(file)

@saveButton.onPress
def save(*args):
	global funge
	file=runpath+"/"+fileIn.text
	if len(funge.plane.matrix)==0:
		modules.statustext.queueText(f"Plane empty! Save stopped for safety!")
		return
	data=dumpBf(funge.plane)
	open(file,'w').write(data)
	modules.statustext.queueText(f"Saved file *{file}*")
	for cb in onSave:
		cb(file)

clearTries=0
@clearButton.onPress
def clear(*args):
	global clearTries
	clearTries+=1
	if clearTries==5:
		funge.plane.matrix.clear()
		modules.statustext.queueText("Cleared!")
		clearTries=0
	else:
		modules.statustext.queueText(f"Press {5-clearTries} more times to clear")

killTries=0
@killButton.onPress
def kill(*args):
	global killTries
	killTries+=1
	if killTries==2:
		funge.pointers.clear()
		modules.statustext.queueText("Killed!")
		killTries=0
	else:
		modules.statustext.queueText(f"Press {2-killTries} more times to clear")

def modInit(m,config,lock):
	global funge,modules,sidebar,runpath
	modules=m
	runpath=config["RunPath"]
	here=pathlib.Path(config["RunPath"])
	here=list(here.glob("*.b98"))
	if len(here)==1:
		fileIn.text=str(here[0]).split("/")[-1]

	funge=fng.Funge([],fng.Space2d(),bng.befunge2d)

	sidebar=m.sidebar.Sidebar("File",visual,interactives)
	m.sidebar.addSidebar(sidebar)

	if len(argv)>1:
		if argv[1] in ["-h","--help","-help"]:
			cont=open("Tutorial.b98",'r').read()
			loadBf(cont,funge.plane,0,0)
			modules.statustext.queueText("Tutorial opened.")
		else:
			file=runpath+"/"+argv[1]
			try:
				cont=open(file,'r').read()
			except:
				modules.statustext.queueText(f"File '*{file}*' inaccessible!")
				return
			loadBf(cont,funge.plane,0,0)
			modules.statustext.queueText(f"{file} opened.")
			fileIn.text=argv[1]