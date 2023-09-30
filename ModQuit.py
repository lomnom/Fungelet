import TermIntr as ti
import TermUI as tui

quitCallbacks=[]
welcomeText=" Press *ctrl right* to edit!"

def modInit(modules,config,lock):
	listener=ti.Listener()
	quitKey=config["quitKey"]
	@listener.handle
	def handle(key):
		if key==quitKey:
			nonlocal modules
			for callback in quitCallbacks:
				if not callback():
					return 
			modules.quitlock.quitLock.unlock()

	modules.ui.addIntr(listener)
	modules.statustext.queueText("Press *ctrl w* to quit!"+welcomeText)