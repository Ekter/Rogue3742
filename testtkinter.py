from tkinter import * 
fenetre = Tk()
canvas = Canvas(fenetre,width=1000,height=600)
filename = PhotoImage(file = "images/sol_1.png")
for x in range(-10,10):
    image = canvas.create_image(320+x*32, 156, anchor=NE, image=filename)
canvas.pack()

fenetre.mainloop()
