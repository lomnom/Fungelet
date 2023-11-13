from yaml import safe_load as load
from Modules import *
from CatchLock import CatchLock
import os

runpath = os.path.abspath(".")

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

toLoad=load(open("Modules.yaml").read())
configs=load(open("Config.yaml").read())
prefix=toLoad['prefix']

objects=[__import__(prefix+name) for name in toLoad['modules']]
modules=Modules(prefix=prefix)
lock=CatchLock() #catchlock unlocked when all modules are loaded
lock.lock()
calls=[]

for module in objects:
	modules.add(module)
	name=module.__name__[len(prefix):]
	if name in configs:
		config=configs[name]
	else:
		config={}
	config["RunPath"]=str(runpath)
	call=module.modInit(modules,config,lock)
	if call:
		calls.append(call)

lock.unlock()

for call in calls:
	call(modules)
