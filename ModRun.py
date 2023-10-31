import TermUI as tui 
import TermIntr as ti
from threading import Thread
from time import sleep

executing=False
funge=None
quitLock=None

def runner(delay):
	while executing and quitLock.locked(): #todo: implement using stopwatch
		sleep(delay)
		funge.step()
		renderer()

def run(delay):
	global executing
	if executing: return
	executing=True
	Thread(target=runner,args=(delay,)).start()

def stop():
	global executing
	if not executing: return
	executing=False

listener=None
def modInit(m,config,lock):
	global funge,listener,executing,renderer,quitLock,message
	funge=m.load.funge
	renderer=lambda: m.ui.root.frames.schedule(0,tui.sched.framesLater)
	quitLock=m.quitlock.quitLock
	message=m.statustext.queueText

	rateInput=ti.Textbox("ctrl l",text="15")

	visual=tui.VStack(
		tui.Text("Steps per second:"),
		rateInput,
		tui.Nothing(height=1),
		tui.Text(config["StepKey"]+" anywhere to step"),
		tui.Text(config["RunKey"]+" anywhere to execute/halt")
	)

	sidebar=m.sidebar.Sidebar("Run",visual,rateInput)
	m.sidebar.addSidebar(sidebar)
	
	listener=ti.Listener()
	@listener.handle
	def handler(key):
		global executing
		if key==config["StepKey"]:
			funge.step()
			message("Stepped!")
		elif key==config["RunKey"]:
			if not executing:
				run(1/float(rateInput.text))
				message(f"Execution started at {round(float(rateInput.text))} ticks per second")
			else:
				stop()
				message("Execution stopped!")
	m.ui.addIntr(listener)