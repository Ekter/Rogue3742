"""██████████
    ██████████
    ██████████
    ██████████
    ██████████
    ██████████
    ██████████■
    ██████████
     █ █ █ █ █
    █ █ █ █ █ 
     █ █ █ █ █

"""
import random
class Carte(str):
    def remplirrectangle(self,x1,y1,x2,y2):
        carteliste=self.split("\n")
        cartelisteliste=[i.split("") for i in carteliste]
        print(cartelisteliste)


carte=Carte((" "*37+"\n")*37)
carte.remplirrectangle(0,0,0,0)
"""for i in range(4):

for i in carteliste:
    k=random.randint(0,len())
    i=i
"""