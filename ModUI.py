import TermUI as tui
import TermCanvas as tc
import Terminal as trm
import TermIntr as ti
from threading import Thread,Lock

thread=None
root=None
stack=tui.ZStack()
intr=ti.Group()

def addElem(element):
	stack.insertChild(element,0)
	root.frames.schedule(0,tui.sched.framesLater)

def removeElem(element):
	stack.disownChild(element)
	root.frames.schedule(0,tui.sched.framesLater)

def addIntr(added):
	intr.addIChild(added)

def removeIntr(added):
	intr.orphanIChild(added)

def modInit(modules,config,lock):
	global thread,explosionKey
	completed=Lock()
	completed.acquire()

	tc.NOCTRLC_CANVAS=not config["CtrlCSigint"]

	def main(cnv):
		global root,stack,intr
		nonlocal modules,completed
		root=tui.Root(
			cnv,
			stack
		)

		intrRoot=ti.IntrRoot(
			root.frames,
			intr
		)

		completed.release()
		modules.quitlock.quitLock.waitUnlock()

	thread=Thread(target=tc.canvasApp,args=(main,))
	thread.start()
	completed.acquire()

	addElem(tui.FrameRoller().align(alignV="bottom",alignH="right"))

	explosionKey=ti.Button("explode",config["ExplosionKey"])
	addIntr(explosionKey)

	@explosionKey.onToggle
	def boom(*_):
		raise StopIteration