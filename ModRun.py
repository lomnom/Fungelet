import TermUI as tui 
import TermIntr as ti
from threading import Thread
from time import sleep
import Befunge as bf
import Terminal as trm

executing=False
funge=None
quitLock=None

endCalls=[
	lambda e,tick: message(
		f"Execution ended after {tick} ticks with {e.args}" if e else f"Execution stopped after {tick} ticks"
	) if tick>=0 else "Stepped!"
]

ceil=lambda n: round(n+0.5)
stopped=None
def runner(delay,renderSpace=0.05): #time between render calls
	global executing,stopped
	stopwatch=trm.Stopwatch()
	tick=0
	frameDelay=ceil(renderSpace/delay)
	stopwatch.start()
	exception=None # becomes something when ending
	while executing and quitLock.locked():
		tick+=1
		for pointer in (funge.pointers[funge.pointers.index(stopped):] if stopped and stopped in funge.pointers else funge.pointers[:]):
			try:
				pointer.step()
			except bf.FungeExitedException as e:
				exception=e
				stopped=pointer
				break
		if exception:
			break
		stopped=None

		if (tick%frameDelay)==0:
			renderer()

		wait=(tick*delay)-stopwatch.time()
		if wait>=0:
			sleep(wait)
		else:
			if (tick%(frameDelay*5))==0:
				time=round(-wait*10000)/10
				if time>0:
					message(f"Execution behind by {time}ms")
	for call in endCalls:
		call(exception,tick)
	executing=False
	stopwatch.stop()

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
	global funge,listener,executing,renderer,quitLock,message,frames
	funge=m.load.funge
	frames=m.ui.root.frames
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
			try:
				funge.step()
			except bf.FungeExitedException as e:
				for call in endCalls:
					call(e,-1)
			m.ui.root.frames.schedule(2,tui.sched.framesLater)
		elif key==config["RunKey"]:
			if not executing:
				message(f"Execution started at {round(float(rateInput.text))} ticks per second")
				run(1/float(rateInput.text))
			else:
				stop()
				m.ui.root.frames.schedule(3,tui.sched.framesLater)
	m.ui.addIntr(listener)