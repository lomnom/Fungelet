class Modules:
	def __init__(self,modules=None,prefix=''):
		if modules is None:
			self.modules={}
		else:
			self.modules=modules
		self.prefix=prefix

	def add(self,module):
		assert(module.__name__.startswith(self.prefix))
		self.modules[module.__name__[len(self.prefix):].lower()]=module

	def __getattr__(self,name):
		return self.modules[name]