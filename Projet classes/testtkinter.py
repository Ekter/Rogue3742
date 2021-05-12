from tkinter import * 
from tkinter.messagebox import *
fenetre = Tk()
canvas = Canvas(fenetre,width=1000,height=600)
filename = PhotoImage(file = "ground.png")
image = canvas.create_image(32, 32, anchor=NE, image=filename)
canvas.pack()

fenetre.mainloop()
