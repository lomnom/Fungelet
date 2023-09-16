from threading import Lock

class CatchLock:
	def __init__(self):
		self._lock=Lock()

	def lock(self):
		if not self._lock.locked():
			self._lock.acquire()

	def unlock(self):
		if self._lock.locked():
			self._lock.release()

	def waitUnlock(self):
		if self._lock.locked():
			self._lock.acquire()
			self._lock.release()

	def locked(self):
		return self._lock.locked()