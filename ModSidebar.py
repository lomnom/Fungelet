import TermUI as tui 
import TermIntr as ti
import TermCanvas as tc

class Sidebar:
	def __init__(self,name,visual,interactive):
		self.name=name
		self.visual=visual
		self.intr=interactive

def addSidebar(sidebar):
	index=elems.visible
	intrs.addIChild(sidebar.intr)
	elems.addChild(sidebar.visual)
	scroller.addValue(sidebar.name)

	if index is None:
		selectSidebar(sidebar)

def deleteSidebar(sidebar):
	index=elems.children.index(sidebar.visual)

	scroller.removeIndex(index)
	intrs.orphanIChild(sidebar.intr)
	elems.disownChild(sidebar.visual)

def selectSidebar(sidebar):
	index=elems.children.index(sidebar.visual)
	selectSidebarI(index)

def selectSidebarI(index):
	scroller.setPosition(index)
	intrs.select(index)
	elems.switchTo(index)

intrs=None
elems=None
scroller=None
def modInit(modules,config,lock):
	global intrs,elems,scroller
	intrs=ti.Switcher(None)
	elems=tui.ElementSwitcher(visible=None)
	scroller=ti.Roller([],0,"horizontal",up=config["next"],down=config["prev"])

	@scroller.onChange
	def scroll(pos,val):
		intrs.select(pos)
		elems.switchTo(pos)

	modules.ui.addElem(
		tui.HStack(
			tui.Seperator("vertical",tui.lines.dotted.v),
			tui.VStack(
				scroller.align(alignH="middle").pad(right=2,left=2),
				elems.align(alignH="middle")
			).align(alignH="middle")
		).align(alignH="right")
	)

	modules.ui.addIntr(scroller)
	modules.ui.addIntr(intrs)
	pass