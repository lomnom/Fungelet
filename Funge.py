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
	def __init__(self,symbol,name,description):
		self.symbol=symbol
		self.description=description
		self.name=name
		def defaultTransform(instr,delta,pos):
			yield (delta,pos+delta)
		self._transform=defaultTransfom
		self._run=None

	def runner(self,func):
		self._run=func

	def run(self,funge,pointer):
		self._run(self,funge,pointer)

	def transformer(self,func): #next position possibilities
		self._transform=func

	def transforms(self,delta,position):
		yield from self._transform(self,delta,position)

class FungeExitedException(BaseException):
	pass

class Pointer:
	def __init__(self,funge,position,delta,stack,stackStack):
		self.pos=position
		self.delta=delta
		self.funge=funge
		self.stack=stack #list
		self.stackStack=stackStack #list

	def step(self):
		self.funge.instr(self.funge.plane[self.pos],self) #instruction does the moving

	def stackPop(self):
		if self.stack:
			return stack.pop()
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

class Space2d(Space):
	defaultValue=ord(" ")
	def __init__(self,matrix=None):
		if not matrix:
			self.matrix={}
		else:
			self.matrix=matrix
		self.maxX,self.maxY=0,0
		self.minX,self.minY=0,0

	def __getitem__(self,coord):
		row=self.matrix.get(coord.y)
		return row.get(coord.x,self.defaultValue) if row else self.defaultValue

	def __setitem__(self,coord,value):
		if value:
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
					if coord.y==self.maxY:
						self.maxY=max(self.matrix.values)
					if coord.y==self.minY:
						self.maxY=min(self.matrix.values)
				if coord.x==self.maxX:
					self.maxX=max([max(row) for row in self.matrix])
				if coord.x==self.minX:
					self.maxX=min([min(row) for row in self.matrix])

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
				for delta,forecast in pointer.funge.instrs[self[pointer.pos]].transforms(pointer.delta,pointer.pos):
					if visible(forecast):
						result[forecast.y-y][forecast.x-x]={
							Vect2d(1,0):'→',Vect2d(0,1):'↓',Vect2d(-1,0):"←",Vect2d(0,-1):"↑"
						}[delta]

		#format 2d list into string
		return '\n'.join([''.join(line) for line in result])

	def limits(self):
		return (Vect2d(self.minX,self.minY),Vect2d(self.maxX-self.minX+1,self.maxY-self.minY+1))

######### instructions for 2d-befunge
import random
class BfPointer(Pointer):
	def step(self):
		currentCell=self.funge.plane[self.pos]
		if not currentCell==self.funge.plane.defaultValue:
			self.funge.instr(self.funge.plane[self.pos],self) #instruction does the moving

		corner,size=self.funge.plane.limits()
		outside=lambda: self.pos>(size+corner) or self.pos<corner

		while self.funge.plane[self.pos]==self.funge.plane.defaultValue: #wrapping
			self.pos+=self.delta # keep moving till instruction
			if outside():	
				while outside():
					self.pos-=self.delta #backtrack till back inside 

				landing=None
				while not (self.pos>(size+corner) or self.pos<corner): #when inside, backtrack to other end
					self.pos-=self.delta
					if self.funge.plane[self.pos]!=self.funge.plane.defaultValue: #take note of instructions on path
						landing=self.pos.copy()

				self.pos=landing #land on last seen instruction

				if not landing:
					raise ValueError("Infinite wrap loop (No instructions on the IP path)")
				break 
befunge2d={
}
def befunge2dInstr(instruction):
	befunge2d[ord(instruction.symbol)]=instruction

nothing=Instruction(chr(Space2d.defaultValue),"Space","Does nothing, skipped over")
@nothing.runner
def run(instr,funge,pointer):
	raise ValueError("This should not happen")
befunge2dInstr(nothing)

nop=Instruction('z',"Nop","Does nothing, but not skipped over")
@nop.runner
def run(instr,funge,pointer):
	pointer.pos+=pointer.delta #THIS MUST HAPPEN
befunge2dInstr(nop)

def dirChgInstr(char,name,description,change):
	direction=Instruction(char,name,description)
	@direction.runner
	def run(instr,funge,pointer):
		pointer.delta=change(pointer.delta)
		pointer.pos+=pointer.delta

	@direction.transformer
	def transforms(instr,delta,position):
		newDelta=change(delta)
		yield (newDelta,position+newDelta)
	befunge2dInstr(direction)

# Movement in cardinal directions
dirChgInstr(
	">","Go East","Set delta to (1,0)",
	lambda delta: Vect2d(1,0)
)
dirChgInstr(
	"<","Go West","Set delta to (-1,0)",
	lambda delta: Vect2d(-1,0)
)
dirChgInstr(
	"^","Go North","Set delta to (0,-1)",
	lambda delta: Vect2d(0,-1)
)
dirChgInstr(
	"v","Go South","Set delta to (0,1)",
	lambda delta: Vect2d(0,1)
)

# Relative direction changes
dirChgInstr(
	"]","Turn Right","Turn 90 degrees clockwise",
	lambda delta: Vect2d(-delta.y,delta.x)
)
dirChgInstr(
	"[","Turn Left","Turn 90 degrees anti-clockwise",
	lambda delta: Vect2d(delta.y,-delta.x)
)

dirChgInstr(
	"r","Reverse","Go in the opposite direction",
	lambda delta: -delta
)

# other delta functions
goAway=Instruction('?',"Go Away","Go north, south east or west randomly")
goAway.directions=[Vect2d(1,0),Vect2d(-1,0),Vect2d(0,1),Vect2d(0,-1)]

@goAway.runner
def run(instr,funge,pointer):
	pointer.delta=random.choice(instr.directions)
	pointer.pos+=pointer.delta

@goAway.transformer
def transforms(instr,delta,position):
	for direction in instr.directions:
		yield (direction,position+direction)
befunge2dInstr(goAway)

setDelta=Instruction('x',"Set Delta","Pops dY THEN dX off the stack. Sets delta to (dX,dY)")

@setDelta.runner
def run(instr,funge,pointer):
	dY=pointer.stackPop()
	pointer.delta=Vect2d(pointer.stackPop(),dY)
	pointer.pos+=pointer.delta

@setDelta.transformer
def transforms(instr,delta,position):
	return
	yield
befunge2dInstr(setDelta)

