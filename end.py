import random
import copy
import math
from tkinter import *
from tkinter.messagebox import *

def heal(creature):
    creature.hp+=3
    return True

def teleport(creature,unique=True):
    k=random.choice(theGame().floor._rooms).randEmptyCoord(theGame().floor)
    x=theGame().floor.pos(creature)
    m=k-x
    theGame().floor.move(creature,m)
    if unique and "!" in creature._inventory  :
        creature._inventory.remove("!")
    return unique

def tp(creature):
    k=random.choice(theGame().floor._rooms).randEmptyCoord(theGame().floor)
    x=theGame().floor.pos(creature)
    m=k-x
    theGame().floor.move(creature,m)
    return False

class Coord(object) :
    "Les coordonées"

    def __init__(self,x,y) :
        self.x=x
        self.y=y

    def __eq__(self,other) :
        return (self.x==other.x and self.y==other.y)

    def __repr__(self) :
        return "<"+str(self.x)+","+str(self.y)+">"

    def __add__(self,other) :
        return Coord(self.x+other.x,self.y+other.y)

    def __sub__(self,other) :
        return Coord(self.x-other.x,self.y-other.y)

    def distance(self,other) :
        k=self-other
        return math.sqrt((k.x) ** 2+(k.y) ** 2)

    def direction(self,other) :
        d=self-other
        h=self.distance(other)
        x=d.x/h
        if x>1/math.sqrt(2) :
            return Coord(-1,0)
        elif x<-1/math.sqrt(2) :
            return Coord(1,0)
        else :
            if d.y>0 :
                return Coord(0,-1)
            else :
                return Coord(0,1)


class Element(object) :
    "Un élément du jeu"

    def __init__(self,nom,abbrv="") :
        self.name=nom
        self.abbrv=nom[0] if abbrv=="" else abbrv

    def __repr__(self) :
        return self.abbrv

    def description(self) :
        return ("<"+self.name+">")

    def meet(self,hero) :
        raise NotImplementedError("Not implemented yet")


class Equipment(Element) :
    "Les équipements !"
    def __init__(self,name,abbrv="",usage=None):
        Element.__init__(self,name,abbrv)
        self.usage=usage


    def meet(self,hero) :
        hero.take(self)
        theGame().addMessage("You pick up a "+str(self.name))
        return True

    def use(self,creature):
        if self.usage!=None :
            theGame().addMessage("The "+str(creature.name)+" uses the "+str(self.name))
            return self.usage(creature)
        theGame().addMessage( "The "+str(self.name)+" is not usable")
        return False


class Creature(Element) :
    "Les monstres du jeu !"

    def __init__(self,name,hp,abbrv="",strength=1) :
        Element.__init__(self,name,abbrv)
        self.hp=hp
        self.strength=strength

    def description(self) :
        return Element.description(self)+"("+str(self.hp)+")"

    def meet(self,hero) :
        self.hp+=-(hero.strength)
        theGame().addMessage("The "+str(hero.name)+" hits the "+str(self.description()))
        if self.hp>0 :
            return False
        return True


class Hero(Creature) :
    "Le Hero de l'aventure !"

    def __init__(self,name="Hero",hp=10,abbrv="@",strength=2) :
        Creature.__init__(self,name,hp,abbrv,strength)
        self._inventory=[]

    def take(self,elem) :
        if type(elem)!=Equipment :
            raise TypeError
        self._inventory.append(elem)

    def description(self) :
        return Creature.description(self)+str(self._inventory)

    def fullDescription(self) :
        k=""
        for i in self.__dict__ :
            if i=="_inventory" :
                if self._inventory!=[] :
                    q=("> "+"INVENTORY"+" : "+str([k.name for k in self._inventory]))
                else :
                    q=("> "+"INVENTORY : []")
            else :
                k+=("> "+str(i)+" : "+str(self.__dict__[i])+"\n")
        k+=q
        return k

    def use(self,item):
        if type(item)!=Equipment :
            raise TypeError
        if item not in self._inventory :
            raise ValueError
        k=item.use(self)
        if k==True:
            self._inventory.remove(item)



class Game(object) :
    "Le jeu !"

    equipments={0 : [Equipment("potionH","!",usage=heal),Equipment("gold","o")],1 : [Equipment("sword"),Equipment("bow"),Equipment("potionT","*",usage=teleport)],
                2 : [Equipment("chainmail")],3 :[Equipment("portoloin","w",usage=tp)]}
    monsters={0 : [Creature("Goblin",4),Creature("Bat",2,"W")],
              1 : [Creature("Ork",6,strength=2),Creature("Blob",10)],5 : [Creature("Dragon",20,strength=3)]}

    _actions={"z" : lambda hero : theGame().floor.move(hero,Coord(0,-1)),"s" : lambda hero : theGame().floor.move(hero,Coord(0,1)),
              "q" : lambda hero : theGame().floor.move(hero,Coord(-1,0)),"d" : lambda hero : theGame().floor.move(hero,Coord(1,0)),
              "i" : lambda hero : theGame().addMessage(str(hero.fullDescription())),
              "k" : lambda hero : hero.meet(Creature(name="Mort",hp=9999,strength=hero.hp+9000))," " : lambda hero : None,
              "u" : lambda hero : hero.use(theGame().select(hero._inventory))}

    def __init__(self,hero=None,level=1,floor='',_message='') :
        self.hero=Hero() if hero==None else hero
        self.level=level
        self.floor=None if floor=='' else floor
        self._message=[] if _message=='' else _message

    def buildFloor(self) :
        self.floor=Map(hero=self.hero)

    def addMessage(self,msg) :
        self._message.append(msg)

    def readMessages(self) :
        k=''
        for i in range(len(self._message)) :
            k+=str(self._message[0])+". "
            self._message=self._message[1 :]
        return k

    def randElement(self,collection) :
        x=int(random.expovariate(1/self.level))
        while x not in collection :
            x=x-1
        return copy.copy(random.choice(collection[x]))

    def randEquipment(self) :
        return self.randElement(self.equipments)

    def randMonster(self) :
        return self.randElement(self.monsters)

    def select(self,l):
        m=l.copy()
        for i in l :
            k=l.index(i)
            m[k]=str(k)+": "+i.name
        theGame().addMessage("Choose item>"+str(m))
        canvas.create_text(1600,920,text=theGame().readMessages(),font="Arial 16 italic",fill="blue")
        canvas.pack()
        fenetre.bind("0",chiffre)
        fenetre.bind("1",chiffre)
        fenetre.bind("2",chiffre)
        fenetre.bind("3",chiffre)
        fenetre.bind("4",chiffre)
        fenetre.bind("5",chiffre)
        fenetre.bind("6",chiffre)
        fenetre.bind("7",chiffre)
        fenetre.bind("8",chiffre)
        fenetre.bind("9",chiffre)


    def play(self):
        self.buildFloor()
        self.floor.hero.hp=10
        draw()




class Room(object) :
    "Les salles"

    def __init__(self,c1,c2) :
        self.c1=c1
        self.c2=c2

    def __repr__(self) :
        return "["+str(self.c1)+", "+str(self.c2)+"]"

    def __contains__(self,item) :
        return self.c1.x<=item.x<=self.c2.x and self.c1.y<=item.y<=self.c2.y

    def center(self) :
        return Coord((self.c1.x+self.c2.x)//2,(self.c1.y+self.c2.y)//2)

    def intersect(self,s2) :
        return s2.c1 in self or s2.c2 in self or Coord(s2.c1.x,s2.c2.y) in self or Coord(s2.c2.x,
                                                                                         s2.c1.y) in self or self.c1 in s2 or self.c2 in s2 or Coord(
            self.c1.x,self.c2.y) in s2 or Coord(self.c2.x,self.c1.y) in s2

    def randCoord(self) :
        return Coord(random.randint(self.c1.x,self.c2.x),random.randint(self.c1.y,self.c2.y))

    def randEmptyCoord(self,map) :
        k=self.randCoord()
        while k==self.center() or map.get(k)!=map.ground :
            k=self.randCoord()
        return k

    def decorate(self,map) :
        map.put(self.randEmptyCoord(map),theGame().randEquipment())
        map.put(self.randEmptyCoord(map),theGame().randMonster())


class Map(object) :
    "La map"
    ground="."
    empty=" "
    dir={'z' : Coord(0,-1),'s' : Coord(0,1),'d' : Coord(1,0),'q' : Coord(-1,0)}

    def __init__(self,size=20,hero=None,nbrooms=7) :
        self.size=size
        self._roomsToReach=[]
        self._rooms=[]
        self.hero=Hero() if hero==None else hero
        self._mat=[]
        for i in range(size) :
            self._mat.append([])
        for i in range(size) :
            for k in range(size) :
                self._mat[i].append(self.empty)
        self.generateRooms(nbrooms)
        self.reachAllRooms()
        self._mat[self._rooms[0].center().y][self._rooms[0].center().x]=self.hero
        self._elem={self.hero : Coord(self._rooms[0].center().x,self._rooms[0].center().y)}
        for i in self._rooms :
            i.decorate(self)

    def __repr__(self) :
        k=""
        for i in self._mat :
            for h in i :
                k+=str(h)
            k+="\n"
        return k

    def __len__(self) :
        return self.size

    def __contains__(self,item) :
        if type(item)==Coord :
            return (0<=item.x<=len(self)-1 and 0<=item.y<=len(self)-1)
        for i in self._mat :
            if item in i :
                return True
        return False

    def get(self,c) :
        self.checkCoord(c)
        return self._mat[c.y][c.x]

    def pos(self,e) :
        self.checkElement(e)
        h=-1
        for i in self._mat :
            h+=1
            if e in i :
                k=i.index(e)
                return Coord(k,h)

    def put(self,c,e) :
        self.checkCoord(c)
        self.checkElement(e)
        if self._mat[c.y][c.x]!=self.ground :
            raise ValueError('Incorrect cell')
        if e in self :
            raise KeyError('Already placed')
        self._mat[c.y][c.x]=e
        self._elem[e]=c

    def rm(self,c) :
        k=self.get(c)
        del self._elem[k]
        self._mat[c.y][c.x]=self.ground

    def move(self,e,way) :
        """Moves the element e in the direction way."""
        orig=self.pos(e)
        dest=orig+way
        if dest in self :
            if self.get(dest)==Map.ground :
                self._mat[orig.y][orig.x]=Map.ground
                self._mat[dest.y][dest.x]=e
                self._elem[e]=dest
            elif self.get(dest)!=Map.empty and self.get(dest).meet(e) and self.get(dest)!=self.hero :
                self.rm(dest)

    def addRoom(self,room) :
        for i in range(room.c1.y,room.c2.y+1) :
            for k in range(room.c1.x,room.c2.x+1) :
                self._mat[i][k]=self.ground
        self._roomsToReach.append(room)

    def findRoom(self,coord) :
        for i in self._roomsToReach :
            if coord in i :
                return i
        return False

    def intersectNone(self,room) :
        for i in self._roomsToReach :
            if i.intersect(room) :
                return False
        return True

    def dig(self,coord) :
        self._mat[coord.y][coord.x]=self.ground
        k=self.findRoom(coord)
        if k!=False :
            self._rooms.append(k)
            self._roomsToReach.remove(k)

    def corridor(self,start,end) :
        for i in range(max(start.y,end.y)-min(start.y,end.y)+1) :
            if start.y<end.y :
                self.dig(Coord(start.x,start.y+i))
            else :
                self.dig(Coord(start.x,start.y-i))
        for i in range(max(start.x,end.x)-min(start.x,end.x)+1) :
            if start.x<end.x :
                self.dig(Coord(start.x+i,end.y))
            else :
                self.dig(Coord(start.x-i,end.y))

    def reach(self) :
        sd=random.choice(self._rooms)
        sf=random.choice(self._roomsToReach)
        self.corridor(sd.center(),sf.center())

    def reachAllRooms(self) :
        self._rooms.append(self._roomsToReach[0])
        self._roomsToReach=self._roomsToReach[1 :]
        while self._roomsToReach!=[] :
            self.reach()

    def randRoom(self) :
        x1=random.randint(0,len(self)-3)
        y1=random.randint(0,len(self)-3)
        largeur=random.randint(3,8)
        hauteur=random.randint(3,8)
        x2=min((len(self)-1),(x1+largeur))
        y2=min((len(self)-1),(y1+hauteur))
        return Room(Coord(x1,y1),Coord(x2,y2))

    def generateRooms(self,n) :
        for i in range(n) :
            k=self.randRoom()
            if self.intersectNone(k) :
                self.addRoom(k)

    def checkCoord(self,c) :
        if not (isinstance(c,Coord)) :
            raise TypeError('Not a Coord')
        if c not in self :
            raise IndexError('Out of map coord')

    def checkElement(self,c) :
        if not (isinstance(c,Element)) :
            raise TypeError('Not a Element')

    def moveAllMonsters(self) :
        for i in self._elem :
            if isinstance(i,Creature) and not (isinstance(i,Hero)) and self.get(
                    self._elem[i]+self._elem[i].direction(self._elem[self.hero]))==self.ground :
                if self._elem[i].distance(self._elem[self.hero])<6 :
                    self.move(i,self._elem[i].direction(self._elem[self.hero]))
            elif isinstance(i,Creature) and not (isinstance(i,Hero)) and self._elem[i].distance(
                    self._elem[self.hero])<=1 :
                self.hero.meet(i)

def dpl():
    h=100
    l=400
    theGame().floor.moveAllMonsters()
    canvas.delete("all")
    for i in theGame().floor._mat :
        l=400
        for k in i :
            if k==theGame().floor.hero :
                canvas.create_image(l+1,h+5,image=sol_im)
                canvas.create_image(l,h+5,image=Hero_im)
            elif k!=" " and k!="." :
                canvas.create_image(l+1,h+5,image=sol_im)
                canvas.create_image(l,h,image=choose_im(k))
            elif k=="." :
                canvas.create_image(l+1,h+5,image=sol_im)
            else :
                canvas.create_text(l,h,text=str(k),font="Arial 16")
            l+=32
        h+=32
    canvas.create_text(1600,900,text=theGame().readMessages(),font="Arial 16 italic",fill="blue")
    canvas.create_text(85,60,text=theGame().floor.hero.description(),font="Arial 16 italic",fill="blue")
    if theGame().floor.hero.hp<1 :
        end()


def movez(event) :
    if event.char in theGame()._actions :
        theGame()._actions[event.char](theGame().floor.hero)
    dpl()

def chiffre(event):
    k=theGame().floor.hero._inventory.copy()
    for i in theGame().floor.hero._inventory :
        h=k.index(i)
        k[h]=str(h)+": "+i.name
    for h in k :
        if h[0]==event.char :
            s=k.index(h)
            theGame().floor.hero.use(theGame().floor.hero._inventory[s])
            dpl()
    return None

def draw() :
    canvas.config(width=1920,height=1080)
    h=100
    l=400
    canvas.delete("all")
    for i in theGame().floor._mat :
        l=400
        for k in i :
            if k==theGame().floor.hero :
                canvas.create_image(l+1,h+5,image=sol_im)
                canvas.create_image(l,h+5,image=Hero_im)
            elif k!=" " and k!="." :
                canvas.create_image(l+1,h+5,image=sol_im)
                canvas.create_image(l,h,image=choose_im(k))
            elif k==".":
                canvas.create_image(l+1,h+5,image=sol_im)
            else :
                canvas.create_text(l,h,text=str(k),font="Arial 16")
            l+=32
        h+=32
    fenetre.bind("z",movez)
    fenetre.bind("q",movez)
    fenetre.bind("s",movez)
    fenetre.bind("d",movez)
    fenetre.bind("u",movez)
    fenetre.bind("k",movez)
    fenetre.bind("i",movez)
    fenetre.bind("<space>",movez)
    canvas.pack()
    fenetre.mainloop()

def theGame(game=Game()) :
    return game

def restart() :
    if askyesno('Titre 1','Sûr ?') :
        newGame()
        m=theGame()
        canvas.config(width=1920,height=1080)
        m.play()

def newGame():
    theGame=lambda game=Game():game


def ext():
    exit(0)

def end() :
    canvas.delete("all")
    jouer.destroy()
    nom.destroy()
    exitjeu.destroy()
    canvas.config(width=1920,height=60)
    bas.config(width=1920,height=60)
    mid_t_s.config(width=1920,height=0)
    mess_mort.pack()
    mid.pack()
    reset.pack()
    deadexit.pack()
    basbas.pack()

def choose_im(k):
    h=[Hero_im,sol_im,Goblin_im,Bow_im,Sword_im,gold_im,Blob_im,Chainmail_im,Bat_im,potionT_im,potionH_im,Ork_im]
    h_=["Hero_im","sol_im","Goblin_im","Bow_im","Sword_im","gold_im","Blob_im","Chainmail_im","Bat_im","potionT_im","potionH_im","Ork_im"]
    for i in h_ :
        if k.name==i[:len(i)-3]:
            return h[h_.index(i)]

def start():
    canvas.config(width=1920,height=140)
    nom.pack()
    mid_t_s.pack()
    jouer.pack()
    exitjeu.pack()
    bas.pack()
    fenetre.mainloop()

def clicjouer() :
    if askyesno('Titre 1','Êtes-vous sûr de vouloir faire ça?') :
        m=theGame()
        m.play()


fenetre=Tk()
fenetre.attributes('-fullscreen',True)
Hero_im=PhotoImage(file="images/hero_de_face_final.png")
sol_im=PhotoImage(file="images/sol_1.png")
sol_img2=PhotoImage(file="images/sol_2.png")
sol_img3=PhotoImage(file="images/sol_3.png")
sol_img4=PhotoImage(file="images/sol_4.png")

Goblin_im=PhotoImage(file="images/sol_1.png")
Bow_im=PhotoImage(file="images/sol_1.png")
Sword_im=PhotoImage(file="images/sol_1.png")
gold_im=PhotoImage(file="images/sol_1.png")
Blob_im=PhotoImage(file="images/sol_1.png")
Chainmail_im=PhotoImage(file="images/sol_1.png")
Bat_im=PhotoImage(file="images/sol_1.png")
potionT_im=PhotoImage(file="images/sol_1.png")
potionH_im=PhotoImage(file="images/fiole_3_final.png")
Ork_im=PhotoImage(file="images/sol_1.png")
canvas=Canvas(fenetre,width=1920,height=1080)
mid=Canvas(fenetre,width=1920,height=200)
mid_t_s=Canvas(fenetre,width=1920,height=200)
bas=Canvas(fenetre,width=1920,height=700)
basbas=Canvas(fenetre,width=1920,height=700)
label = Label(fenetre, text="Vous êtes mort !",font="Arial 26")
jouer=Button(width=10,height=3,text='Jouer',command=clicjouer)
nom=Label(fenetre,text="NOM DU JEU !",font="Arial 30",fg='red',bg='pink')
exitjeu=Button(text='Exit',command=ext)
reset=Button(text='Restart',command=restart)
deadexit=Button(text='Exit',command=ext)
mess_mort=Label(fenetre,text="Vous êtes mort !",font="Arial 26")
canvas.pack()

#m=theGame()
#m.play()
start()
