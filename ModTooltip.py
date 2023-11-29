import TermUI as tui
import TermIntr as ti
import Befunge as bf

class Tooltip(tui.Element):
	def __init__(self,instrSet,x,y,highlight):
		instrs={}
		for key in instrSet:
			instr=instrSet[key]
			if instr.theme in instrs:
				instrs[instr.theme].append(instr)
			else:
				instrs[instr.theme]=[instr]
		instrs=list(instrs.values())

		cats=[]
		for cat in instrs:
			row="".join([instr.symbol for instr in cat])
			if len(row)>12:
				temp=[]
				while row:
					temp.append(row[:8])
					row=row[8:]
				cats.append(temp)
			else:
				cats.append([row])
		cats.sort(key=lambda cat: max([len(row) for row in cat]),reverse=True)
		string=[]
		for cat in cats:
			for row in cat:
				string.append(row)
		self.string=string
		self.instrs=instrSet
		self.text=tui.Text("%_\033"+"\n".join(string)+"\033_%",inc=(0,1),newline=(1,0))
		self.x=x
		self.y=y
		self.highlight=highlight

	def size(self):
		return self.text.size()

	def render(self,cnv,x,y,h,w):
		self.text.render(cnv,x,y,h,w)
		cnv.matrix[y+self.y][x+self.x].flags^={'r'}
		for cx in range(x,x+len(self.string)):
			for cy in range(y,y+len(self.string[cx-x])):
				self.highlight(cnv.matrix[cy][cx],ord(self.string[cx-x][cy-y]))

tooltip=None
element=None
listener=None
shown=False

def modInit(m,config,lock):
	global tooltip,element,listener,shown
	tooltip=Tooltip(bf.befunge2d,0,0,m.highlight.highlightMod)
	element=tui.VStack(
		tui.VStack(
			tooltip
		).pad(left=1,right=1)
		 .alter({
		 	"flags":lambda char,x,y: char.flags|{'d'}
		 },before=False)
		 .box(tui.lines.thick,label="Tiles",style="*"),
		 tui.Nothing(1,0)
	).align(alignV="bottom")

	listener=ti.Listener()
	@listener.handle
	def handle(key):
		global shown
		if key==config["TipKey"]:
			if shown:
				m.ui.removeElem(element) #remove
				m.ui.addIntr(m.cursor.movement)
				shown=False
			else:
				m.ui.addElem(element,-1)
				m.ui.removeIntr(m.cursor.movement)
				m.statustext.queueText("*ctrl l* to exit or *enter* to choose.")
				shown=True
		elif shown:
			oldx=tooltip.x
			oldy=tooltip.y
			if key==config["Place"]:
				m.load.funge.plane[m.cursor.cursor]=ord(tooltip.string[tooltip.x][tooltip.y])
				m.statustext.queueText("Placed instruction.")
			elif key==config["_"]["Cursor"]["Up"]:
				tooltip.y-=1
			elif key==config["_"]["Cursor"]["Down"]:
				tooltip.y+=1
			elif key==config["_"]["Cursor"]["Left"]:
				tooltip.x-=1
			elif key==config["_"]["Cursor"]["Right"]:
				tooltip.x+=1
			if 0>tooltip.x or tooltip.x>=len(tooltip.string) or 0>tooltip.y or tooltip.y>=len(tooltip.string[tooltip.x]):
				tooltip.x=oldx
				tooltip.y=oldy
			instr=bf.befunge2d[ord(tooltip.string[tooltip.x][tooltip.y])]
			m.statustext.queueText(f"*[{instr.theme}]* - \033{instr.description} \033")
			m.ui.root.frames.schedule(
				1,tui.sched.framesLater
			)

	m.ui.addIntr(listener)