from yaml import safe_load as load
from Modules import *
from threading import Lock

config=load(open("Modules.yaml").read())
prefix=config['prefix']

objects=[__import__(prefix+name) for name in config['modules']]
modules=Modules(prefix=prefix)
lock=Lock()
lock.acquire()

for module in objects:
	modules.add(module)
	module.modInit(modules,lock)

lock.release()

print(modules.select.LMAO)