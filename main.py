#BUG: Snake sticks its tongue out is still an issue when it passes over the body and then it thinks it isn't the body.
#Main Improvement: Implement A* instead of my current logic, does it go slower? Or does the consistency and less weirdness over take any time loss. 

#If you wish to run this for yourself, you may need to change some of the many constants, but all the constants should update everything througout the code
#Once you get it all updated, running it should work, just make sure you have the snake window selected. Sorry if it doesn't ):

import PIL
import pyautogui
from pynput.keyboard import Key, Controller
import time
import random


#Numbers
SQUARESIZE = 32 #The number of pixels each square is. If it's odd, well, there might be some issues, but it shouldn't be
LEFTOFFSET = 28 + (SQUARESIZE/2) #The distance the first square is from the left side, no centering needed
TOPOFFSET = 86 + (SQUARESIZE/2) #The distance the first square is from the top, no centering needed
WIDTH = 17 #How many squares wide
HEIGHT = 15 #How many squares tall
SPEED = .002 #This doesn't need an update
X1 = 0 #The first x position to start the screenshot
Y1 = 112 #The first y position to start the screenshot
SWIDTH = 600 #The width of the screenshot
SHEIGHT = 600 #The height of the screenshot
#These variables are the same as above, but it takes a screenshot of the time once it is over to save
TX1 = 385 #The first x position to start the screenshot for the time at the end
TY1 = 112 #The first y position to start the screenshot for the time at the end
TSWIDTH = 100 #The width of the screenshot for the time at the end
TSHEIGHT = 80 #The height of the screenshot for the time at the end
PATH = r'D:\Google Snake AI' #The path to where the python file is. RECOMMENDATION: It is recommended that you put it in its own folder so that saved screenshots are easy to find

#These don't need to be updated
#Tile States
EMPTY = u"\u00B7"
HEAD = "O"
BODY = "X"
FRUIT = "F"
TEST = "T" #DEBUG ONLY

class Game:
    def __init__(self,width,height): #Defines all variables
        global myScreenshot
        self.headPositions = []
        self.fruitPosition = []
        self.width = width
        self.height = height
        self.tiles = []
        self.direction = None
        for row in range(height):
            self.tiles.append([])
            for col in range(width):
                color = myScreenshot.getpixel((LEFTOFFSET+(col*SQUARESIZE),TOPOFFSET+(row*SQUARESIZE)))
                self.tiles[row].append(Tile(col,row,color,self))
    
    def printBoard(self): #Prints Board
        for row in self.tiles:
            #print(row)
            for tile in row:
                print(tile.state, end = '')
            print()
        print()
    
    def offBoard(self,x,y): #Checks if a certain tile is off the board
        if (x < 0 or y < 0 or x >= self.width or y >= self.height):
            return True
        return False
    
    def countRow(self,row): #Counts the number of body tiles in a row
        count = 0
        for i in range(self.width):
            if self.tiles[row][i].state == BODY:
                count += 1
        return count
        
    def countColumn(self,col): #Counts the number of body tiles in a column
        count = 0
        for i in range(self.height):
            if self.tiles[i][col].state == BODY:
                count += 1
        return count
    
    def addNewHead(self): #Adds the previous head back in if a new one is not found
        for row in range(self.height):
            for col in range(self.width):
                if self.tiles[row][col].prevState == HEAD:
                    self.tiles[row][col].state = HEAD
                    self.headPositions.append([row,col])
                    return
    
    def playing(self): #Sees if the game is being played or not
        global myScreenshot
        #print(myScreenshot.getpixel((5,5)))
        return not self.headPositions == []
    
    def updateBoard(self): #Updates the Boards Current State
        global myScreenshot
        
        self.headPositions.clear()
        for row in range(self.height):
            for col in range(self.width):
                color = myScreenshot.getpixel((LEFTOFFSET+(col*SQUARESIZE),TOPOFFSET+(row*SQUARESIZE)))
                lastState = self.tiles[row][col].setState(self, color)
                if lastState == HEAD:
                    self.headPositions.append([row,col])
                if lastState == FRUIT:
                    self.fruitPosition = [row, col]
        if (len(self.headPositions) == 0): #If there's no heads, add the old one back in
            self.addNewHead() #Adds the old head back in if the screenshot was taken fast enough
        count = 0
        while(len(self.headPositions) > 1 and count < 5): #if there's multiple heads, get rid of misinterpreted heads
            #self.printBoard()
            count += 1
            for i in range(len(self.headPositions)):
                currTile = self.tiles[self.headPositions[i][0]][self.headPositions[i][1]]
                #print(currTile.checkSurrounding(self))
                if currTile.checkSurrounding(self):
                    self.headPositions.pop(i)
                    #print(len(self.headPositions))
                    break
    
    def decideDirection(self): #The logic that deicdes direction
        #print(self.headPositions)
        headTile = self.tiles[self.headPositions[0][0]][self.headPositions[0][1]]
        fruitTile = self.tiles[self.fruitPosition[0]][self.fruitPosition[1]]
        thought = None #Thought is what the snake currently thinks it should do. None = current direction
        if headTile.x == fruitTile.x and headTile.y == fruitTile.y:  #Fixes part of fruit glitch, where fruit hasn't even started spawning yet
            return thought
        
        options = [Key.up,Key.right,Key.down,Key.left] #All four different options, something from this list must be chosen.
        #Remove Directions that have a body in the way, or are off the grid, because those kill right away, so there's no reason to even think about it. 
        if self.offBoard(headTile.x, headTile.y-1):
            options.remove(Key.up)
        elif self.tiles[headTile.y-1][headTile.x].state == BODY:
            options.remove(Key.up)
            
        if self.offBoard(headTile.x, headTile.y+1):
            options.remove(Key.down)
        elif self.tiles[headTile.y+1][headTile.x].state == BODY:
            options.remove(Key.down)
        
        if self.offBoard(headTile.x-1, headTile.y):
            options.remove(Key.left)
        elif self.tiles[headTile.y][headTile.x-1].state == BODY:
            options.remove(Key.left)
        
        if self.offBoard(headTile.x+1, headTile.y):
            options.remove(Key.right)
        elif self.tiles[headTile.y][headTile.x+1].state == BODY:
            options.remove(Key.right)
            
            
        #print(options)
        if (len(options) == 0): #If there are no options, just go to your death
            return thought
        if (len(options) == 1): #If there is only one options, choose that one
            return options[0]
        
        #Think about which direction would head towards the fruit
        if headTile.y > fruitTile.y:
            thought = Key.up
        elif headTile.y < fruitTile.y:
            thought =  Key.down
        elif headTile.x > fruitTile.x:
            thought =  Key.left
        elif headTile.x < fruitTile.x:
            thought =  Key.right
        
        count = 3
        while(options.count(thought) == 0): #If Options does not contain the thought, find a new one
            if thought == Key.left or thought == Key.right: #Provide an aditional buffer? If two spaces up is filled, it's probably not a good way to go. 
                if headTile.y > fruitTile.y: #Try moving towards the fruit in the other direction (horizontal, vertical) maybe
                    thought = Key.up
                elif headTile.y < fruitTile.y:
                    thought = Key.down
            if thought == Key.up or thought == Key.down:
                if headTile.x > fruitTile.x:
                    thought = Key.left
                elif headTile.x < fruitTile.x:
                    thought = Key.right
            count -= 1 #Check this a few times, and if more should be added here
            if count == 0: #Improve logic, don't just choose at random in this case, choose the way that has the least body in the way, also, if moving away from fruit, try to change mind
                if headTile.x == fruitTile.x: #if both prefered directions are bad, remove the directions that are already matched up; this is what could be improved
                    if options.count(Key.down) > 0:
                        options.remove(Key.down)
                    if options.count(Key.up) > 0:
                        options.remove(Key.up)
                if headTile.y == fruitTile.y:
                    if options.count(Key.left) > 0:
                        options.remove(Key.left)
                    if options.count(Key.right) > 0:
                        options.remove(Key.right)
                        
                print(options) #If there's no options left, just keep going
                if (len(options) == 0):
                    return None
                if (len(options) == 1): #If there's one option, choose that one
                    return options[0]
                
                #Choose direction based on which seems safer by counting the number of bodies immediately going that direction
                currMin = 9999 #As long as your board isn't bigger than 9999 you're fine
                for choice in options: #*Can improve a lot if you check to see if there's a body to both sides of you and add a huge penalty to that*, if neccesary
                    if choice == Key.down: #This whole thing might not even work, but I think it does
                        total = self.countRow(headTile.y+1)
                        if total < currMin:
                            thought = choice
                            currMin = total
                    if choice == Key.up:
                        total = self.countRow(headTile.y-1)
                        if total < currMin:
                            thought = choice
                            currMin = total
                    if choice == Key.left:
                        total = self.countColumn(headTile.x-1)
                        if total < currMin:
                            thought = choice
                            currMin = total
                    if choice == Key.right:
                        total = self.countColumn(headTile.x+1)
                        if total < currMin:
                            thought = choice
                            currMin = total
                    
                    #thought = random.choice(options)
        
        return thought #Now return what you think is best, which still might suck
        

    
class Tile:
    def __init__(self, x, y, color, game): #Init variables
        self.size = SQUARESIZE
        self.x = x
        self.y = y
        self.state = None
        self.setState(game, color)
        
    def setState(self, game, color): #Set the state based on a color
        self.prevState = self.state
        #print(color[2])
        if color == (231, 71, 29): #Color of the fruit
            self.state = FRUIT
        elif color[2] < 100: #One of the two green tiles or the red tounge (that isn't slightly transparent)
            self.state = EMPTY
        else:
            self.state = BODY
        
        if not self.prevState == None and self.state == BODY and (self.prevState == EMPTY or self.prevState == FRUIT): #If it was empty last, make it the head
            self.state = HEAD 
        return self.state
    
    def checkSurrounding(self,game): #Just simply for removing double heads, don't worry a whole lot about how it actually works
        count = 0
        for i in range(2):
            xoffset = i or -1
            #print(game.tiles[self.y][self.x+xoffset].state)
            if not game.offBoard(self.x+xoffset, self.y) and game.tiles[self.y][self.x+xoffset].state == BODY:
                self.state = BODY
                #print(self.state)
            elif not game.offBoard(self.x+xoffset, self.y) and game.tiles[self.y][self.x+xoffset].state == HEAD:
                count += 1
        if self.state == BODY:
            return True
        
        for j in range(2):
            yoffset = j or -1
            #print(game.tiles[self.y][self.x+xoffset].state)
            if not game.offBoard(self.x, self.y+yoffset) and game.tiles[self.y+yoffset][self.x].state == BODY:
                self.state = BODY
                #print(self.state)
            elif not game.offBoard(self.x, self.y+yoffset) and game.tiles[self.y+yoffset][self.x].state == HEAD:
                count += 1
        if self.state == BODY:
            return True    
        if count == 0: #There's not heads it also means it is bad. 
            return True
        return False
        
        
photoCount = 0 #When rerunning, this will delete old times
myScreenshot = pyautogui.screenshot(region=(TX1,TY1,TSWIDTH,TSHEIGHT)) #Use PIL's instead?
myScreenshot.save(PATH + r'\screenshots\timetest.png')
myScreenshot = pyautogui.screenshot(region=(X1,Y1,SWIDTH,SHEIGHT)) #Use PIL's instead?
myScreenshot.save(PATH + r'\screenshots\snake.png')

myGame = Game(WIDTH,HEIGHT)
Keyboard = Controller()

time.sleep(.5)
oldDirection = None

while (True): #Loop forever, just run the stuff
    myScreenshot = pyautogui.screenshot(region=(X1,Y1,SWIDTH,SHEIGHT)) #Use PIL's instead?
    myGame.updateBoard()
    if myGame.playing():
        direction = myGame.decideDirection()
        if not direction == None and not direction == oldDirection:
            Keyboard.press(direction) 
            print("Moving " + str(direction))
            myGame.direction = direction
        oldDirection = direction
        if (myScreenshot.getpixel((5,5)) == (22, 35, 13)):
            myScreenshot = pyautogui.screenshot(region=(TX1,TY1,TSWIDTH,TSHEIGHT)) #Use PIL's instead?
            myScreenshot.save(PATH + r'\screenshots\time' + str(photoCount) + r'.png')
            photoCount += 1
            Keyboard.press('r')
            time.sleep(.5)
            Keyboard.press(Key.right)
            time.sleep(.25)
            myScreenshot = pyautogui.screenshot(region=(X1,Y1,SWIDTH,SHEIGHT))
            myGame.updateBoard()
            time.sleep(.25)
    else:
        if (myScreenshot.getpixel((5,5)) == (22, 35, 13)):
            myScreenshot = pyautogui.screenshot(region=(TX1,TY1,TSWIDTH,TSHEIGHT)) #Use PIL's instead?
            myScreenshot.save(PATH + r'\screenshots\time' + str(photoCount) + r'.png')
            photoCount += 1
            Keyboard.press('r')
            time.sleep(.5)
            Keyboard.press(Key.right)
            time.sleep(.25)
            myScreenshot = pyautogui.screenshot(region=(X1,Y1,SWIDTH,SHEIGHT))
            myGame.updateBoard()
            time.sleep(.25)
    myGame.printBoard()
    #time.sleep(SPEED)



