from yaml import safe_load as load
from Modules import *
from CatchLock import CatchLock

toLoad=load(open("Modules.yaml").read())
configs=load(open("Config.yaml").read())
prefix=toLoad['prefix']

objects=[__import__(prefix+name) for name in toLoad['modules']]
modules=Modules(prefix=prefix)
lock=CatchLock() #catchlock unlocked when all modules are loaded
lock.lock()

for module in objects:
	modules.add(module)
	name=module.__name__[len(prefix):]
	if name in configs:
		config=configs[name]
	else:
		config={}
	module.modInit(modules,config,lock)

lock.unlock()
