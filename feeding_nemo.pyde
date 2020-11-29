add_library('minim')

import random, os, datetime

path = os.getcwd()

WIDTH = 800
HEIGHT = 700

# this is to set random direction for every Fish object during __init__() (also nemo and enemies as they inherit from Fish class)
directions = [LEFT, RIGHT]

# font for text (LEVEL, TIMER, SCORE)
font = loadFont(path + "/data/bebas_neue.vlw")

class Fish():
    def __init__(self, posX, posY, size, img, speed):
        
        # the x and y coordinates of the obj, x and y seemed confusing so I've used posX and posY
        self.posX = posX
        self.posY = posY
        
        # image path for nemo and enemies
        self.img = loadImage(path + "/images/" + img)
        
        # instead of radius, i've called it size so that we can take this variable to compare nemo's size and enemies' size when they're near
        self.size = size

        # this speed determines the increment for posX and posY when the obj moves around the screen, see mouseHandler()
        self.speed = speed
        
        # initializing random direction for nemo and enemies
        self.direction = random.choice(directions)
        
        # this is to crop every characters image
        # like in super mario, there's one single image for mario and then prof. crops it to show movement animation at every certain frameCount
        # for eg: in our game, the nemo_char.png has 5 nemos together
        # so we generate a random position from 0 to 4 and then multiply this value with (total image size)/5 i.e. the size of individual character (nemo or enemy)
        self.cropStart = random.randint(0, 4)
    
    def display(self):
        
        # individual image size of our character (because we have 5 images in a single PNG)
        # total image width / 5
        singleSize = self.img.width / 5
        
        # when frameCount % 5, we use the cropStart value to determine our start position (x1, y1) like (self.cropStart * singleSize, 0)
        if frameCount % 5 == 0 or frameCount == 1:
            
            # when cropStart reaches 5 we need to set it to 0 cuz 5 * singleSize is null
            self.cropStart += 1
            if self.cropStart >= 5:
                self.cropStart = 0 
                
        # checking the direction of our Fish (also nemo, enemies) and displaying them respectively
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
    
class Enemy(Fish):
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
        
        # this is for the timer, we take the datetime value during __init__ and then on every frame we check time diffrence in seconds
        # then we use the getTimer() function inside Game class to get the timer format in M:S
        self.start = datetime.datetime.now()
        
        self.level = 1
        
        # the following line was here before. going through the code again, I realized it was unnecessary. I only used it for testing, so it's not required now
        # self.playerMove = {LEFT: False, RIGHT: False, UP: False, DOWN: False} 
        
        self.nemo = Player(self.w/2, self.h/2, 80, "nemo_char.png", 3.2)
        
        # to know which screen we're in, Main Menu, the Game, GameOver screen
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
            
            # LEVEL, TIMER and SCORE
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
            
            # I placed the mousePressed here instead of using mousePressed() function at the end
            # cuz we need to check it every time the game updates
            # if we use mousePressed() at the end, it'll trigger the function just once
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
        
    # to get the TIMER format (M:S)
    def getTimer(self, seconds):
        minutes = floor(seconds / 60)
        
        timeString = ""
        
        if minutes > 0:
            timeString = str(minutes) + ":" + str(floor(seconds - (minutes * 60)))
        else:
            timeString = "0:" + str(floor(seconds))
            
        return timeString
    
    # for the MainMenu
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
    if keyCode == 32: # SPACEBAR
        print("hello")
        
    if keyCode == ENTER:
        """whichever function we use
        what this key will do: if game.alive increment level else game.alive = True
        game.keyHandler[ENTER] = True"""
    if keyCode == ESC:
        """end game? change game.alive to False basically 
        we don't have to use it it's just an option"""

# this is the main function that handles nemo's movement
def mouseHandler():
    
    # addition: rotate() fish while moving towards the diagonals
    
    # to get the center co-ordinates of our nemo instead of getting top left coordinates
    playerCenterX = game.nemo.posX + game.nemo.size / 2
    playerCenterY = game.nemo.posY + game.nemo.size / 2
    
    # posX and posY increment values
    # increment will be the speed of Fish
    # that's why I've used speed inside the Fish class
    # we can declare different speed for our nemo and other individual enemies as well as the shark
    increment = [0, 0]
    
    # if the mouse position is more than half of the nemo's size, we move Nemo, else it doesn't move
    if (mouseY - playerCenterY) < (-1) * (game.nemo.size / 2):
        increment[1] = -(game.nemo.speed)
        
    elif (mouseY - playerCenterY) > (game.nemo.size / 2):
        increment[1] = game.nemo.speed
    
    if (mouseX - playerCenterX) < (-1) * (game.nemo.size / 2):
        game.nemo.direction = LEFT
        increment[0] = (-game.nemo.speed)
        
    elif (mouseX - playerCenterX) > (game.nemo.size / 2):
        game.nemo.direction = RIGHT
        increment[0] = game.nemo.speed
        
    # checking if the player is within the game window
    if game.nemo.posX + increment[0] < (game.w - game.nemo.size) and game.nemo.posX + increment[0] > 0:
        game.nemo.posX += increment[0]
        
    if game.nemo.posY + increment[1] < (game.h - game.nemo.size) and game.nemo.posY + increment[1] > 0:
        game.nemo.posY += increment[1] 
    
    
# mouseReleased() is not necessary as we removed game.playerMove
