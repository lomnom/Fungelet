import TermUI as tui 
import TermIntr as ti
import TermCanvas as tc

def newSidebar(name):
	textbox=ti.Textbox('a',text=name)
	return modules.sidebar.Sidebar(name,textbox,textbox)

def modInit(m,config,lock):
	global modules
	modules=m

	sidebar=modules.sidebar

	sidebar.addSidebar(newSidebar("test1"))
	t2=newSidebar("test2")
	sidebar.addSidebar(t2)
	t3=newSidebar("Test3")
	sidebar.addSidebar(t3)
	sidebar.deleteSidebar(t3)
	sidebar.addSidebar(newSidebar("test4"))
	sidebar.selectSidebar(t2)