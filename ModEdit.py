import Befunge as bfg
import Funge as fng
import TermIntr as ti
import TermUI as tui

plane=None
cursor=None

moveButton=ti.Button("toggle automove","tab",toggle=True,activated=True)
listener=ti.Listener()
@listener.handle
def handler(key):
	if len(key)==1:
		if key=="\n":
			return
		else:
			plane[cursor.cursor]=ord(key)
			if moveButton.activated and not cursor.step(certain=True):
				cursor.cursor+=cursor.cursorDelta
	elif key=="backspace":
		if moveButton.activated:
			if plane[cursor.cursor]==plane.defaultValue:
				cursor.cursor-=cursor.cursorDelta
				if plane[cursor.cursor]==plane.defaultValue:
					cursor.cursor+=cursor.cursorDelta
		del plane[cursor.cursor]
	cursor.updateInfo(cursor.cursorDelta,cursor.cursor)

valueButton=ti.Button("put value","ctrl k")
valueBox=ti.Textbox("ctrl l",text="")

statusText=None
@valueButton.onPress
def putDown(*_):
	try:
		plane[cursor.cursor]=int(valueBox.text)
		cursor.updateInfo(cursor.cursorDelta,cursor.cursor)
	except ValueError:
		statusText(f"Invalid number '{valueBox.text}'!")

stack=tui.VStack(
	tui.Text("Type to put tile down!")
		.pad(bottom=1),
	moveButton,
	valueButton,
	tui.HStack(
		tui.Text("*value -> *"),
		valueBox
	),
)
intr=ti.Group(
	listener,
	valueBox,
	valueButton,
	moveButton
)

def modInit(m,config,lock):
	global plane,cursor,statusText
	plane=m.load.funge.plane
	cursor=m.cursor
	statusText=m.statustext.queueText

	sidebar=m.sidebar.Sidebar("Editor",stack,intr)

	def prioritise(m):
		m.sidebar.addSidebar(sidebar)

	return prioritise