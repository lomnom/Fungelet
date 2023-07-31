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

class SidebarPos(tui.GenElement):
	def __init__(self,scroller):
		self.scroller=scroller

	def innards(self):
		return tui.Text(f"(at {self.scroller.position+1}/{len(self.scroller.values)})")

intrs=None
elems=None
scroller=None
def modInit(modules,config,lock):
	global intrs,elems,scroller
	intrs=ti.Switcher(None)
	elems=tui.ElementSwitcher(visible=None)
	scroller=ti.Roller([],0,"horizontal",up=config["next"],down=config["prev"])
	tracker=SidebarPos(scroller)

	@scroller.onChange
	def scroll(pos,val):
		intrs.select(pos)
		elems.switchTo(pos)

	modules.ui.addElem(
		tui.VStack(
			tui.HStack(
				tui.Text("*|Sidebars|*").pad(right=1),
				tracker
			).align(alignH="middle"),
			scroller.align(alignH="middle")
				.pad(right=2,left=2),
			tui.Seperator("horizontal",tui.lines.dotted.h,style="`")
				.pad(left=1,right=1),
			elems
				.pad(left=2,right=2)
		).align(alignH="right")
	)

	modules.ui.addIntr(scroller)
	modules.ui.addIntr(intrs)
	pass