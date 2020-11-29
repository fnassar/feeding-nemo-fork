import random
import time
class Oval:
    
    def __init__(self, x, y, w, h, r,g,b):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.r = r
        self.g = g
        self.b = b
        self.movingLeft = True
        self.movingUp = True
        self.mvx = -10
        self.mvy = -10
    
    def display(self):
        
        if self.x - self.w/2 < 0 and self.movingLeft == True:
            self.movingLeft = False
            self.mvx = 10
            self.w += 50
            self.h += 50
            self.r = random.randint(0, 255)
            self.g = random.randint(0, 255)
            self.b = random.randint(0, 255)
        
      
        if self.x + self.w/2 > 800 and self.movingLeft == False:
            self.movingLeft = True
            self.mvx = -10
            if self.w > 0:
                self.w -= 50
                self.h -= 50
            self.r = random.randint(0, 255)
            self.g = random.randint(0, 255)
            self.b = random.randint(0, 255)  
        
        
        if self.y - self.w/2 < 0 and self.movingUp == True:
            self.movingUp = False
            self.mvy = 10
            self.r = random.randint(0, 255)
            self.g = random.randint(0, 255)
            self.b = random.randint(0, 255)
      
        if self.y + self.w/2 > 600 and self.movingUp == False:
            self.movingUp = True
            self.mvy = -10
            self.r = random.randint(0, 255)
            self.g = random.randint(0, 255)
            self.b = random.randint(0, 255)  
        
    
            
        
        
        
        self.x += self.mvx
        self.y += self.mvy 
        # self.r = random.randint(0, 255)
        # self.g = random.randint(0, 255)
        # self.b = random.randint(0, 255)
        
        
        ellipse(self.x,self.y,self.w,self.h)
        
        fill(self.r, self.g, self.b)
        
class Bunch_of_Ovals(list):
    
    def __init__(self, numOvals):
        
        for i in range(numOvals):
            x = random.randint(0,800)
            y = random.randint(0,600)
            w = 100
            h = 100
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            self.append(Oval(x,y,w,h,r, g, b))
    
    
    def display_ovals(self):
        
        for oval in self:
            oval.display()
            
ovals = Bunch_of_Ovals(5)
        
def setup():
    size(800,600)
    
    background(255,255,255)
    
def draw():
    background(255,255,255)
    ovals.display_ovals()
    #time.sleep(1)
