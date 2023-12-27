import TermUI as tui 
import TermIntr as ti
from threading import Thread
from time import sleep
import Befunge as bf
import Terminal as trm

executing=False
funge=None
quitLock=None

endCalls=[lambda e,tick: message(f"Execution ended after {tick} ticks with {e.args}")]

ceil=lambda n: round(n+0.5)
def runner(delay,renderSpace=0.05): #time between render calls
	global executing
	stopwatch=trm.Stopwatch()
	tick=0
	frameDelay=ceil(renderSpace/delay)
	stopwatch.start()
	try:
		while executing and quitLock.locked(): #todo: implement using stopwatch
			tick+=1
			for pointer in funge.pointers[:]:
				if not executing:
					break
				pointer.step()

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
	except bf.FungeExitedException as e:
		for call in endCalls:
			call(e,tick)
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
			message("Stepped!")
		elif key==config["RunKey"]:
			if not executing:
				message(f"Execution started at {round(float(rateInput.text))} ticks per second")
				run(1/float(rateInput.text))
			else:
				stop()
				message("Execution stopped!")
				m.ui.root.frames.schedule(3,tui.sched.framesLater)
	m.ui.addIntr(listener)