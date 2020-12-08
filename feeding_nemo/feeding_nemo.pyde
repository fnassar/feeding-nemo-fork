add_library('minim')

import random, os, datetime, math, socket, threading, sys

path = os.getcwd()

WIDTH = 1100
HEIGHT = 684

# this is to set random direction for every Fish object during __init__() (also nemo and enemies as they inherit from Fish class)
directions = [LEFT, RIGHT]

# font for text (LEVEL, TIMER, SCORE)
font = loadFont(path + "/fonts/bebas_neue.vlw")
audio = Minim(this)

gameStarted = False

class Network():
    def __init__(self):
        self.DISCONNECT_MSG = "##DISCONNECT##"
        self.FORMAT = "utf-8"
        
        PORT = 4040
        SERVER = "40.76.33.105"
        self.ADDR = (SERVER, PORT)
        
        self.player = 0
        self.scores = {1: "000", 2: "000", 3: "000"}
        self.success = False
        
        self.serverFull = False
    
    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        game.screen = 10
        thread = threading.Thread(target = self.send, args = ("PLAYER_000:000",))
        thread.start()
    
    def send(self, msg):
        try:
            message = msg.encode(self.FORMAT)
            self.client.send(message)
            
            if self.player == 0:
                res = self.client.recv(1).decode(self.FORMAT)
        
                if res == "F":
                    self.serverFull = True
                else:
                    self.player = int(res)
                    
                    res = self.client.recv(16).decode(self.FORMAT)
                    while res.strip() != "[NEMO.INITIATE]":
                        res = self.client.recv(16).decode(self.FORMAT)
                        
                    self.success = True
                    game.screen = 1
                    game.start = datetime.datetime.now()
            else:
                res = self.client.recv(19).decode(self.FORMAT)
                res = res.replace("[", "").replace("]", "")
                
                for s in res.split(","):
                    singleData = s.split(":")
                    player = int(singleData[0])
                    score = singleData[1]
                    self.scores[player] = score
        except:
            sys.exit()
                
    def updateScore(self):
        data = "PLAYER_00" + str(self.player) + ":" + "0" * (3 - len(str(game.score))) + str(game.score)
        thread = threading.Thread(target = self.send, args = (data,))
        thread.start()
        
class Fish():
    def __init__(self, posX, posY, size, img, speed):
        
        # the x and y coordinates of the obj, x and y seemed confusing so I've used posX and posY
        self.posX = posX
        self.posY = posY
        
        self.rotation = 0
        
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
        self.update()
        
        playerCenterX, playerCenterY = self.getCenterCoordinates()
        if self.__class__.__name__ == "Player":
            self.rotation = math.atan2((mouseY - playerCenterY), (mouseX - playerCenterX))
    
        # individual image size of our character (because we have 5 images in a single PNG)
        # total image width / 5
        singleSize = self.img.width / self.imageCount
        ratio = float(self.img.height) / float(singleSize)
        
        # when frameCount % 5, we use the cropStart value to determine our start position (x1, y1) like (self.cropStart * singleSize, 0)
        if frameCount % 5 == 0 or frameCount == 1:
            
            # when cropStart reaches 5 we need to set it to 0 cuz 5 * singleSize is null
            self.cropStart += 1
            if self.cropStart >= self.imageCount:
                self.cropStart = 0 
                
        # checking the direction of our Fish (also nemo, enemies) and displaying them respectively
        if abs(self.rotation) > (math.pi / 2):
            self.direction = LEFT
        else:
            self.direction = RIGHT
            
        pushMatrix()
        imageMode(CENTER)
        translate(self.posX, self.posY)
        rotate(self.rotation)
        
        if self.direction == RIGHT:
            scale(1, 1)
            image(self.img, 0, 0, self.size, self.size * ratio, self.cropStart * singleSize, 0, self.cropStart * singleSize + singleSize, self.img.height)
        else:
            scale(-1, 1)
            image(self.img, 0, 0, -self.size, self.size * ratio, (self.cropStart * singleSize + singleSize), self.img.height, self.cropStart * singleSize, 0)
            
        popMatrix()
        
    def getCenterCoordinates(self):
        return self.posX + self.size / 2, self.posY + self.size / 2
        
class Player(Fish):
    def __init__(self, posX, posY, size, img, speed):
        Fish.__init__(self, posX, posY, size, img, speed)
        
        self.imageCount = 8
        self.alive = True
        
        self.eat = audio.loadFile(path + "/audio/nemo_eat.mp3")
        self.tokenEat = audio.loadFile(path + "/audio/token.mp3")
    
    def update(self):
        if mousePressed:
            mouseHandler()
    
class Enemy(Fish):
    def __init__(self, posX, posY, size, img, speed, imageCount):
        Fish.__init__(self, posX, posY, size, img, speed)
        self.imageCount = imageCount
        
        self.increment = [self.speed, self.speed]
        
    def update(self):
        self.check()
        
        if (self.posX + self.size / 2 + self.speed) > game.w:
            self.rotation = math.pi
            self.increment[0] = -self.speed
        elif (self.posX - self.size / 2 - self.speed) < 0:
            self.rotation = 0
            self.increment[0] = self.speed
            
        if (self.posY + self.size / 2 + self.speed) > game.h:
            self.increment[1] = -self.speed
        elif (self.posY - self.size / 2 - self.speed) < 0:
            self.increment[1] = self.speed
        
        self.posX += self.increment[0]
        self.posY += self.increment[1]
    
    def check(self):
        if dist(self.posX, self.posY, game.nemo.posX, game.nemo.posY) < self.size / 2 + game.nemo.size / 3:
            if self.size > game.nemo.size:
                game.nemo.alive = False
            else:
                game.nemo.eat.rewind()
                game.nemo.eat.play()
                game.score += 10
                
                if game.multiPlayer:
                    game.network.updateScore()
                    
                game.preys.remove(self)
                
class Shark(Enemy):
    def __init__(self, posX, posY, size, img, speed, imageCount):
        Enemy.__init__(self, posX, posY, size, img, speed, imageCount)
        
        self.inGame = False
        
        self.sound = audio.loadFile(path + "/audio/shark.mp3")
    
    def update(self):
        self.check()
        
        self.increment = [-self.speed * 4, 0]
        
        self.posX += self.increment[0]
        self.posY += self.increment[1]
        
        if self.posX <= (-self.size / 2):
            self.inGame = False
            self.posX, self.posY = game.w + self.size / 2, random.randint(50, game.h - 50)

class Token():
    def __init__(self, x, y):
        self.posX = x 
        self.posY = y
        self.img = loadImage(path + "/images/token.png")
        self.size = 30
        
        self.cropStart = random.randint(1, 23)
        self.eaten = False

    def display(self):
        tokenSize = self.img.width / 23 # the sprite has 23 tokens so i divide by 23

        if frameCount % 2 == 0 or frameCount == 1:
            self.cropStart += 1
            if self.cropStart >= 23:
                self.cropStart = 0
                
        image(self.img, self.posX, self.posY, self.size, self.size, self.cropStart * tokenSize, 0, self.cropStart * tokenSize + tokenSize, self.img.height)
        
        if dist(self.posX, self.posY, game.nemo.posX, game.nemo.posY) <= (game.nemo.size / 2 + self.size / 2):
            game.nemo.tokenEat.rewind()
            game.nemo.tokenEat.play()
            game.score += 1
            
            if game.multiPlayer: # update score on network
                game.network.updateScore()
            
            game.tokens.remove(self)
        
class Game():
    def __init__(self, w, h):
        
        self.w = w
        self.h = h
        
        self.multiPlayer = False
        self.network = None
        self.keyHandler = {32: False, 10: False, 83: False, 77: False}

        # to know which screen we're in, Main Menu, the Game, GameOver screen
        self.screen = 0
        
        # this is for the timer, we take the datetime value during __init__ and then on every frame we check time diffrence in seconds
        # then we use the getTimer() function inside Game class to get the timer format in M:S
        self.score = 0
        self.level = 1
        
        self.start = datetime.datetime.now()
        self.nemo = Player(200, 200, 90, "nemo.png", 4) # if self.level == 1 else 130
        
        self.bg = Background(self.w, self.h)
        
        self.tokens = []
        
        fishCount = [6, 5, 5, 6, 6]
        self.preys = []
        for i in range(1):
            fish = random.randint(0, 4)
            self.preys.append(Enemy(random.randint(100, self.w - 100), random.randint(50, self.h - 50), self.nemo.size / 2, "fish" + str(fish + 1) + ".png", random.uniform(1.5, 3), fishCount[fish]))
        
                              
        self.predators = []
        for i in range(1):
            self.predators.append(Enemy(random.randint(300, self.w - 100), random.randint(50, self.h - 50), self.nemo.size * 1.5, "predator.png", random.uniform(1.5, 2.2), 9))

        self.shark = Shark(self.w, random.randint(50, self.h - 50), self.nemo.size * 3, "shark.png", random.uniform(1.5, 2.2), 6)
        
        global gameStarted
        if not gameStarted:
            self.background = audio.loadFile(path + "/audio/background.mp3")
            self.background.loop()
            gameStarted = True
        
        self.gameOverAudio = audio.loadFile(path + "/audio/game_over.mp3")
        
        self.mainMenuImg = loadImage(path + "/images/mainMenu.png")
        self.level1Img = loadImage(path + "/images/level2.png")
        self.level2Img = loadImage(path + "/images/GAMEEND.png")
        
    def update(self):
        if self.screen == 0:
            self.mainMenu()
            
        elif self.screen == 2:
            self.shark.sound.pause()
            if self.level == 1:
                imageMode(CORNER)
                image(self.level1Img,0,0)
                
                self.nemo = Player(200, 200, 110, "nemo.png", 4)
                                
                self.preys = []
                fishCount = [6, 5, 5, 6, 6]
                for i in range(10):
                    fish = random.randint(0, 4)
                    self.preys.append(Enemy(random.randint(100, self.w - 100), random.randint(50, self.h - 50), self.nemo.size / 3, "fish" + str(fish + 1) + ".png", random.uniform(1.5, 3), fishCount[fish]))
                    
                for i in range(5):
                    self.preys.append(Enemy(random.randint(300, self.w - 100), random.randint(50, self.h - 50), self.nemo.size * 1.5/2, "predator.png", random.uniform(1.5, 2.2), 9))
                
                self.predators = []
                for i in range(3):
                    self.predators.append(Enemy(random.randint(300, self.w - 100), random.randint(50, self.h - 50), self.nemo.size * 1.5, "predator2.png", random.uniform(1.5, 2.2), 8))

                self.shark = Shark(self.w, random.randint(50, self.h - 50), self.nemo.size * 4, "shark.png", random.uniform(1.5, 2.2), 6)
                if self.keyHandler[32] == True:
                    self.level = 2
                    self.screen = 1
                
            elif self.level == 2:
                imageMode(CORNER)
                image(self.level2Img,0,0)
                if self.keyHandler[32]:
                    self.screen = 0
                
            
            
        elif self.screen == 1 and self.nemo.alive:
            self.bg.display()
            self.nemo.display()
            
            if len(self.preys) == 0:
                self.screen = 2
            
            timeSpent = floor((datetime.datetime.now() - self.start).total_seconds())
            # the stars will apear every 25 seconds
            # the frame count part is because frame rate is 60fps so more than just one would apear without it
            if (timeSpent % 10 == 0) and (frameCount % 20 == 0 or frameCount == 1) and len(self.tokens) <= 10: 
                self.tokens.append(Token(random.randint(100, self.w - 100), random.randint(100, self.h - 100)))

            for token in self.tokens:
                token.display()
    
            for otherFish in self.preys + self.predators:
                otherFish.display()

            if timeSpent % 30 == 0 and timeSpent != 0:
                self.shark.inGame = True
                self.shark.sound.rewind()
                self.shark.sound.loop()
                
            if self.shark.inGame:
                self.shark.display()
            else:
                self.shark.sound.pause()
                
            # LEVEL, TIMER and SCORE
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
                
            textAlign(LEFT)
            textSize(30)
            text("LEVEL " + str(self.level), 20, 40)
            
            textSize(22)
            text(self.getTimer((datetime.datetime.now() - self.start).total_seconds()), 20, 65)
       
        elif self.screen == 10:
            textAlign(CENTER)
            textMode(CENTER)
            textSize(40)
            
            waitingTxt = "WAITING FOR OTHER PLAYERS TO JOIN..."
            if self.network.serverFull:
                waitingTxt = "SORRY, THE SERVER IS BUSY"
            text(waitingTxt, self.w / 2, self.h / 2)
            textSize(25)
            text("Press ESC to exit", self.w / 2, (self.h / 2) + 30)
            
        else:
            self.shark.sound.pause()
            self.gameOverAudio.play()
            
            textAlign(CENTER)
            textMode(CENTER)
            textSize(70)
            text("GAME OVER", self.w / 2, self.h / 2)
            
            if not self.multiPlayer:
                textSize(25)
                text("Press SPACE to restart", self.w / 2, (self.h / 2) + 50)
                
                if self.keyHandler[32]:
                    self.newGame()
        
    # to get the TIMER format (M:S)
    def getTimer(self, seconds):
        minutes = floor(seconds / 60)
        
        timeString = ""
        
        if minutes > 0:
            timeString = str(minutes) + ":" + str(floor(seconds - (minutes * 60)))
        else:
            timeString = "0:" + str(floor(seconds))
            
        return timeString
    
    def newGame(self):
        self.screen = 1
        global game
        game = Game(WIDTH, HEIGHT)
        
    # for the MainMenu
    def mainMenu(self):
        background(255)
        imageMode(CENTER)
        image(self.mainMenuImg, self.w / 2, self.h / 2, self.w, self.h)
        
        if self.keyHandler[83]:
            self.screen = 1
            self.start = datetime.datetime.now()
            
        elif self.keyHandler[77]:
            self.multiPlayer = True
            self.network = Network()
            self.network.connect()

class Background():
    def __init__(self, w, h):
        self.bgImage = loadImage(path + "/images/marine.png")
        self.w = w
        self.h = h
        
        self.xShift = 0
        
        self.otherImages = []
        for i in range(3, 0, -1):
            self.otherImages.append(loadImage(path + "/images/" + str(i) + ".png"))
        
    def display(self):
        
        if game.nemo.direction == RIGHT:
            self.xShift += 2
        elif game.nemo.direction == LEFT: 
            self.xShift -= 2
        else:
            self.xShift = 0
        
        count = 1
        x = 0
        for img in self.otherImages:
            if count == 1:
                x = self.xShift // 3
            elif count == 2:
                x = self.xShift // 2
            else:
                x = self.xShift        
            
            widthR = x % self.w
            widthL = self.w - widthR
            
            #make the image wrap around
            imageMode(CORNER)
            image(img, 0, 0, widthL, self.h, widthR, 0, self.w, self.h)
            image(img, widthL, 0, widthR, self.h, 0, 0, widthR, self.h)
            
            count += 1
    
game = Game(WIDTH, HEIGHT)

def setup():
    size(WIDTH, HEIGHT)
    textFont(font)

def draw():
    background(game.bg.bgImage)
    game.update()
    
def keyPressed():
    if keyCode == 32: # and game.nemo.alive == False: # SPACEBAR
        game.keyHandler[32] = True
        
    elif keyCode == 10: # ENTER
        game.keyHandler[10] = True
    
    elif keyCode == 83: # S or s
        game.keyHandler[83] = True
        
    elif keyCode == 77: # M or m
        game.keyHandler[77] = True
        
    elif keyCode == 27: # ESC
        sys.exit()

def mouseHandler():
    playerCenterX, playerCenterY = game.nemo.getCenterCoordinates()
    
    increment = [0, 0]
    if (mouseY - playerCenterY) < (-1) * (game.nemo.size / 2):
        increment[1] = -(game.nemo.speed)
        
    elif (mouseY - playerCenterY) > (game.nemo.size / 2):
        increment[1] = game.nemo.speed
    
    if (mouseX - playerCenterX) < (-1) * (game.nemo.size / 2):
        increment[0] = (-game.nemo.speed)
        
    elif (mouseX - playerCenterX) > (game.nemo.size / 2):
        increment[0] = game.nemo.speed
        
    if game.nemo.posX + increment[0] < (game.w - game.nemo.size / 2) and game.nemo.posX + increment[0] > game.nemo.size / 2:
        game.nemo.posX += increment[0]
        
    if game.nemo.posY + increment[1] < (game.h - game.nemo.size / 2) and game.nemo.posY + increment[1] > game.nemo.size / 2:
        game.nemo.posY += increment[1] 
