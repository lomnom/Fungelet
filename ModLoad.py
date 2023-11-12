import TermUI as tui 
import TermIntr as ti
import TermCanvas as tc
import Funge as fng
import Befunge as bng
import pathlib

fileIn=ti.Textbox("ctrl l")
loadButton=ti.Button("load","L")
saveButton=ti.Button("save","S")
clearButton=ti.Button("clear","C")

onLoad=[]
onSave=[]

interactives=ti.Group(
	clearButton,
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
	saveButton,
	clearButton
)

funge=None

def loadBf(text,plane,sx,sy):
	for row,line in enumerate(text.split("\n")):
		for x,char in enumerate(line):
			if char!=' ':
				plane[fng.Vect2d(x+sx,row+sy)]=ord(char)

def dumpBf(plane):
	output=""
	corner,size=plane.limits()
	for y in range(corner.y,corner.y+size.y):
		prevX=-1
		row=plane.matrix.get(y)
		if row:
			for x in sorted(row.keys()):
				output+=" "*((x-prevX)-1)
				output+=chr(row[x])
				prevX=x
		output+="\n"
	return output[:-1]

@loadButton.onPress
def load(*args): #todo: spawn relative to cursor
	global funge
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

tries=0
@clearButton.onPress
def clear(*args):
	global tries
	tries+=1
	if tries==5:
		funge.plane.matrix.clear()
		modules.statustext.queueText("Cleared!")
		tries=0
	else:
		modules.statustext.queueText(f"Press {5-tries} more times to clear")

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