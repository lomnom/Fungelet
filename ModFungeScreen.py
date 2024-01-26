import TermUI as tui
import TermIntr as ti
from Befunge import befunge2d as bf

#x and y are canvas coordinates of rendered top left
class BfSpaceDisplay(tui.Element):
	def __init__(
		self,space,where=lambda rx,ry,ph,pw: (0,0), uniqueBg=False,
		markers=[],modifiers=[]
	): 
		self.space=space
		self.where=where
		self.markers=markers
		self.modifiers=modifiers
		self.uniqueBg=uniqueBg

	def size(self):
		return (0,0)

	def render(self,cnv,rx,ry,ph,pw):
		cx,cy=self.where(rx,ry,ph,pw)
		for y in range(ph):
			row=self.space.matrix.get(cy+y)
			if row:
				for x in range(pw):
					character=row.get(cx+x)
					if character is not None:
						rendered=cnv.matrix[ry+y][rx+x]
						if 32<=character<=126: #ascii normal character
							rendered.char=chr(character)
							if self.uniqueBg:
								rendered.bcolor=str(character%256)
						for modifier in self.modifiers:
							modifier(rendered,character,(y,x),(ry+y,rx+x),(cy,cx))

		for markers in self.markers:
			for marker in markers():
				mx,my,func=marker
				if (cx+pw)>mx>=(cx) and (cy+ph)>my>=(cy):
					rendered=cnv.matrix[ry+(my-cy)][rx+(mx-cx)]
					func(rendered)

def originMarker():
	def originMod(char):
		char.flags|={'u'}
	yield (0,0,originMod)

display=None
def modInit(m,config,lock):
	global display
	display=BfSpaceDisplay(m.load.funge.plane)

	config['OriginMarker'] and display.markers.append(originMarker)

	m.ui.addElem(display)