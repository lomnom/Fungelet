import TermUI as tui
import TermIntr as ti
import Funge as f3e
from Befunge import befunge2d as bf
colorScheme={
	'Termination':"1", 
	'Delta': "2",
	'Delta+': "3", 
	'Logic':"4",
	'Position':"5", 
	'Math':"6", 
	'Value':"7", 
	'Stack':"159",
	'Nothing':"8", 
	'I/O':"214",

	'Funge Space':"11",  
	'Debug':"12", 
	'Strings':"13", 
	'Concurrency':"10", 
	'Repetition':"15", 
}

class BfSpaceDisplay(tui.Element):
	def __init__(self,space,where=lambda rx,ry,ph,pw: (-10,-5),markers=lambda: []): #x and y are canvas coordinates of rendered top left
		self.space=space
		self.where=where
		self.markers=markers

	def size(self):
		return (0,0)

	def render(self,cnv,rx,ry,ph,pw):
		cx,cy=self.where(rx,ry,ph,pw)
		for y in range(ph):
			row=self.space.matrix.get(cy+y)
			if row:
				for x in range(pw):
					character=row.get(cx+x)
					if character:
						rendered=cnv.matrix[ry+y][rx+x]
						rendered.char=chr(character)
						if character in bf:
							instruction=bf[character]
							rendered.fcolor=colorScheme[instruction.theme]
		for marker in self.markers():
			mx,my,func=marker
			if (cx+pw)>mx>=(cx) and (cy+ph)>my>=(cy):
				rendered=cnv.matrix[ry+(my-cy)][rx+(mx-cx)]
				func(rendered)