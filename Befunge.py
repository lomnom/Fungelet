from Funge import *

######### instructions for 2d-befunge (https://github.com/catseye/Funge-98/blob/master/doc/funge98.markdown#instructions)
import random

defaultInstr=None
class Instructions(dict):
	def __getitem__(self,item):
		global defaultInstr
		return super().get(item,defaultInstr)

befunge2d=Instructions()
def befunge2dInstr(instruction):
	befunge2d[ord(instruction.symbol)]=instruction

class BfPointer(Pointer):
	def __init__(self,funge,position,delta,stack,stackStack,storageOffset):
		self.pos=position
		self.delta=delta
		self.funge=funge
		self.stack=stack #list
		self.stackStack=stackStack
		self.mode=0
		self.offset=storageOffset

def stringMode(self):
	currentChar=self.funge.plane[self.pos]
	if currentChar==self.funge.plane.defaultValue \
	   and self.funge.plane[self.pos+self.delta]==self.funge.plane.defaultValue:
		self.stackPush(self.funge.plane.defaultValue)
		self.delta,self.pos=wrap(self.delta,self.pos,self.funge.plane)
	elif currentChar==ord(quotes.symbol):
		quotes.run(self.funge,self)
		while self.mode==0 and self.funge.instrs[(currentCell:=self.funge.plane[self.pos])].zeroTick:
			self.funge.instr(currentCell,self)
	else:
		self.stackPush(currentChar)
		self.pos+=self.delta

BfPointer.steppers=tuple(list(BfPointer.steppers)+[stringMode])

quotes=Instruction('"',"String mode","Toggle string mode","Strings")
@quotes.runner
def run(instr,funge,pointer):
	pointer.pos+=pointer.delta
	pointer.mode=1 if pointer.mode==0 else 0

@quotes.transformer
def transforms(instr,delta,position,space): #TODO: support transforms with special modes
	return
	yield
befunge2dInstr(quotes)

debug=Instruction('D',"Debug","Print 'Debug' to stdout","Debug")
@debug.runner
def run(instr,funge,pointer):
	print("Debug, "+str(pointer.pos))
	pointer.pos+=pointer.delta
befunge2dInstr(debug)

def outsideField(pos,size,corner):
	return pos>(size+corner) or pos<corner

#[a,b,c] for ax+by=c

#a=(y2-y1), b=(x1-x2), c=ax1-by1
def mkline(x1,y1,x2,y2):
	a=(y2-y1)
	b=(x1-x2)
	c=a*x1 + b*y1
	return [a,b,c]

def equal(a,b):
	v=[]
	for an,bn in zip(a,b):
		if an!=bn and (an==0 or bn==0):
			return False
		(an==bn==0 or v.append(an/bn))
	return len(set(v))<=1

class All: 
	pass

# a1x + b1y = c1, a2x + b2y = c2
# y = (c1a2 - c2a1)/(b1a2 - b2a1)
# x = (c1 - b1y)/a1
def intersection(a,b):
	n = ((a[1]*b[0]) - (b[1]*a[0]))
	if n==0:
		if equal(a,b):
			return All
		return None
	y = ((a[2]*b[0]) - (b[2]*a[0])) / n 

	n = ((a[0]*b[1]) - (b[0]*a[1]))
	if n==0:
		return None
	x = ((a[2]*b[1]) - (b[2]*a[1])) / n
	return [x,y]

def intersections(by,lines):
	results=[]
	for line in lines:
		result=intersection(line,by)
		if result is not None:
			results.append(result)
	return results

def rangeResults(x,y,h,w,results):
	h-=1
	w-=1
	for result in results:
		if result==All:
			return True
		elif ((x+w)>=result[0]>=x) and ((y+h)>=result[1]>=y):
			return True
	return False

def roundpp(val,chunk,offset,direction): #direction=1 if ceil else -1 for floor
	chunk=abs(chunk)
	val=val-offset+(direction*0.5*chunk)
	diff=val%chunk
	if diff>=(0.5*chunk):
		return val+(chunk-diff)+offset
	else:
		return val-diff+offset

ZEROVECT=Vect2d(0,0)
def wrap(delta,pos,space):
	corner,size=space.limits()
	end=corner+(size-Vect2d(1,1))
	if (not space[pos]==space.defaultValue) or size==ZEROVECT:
		return (delta,pos)
	starting=(delta.copy(),pos.copy())

	if outsideField(pos,size,corner): 
		#use coordinate geometry to check if line of path intersects box
		topLine=mkline(corner.x,corner.y,corner.x+1,corner.y) #corner.x+1 instead of end.x in case width 0
		bottomLine=mkline(corner.x,end.y,corner.x+1,end.y) #vice versa
		leftLine=mkline(corner.x,corner.y,corner.x,corner.y+1)
		rightLine=mkline(end.x,corner.y,end.x,corner.y+1)
		box=[topLine,bottomLine,leftLine,rightLine]

		pointerLine=mkline(pos.x,pos.y,pos.x+delta.x,pos.y+delta.y)

		hits=intersections(pointerLine,box)
		onCourse=rangeResults(corner.x,corner.y,size.y,size.x,hits)
		if not onCourse:
			return starting

		hits=[Vect2d(coord[0],coord[1]) for coord in hits if coord!=All]
		hits=sorted(hits,key=lambda v: abs(v-pos)) #small distance first
		hit=hits[0] 

		# use inequalities to check if moving towards or away
		nextPos=pos+delta
		diffDiff=abs(hit-nextPos)-abs(hit-pos) #positive is moving away

		if diffDiff>ZEROVECT: #moving away
			hit=hits[1] #use bigger distance (other side of board)
		elif diffDiff<ZEROVECT: #moving towards
			pass #use smaller distance (closer to pointer side)
		else: #delta (0,0) lmao
			return starting

		# coord around start of wrapping
		if delta.x:
			x=roundpp(hit.x,delta.x,pos.x%delta.x,0)
		else:
			x=hit.x

		if delta.y:
			y=roundpp(hit.y,delta.y,pos.y%delta.y,0)
		else:
			y=hit.y

		if outsideField(pos,size,corner):
			pos+=delta

		return (delta,Vect2d(int(x),int(y)))
	else:
		while not outsideField(pos,size,corner): #find instruction in front
			if space[pos]!=space.defaultValue:
				return (delta,pos)
			pos+=delta
		delta=-delta
		pos+=delta
		while not outsideField(pos,size,corner): #go to other end
			pos+=delta
		delta=-delta
		pos+=delta
		while not outsideField(pos,size,corner): #find instruction at other end
			if space[pos]!=space.defaultValue:
				return (delta,pos)
			pos+=delta
		return starting #no instruction found

nothing=Instruction(chr(Space2d.defaultValue),"Space","Does nothing, skipped over (in 0 ticks)","Nothing")
nothing.zeroTick=True
@nothing.runner
def run(instr,funge,pointer):
	pointer.delta,pointer.pos=wrap(pointer.delta,pointer.pos,funge.plane)

@nothing.transformer
def transforms(instr,delta,position,space):
	yield wrap(delta,position,space)
befunge2dInstr(nothing)

def jump(delta,pos,space,jmpChr):
	corner,size=space.limits()
	outside=lambda: pos>(size+corner) or pos<corner
	if space[pos]==jmpChr:
		pos+=delta
		while space[pos]!=jmpChr:
			pos+=delta
			if outside():
				delta,pos=wrap(delta,pos,space)
		pos+=delta
	return (delta,pos)

jumpOver=Instruction(';',"Jump Over","Jump to cell after the next Jump Over in path (takes 0 ticks)","Position")
jumpOver.zeroTick=True
@jumpOver.runner
def run(instr,funge,pointer):
	pointer.delta,pointer.pos=jump(pointer.delta,pointer.pos,funge.plane,ord(';'))

@jumpOver.transformer
def transforms(instr,delta,pos,space):
	yield jump(delta,pos,space,ord(';'))
befunge2dInstr(jumpOver)

nop=Instruction('z',"Nop","Does nothing, but not skipped over","Nothing")
@nop.runner
def run(instr,funge,pointer):
	pointer.pos+=pointer.delta #THIS MUST HAPPEN
befunge2dInstr(nop)

def dirChgInstr(char,name,description,change):
	direction=Instruction(char,name,description,"Delta")
	@direction.runner
	def run(instr,funge,pointer):
		pointer.delta=change(pointer.delta)
		pointer.pos+=pointer.delta

	@direction.transformer
	def transforms(instr,delta,position,space):
		newDelta=change(delta)
		yield (newDelta,position+newDelta)
	befunge2dInstr(direction)

# Movement in cardinal directions
dirChgInstr(
	">","Go East","Set delta to (1,0)",
	lambda delta: Vect2d.east
)
dirChgInstr(
	"<","Go West","Set delta to (-1,0)",
	lambda delta: Vect2d.west
)
dirChgInstr(
	"^","Go North","Set delta to (0,-1)",
	lambda delta: Vect2d.north
)
dirChgInstr(
	"v","Go South","Set delta to (0,1)",
	lambda delta: Vect2d.south
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
defaultInstr=befunge2d[ord('r')]

# other delta functions
goAway=Instruction('?',"Go Away","Go north, south east or west randomly","Delta+")
goAway.directions=[Vect2d.north,Vect2d.south,Vect2d.east,Vect2d.west]

@goAway.runner
def run(instr,funge,pointer):
	pointer.delta=random.choice(instr.directions)
	pointer.pos+=pointer.delta

@goAway.transformer
def transforms(instr,delta,position,space):
	for direction in instr.directions:
		yield (direction,position+direction)
befunge2dInstr(goAway)

setDelta=Instruction('x',"Set Delta","Pops dY THEN dX off the stack. Sets delta to (dX,dY)","Delta+")

@setDelta.runner
def run(instr,funge,pointer):
	dY=pointer.stackPop()
	pointer.delta=Vect2d(pointer.stackPop(),dY)
	pointer.pos+=pointer.delta

@setDelta.transformer
def transforms(instr,delta,position,space):
	return
	yield
befunge2dInstr(setDelta)

# Control flow
trampoline=Instruction('#',"Trampoline","Skip over next cell in path","Position")
@trampoline.runner
def run(instr,funge,pointer):
	pointer.pos+=pointer.delta*2

@trampoline.transformer
def transforms(instr,delta,position,space):
	yield (delta,position+(delta*2))
befunge2dInstr(trampoline)

exit=Instruction('@',"Stop","Kill current IP","Termination")
@exit.runner
def run(instr,funge,pointer):
	funge.pointers.pop(funge.pointers.index(pointer))
	if not funge.pointers:
		raise FungeExitedException(0)

@exit.transformer
def transforms(instr,delta,position,space):
	return
	yield
befunge2dInstr(exit)

trampoline=Instruction('j',"Jump forward","Move [popped value]+1 times","Position")
@trampoline.runner
def run(instr,funge,pointer):
	pointer.pos+=pointer.delta*pointer.stackPop()

@trampoline.transformer
def transforms(instr,delta,position,space):
	return
	yield
befunge2dInstr(trampoline)

end=Instruction('q',"Quit","Kill program. Exit code will be popped value","Termination")
@end.runner
def run(instr,funge,pointer):
	raise FungeExitedException(pointer.stackPop())

@end.transformer
def transforms(instr,delta,position,space):
	return
	yield
befunge2dInstr(end)

iterate=Instruction('k',"Iterate","Execute next instruction [popped value] times","Repetition")
@iterate.runner
def run(instr,funge,pointer):
	iterations=pointer.stackPop()
	if iterations>0:
		pointer.pos+=pointer.delta
		location=pointer.pos.copy()
		for iteration in range(iterations):
			pointer.pos=location.copy()
			pointer.funge.instr(pointer.funge.plane[pointer.pos],pointer)
	else:
		pointer.pos+=pointer.delta*2
befunge2dInstr(iterate)

# Data pushers
def pushInstr(char,name,description,data):
	pusher=Instruction(char,name,description,"Value")
	@pusher.runner
	def run(instr,funge,pointer):
		pointer.pos+=pointer.delta
		pointer.stackPush(data)
	befunge2dInstr(pusher)

for number,char in enumerate("0123456789abcdef"):
	pushInstr(
		char,f"Push {number}",f"Push {number} to the stack",number 
	)

# Decision making
lnot=Instruction('!',"Not","Logical not - pop a value and push 1 if val==0 else 0","Logic")
@lnot.runner
def run(instr,funge,pointer):
	value=pointer.stackPop()
	if value==0:
		pointer.stackPush(1)
	else:
		pointer.stackPush(0)
	pointer.pos+=pointer.delta
befunge2dInstr(lnot)

gt=Instruction('`',"Greater Than","Pops b then a. Pushes one if a>b, else zero.","Logic")
@gt.runner
def run(instr,funge,pointer):
	a=pointer.stackPop()
	b=pointer.stackPop()
	if b>a:
		pointer.stackPush(1)
	else:
		pointer.stackPush(0)
	pointer.pos+=pointer.delta
befunge2dInstr(gt)

ewIf=Instruction('_',"East West If","Pops a value, acts like > if zero, else <","Logic")
@ewIf.runner
def run(instr,funge,pointer):
	n=pointer.stackPop()
	if n==0:
		pointer.delta=Vect2d.east
	else:
		pointer.delta=Vect2d.west
	pointer.pos+=pointer.delta

@ewIf.transformer
def transforms(instr,delta,position,space):
	yield (Vect2d.east,position+Vect2d.east)
	yield (Vect2d.west,position+Vect2d.west)
befunge2dInstr(ewIf)

nsIf=Instruction('|',"North South If","Pops a value, acts like v if zero, else ^","Logic")
@nsIf.runner
def run(instr,funge,pointer):
	n=pointer.stackPop()
	if n==0:
		pointer.delta=Vect2d.south
	else:
		pointer.delta=Vect2d.north
	pointer.pos+=pointer.delta

@nsIf.transformer
def transforms(instr,delta,position,space):
	yield (Vect2d.south,position+Vect2d.south)
	yield (Vect2d.north,position+Vect2d.north)
befunge2dInstr(nsIf)

nsIf=Instruction('w',"Compare","Pops b then a. if a<b, act like [, if a>b, act like ], no effect if a==b.","Logic")
@nsIf.runner
def run(instr,funge,pointer):
	b=pointer.stackPop()
	a=pointer.stackPop()
	if a<b:
		pointer.delta=Vect2d(pointer.delta.y,-pointer.delta.x)
	elif a>b:
		pointer.delta=Vect2d(-pointer.delta.y,pointer.delta.x)
	pointer.pos+=pointer.delta

@nsIf.transformer
def transforms(instr,delta,position,space):
	right=Vect2d(-delta.y,delta.x)
	left=Vect2d(delta.y,-delta.x)
	yield (right,position+right)
	yield (left,position+left)
	yield (delta,position+delta)
befunge2dInstr(nsIf)

# math
def simpleOpInstr(symbol,name,func):
	op=Instruction(symbol,name,f"Pops b then a. Pushes a{symbol}b.","Math")
	@op.runner
	def run(instr,funge,pointer):
		b=pointer.stackPop()
		a=pointer.stackPop()
		pointer.stackPush(int(func(a,b)))
		pointer.pos+=pointer.delta
	befunge2dInstr(op)

simpleOpInstr('+',"Add",lambda a,b: a+b)
simpleOpInstr('*',"Multiply",lambda a,b: a*b)
simpleOpInstr('-',"Subtract",lambda a,b: a-b)
simpleOpInstr('/',"Divide",lambda a,b: a/b if a or b else 0)
simpleOpInstr('%',"Modulo",lambda a,b: a%b)

# Stack manipulation
pop=Instruction('$',"Pop","Pop a value and discard it","Stack")
@pop.runner
def run(instr,funge,pointer):
	pointer.stackPop()
	pointer.pos+=pointer.delta
befunge2dInstr(pop)

pop=Instruction(':',"Duplicate","Pop a value and push it twice, duplicating it","Stack")
@pop.runner
def run(instr,funge,pointer):
	value=pointer.stackPop()
	pointer.stackPush(value)
	pointer.stackPush(value)
	pointer.pos+=pointer.delta
befunge2dInstr(pop)

swap=Instruction('\\',"Swap","Swap the top two values on the stack","Stack")
@swap.runner
def run(instr,funge,pointer):
	a=pointer.stackPop()
	b=pointer.stackPop()
	pointer.stackPush(a)
	pointer.stackPush(b)
	pointer.pos+=pointer.delta
befunge2dInstr(swap)

clear=Instruction('n',"Clear","Clear the stack","Stack")
@clear.runner
def run(instr,funge,pointer):
	pointer.stack=[]
	pointer.pos+=pointer.delta
befunge2dInstr(clear)

# StackStack manipulation

## TODO lol

# Editing FungeSpace
put=Instruction('p',"Put","Pops y, then x, then c. Places ascii code c at (x,y)+storage offset","Funge Space")
@put.runner
def run(instr,funge,pointer):
	y=pointer.stackPop()
	x=pointer.stackPop()
	c=pointer.stackPop()
	funge.plane[Vect2d(x,y)+pointer.offset]=c
	pointer.pos+=pointer.delta
befunge2dInstr(put)

get=Instruction('g',"Get","Pops y, then x. Pushes ascii value of character at (x,y)+storage offset","Funge Space")
@get.runner
def run(instr,funge,pointer):
	y=pointer.stackPop()
	x=pointer.stackPop()
	pointer.stackPush(funge.plane[Vect2d(x,y)+pointer.offset])
	pointer.pos+=pointer.delta
befunge2dInstr(get)

# stdin & stdout TODO: act like r if fail
stdout=print
stdin=input

OUTNUM=lambda n: stdout(n) 
INNUM=lambda: int(stdin())
OUTCHAR=lambda c: stdout(chr(c))
INCHAR=lambda: ord(stdin()[0])

outNum=Instruction('.',"Output Decimal","Pops and prints the number.","I/O")
@outNum.runner
def run(instr,funge,pointer):
	n=pointer.stackPop()
	OUTNUM(n)
	pointer.pos+=pointer.delta
befunge2dInstr(outNum)

outChar=Instruction(',',"Output Character","Pops and prints the character.","I/O")
@outChar.runner
def run(instr,funge,pointer):
	c=pointer.stackPop()
	OUTCHAR(c)
	pointer.pos+=pointer.delta
befunge2dInstr(outChar)

inNum=Instruction('&',"Input Decimal","Pushes number from user input.","I/O")
@inNum.runner
def run(instr,funge,pointer):
	pointer.stackPush(INNUM())
	pointer.pos+=pointer.delta
befunge2dInstr(inNum)

inNum=Instruction('~',"Input Character","Pushes character from user input.","I/O")
@inNum.runner
def run(instr,funge,pointer):
	pointer.stackPush(INCHAR())
	pointer.pos+=pointer.delta
befunge2dInstr(inNum)

# File I/O (TODO)

# System execution (TODO)

# System info: no. omg

# Concurrency
split=Instruction('t',"Split","Duplicates instruction pointer with an opposite delta.","Concurrency")
@split.runner
def run(instr,funge,pointer):
	newPointer=BfPointer(
		funge,pointer.position,-pointer.delta,pointer.stack,pointer.stackStack,pointer.offset
	)
	funge.pointers=[newPointer]+funge.pointers
	pointer.pos+=pointer.delta
	newPointer.pos+=newPointer.delta
befunge2dInstr(split)