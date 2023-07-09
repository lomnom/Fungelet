from CatchLock import CatchLock
quitLock=None
def modInit(modules,config,lock):
	global quitLock
	quitLock=CatchLock()
	quitLock.lock()