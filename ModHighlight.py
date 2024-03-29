import TermUI as tui
import TermIntr as ti
from Befunge import befunge2d as bf

#todo: ignore quotes?

flashingQuestionMark=None
def highlightMod(rendered,character,*args):
	instr=bf.get(ord(rendered.char))
	if character in bf:
		rendered.fcolor=scheme[instr.theme]
	elif not 32<=character<=126: #ascii normal character
		if flashingQuestionMark:
			rendered.char="?"
			rendered.flags|={'f'}
		rendered.bcolor=str(character%255+1)
		rendered.flags|={'i'}

enabled=None

def disable(quiet=False):
	global enabled
	modules.fungescreen.display.modifiers.remove(highlightMod)
	modules.ui.root.frames.schedule(0,tui.sched.framesLater)
	quiet or modules.statustext.queueText("Highlighting disabled")
	enabled=False

def enable(quiet=False):
	global enabled
	modules.fungescreen.display.modifiers.append(highlightMod)
	modules.ui.root.frames.schedule(0,tui.sched.framesLater)
	quiet or modules.statustext.queueText("Highlighting enabled")
	enabled=True

toggle=ti.Listener()
@toggle.handle
def key(key):
	global enabled
	if key=="ctrl h":
		if enabled:
			disable()
		else:
			enable()

scheme=None
def modInit(m,config,lock):
	global scheme,modules,enabled,flashingQuestionMark
	modules=m
	enabled=config["DefaultEnable"]
	scheme=config["Scheme"]
	flashingQuestionMark=config["FlashingQuestionMark"]

	m.ui.addIntr(toggle)

	if enabled:
		enable(quiet=True)
	else:
		disable(quiet=True)