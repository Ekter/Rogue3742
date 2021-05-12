#Projet Roguelike, par Nino Mulac
#from time import sleep
import random
from typing import *
from tkinter import *
import copy
import math

class Coord(object):
    "Vec2D"
    def __init__(self,x : int ,y : int ):
        self.x=int(x)
        self.y=int(y)
    def __repr__(self) -> str:
        return "<"+str(self.x)+","+str(self.y)+">"
    def __eq__(self,other) -> bool:
        return self.x==other.x and self.y==other.y
    def __ne__(self,other) -> bool:
        return not(self==other)
    def __add__(self,other):
        if type(other) is Coord:
            return Coord(self.x+other.x,self.y+other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x+other,self.y+other)
    def __neg__(self):
        return Coord(-self.x,-self.y)
    def  __mul__(self,other):
        if type(other) is Coord:
            return Coord(self.x*other.x,self.y*other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x*other,self.y*other)
    def middle(self,other):
        return (self+other)//2
    def __sub__(self,other):
        if type(other) is Coord:
            return Coord(self.x-other.x,self.y-other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x-other,self.y-other)
    def coin1(self,other):
        return Coord(self.x,other.y)
    def coin2(self,other):
        return Coord(other.x,self.y)
    def __abs__(self):
        return Coord(abs(self.x),abs(self.y))
    def __floordiv__(self,other):
        if type(other) is Coord:
            return Coord(self.x/other.x,self.y/other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x/other,self.y/other)
    def __truediv__(self,other):
        if type(other) is Coord:
            return Coord(self.x/other.x,self.y/other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x/other,self.y/other)
    def __len__(self) -> float:
        return math.sqrt(self.x**2+self.y**2)
    def __lt__(self,other) -> bool:
        if type(other) is Coord:
            return len(self)<len(other)
        if (type(other) is int) or (type(other) is float):
            return len(self)<other
    def __gt__(self,other) -> bool:
        if type(other) is Coord:
            return len(self)>len(other)
        if (type(other) is int) or (type(other) is float):
            return len(self)>other
    def __le__(self,other) -> bool:
        if type(other) is Coord:
            return len(self)<=len(other)
        if (type(other) is int) or (type(other) is float):
            return len(self)<=other
    def __ge__(self,other) -> bool:
        if type(other) is Coord:
            return len(self)>=len(other)
        if (type(other) is int) or (type(other) is float):
            return len(self)>=other
    def distance(self,other) -> float:
        return (self-other).__len__()
    def dirtrig(self):
        if self==Coord(0,0):
            return Coord(0,0)
        cos=self.x/self.__len__()
        if cos>math.sqrt(2):
            return Coord(-1,0)
        if cos<-math.sqrt(2):
            return Coord(1,0)
        if self.y>0:
            return Coord(0,-1)
        return Coord(0,1)
    def direction(self,other):
        return (self-other).dirtrig()
    def inverse(self):
        return Coord(self.y,self.x)

def heal(creature):
    creature.hp+=3
    return True

def teleport(creature, unique):
    f=theGame().floor
    l=len(f)
    c=Coord(random.randint(0,l),random.randint(0,l))
    while f[c]!=Map.empty:
        c=f[Coord(random.randint(0,l),random.randint(0,l))]
    f.move(creature,c-f.pos(creature))
    return unique

def getch():
    """Single char input, only works only on mac/linux/windows OS terminals"""
    try:
        import termios
        # POSIX system. Create and return a getch that manipulates the tty.
        import sys, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch().decode('utf-8')

class Element(object):
    "Élement de base pour la construction du roquelike"
    def __init__(self,name,abbrv=None):
        self.name=name
        if abbrv==None:
            self.abbrv=name[0]
        else:
            self.abbrv=abbrv
    def __repr__(self):
        return self.abbrv
    def description(self):
        return "<{}>".format(self.name)
    def meet(self,hero):
        raise NotImplementedError("Not implemented yet")

class Equipment(Element):
    "Élément ramassable et équipable par le héros"
    def __init__(self,name,abbvr=None,usage=None):
        Element.__init__(self,name,abbvr)
        self.usage=usage
    def meet(self,hero):
        theGame().addMessage(f"You pick up a {self.name}")
        return Hero.take(hero,self)
    def use(self,creature):
        if self.usage!=None:
            theGame().addMessage(f"The {creature.name} uses the {self.name}")
            return self.usage(creature)
        theGame().addMessage(f"The {self.name} is not usable")
        return False


class Creature(Element):
    "Élement possédant des pv et une force, pouvant se déplacer"
    def __init__(self,name,hp,abbrv=None,strength=1):
        Element.__init__(self,name,abbrv)
        self.hp=hp
        self.strength=strength
    def description(self):
        return Element.description(self)+"({})".format(self.hp)
    def meet(self,other):
        self.hp-=other.strength
        theGame().addMessage(f"The {other.name} hits the {self.description()}")
        #if self.hp>0:
        #    other.hp-=self.strength
        #    theGame().addMessage(f"The {self.name} hits the {other.description()}")
        #    return False
        return False if self.hp>0 else True 

class Room(object):
    "Salle composant la Map, est définie par les coordonnées de ses coins"
    def __init__(self,c1:Coord,c2:Coord)->None:
        self.c1=c1
        self.c2=c2
    def __contains__(self,coord:Coord)->bool:
        return self.c1.x<=coord.x<=self.c2.x and self.c1.y<=coord.y<=self.c2.y
    def __repr__(self) -> str:
        return f"[<{self.c1.x},{self.c1.y}>, <{self.c2.x},{self.c2.y}>]"
    def center(self)->Coord:
        return self.c1.middle(self.c2)
    def coins(self)->List[Coord]:
        return [self.c1,self.c2,self.c1.coin1(self.c2),self.c2.coin1(self.c1)]
    def intersect(self,other)->bool:
        for i in self.coins():
            if i in other:
                return True
        for i in other.coins():
            if i in self:
                return True
        return False
    def randCoord(self):
        return Coord(random.randint(self.c1.x,self.c2.x),random.randint(self.c1.y,self.c2.y))
    def randEmptyCoord(self,map):
        coord=self.center()
        cc=self.center()
        while coord in map._elem.values() or coord==cc:
            coord=self.randCoord()
        return coord
    def decorate(self,map):
        map.put(self.randEmptyCoord(map),theGame().randEquipment())
        map.put(self.randEmptyCoord(map),theGame().randMonster())

class Hero(Creature):
    "Le héros, controllé par le joueur"
    def __init__(self,name="Hero",hp=10,abbrv="@",strength=2):
        Creature.__init__(self,name,hp,abbrv,strength)
        self._inventory=[]
    def take(self,equip):
        if isinstance(equip,Equipment):
            self._inventory.append(equip)
            return True
        raise TypeError
    def description(self):
        return Creature.description(self)+"{}".format(self._inventory)
    def __repr__(self):
        return self.abbrv
    def fullDescription(self):
        a=self.__dict__
        res=""
        for i in a:
            if i[0]!="_":
                res+=f"> {i} : {a[i]}\n"
        res+="> INVENTORY : "+str([x.name for x in self._inventory])
        return res
    def kill(self):
        self.hp=0
    def use(self,item : Equipment):
        if not(type(item) is Equipment):
            raise TypeError("C'est pas un équipement!")
        if not(item in self._inventory):
            raise ValueError("Tu l'as pas, tu peux pas l'utiliser!")
        if item.use(self):
            self._inventory.remove(item)

class Map(object):
    "Carte du jeu dans lequel évoluent le héros et les créatures"
    ground="."
    empty=" "
    dir={'z': Coord(0,-1), '\x1b': Coord(0,0) , 's': Coord(0,1), 'd': Coord(1,0), 'q': Coord(-1,0)}
    def __init__(self,size=20,hero=None,ground=".",empty=" ",nbrooms=7,dir={'z': Coord(0,-1), 's': Coord(0,1), 'd': Coord(1,0), 'q': Coord(-1,0)}) -> None:
        self.ground=ground
        self.empty=empty
        self.nbrooms=nbrooms
        self.dir=dir
        self._rooms=[]
        self._roomsToReach=[]
        if hero==None:
            self.hero=Hero()
        else:
            self.hero=hero
        self._mat=[[self.empty for i in range(size)] for k in range(size)]
        self._elem={}
        self.generateRooms(self.nbrooms)
        self.reachAllRooms()
        self.put(self._rooms[0].center(),self.hero)
        self.updatemat()
        for i in self._rooms:
            i.decorate(self)
    def draw(self,fenetre,dicimage,canvas)-> None:
        for i in range(len(self)):
            for k in range(len(self)):
                if self[Coord(i,k)]==Map.ground:
                    canvas.create_image(32*k, 32*i, anchor=NE, image= dicimage.get("sol"))
                if self[Coord(i,k)]!=Map.empty:
                    canvas.create_image(32*k, 32*i, anchor=NE, image= dicimage.get("ground"))
        canvas.pack()
    def __repr__(self) -> str:
        return "\n".join(["".join([str(self._mat[n][k]) for k in range(len(self))]) for n in range(len(self))])+"\n"
    def __len__(self) -> int:
        return len(self._mat)
    def __contains__(self,item) -> bool:
        if isinstance(item,Coord):
            return 0<=item.x<=len(self)-1 and 0<=item.y<=len(self)-1
        return item in self._elem.keys()
    def __getitem__(self,item) -> Any:
        if type(item) is Coord:
            return self.get(item,False)
        else:
            return self.pos(item,False)
    def __setitem__(self,cle,valeur)->None:
        if type(cle) is Coord:
            self.put(cle,valeur)
        else:
            if not cle in self:
                self.put(valeur,cle)
            else:
                self.tp(cle,valeur)
    def get(self,coord : Coord, testeroupas=True) -> Element:
        if testeroupas:
            self.checkCoord(coord)
        for i,j in self._elem.items():
            if j==coord:
                return i
        return self._mat[coord.y][coord.x]
    def pos(self,element : Element) -> Coord:
        self.checkElement(element)
        return self._elem.get(element)
    def updatemat(self,x=-1,y=-1,pastouchemap=True) -> None:
        if pastouchemap:
            for i in self._elem.keys():
                    self._mat[self._elem.get(i).y][self._elem.get(i).x]=i.abbrv
        else:
            if x==-1 and y==-1:
                self._mat=[[Map.empty for i in range(len(self._mat))] for k in range(len(self._mat))]
                for i in self._elem.keys():
                    self._mat[self._elem.get(i).y][self._elem.get(i).x]=i.abbrv
            else:
                self._mat[y][x]=Map.ground
                for i in self._elem.keys():
                    self._mat[self._elem.get(i).y][self._elem.get(i).x]=i.abbrv
    def groundize(self,coord : Coord) -> None:
        self._mat[coord.y][coord.x]=Map.ground
    def elementize(self,coord : Coord, abbrv : str) -> None:
        self._mat[coord.y][coord.x]=abbrv
    def put(self,coord : Coord,element : Element) -> None:
        self.checkCoord(coord)
        self.checkElement(element)
        if self[coord]==self.empty or isinstance(self[coord],Element):
            raise ValueError('Incorrect cell')
        if element in self:
            raise KeyError('Already placed')
        self._elem[element]=Coord(coord.x,coord.y)
        self.elementize(coord,element.abbrv)
    def rm(self,element : Element) -> None:
        if type(element) is Coord:
            self.checkCoord(element)
            self._elem = {key:val for key, val in self._elem.items() if not val == element}
            self.groundize(element)
        else:
            self.groundize(self.pos(self._elem.pop(element)))
    def move(self,element : Element,way : Coord) -> None:
        coordarr=self.pos(element)+way
        if coordarr in self:
            if not coordarr in self._elem.values() and self._mat[coordarr.y][coordarr.x]==Map.ground:
                self.groundize(self.pos(element))
                self._elem[element]=coordarr
                self.elementize(coordarr,element.abbrv)
            elif self._mat[coordarr.y][coordarr.x]!=Map.empty:
                if self.get(coordarr).meet(element):
                    self.rm(coordarr)
    def tp(self,element : Element,dest : Coord) -> None:
        self.move(element,self.pos(element)-dest)
    def play(self,fenetre : Tk,dicimage : dict,canvas)-> None:
        print("--- Welcome Hero! ---")
        while self.hero.hp > 0:
            print()
            print(self)
            self.draw(fenetre,dicimage,canvas)
            print(self.hero.description())
            dir= Map.dir.get(getch())
            if type(dir) is Coord:
                self.move(self.hero, dir)
        print("--- Game Over ---")
    def remplirrectangle(self,c1:Coord,c2:Coord,thing=" ") -> None:
        for i in range(c1.x,c2.x+1):
            for j in range(c1.y,c2.y+1):
                self._mat[j][i]=thing
    def addRoom(self,room:Room) -> None:
        self._roomsToReach.append(room)
        self.remplirrectangle(room.c1,room.c2,Map.ground)
    def findRoom(self,coord : Coord) -> Any:
        for i in self._roomsToReach:
            if coord in i:
                return i
        return False
    def intersectNone(self,room : Room) -> bool:
        for i in self._roomsToReach:
            if room.intersect(i):
                return False
        return True
    def dig(self,coord : Coord) -> None:
        self._mat[coord.y][coord.x]=Map.ground
        a=self.findRoom(coord)
        if a:
            self._rooms.append(a)
            self._roomsToReach.remove(a)
    def corridor(self,c1 : Coord,c2 : Coord) -> None:
        self.dig(c1)
        coord=Coord(c1.x,c1.y)
        while not(coord==c2):
            coord+=self.dircorridor(coord,c2)
            self.dig(coord)
    def dircorridor(self,c1 : Coord,c2 : Coord) -> Coord:
        if c1.y!=c2.y:
            return Coord(0,1) if c1.y<c2.y else Coord(0,-1)
        if c1.x!=c2.x:
            return Coord(1,0) if c1.x<c2.x else Coord(-1,0)
    def reach(self) -> None:
        r1=random.choice(self._rooms)
        r2=random.choice(self._roomsToReach)
        self.corridor(r1.center(),r2.center())
    def reachAllRooms(self) -> None:
        self._rooms.append(self._roomsToReach.pop(0))
        while len(self._roomsToReach)>0:
            self.reach()
    def randRoom(self) -> Room:
        x1=random.randint(0,len(self)-3)
        y1=random.randint(0,len(self)-3)
        largeur=random.randint(3,8)
        hauteur=random.randint(3,8)
        x2=min(len(self)-1,x1+largeur)
        y2=min(len(self)-1,y1+hauteur)
        return Room(Coord(x1,y1),Coord(x2,y2))
    def generateRooms(self,n) -> None:
        for i in range(n):
            r=self.randRoom()
            if self.intersectNone(r):
                self.addRoom(r)
    def checkCoord(self,coord):
        if not(type(coord) is Coord):
            raise TypeError('Not a Coord')
        if not coord in self:
            raise IndexError('Out of map coord')
    def checkElement(self,elem):
        if not(isinstance(elem,Element)):
            raise TypeError('Not a Element')
    def moveAllMonsters(self):
        for i in self._elem:
            if type(i) is Creature and self.pos(i).distance(self.pos(self.hero))<=6:
                self.move(i,self.pos(i).direction(self.pos(self.hero)))

class Game(object):
    "Jeu"
    _actions={"z" : lambda hero : theGame().floor.move(hero,Coord(0,-1)),
              "s" : lambda hero : theGame().floor.move(hero,Coord(0,1)),
              "q" : lambda hero : theGame().floor.move(hero,Coord(-1,0)),
              "d" : lambda hero : theGame().floor.move(hero,Coord(1,0)),
              "i" : lambda hero : theGame().addMessage(hero.fullDescription()),
              "k" : lambda hero : hero.kill(),
              " " : lambda hero : theGame().tour(),
              "u" : lambda hero : hero.use(theGame().select(hero._inventory))
              }
    monsters = { 0: [ Creature("Goblin",4), Creature("Bat",2,"W") ],
                 1: [ Creature("Ork",6,strength=2), Creature("Blob",10) ],
                 5: [ Creature("Dragon",20,strength=3) ] }
    equipments = { 0: [ Equipment("potion","!",usage=heal), Equipment("gold","o") ],
                   1: [ Equipment("sword"), Equipment("bow"),Equipment("potion","!",usage= lambda creature : teleport(creature,True)) ],
                   2: [ Equipment("chainmail") ],
                   3: [ Equipment("portoloin","w",usage= lambda creature : teleport(creature,False))]}
    def __init__(self,hero=None,level=1):
        self.hero=Hero()
        if hero!=None:
            self.hero=hero
        self.level=level
        self.floor=None
        self._message=[]
    def buildFloor(self,size=20) -> None:
        self.floor=Map(hero=self.hero,size=size)
    def addMessage(self,msg) -> None:
        self._message.append(msg)
    def readMessages(self) -> str:
        if self._message!=[]:
            a=". ".join(self._message)+". "
            self._message=[]
            return a
        return ""
    def randElement(self,collection : dict) -> Element:
        x=random.expovariate(1/self.level)
        n=int(x)
        while not(n in collection):
            n-=1
        return copy.copy(random.choice(collection[n]))
    def randEquipment(self) -> Equipment:
        return self.randElement(self.equipments)
    def randMonster(self) -> Creature:
        return self.randElement(self.monsters)
    def select(self,l : List[Equipment]) -> Equipment:
        print("Choose item>",[f"{i}: {l[i].name}" for i in range(len(l))])
        a=getch()
        if a in [str(i) for i in range(len(l))]:
            return l[int(a)]
    def tour(self):
        self.floor.moveAllMonsters()
    def play(self):
        """Main game loop"""
        self.buildFloor()
        print("--- Welcome Hero! ---")
        while self.hero.hp > 0:
            print()
            print(self.floor)
            print(self.hero.description())
            print(self.readMessages())
            c = getch()
            if c in Game._actions:
                Game._actions[c](self.hero)
            self.tour()
        print("--- Game Over ---")

def theGame(game = Game()) -> Game:
    return game

def playthegame(dicimages,fen):
    canvas = Canvas(fen,width=1000,height=600)
    theGame().buildFloor(20)
    theGame().floor.play(fen,dicimages,canvas)
    """actions={"z" : lambda hero : theGame().floor.move(hero,Coord(0,-1)),
              "s" : lambda hero : theGame().floor.move(hero,Coord(0,1)),
              "q" : lambda hero : theGame().floor.move(hero,Coord(-1,0)),
              "d" : lambda hero : theGame().floor.move(hero,Coord(1,0)),
              "i" : lambda hero : theGame().addMessage(hero.fullDescription()),
              "k" : lambda hero : hero.kill(),
              "<space>" : lambda hero : None,
              "u" : lambda hero : hero.use(theGame().select(hero._inventory))}"""
    actions={ "z" : lambda hero :zgetch(),
              "s" : lambda hero :sgetch(),
              "q" : lambda hero :qgetch(),
              "d" : lambda hero :dgetch(),
              "i" : lambda hero :igetch(),
              "k" : lambda hero :kgetch(), 
              "u" : lambda hero :ugetch() }
    theGame().floor.draw(fen,dicimages,canvas)

    [fen.bind(i,actions[i]) for i in actions]
    fen.mainloop()


def updategraph(canvas,dicimages):
    h=100
    theGame().floor.moveAllMonsters()
    canvas.delete("all")
    for i in theGame().floor._mat :
        l=400
        for k in i:
            if k==theGame().floor.hero:
                canvas.create_image(l+1,h+5,image=random.choice(dicimages.get("sol")))
                canvas.create_image(l,h+5,image=random.choice(dicimages.get("sol")))
            elif k!=" " and k!="." :
                canvas.create_image(l+1,h+5,image=random.choice(dicimages.get("sol")))
                canvas.create_image(l,h,image=random.choice(dicimages.get(k)))
            elif k=="." :
                canvas.create_image(l+1,h+5,image=random.choice(dicimages.get("sol")))
            else :
                canvas.create_text(l,h,text=str(k),font="Arial 16")
            l+=32
        h+=32
    canvas.create_text(1600,900,text=theGame().readMessages(),font="Arial 16 italic",fill="blue")
    canvas.create_text(85,60,text=theGame().floor.hero.description(),font="Arial 16 italic",fill="blue")
    canvas.pack()
    if theGame().floor.hero.hp<1 :
        end()

fen=Tk()
fen.attributes('-fullscreen',True)
imgPATH="images/"
hero_idle=PhotoImage(file=imgPATH+"hero_de_face_final.png")
sol_img1=PhotoImage(file=imgPATH+"sol_1.png")
sol_img2=PhotoImage(file=imgPATH+"sol_2.png")
sol_img3=PhotoImage(file=imgPATH+"sol_3.png")
sol_img4=PhotoImage(file=imgPATH+"sol_4.png")
pot_img=PhotoImage(file=imgPATH+"fiole_3_final.png")
dicimages={Map.ground : [sol_img1,sol_img2,sol_img3,sol_img4], "@" : [hero_idle],"!":[pot_img]}
def zgetch():
    getch=lambda a : "z"
def sgetch():
    getch=lambda a : "s"
def qgetch():
    getch=lambda a : "q"
def dgetch():
    getch=lambda a : "d"
def igetch():
    getch=lambda a : "i"
def kgetch():
    getch=lambda a : "k"
def ugetch():
    getch=lambda a : "u"

playthegame(dicimages,fen)
"""
██████████
██████████
██████████🍟
██████████0675130307
██████████vignolopatrizia@gmail.com
██████████pattylyra
██████████■
██████████௹₯
█ █ █ █ █
█ █ █ █ █ lgibart@i3s.unice.fr
█ █ █ █ █
"""