import PIL

from tkinter import *
from PIL import Image, ImageTk
from enum import Enum

class Displayer:
    def __init__(self, title, width=None, height=None):
        self.root = Tk()
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.btn = Button(self.root, text='Capturar Fundo', command=self.changeState)
        self.main = Label(self.root)
        self.main.pack()
        self.btn.pack()
        self.main.bind('<ButtonPress>', self.buttonPress)
        self.main.bind('<B1-Motion>', self.mouseMove)
        self.main.bind('<Button-4>', self.scrollUp)
        self.main.bind('<Button-5>', self.scrollDown)

        self.title, self.width, self.height = title, width, height
        self.x = self.y = self.previousX = self.previousY = 0
        self.zoomFactor = 1.25
        self.state = True

    # Update the currently showing frame and return key press char code
    def step(self, image):
        img = PIL.Image.fromarray(image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.main.imgtk = imgtk
        self.main.configure(image=imgtk)
        self.root.update_idletasks()
        self.root.update()
        
        return int(self.x), int(self.y), int(self.width), int(self.height)

    def changeState(self):
        self.state = not self.state
    
    def buttonPress(self, event):
        self.previousX, self.previousY = event.x, event.y
        
    def mouseMove(self, event):
        self.x += event.x - self.previousX
        self.y += event.y - self.previousY
        self.previousX, self.previousY = event.x, event.y
        
    def scrollUp(self, event):
        x1, y1 = event.x, event.y
        self.x = x1 - (x1 - self.x) * self.zoomFactor
        self.y = y1 - (y1 - self.y) * self.zoomFactor
        self.width *= self.zoomFactor
        self.height *= self.zoomFactor

    def scrollDown(self, event):
        x1, y1 = event.x, event.y
        self.x = x1 - (x1 - self.x) / self.zoomFactor
        self.y = y1 - (y1 - self.y) / self.zoomFactor
        self.width /= self.zoomFactor
        self.height /= self.zoomFactor