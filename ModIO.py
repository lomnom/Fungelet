import TermUI as tui
import TermIntr as ti
import Funge as fng
import Befunge as bf

inbox=ti.Textbox("ctrl l",formatters=[ti.asciify])
outbox=tui.Text("\033\033")

clearInput=ti.Button("clear","C")
@clearInput.onToggle
def handler(_):
	inbox.text=""

clearOutput=ti.Button('clear',"c")
@clearOutput.onToggle
def handler(_):
	outbox.text='\033\033'

display=tui.ScrollBox(
	tui.VStack(
		clearInput,
		tui.Text("*_Input buffer_*"),
		inbox,
		tui.Seperator("horizontal",tui.lines.dotted.h,style="`"),
		clearOutput,
		tui.Text("*_Output buffer_*"),
		outbox,
		tui.Text("Press w and s to scroll `(w,s)` ")
			.pad(top=1)
	),
	style=[False,False,False,True],
	axes=[True,False]
)

def print(msg):
	global stuff
	if type(msg) is str:
		outbox.text=outbox.text[:-1]+ti.asciify(msg)+"\033"
	else:
		outbox.text=outbox.text[:-1]+ti.asciify(repr(msg))+"\n"+"\033"
		pass

bf.stdout=print

def inNum():
	result=""
	start=None
	for index,char in enumerate(inbox.text):
		if char.isnumeric():
			start=index
			break
	if start==None:
		return None
	end=start+1
	for index,char in enumerate(inbox.text[start:]+'L'):
		if not char.isnumeric():
			end=index+start
			break
	result=inbox.text[start:end]
	inbox.text=inbox.text[:start]+inbox.text[end:]
	return int(result)

blockingInput=None

def bfInNum():
	result=inNum()
	if result==None:
		if blockingInput:
			raise bf.FungeExitedException(input)
		else:
			return None
	else:
		return result

bf.INNUM=bfInNum 

def inChar():
	if len(inbox.text)>0:
		result=inbox.text[0]
		inbox.text=inbox.text[1:]
		return ord(result)
	else:
		return None

def bfInChar():
	result=inChar()
	if result==None:
		if blockingInput:
			raise bf.FungeExitedException(input)
		else:
			return None
	else:
		return result

bf.INCHAR=bfInChar

def modInit(m,config,lock):
	global modules,bl,blockingInput

	blockingInput=bool(config["BlockingInput"])
	def inputNotify(e,tick):
		if e.args[0]==input:
			m.statustext.queueText("Input required! Restart execution once entered!")

	m.run.endCalls.append(inputNotify)

	intr=ti.Group(
		inbox,
		clearOutput,
		clearInput,
		ti.scrollerInput(display.scroller,m.ui.root.frames,inputs=["w","s",None,None])
	)

	modules=m
	sidebar=m.sidebar.Sidebar("IO",display,intr)
	m.sidebar.addSidebar(sidebar)
