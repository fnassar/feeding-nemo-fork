'''
Feeding Nemo
Final Project - Team Pink (#4)
Intro to CS, Fall 2020
'''

add_library('minim')

import random, os, datetime, math, socket, threading, sys

# path to the current working directory
path = os.getcwd()

# game dimensions
WIDTH = 1100
HEIGHT = 684

# direction options when a game character is initialized
directions = [LEFT, RIGHT]

# Bebas Neue - Font for the text
font = loadFont(path + "/fonts/bebas_neue.vlw")

# Minim object for sound
audio = Minim(this)

# to track if the game has already started once
gameStarted = False

# class used for communicating with the server
# during Multiplayer Mode
class Network():
    def __init__(self):    
        # data encoding and decoding format
        self.__FORMAT = "utf-8"
        
        # server connection info
        PORT = 4040
        SERVER = "40.76.33.105" # Public IP Address of the Microsoft Azure VM (OS - Linux [ubuntu 18.04])
        self.__ADDR = (SERVER, PORT)
        
        self.player = 0
        self.scores = {1: "000", 2: "000", 3: "000"}
        self.success = False
        
        # to check if the server already has a session started
        # by other players
        self.serverFull = False
    
    # method used to connect to the server
    def connect(self):
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect(self.__ADDR)
        
        # to show WAITING screen while other players are getting ready
        game.screen = 10
        
        # starting a new thread for communication
        # in order to make it asynchronous
        thread = threading.Thread(target = self.__send, args = ("PLAYER_000:000",))
        thread.start()
    
    # method that sends data to the server
    def __send(self, msg):
        try:
            message = msg.encode(self.__FORMAT)
            self.__client.send(message)
            
            if self.player == 0:
                # first data it receives will be the player position
                res = self.__client.recv(1).decode(self.__FORMAT)
        
                # in case the server is full, it receives "F"
                if res == "F":
                    self.serverFull = True
                else:
                    self.player = int(res)
                    
                    res = self.__client.recv(16).decode(self.__FORMAT)
                    
                    # once everyone is ready, it receives "[NEMO.INITIATE]"
                    # and the game will start for everyone
                    while res.strip() != "[NEMO.INITIATE]":
                        res = self.__client.recv(16).decode(self.__FORMAT)
                        
                    self.success = True
                    game.screen = 1
                    
                    # assigning the start time (for timer)
                    game.start = datetime.datetime.now()
            else:
                # receiving scores of all players
                res = self.__client.recv(19).decode(self.__FORMAT)
                res = res.replace("[", "").replace("]", "")
                
                # deciphering scores
                for s in res.split(","):
                    singleData = s.split(":")
                    player = int(singleData[0])
                    score = singleData[1]
                    self.scores[player] = score
        except:
            # exit if there's any error
            sys.exit()
    
    # method that sends score data to the server
    def updateScore(self):
        data = "PLAYER_00" + str(self.player) + ":" + "0" * (3 - len(str(game.score))) + str(game.score)
        thread = threading.Thread(target = self.__send, args = (data,))
        thread.start()
        
# every character is a Fish, so this is the super class
# which will be inherited by the Player[Nemo], Preys, Predators, and Shark [Enemy]
class Fish():
    def __init__(self, posX, posY, size, img, speed):
        # character's position and rotation
        self.posX = posX
        self.posY = posY
        self.rotation = 0
        
        # character's image
        self._img = loadImage(path + "/images/" + img)
        
        # size and speed
        self.size = size
        self.speed = speed
        
        # assigning random direction during initialization
        self.direction = random.choice(directions)
        
        # start index for cropping the image
        self._cropStart = random.randint(0, 4)
    
    # method to render character on screen
    def display(self):
        self._update()
        
        # center coordinates to calculate angle for rotation
        playerCenterX, playerCenterY = self.getCenterCoordinates()
        if self.__class__.__name__ == "Player":
            # using arctan of the slope
            # math.atan2() to get angle in radians
            self.rotation = math.atan2((mouseY - playerCenterY), (mouseX - playerCenterX))

        # individual size of the character in sprite image
        singleSize = int(self._img.width / self.imageCount)
        
        # character ratio
        ratio = float(self._img.height) / float(singleSize)
        
        # updating the crop index for image
        if frameCount % 5 == 0 or frameCount == 1:
            self._cropStart += 1
            if self._cropStart >= self.imageCount:
                self._cropStart = 0 
                
        # assigning direction with respect to the rotation angle 
        if abs(self.rotation) > (math.pi / 2):
            self.direction = LEFT
        else:
            self.direction = RIGHT
        
        # rendering character on screen
        pushMatrix()
        imageMode(CENTER)
        translate(self.posX, self.posY)
        rotate(self.rotation)
        
        if self.direction == RIGHT:
            scale(1, 1)
            image(self._img, 0, 0, self.size, self.size * ratio, self._cropStart * singleSize, 0, (self._cropStart * singleSize + singleSize), self._img.height)
        else:
            scale(-1, 1)
            image(self._img, 0, 0, -self.size, self.size * ratio, (self._cropStart * singleSize + singleSize), self._img.height, self._cropStart * singleSize, 0)
            
        popMatrix()
        
    # method to get central coordinates
    def getCenterCoordinates(self):
        return self.posX + self.size / 2, self.posY + self.size / 2

# main player of the game - Nemo
class Player(Fish):
    def __init__(self, posX, posY, size, img, speed):
        Fish.__init__(self, posX, posY, size, img, speed)
        
        self.imageCount = 8
        self.alive = True
        
        # audio
        self.eat = audio.loadFile(path + "/audio/nemo_eat.mp3")
        self.tokenEat = audio.loadFile(path + "/audio/token.mp3")
    
    # method to update the player movements
    def _update(self):
        if mousePressed:
            mouseHandler()

# class for Preys, Predators and the Shark (all are enemies)
class Enemy(Fish):
    def __init__(self, posX, posY, size, img, speed, imageCount):
        Fish.__init__(self, posX, posY, size, img, speed)
        self.imageCount = imageCount
        
        # for incrementing the position
        self.__increment = [self.speed, self.speed]
        
    # to update direction and position
    def _update(self):
        self._check()
        
        if (self.posX + self.size / 2 + self.speed) > game.w:
            self.rotation = math.pi
            self.__increment[0] = -self.speed
        elif (self.posX - self.size / 2 - self.speed) < 0:
            self.rotation = 0
            self.__increment[0] = self.speed
            
        if (self.posY + self.size / 2 + self.speed) > game.h:
            self.__increment[1] = -self.speed
        elif (self.posY - self.size / 2 - self.speed) < 0:
            self.__increment[1] = self.speed
        
        self.posX += self.__increment[0]
        self.posY += self.__increment[1]
    
    # to check if the enemy eats Nemo or is eaten by Nemo
    def _check(self):
        if dist(self.posX, self.posY, game.nemo.posX, game.nemo.posY) < self.size / 2 + game.nemo.size / 3:
            if self.size > game.nemo.size:
                game.nemo.alive = False
            else:
                game.nemo.eat.rewind()
                game.nemo.eat.play()
                game.score += 10
                
                # in case Multiplayer mode is ON, update the score on network
                if game.multiPlayer:
                    game.network.updateScore()
                    
                game.preys.remove(self)

# Shark is an enemy so it inherits from Enemy class (which inherits from Fish)
# multilevel inheritance        
class Shark(Enemy):
    def __init__(self, posX, posY, size, img, speed, imageCount):
        Enemy.__init__(self, posX, posY, size, img, speed, imageCount)
        
        self.inGame = False
        
        # audio for Shark
        self.sound = audio.loadFile(path + "/audio/shark.mp3")
    
    # to update its position
    def _update(self):
        self._check()
        
        self.__increment = [-self.speed * 4, 0]
        
        self.posX += self.__increment[0]
        self.posY += self.__increment[1]
        
        if self.posX <= (-self.size / 2):
            self.inGame = False
            self.posX, self.posY = game.w + self.size / 2, random.randint(50, game.h - 50)

# Tokens or Stars in game that Nemo has to collect
class Token():
    def __init__(self, x, y):
        
        # x, y positions
        self.posX = x 
        self.posY = y
        
        # token image
        self.__img = loadImage(path + "/images/token.png")
        
        # its size
        self.__size = 30
        
        # crop index similar to Fish
        self.__cropStart = random.randint(1, 23)
        
        # image count for rotating animation
        self.__imageCount = 23

    # to render token on screen
    def display(self):
        tokenSize = self.__img.width / self.__imageCount

        if frameCount % 2 == 0 or frameCount == 1:
            self.__cropStart += 1
            if self.__cropStart >= 23:
                self.__cropStart = 0
                
        image(self.__img, self.posX, self.posY, self.__size, self.__size, self.__cropStart * tokenSize, 0, self.__cropStart * tokenSize + tokenSize, self.__img.height)
        
        # to check if it is eaten by Nemo
        if dist(self.posX, self.posY, game.nemo.posX, game.nemo.posY) <= (game.nemo.size / 2 + self.__size / 2):
            game.nemo.tokenEat.rewind()
            game.nemo.tokenEat.play()
            
            game.score += 1
            
            if game.multiPlayer:
                game.network.updateScore()
            
            game.tokens.remove(self)

# the main Game class
class Game():
    def __init__(self, w, h):
        
        # dimensions
        self.w = w
        self.h = h
        
        # multiplayer status
        self.multiPlayer = False
        self.network = None
        
        # keyboard key handler
        self.keyHandler = {32: False, 10: False, 83: False, 77: False}

        # screen index - Main Menu, Gameplay, Win, Game Over
        self.screen = 0
        
        # player's score
        self.score = 0
        
        # level index
        self.level = 1
        
        # start time when initialized - for timer
        self.start = datetime.datetime.now()
        
        # game's background (with parallex effect)
        self.bg = Background(self.w, self.h)
        
        # tokens that Nemo has to collect
        self.tokens = []
        
        # to add Nemo, preys, predators, and shark
        self.__addCharacters(self.level)
        
        # if it's a restart, we don't play background music again
        global gameStarted
        if not gameStarted:
            self.background = audio.loadFile(path + "/audio/background.mp3")
            self.background.loop()
            gameStarted = True
        
        # audio for game over
        self.__gameOverAudio = audio.loadFile(path + "/audio/game_over.mp3")
        
        # images for multiple screens
        self.__mainMenuImg = loadImage(path + "/images/mainMenu.png")
        self.__level2WelcomeImg = loadImage(path + "/images/level2Welcome.png")
        self.__winImg = loadImage(path + "/images/winImage.png")
    
    # method that adds characters in level 1 and 2 (in different ways)
    def __addCharacters(self, state):
        
        # the main player - Nemo
        self.nemo = Player(200, 200, 90 if state == 1 else 110, "nemo.png", 4)
        
        # preys and predators
        fishCount = [6, 5, 4, 6, 6]
        self.preys = []
        for i in range(15 if state == 1 else 10):
            fish = random.randint(0, 4)
            self.preys.append(Enemy(random.randint(100, self.w - 100), random.randint(50, self.h - 50), self.nemo.size / (2 if state == 1 else 3), "fish" + str(fish + 1) + ".png", random.uniform(1.5, 3), fishCount[fish]))
                              
        self.predators = []
        for i in range(5):
            fish = Enemy(random.randint(300, self.w - 100), random.randint(50, self.h - 50), self.nemo.size * 1.5 / (1 if state == 1 else 2), "predator.png", random.uniform(1.5, 2.2), 5)
            if state == 1:
                self.predators.append(fish)
            else:
                self.preys.append(fish)
        
        if not state == 1:
            for i in range(3):
                self.predators.append(Enemy(random.randint(300, self.w - 100), random.randint(50, self.h - 50), self.nemo.size * 1.5, "predator2.png", random.uniform(1.5, 2.2), 9))

        # the shark that enters every 30 seconds
        self.shark = Shark(self.w, random.randint(50, self.h - 50), self.nemo.size * 3, "shark.png", random.uniform(1.5, 2.2), 6)
        
    # to update the game screen
    def update(self):        
        if self.screen == 0:
            # main menu
            self.__mainMenu()
            
        elif self.screen == 2:
            self.shark.sound.pause()
            
            # to show welcome screen before Level 2
            if self.level == 1:
                imageMode(CORNER)
                image(self.__level2WelcomeImg, 0, 0)
                
                if self.keyHandler[32] == True:
                    self.__addCharacters(2)
                    self.level = 2
                    self.screen = 1
                    
                    self.__resetKeys()
            
            # if the user wins, showing a winning screen
            elif self.level == 2:
                imageMode(CORNER)
                image(self.__winImg, 0, 0)
                
                if self.keyHandler[32]:
                    
                    if not self.multiPlayer:
                        self.__newGame()
                    else:
                        # if multiplayer mode was ON, showing scores of all players
                        self.screen = 11
                        
                    self.__resetKeys()
        
        # the main gameplay
        elif self.screen == 1 and self.nemo.alive:
            self.bg.display()
            self.nemo.display()
            
            # if there are no preys, Nemo moves to new level or wins
            if len(self.preys) == 0:
                self.screen = 2
            
            # total seconds spent
            timeSpent = floor((datetime.datetime.now() - self.start).total_seconds())
            
            # to update the tokens every 10 seconds
            if (timeSpent % 10 == 0) and (frameCount % 20 == 0 or frameCount == 1) and len(self.tokens) <= 10: 
                self.tokens.append(Token(random.randint(100, self.w - 100), random.randint(100, self.h - 100)))
            
            # displaying the tokens
            for token in self.tokens:
                token.display()
    
            # displaying other fish (preys and predators)
            for otherFish in self.preys + self.predators:
                otherFish.display()

            # entering shark every 30 seconds
            if timeSpent % 30 == 0 and timeSpent != 0:
                self.shark.inGame = True
                
                # playing shark's sound
                self.shark.sound.rewind()
                self.shark.sound.loop()
            
            if self.shark.inGame:
                self.shark.display()
            else:
                self.shark.sound.pause()
            
            # displaying the Score(s)
            textMode(CORNER)
            fill(255)
            
            textAlign(RIGHT)
            textSize(30)
            text("SCORE", self.w - 20, 40)
            
            textSize(22)
            if self.multiPlayer:
                count = 0
                for s in self.network.scores:                    
                    player = "YOU"
                    if s != self.network.player:
                        player = "P" + str(s)
                        
                    text(player + ": " + str(self.network.scores[s]), self.w - 20, 65 + count * 25)
                    
                    count += 1
            else:
                text(self.score, self.w - 20, 65)
            
            # displaying level index
            textAlign(LEFT)
            textSize(30)
            text("LEVEL " + str(self.level), 20, 40)
            
            textSize(22)
            text(self.__getTimer((datetime.datetime.now() - self.start).total_seconds()), 20, 65)
       
        # displaying waiting screen for multiplayer mode (until other players join)
        elif self.screen == 10:
            textAlign(CENTER)
            textMode(CENTER)
            textSize(40)
            
            waitingTxt = "WAITING FOR OTHER PLAYERS TO JOIN..."
            
            # if the server is busy
            if self.network.serverFull:
                waitingTxt = "SORRY, THE SERVER IS BUSY"
                
            text(waitingTxt, self.w / 2, self.h / 2)
            textSize(25)
            text("Press ESC to exit", self.w / 2, (self.h / 2) + 30)
        
        # if the player wins in multiplayer mode, displaying scores of all players
        elif self.screen == 11:
            textAlign(CENTER)
            textMode(CENTER)
            textSize(40)
            
            text("SCORES", self.w / 2, self.h / 2)
            textSize(25)
            
            allScores = ""
            for count in self.network.scores:
                player = "Player " + str(count)
                if count == self.network.player:
                    player = "You"
                allScores += player + ": " + str(self.network.scores[count])
                
                if count != len(self.network.scores):
                    allScores += " " * 5
                    
            text(allScores, self.w / 2, self.h / 2 + 30)
            
            # starting new game when pressed SPACEBAR
            if self.keyHandler[32]:
                self.__newGame()
                self.__resetKeys()
        
        # the game over screen
        else:
            self.shark.sound.pause()
            self.__gameOverAudio.play()
            
            textAlign(RIGHT)
            textMode(CORNER)
            textSize(30)
            text("YOUR SCORE", self.w - 20, 40)
            textSize(22)
            text(self.score, self.w - 20, 65)
                 
            img = loadImage(path + "/images/gameOver.png")
            imageMode(CORNER)
            image(img,0,0)
            
            if not self.multiPlayer:
                textAlign(CENTER)
                textMode(CENTER)
                textSize(30)
                text("Press SPACE to restart", self.w / 2, (self.h / 2) + 100)
                
                if self.keyHandler[32]:
                    self.__newGame()
                    self.__resetKeys()
    
    # method to get timer (string in the format M:S)
    def __getTimer(self, seconds):
        minutes = floor(seconds / 60)
        
        timeString = ""
        
        if minutes > 0:
            timeString = str(minutes) + ":" + str(floor(seconds - (minutes * 60)))
        else:
            timeString = "0:" + str(floor(seconds))
            
        return timeString
    
    # method to start a new game
    def __newGame(self):
        self.screen = 1
        global game
        game = Game(WIDTH, HEIGHT)
    
    # method to display main menu
    def __mainMenu(self):
        background(255)
        imageMode(CENTER)
        image(self.__mainMenuImg, self.w / 2, self.h / 2, self.w, self.h)
        
        # single player mode - S
        if self.keyHandler[83]:
            self.screen = 1
            self.start = datetime.datetime.now()
            self.__resetKeys()
            
        # multiplayer mode - M
        elif self.keyHandler[77]:
            self.multiPlayer = True
            self.network = Network()
            self.network.connect()
            
            self.__resetKeys()
    
    # resetting keyHandler
    def __resetKeys(self):
        self.keyHandler = {32: False, 10: False, 83: False, 77: False} 

# the background of the game (with parallex effect)
class Background():
    def __init__(self, w, h):
        self.bgImage = loadImage(path + "/images/marine.png")
        
        # dimensions
        self.w = w
        self.h = h
        
        # horizontal shift
        self.__xShift = 0
        
        # other images except for the main background
        self.__otherImages = []
        for i in range(3, 0, -1):
            self.__otherImages.append(loadImage(path + "/images/" + str(i) + ".png"))
    
    # to render the background
    def display(self):
        if game.nemo.direction == RIGHT:
            self.__xShift += 2
        elif game.nemo.direction == LEFT: 
            self.__xShift -= 2
        else:
            self.__xShift = 0
        
        count = 1
        x = 0
        for img in self.__otherImages:
            if count == 1:
                x = self.__xShift // 3
            elif count == 2:
                x = self.__xShift // 2
            else:
                x = self.__xShift        
            
            widthR = x % self.w
            widthL = self.w - widthR
            
            imageMode(CORNER)
            image(img, 0, 0, widthL, self.h, widthR, 0, self.w, self.h)
            image(img, widthL, 0, widthR, self.h, 0, 0, widthR, self.h)
            
            count += 1

# the main game object
game = Game(WIDTH, HEIGHT)

# initial setup
def setup():
    size(WIDTH, HEIGHT)
    textFont(font) # Bebas Neue

# updating the game screen
def draw():
    background(game.bg.bgImage)
    game.update()

# to handle key press
def keyPressed():
    if keyCode == 32: # SPACEBAR
        game.keyHandler[32] = True
        
    elif keyCode == 10: # ENTER
        game.keyHandler[10] = True
    
    elif keyCode == 83: # S or s
        game.keyHandler[83] = True
        
    elif keyCode == 77: # M or m
        game.keyHandler[77] = True
        
    elif keyCode == 27: # ESC
        sys.exit()

# to handle player movement using mouse
def mouseHandler():
    
    # player's center coordinates
    playerCenterX, playerCenterY = game.nemo.getCenterCoordinates()
    
    # get x, y increment values with respect to the mouse position
    increment = [0, 0]
    if (mouseY - playerCenterY) < (-1) * (game.nemo.size / 2):
        increment[1] = -(game.nemo.speed)
        
    elif (mouseY - playerCenterY) > (game.nemo.size / 2):
        increment[1] = game.nemo.speed
    
    if (mouseX - playerCenterX) < (-1) * (game.nemo.size / 2):
        increment[0] = (-game.nemo.speed)
        
    elif (mouseX - playerCenterX) > (game.nemo.size / 2):
        increment[0] = game.nemo.speed
    
    # incrementing the player's position and checking if it's inside game boundaries
    if game.nemo.posX + increment[0] < (game.w - game.nemo.size / 2) and game.nemo.posX + increment[0] > game.nemo.size / 2:
        game.nemo.posX += increment[0]
        
    if game.nemo.posY + increment[1] < (game.h - game.nemo.size / 2) and game.nemo.posY + increment[1] > game.nemo.size / 2:
        game.nemo.posY += increment[1] 
