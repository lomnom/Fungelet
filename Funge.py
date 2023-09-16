class Coord: # location on an infinite plane
	def __add__(self,other):
		raise NotImplementedError

	def __sub__(self,other):
		return self+(-other)

	def __neg__(self): # invert on all axes
		raise NotImplementedError

	def __mul__(self,val):
		raise NotImplementedError

	def copy(self):
		raise NotImplementedError

	def __hash__(self):
		raise NotImplementedError

	def __eq__(self):
		raise NotImplementedError

	def __lt__(self):
		raise NotImplementedError

	def __gt__(self):
		raise NotImplementedError

class Space: # fungespace
	defaultValue=None #value of empty cell
	def __getitem__(self,coord):
		raise NotImplementedError

	def __setitem__(self,coord,value):
		raise NotImplementedError

	def __delitem__(self,coord):
		raise NotImplementedError

	def __contains__(self,coord): #if a cell is not empty
		raise NotImplementedError

	def copy(self):
		raise NotImplementedError

	def limits(self):
		raise NotImplementedError
		return (smallestCoord,size) #2 vectors of size and smallest coordinates

class Instruction:
	def __init__(self,symbol,name,description,theme):
		self.theme=theme
		self.symbol=symbol
		self.description=description
		self.name=name
		def defaultTransform(instr,delta,pos,space):
			yield (delta,pos+delta)
		self._transform=defaultTransform
		self._run=None
		self.zeroTick=False

	def runner(self,func):
		self._run=func

	def run(self,funge,pointer):
		self._run(self,funge,pointer)

	def transformer(self,func): #next position possibilities
		self._transform=func

	def transforms(self,delta,position,space):
		yield from self._transform(self,delta,position,space)

def nextPlaces(pos,delta,instrs,plane,zerotick=True):
	nextPlaces=list(instrs[plane[pos]].transforms(delta,pos,plane))
	changed=True
	while changed:
		changed=False
		for index,nextPlace in reversed(list(enumerate(nextPlaces))):
			nextDelta,nextPos=nextPlace
			if nextPos==pos:
				break
			if zerotick:
				nextInstr=instrs[plane[nextPos]]
				if nextInstr.zeroTick:
					changed=True
					nextPlaces=nextPlaces[:index]+list(nextInstr.transforms(nextDelta,nextPos,plane))+nextPlaces[index+1:]
	return nextPlaces

class FungeExitedException(BaseException):
	pass

def step(self): #must be mode #0
	self.funge.instr(self.funge.plane[self.pos],self) #instruction does the moving
	oldCell=None
	while self.mode==0 and self.funge.instrs[(currentCell:=self.funge.plane[self.pos])].zeroTick:
		if currentCell==oldCell:
			break
		self.funge.instr(currentCell,self)
		oldCell=currentCell

class Pointer:
	steppers=(step,)
	def __init__(self,funge,position,delta,stack,stackStack):
		self.pos=position
		self.delta=delta
		self.funge=funge
		self.stack=stack #list
		self.mode=0

	def step(self):
		self.steppers[self.mode](self)

	def stackPop(self): #End of the list is top of the stack
		if self.stack:
			return self.stack.pop()
		else:
			return 0

	def stackPush(self,val):
		self.stack.append(val)

class Funge:
	def __init__(self,pointers,plane,instructions):
		self.plane=plane
		self.pointers=pointers
		self.instrs=instructions

	def instr(self,instr,pointer):
		self.instrs[instr].run(self,pointer)

	def step(self):
		for pointer in self.pointers:
			pointer.step()

# (Cells are represented by integers)

############## Definition of 2d funge
class Vect2d(Coord):
	def __init__(self,x,y):
		self.x=x
		self.y=y

	def __add__(self,other):
		return Vect2d(self.x+other.x,self.y+other.y)

	def __neg__(self):
		return Vect2d(-self.x,-self.y)

	def __mul__(self,val):
		return Vect2d(self.x*val,self.y*val)

	def copy(self):
		return Vect2d(self.x,self.y)

	def __repr__(self):
		return f"Vect2d({self.x},{self.y})"

	def __hash__(self):
		return hash((self.x,self.y))

	def __eq__(self,other):
		return self.x==other.x and self.y==other.y

	def __lt__(self,other):
		return self.x<other.x or self.y<other.y

	def __gt__(self,other):
		return self.x>other.x or self.y>other.y

Vect2d.east=Vect2d(1,0)
Vect2d.west=Vect2d(-1,0)
Vect2d.north=Vect2d(0,-1)
Vect2d.south=Vect2d(0,1)

class Space2d(Space):
	defaultValue=ord(" ")
	def __init__(self,matrix=None):
		if not matrix:
			self.matrix={}
		else:
			self.matrix=matrix
		self.maxX,self.maxY=0,0
		self.minX,self.minY=0,0

	def clear(self):
		self.matrix={}
		self.maxX,self.maxY=0,0
		self.minX,self.minY=0,0

	def __getitem__(self,coord):
		row=self.matrix.get(coord.y)
		return row.get(coord.x,self.defaultValue) if row else self.defaultValue

	def __setitem__(self,coord,value):
		if value!=self.defaultValue:
			row=self.matrix.setdefault(coord.y, {}) # TODO: optimise this dictionary allocation
			row[coord.x]=value
			if coord.x>self.maxX: self.maxX=coord.x
			if coord.x<self.minX: self.minX=coord.x
			if coord.y>self.maxY: self.maxY=coord.y
			if coord.y<self.minY: self.minY=coord.y
		else:
			del self[coord]

	def __delitem__(self,coord):
		row=self.matrix.get(coord.y)
		if row:
			val=row.pop(coord.x,None)
			if val:
				if not row:
					del self.matrix[coord.y]
					keys=self.matrix.keys()
					if not keys:
						self.maxY=0
					elif coord.y==self.maxY:
						self.maxY=max(keys)
					elif coord.y==self.minY:
						self.maxY=min(keys)
				if self.matrix:
					if coord.x==self.maxX:
						self.maxX=max([max(row) for row in self.matrix.values()])
					if coord.x==self.minX:
						self.maxX=min([min(row) for row in self.matrix.values()])
				else:
					self.maxX=0

	def __contains__(self,coord):
		return (row:=self.matrix.get(coords.y,False)) and (coords.x in row)

	def stringify(self,x,y,h,w,pointers=[]): #very slow, only use for debugging
		result=[]
		for row in range(y,y+h): #Render the plane
			result.append([])
			line=self.matrix.get(row)
			if line:
				for col in range(x,x+w):
					result[-1].append(chr(line.get(col,self.defaultValue)))
			else:
				result[-1]+=w*[chr(self.defaultValue)]

		#Render pointers
		visible=lambda coord:(x+w)>coord.x>=x and (y+h)>coord.y>=y
		for pointer in pointers:
			if visible(pointer.pos):
				result[pointer.pos.y-y][pointer.pos.x-x]="P" #add pointers

				#render forecasts
				if pointer.mode!=0:
					continue
				for delta,forecast in pointer.funge.instrs[self[pointer.pos]].transforms(pointer.delta,pointer.pos,self):
					if visible(forecast):
						result[forecast.y-y][forecast.x-x]={
							Vect2d.east:'→',Vect2d.south:'↓',Vect2d.west:"←",Vect2d.north:"↑"
						}[delta]

		#format 2d list into string
		return '\n'.join([''.join(line) for line in result])

	def limits(self):
		return (Vect2d(self.minX,self.minY),Vect2d(self.maxX-self.minX+1,self.maxY-self.minY+1))

