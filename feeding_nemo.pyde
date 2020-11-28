add_library('minim')

import random, os, datetime

path = os.getcwd()

WIDTH = 800
HEIGHT = 700

directions = [LEFT, RIGHT]
font = loadFont(path + "/data/bebas_neue.vlw")

class Fish():
    def __init__(self, posX, posY, size, img, speed):
        self.posX = posX
        self.posY = posY
        
        self.img = loadImage(path + "/images/" + img)
        self.size = size

        self.speed = speed
        
        self.direction = random.choice(directions)
        
        self.cropStart = random.randint(0, 4)
    
    def display(self):
        singleSize = self.img.width / 5
        
        if frameCount % 5 == 0 or frameCount == 1:
            
            self.cropStart += 1
            if self.cropStart >= 5:
                self.cropStart = 0 
                
        if self.direction == RIGHT:
            pushMatrix()
            scale(1, 1)
            image(self.img, self.posX, self.posY, self.size, self.size, self.cropStart * singleSize, 0, self.cropStart * singleSize + singleSize, self.img.height)
            popMatrix()
        else:
            pushMatrix()
            scale(-1, 1)
            image(self.img, -self.posX, self.posY, -self.size, self.size, self.cropStart * singleSize, 0, self.cropStart * singleSize + singleSize, self.img.height)
            popMatrix()
    
class Player(Fish):
    def __init__(self, posX, posY, size, img, speed):
        Fish.__init__(self, posX, posY, size, img, speed)
        
        self.alive = True
    
    def update(self):
        pass
    
class Prey(Fish):
    def __init__(self, posX, posY, size, img, speed):
        Fish.__init__(self, posX, posY, size, img, speed)

class Predator(Fish):
    def __init__(self, posX, posY, size, img, speed):
        Fish.__init__(self, posX, posY, size, img, speed)

class Shark(Fish):
    def __init__(self, posX, posY, size, img, speed):
        Fish.__init__(self, posX, posY, size, img, speed)

class Tokens():
    def __init__(self):
        self.x = random.randint(100, 1100)
        self.y = random.randint(100, 620)
        
class Game():
    def __init__(self, w, h):
        self.bgImage = loadImage(path + "/images/marine.jpg")
        self.w = w
        self.h = h
        
        self.score = 0
        self.start = datetime.datetime.now()
        
        self.level = 1
        
        self.playerMove = {LEFT: False, RIGHT: False, UP: False, DOWN: False} 
        
        self.nemo = Player(self.w/2, self.h/2, 80, "nemo_char.png", 3.2)
        
        self.screen = 1
        
        #self.bg_music = player.loadFile(path + "/sounds/background.mp3")
        #self.bg_music.loop()
        #self.tokens = []
        #for i in range(10):
        #    self.tokens.append(Tokens())
        #self.preys = []
        #for i in range(20):
        #    self.preys.append(Prey())
        #self.predators = []
        #for i in range(5):
        #    self.predators.append(Predator())
        #self.keyHandler = {ENTER:False, ESC:False}
        
    def update(self):
        if self.screen == 0:
            self.mainMenu()
            
        elif self.screen == 1 and self.nemo.alive:
            self.nemo.display()
            
            textFont(font)
            fill(255)
            
            textAlign(RIGHT)
            textSize(30)
            text("SCORE", self.w - 20, 40)
            
            textSize(22)
            text(str(self.score), self.w - 20, 65)
            
            textAlign(LEFT)
            textSize(30)
            text("LEVEL " + str(self.level), 20, 40)
            
            textSize(22)
            text(self.getTimer((datetime.datetime.now() - self.start).total_seconds()), 20, 65)
            
            if mousePressed:
                mouseHandler()
            
        # x = 0
        # cnt = 1 if paralex ill try to find a backround 
        # that will do that with a fixed front
        
        #for p in self.prey:
        #    p.display()

        #for p2 in self.predators:
        #    p2.display()
        
        #for t in self.tokens:
        #    t.display()
        
    def getTimer(self, seconds):
        minutes = floor(seconds / 60)
        
        timeString = ""
        
        if minutes > 0:
            timeString = str(minutes) + ":" + str(floor(seconds - (minutes * 60)))
        else:
            timeString = "0:" + str(floor(seconds))
            
        return timeString
    
    def mainMenu(self):
        pass
    
game = Game(WIDTH, HEIGHT)

def setup():
    size(WIDTH, HEIGHT)

def draw():
    background(game.bgImage)
    game.update()
    
#i was thinking press enter if you lose or win(to go to the next level or something)
def keyPressed():
    if keyCode == ENTER:
        """whichever function we use
        what this key will do: if game.alive increment level else game.alive = True
        game.keyHandler[ENTER] = True"""
    if keyCode == ESC:
        """end game? change game.alive to False basically 
        we don't have to use it it's just an option"""

def mouseHandler():
    playerCenterX = game.nemo.posX + game.nemo.size / 2
    playerCenterY = game.nemo.posY + game.nemo.size / 2
    
    mouseReleased()
    
    increment = [0, 0]
    
    if (mouseY - playerCenterY) < (-1) * (game.nemo.size / 2):
        game.playerMove[UP] = True
        increment[1] = -(game.nemo.speed)
        
    elif (mouseY - playerCenterY) > (game.nemo.size / 2):
        game.playerMove[DOWN] = True
        increment[1] = game.nemo.speed
    
    if (mouseX - playerCenterX) < (-1) * (game.nemo.size / 2):
        game.playerMove[LEFT] = True
        game.nemo.direction = LEFT
        increment[0] = (-game.nemo.speed)
        
    elif (mouseX - playerCenterX) > (game.nemo.size / 2):
        game.playerMove[RIGHT] = True
        game.nemo.direction = RIGHT
        increment[0] = game.nemo.speed
        
    # checking if the player is within the game window
    if game.nemo.posX + increment[0] < (game.w - game.nemo.size) and game.nemo.posX + increment[0] > 0:
        game.nemo.posX += increment[0]
        
    if game.nemo.posY + increment[1] < (game.h - game.nemo.size) and game.nemo.posY + increment[1] > 0:
        game.nemo.posY += increment[1] 
    
def mouseReleased():
    for k in game.playerMove:
        game.playerMove[k] = False
    
    
