#Incomplete

import TermUI as tui 
import TermIntr as ti

class Sidebar:
	def __init__(self,name,visual,interactive):
		self.name=name
		self.visual=visual
		self.interactive=interactive

intr=None
elem=None
scroller=None
def modInit(modules,config,lock):
	intr=ti.Switcher(0,ti.Nothing())
	elem=tui.ElementSwitcher(tui.Nothing())
	scroller=ti.Roller(["Nothing"],0,"horizontal",up=config["next"],down=config["prev"])
	pass