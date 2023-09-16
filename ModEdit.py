import Befunge as bfg
import Funge as fng
import TermIntr as ti
import TermUI as tui

plane=None
cursor=None

listener=ti.Listener()
@listener.handle
def handler(key):
	if len(key)==1:
		if key=="\n":
			return
		else:
			plane[cursor.cursor]=ord(key)
			if not cursor.step():
				cursor.cursor+=cursor.cursorDelta
	elif key=="backspace":
		if plane[cursor.cursor]==plane.defaultValue:
			cursor.cursor-=cursor.cursorDelta
			if plane[cursor.cursor]==plane.defaultValue:
				cursor.cursor+=cursor.cursorDelta
		del plane[cursor.cursor]

valueButton=ti.Button("put value","ctrl k")
valueBox=ti.Textbox("ctrl l",text="123")

stack=tui.VStack(
	tui.Text("Type to put tile down!")
		.pad(bottom=1),
	valueButton,
	tui.HStack(
		tui.Text("*value -> *"),
		valueBox
	),
)
intr=ti.Group(
	listener,
	valueBox,
	valueButton
)

def modInit(m,config,lock):
	global plane,cursor
	plane=m.load.funge.plane
	cursor=m.cursor

	sidebar=m.sidebar.Sidebar("Editor",stack,intr)
	m.sidebar.addSidebar(sidebar)