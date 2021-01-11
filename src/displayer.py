import PIL
import tkinter
import tkinter.filedialog

from tkinter import *
from PIL import Image, ImageTk
from enum import Enum


class Displayer:
    def __init__(self, webcam, width=None, height=None):
        self.root = Tk()
        self.root.bind("<Escape>", self.quit)
        appModeBtn = Button(
            self.root, text="Toggle App Mode", command=self.changeAppMode
        )
        composeModeBtn = Button(
            self.root, text="Toggle Compose Mode", command=self.changeComposeMode
        )
        selectBackgroundBtn = Button(
            self.root, text="Select Background", command=self.selectBackground
        )

        self.main = Label(self.root)
        self.main.pack()
        appModeBtn.pack()
        composeModeBtn.pack()
        selectBackgroundBtn.pack()
        self.main.bind("<ButtonPress>", self.leftClick)
        self.main.bind("<Button-3>", self.rightClick)
        self.main.bind("<B1-Motion>", self.mouseMove)
        self.main.bind("<Button-4>", self.scrollUp)
        self.main.bind("<Button-5>", self.scrollDown)

        self.width, self.height = width, height
        self.x = self.y = self.previousX = self.previousY = 0
        self.zoomFactor = 1.25

        self.isRunning = True
        self.COMPOSE_MODES = ["image", "screen"]
        self.APP_MODES = ["normal", "compose"]
        self.composeModeIndex = self.appModeIndex = 0
        self.imageFilename = None
        self.webcam = webcam
        self.flipFactor = 1

    # Update the currently showing frame and return key press char code
    def step(self, image):
        img = PIL.Image.fromarray(image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.main.imgtk = imgtk
        self.main.configure(image=imgtk)
        self.root.update_idletasks()
        self.root.update()
        self.webcam.schedule_frame(image)

        return int(self.x), int(self.y), int(self.width), int(self.height)

    def quit(self, *args):
        self.isRunning = False
        self.root.quit()

    def changeAppMode(self):
        self.appModeIndex = (self.appModeIndex + 1) % len(self.APP_MODES)

    def changeComposeMode(self):
        self.composeModeIndex = (self.composeModeIndex + 1) % len(self.COMPOSE_MODES)

    def selectBackground(self):
        self.imageFilename = tkinter.filedialog.askopenfilename()

    @property
    def composeMode(self):
        return self.COMPOSE_MODES[self.composeModeIndex]

    @property
    def appMode(self):
        return self.APP_MODES[self.appModeIndex]

    @property
    def isFlipped(self):
        return self.flipFactor == -1

    def leftClick(self, event):
        self.previousX, self.previousY = event.x, event.y

    def rightClick(self, event):
        self.flipFactor *= -1

    def mouseMove(self, event):
        self.x += self.flipFactor * (event.x - self.previousX)
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