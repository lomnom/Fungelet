import TermUI as tui
import TermIntr as ti
import Befunge as bf
import Funge as fng

def selectingMod(char,value,subPos,matrix,corners):
	global state
	mx,my=(subPos[1]+corners[1],subPos[0]+corners[0])
	if state=="Selecting":
		start=corner.copy()
		end=cursor.cursor.copy()
		if start.x>end.x:
			start.x,end.x=(end.x,start.x)
		if start.y>end.y:
			start.y,end.y=(end.y,start.y)
		if end.y>=my>=start.y and end.x>=mx>=start.x:
			char.bcolor="27"
		# raise ValueError((mx,my),end,start,subPos,corners)
		# raise ValueError

def selectedMarkers():
	global state,cursor
	if state=="Selected":
		root=cursor.cursor
		for y in range(len(data)):
			for x in range(len(data[0])):
				if data[y][x] is not None:
					def changer(char):
						char.char=chr(data[y][x])
						char.bcolor="27"
						char.fcolor="232"
						# raise TypeError
					yield (root.x+x,root.y+y,changer)

state="None"
corner=None
data=None
def modInit(m,config,lock):
	global cursor
	cursor=m.cursor
	statusText=m.statustext.queueText
	m.fungescreen.display.modifiers.append(selectingMod)
	m.fungescreen.display.markers.append(selectedMarkers)
	listener=ti.Listener()
	@listener.handle
	def handle(key):
		global state,corner,data
		if key==config["GrabKey"]:
			if state=="None":
				corner=cursor.cursor.copy()
				state="Selecting"
				statusText(f"Grabber: *Selecting*")
			elif state=="Selecting":
				matrix=m.load.funge.plane.matrix
				start=corner.copy()
				end=cursor.cursor.copy()
				if start.x>end.x:
					start.x,end.x=(end.x,start.x)
				if start.y>end.y:
					start.y,end.y=(end.y,start.y)
				data=[[None for _ in range(end.x-start.x+1)] for _ in range(end.y-start.y+1)]
				for y in matrix:
					if end.y>=y>=start.y:
						row=matrix[y]
						toClear=[]
						for x in row:
							if end.x>=x>=start.x:
								data[y-start.y][x-start.x]=row[x]
								toClear.append(x)
						for x in toClear:
							del row[x]
				state="Selected"
				statusText(f"Grabber: *Selected* - use *{config['PlaceKey']}* to place or *{config['DropKey']}* to drop")
			elif state=="Selected":
				data=list(zip(*data[::-1]))
				statusText(f"Grabber: *Rotated*") #todo: implement smart rotation
		elif key==config["PlaceKey"] or key==config["DropKey"]:
			if state=="Selected":
				plane=m.load.funge.plane
				for y in range(len(data)):
					for x in range(len(data[0])):
						if data[y][x] is not None:
							plane[fng.Vect2d(cursor.cursor.x+x,cursor.cursor.y+y)]=data[y][x]
				statusText(f"Grabber: *Placed*")
				if key==config["DropKey"]:
					state="None"
					data=None
					statusText(f"Grabber: *Dropped*")
			else:
				statusText("Select something with *ctrl c* first!")

	m.ui.addIntr(listener)