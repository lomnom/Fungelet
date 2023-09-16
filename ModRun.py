import TermUI as tui 
import TermIntr as ti
from threading import Thread

#todo: stimulation async in another thread
#todo: statusText
#todo: step buttons c+r c+x

executing=False

def run(rate):
	pass

listener=None
def modInit(m,config,lock):
	global funge,listener,executing
	funge=m.load.funge

	rateInput=ti.Textbox("ctrl l",text="15")

	visual=tui.VStack(
		tui.Text("Steps per second:"),
		rateInput,
		tui.Nothing(height=1),
		tui.Text(config["StepKey"]+" anywhere to step"),
		tui.Text(config["RunKey"]+" anywhere to execute/halt")
	)

	sidebar=m.sidebar.sidebar("Run",visual,rateInput)
	
	listener=ti.Listener()
	@listener.handle
	def handler(key):
		if key==config["StepKey"]:
			funge.step()
		elif key==config["RunKey"]:
			pass