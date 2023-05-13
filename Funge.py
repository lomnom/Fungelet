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

class Instruction:
	symbol=None
	@classmethod
	def run(cls,funge,pointer,stack):
		raise NotImplementedError

	@classmethod
	def transforms(cls,delta,position):
		raise NotImplementedError
		yield (position,delta)

class FungeExitedException(BaseException):
	pass

class Pointer:
	def __init__(self,funge,position,delta,stack):
		self.pos=position
		self.delta=delta
		self.funge=funge
		self.stack=stack #list

	def step(self):
		self.funge.instr(self.funge.plane[self.pos],self) #instruction does the moving

class Funge:
	def __init__(self,pointers,plane,instructions):
		self.plane=plane
		self.pointers=pointers
		self.instrs=instructions

	def instr(self,instr,pointer):
		self.instrs[instr].run(self,pointer,pointer.stack)

	def step(self):
		for pointer in self.pointers:
			pointer.step()

# (Cells are represented by integers)

# Definition of 2d concurrent befunge-98
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

class Space2d(Space):
	defaultValue=ord(" ")
	def __init__(self,matrix=None):
		if not matrix:
			self.matrix={}
		else:
			self.matrix=matrix

	def __getitem__(self,coord):
		row=self.matrix.get(coord.y)
		return row.get(coord.x,self.defaultValue) if row else self.defaultValue

	def __setitem__(self,coord,value):
		if value:
			row=self.matrix.setdefault(coord.y, {}) # TODO: optimise this dictionary allocation
			row[coord.x]=value
		else:
			del self[coord]

	def __delitem__(self,coord):
		row=self.matrix.get(coord.y)
		if row:
			row.pop(coord.x)
			if not row:
				del self.matrix[coord.y]

	def __contains__(self,coord):
		return (row:=self.matrix.get(coords.y,False)) and (coords.x in row)

	def stringify(self,x,y,h,w,pointers=[]): #very slow, only use for debugging
		result=[]
		for row in range(y,y+h):
			result.append([])
			line=self.matrix.get(row)
			if line:
				for col in range(x,x+w):
					result[-1].append(chr(line.get(col,self.defaultValue)))
			else:
				result[-1]+=w*[chr(self.defaultValue)]

		visible=lambda coord:(x+w)>coord.x>=x and (y+h)>coord.y>=y
		for pointer in pointers:
			if visible(pointer.pos):
				result[pointer.pos.y-y][pointer.pos.x-x]="P"
				for delta,forecast in pointer.funge.instrs[self[pointer.pos]].transforms(pointer.delta,pointer.pos):
					if visible(forecast):
						result[forecast.y-y][forecast.x-x]={
							Vect2d(1,0):'→',Vect2d(0,1):'↓',Vect2d(-1,0):"←",Vect2d(0,-1):"↑"
						}[delta]
		return '\n'.join([''.join(line) for line in result])

# instructions for befunge
import random
befunge2d={
}
def befunge2dInstr(instruction):
	befunge2d[ord(instruction.symbol)]=instruction

@befunge2dInstr
class Nothing:
	symbol=' '
	@classmethod
	def run(cls,funge,pointer,stack):
		pointer.pos+=pointer.delta

	@classmethod
	def transforms(cls,delta,position):
		yield (delta,position+delta)

def directionChange(char,change):
	class Direction:
		symbol=char
		@classmethod
		def run(cls,funge,pointer,stack):
			pointer.delta=change(pointer.delta)
			pointer.pos+=pointer.delta

		@classmethod
		def transforms(cls,delta,position):
			yield (delta,position+change(delta))
	return Direction

befunge2dInstr(directionChange(">",lambda dir: Vect2d(1,0)))
befunge2dInstr(directionChange("<",lambda dir: Vect2d(-1,0)))
befunge2dInstr(directionChange("^",lambda dir: Vect2d(0,-1)))
befunge2dInstr(directionChange("v",lambda dir: Vect2d(0,1)))

@befunge2dInstr
class GoAway: #move in random cardinal dir
	symbol='?'
	directions=[Vect2d(1,0),Vect2d(-1,0),Vect2d(0,1),Vect2d(0,-1)]
	@classmethod
	def run(cls,funge,pointer,stack):
		pointer.delta=random.choice(cls.directions)
		pointer.pos+=pointer.delta

	@classmethod
	def transforms(cls,delta,position):
		for direction in cls.directions:
			yield (direction,position+direction)