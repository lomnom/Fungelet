import TermUI as tui
import TermIntr as ti
import Funge as fng
import Befunge as bf

inbox=ti.Textbox("ctrl l",formatters=[ti.asciify])
outbox=tui.Text("\033\033")

clear=ti.Listener()
@clear.handle
def handler(key):
	if key=="C":
		inbox.text=""
	elif key=="c":
		outbox.text='\033\033'

display=tui.ScrollBox(
	tui.VStack(
		tui.Text("Press C to clear `(C)`"),
		tui.Text("*_Input buffer_*"),
		inbox,
		tui.Seperator("horizontal",tui.lines.dotted.h,style="`"),
		tui.Text("Press c to clear `(c)`"),
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
	if (not inbox.text) or (not inbox.text[0].isnumeric()):
		return None
	end=0
	for index,char in enumerate(inbox.text+'L'):
		if not char.isnumeric():
			end=index
			break
	result=inbox.text[:end]
	inbox.text=inbox.text[end:]
	return int(result)

bf.INNUM=inNum 

def inChar():
	if len(inbox.text)>0:
		result=inbox.text[0]
		inbox.text=inbox.text[1:]
		return ord(result)
	else:
		return None
bf.INCHAR=inChar

def modInit(m,config,lock):
	global modules

	intr=ti.Group(
		inbox,
		clear,
		ti.scrollerInput(display.scroller,m.ui.root.frames,inputs=["w","s",None,None])
	)

	modules=m
	sidebar=m.sidebar.Sidebar("IO",display,intr)
	m.sidebar.addSidebar(sidebar)
