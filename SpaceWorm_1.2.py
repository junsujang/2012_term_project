from Tkinter import *
import tkSimpleDialog
import PIL.Image
import ImageTk
import random; import math


GRAVITY=-9.81

class Player(object):
    def __init__(self, possibleMoves, p, p1, bk, playerName, canvas, pWidth,\
        pHeight, pLeft, windV, windA,headLeft, canvasWidth, canvasHeight,\
        terrain, ally, oil):
        self.init()
        self.possibleMoves=possibleMoves
        self.headLeft=headLeft
        self.bk=bk
        self.setWorms()
        self.setPic()
        self.p=p
        self.p1=p1
        self.oil=oil
        self.pName=playerName
        self.canvas=canvas
        self.pWidth=pWidth
        self.pHeight=pHeight
        self.canvasHeight=canvasHeight
        self.canvasWidth=canvasWidth
        self.terrain=terrain
        self.pLeft=pLeft
        self.windV=windV
        self.windA=windA
        self.pY=self.getTopTy(terrain, pLeft+(pWidth/2.0))#y position of players
        self.cx=self.pLeft+self.pWidth
        self.cy=self.pY-self.pHeight
        self.origin=(int(self.pLeft+(self.pWidth)/2.0), self.pY)
        self.pPowermax=int((canvasWidth/1.6)/5)+2
        self.ally=ally
        self.calcRotation()
        self.p=self.p.rotate(math.degrees(self.deltaA))

    def init(self):
        self.nSpecial=3
        self.Weapon="Normal"
        self.pPower=self.counter=self.AIpower=self.moved=0
        self.bodyAngle=self.deltaA=0
        self.explosionTime=10
        self.pHP=100
        self.pMaxAngle=self.bodyAngle+math.radians(80)
        self.pMinAngle=self.bodyAngle+math.radians(30)
        self.pAngle=(self.pMaxAngle+self.pMinAngle)/2.0
        self.bulletR=10
        self.pastA=self.pAngle
        self.mouseClicked=self.pINIT=self.p1INIT=self.pFire=self.explosion=False
        self.destination=self.move=None
        self.opponents=[]
        self.turn=self.specialW=self.user=False
        self.players=[]
        self.targetA=math.radians(55)
        self.explosionR=5
        self.windAlist=[0, 30, 45, 60, 90, 120, 135, 150, 180, 210,\
                        225, 240, 270, 300, 315, 330]
        
    def setWorms(self):
        #set PIL files for worms to be used for players
        self.worm=PIL.Image.open("worm.gif").convert("RGBA")
        self.wormF=PIL.Image.open("wormFlip.gif").convert("RGBA")
        self.wormBaz=PIL.Image.open("wormBaz.gif").convert("RGBA")
        self.wormBazF=PIL.Image.open("wormBazFlip.gif").convert("RGBA")
        self.wormS=PIL.Image.open("wormS.gif").convert("RGBA")
        self.wormSF=PIL.Image.open("wormSFlip.gif").convert("RGBA")
    
    def setShotPic(self):
        #when a player shoots, a worm with bazooka appears
        self.calcRotation()
        if self.headLeft:
            self.p=self.wormBaz
        if not self.headLeft:
            self.p=self.wormBazF
        self.p=self.p.rotate(math.degrees(self.deltaA))
    
    def setPic(self):
        #set worms picture accordingly
        #For every movement, the worm stretches back and forth
        moved=self.moved
        if self.headLeft and moved%2==0:
            self.p=self.worm
        elif self.headLeft and moved%2==1:
            self.p=self.wormS
        elif not self.headLeft and moved%2==0:
            self.p=self.wormF
        elif not self.headLeft and moved%2==1:
            self.p=self.wormSF
   
    def p1ProjectileINIT(self):
        #divide the power into x and y components
        if self.headLeft:
            self.pVy=self.pPower*math.cos(self.pAngle)
            self.pVx=self.pPower*math.sin(self.pAngle)
        else:
            self.pVy=self.pPower*math.sin(self.pAngle)
            self.pVx=self.pPower*math.cos(self.pAngle)

    def windINIT(self):
        #seperate windV into x and y components
        windV=self.windV
        windA=self.windA
        self.WindX=windV*math.cos(windA)
        self.WindY=windV*math.sin(windA)

    def projectileReset(self):
        #reset the info used for calculating projectile
        self.pVy=self.pVx=0
        if self.headLeft:
            self.cx=self.pLeft
        if not self.headLeft:
            self.cx=self.pLeft+self.pWidth
        self.cy=self.pY-self.pHeight
    
    def HPreduction(self, cx, cy):
        for player in self.players:
            #D=(x^2+y^2)^(1/2)
            D=((player.origin[0]-cx)**2+(player.origin[1]-cy)**2)**0.5
            if not self.specialW:
                if D<=50 and D>40: #normal shots
                    player.pHP-=self.bulletR
                elif D<=40 and D>=20:
                    player.pHP-=self.bulletR*2
                elif D<20 and D>5:
                    player.pHP-=self.bulletR*3
                elif D<=5 and D>0:
                    player.pHP-=self.bulletR*4
            else: #for special shots, the reduction is smaller
                if D<=50 and D>20:
                    player.pHP-=self.bulletR
                elif D<=20:
                    player.pHP-=self.bulletR*2

    def getTopTy(self, image, x):
        #get the y coord with terrain color checked from top to bottom
        for y in xrange(700):
            (r, g, b)=self.getRGB(image, x,  y)
            if r==162 and g==1 and b==1:
                return y
    
    def getTy(self, image, x):
        #get the y coord with terrain color checked from bottom to top
        for y in xrange(700, -1, -1):
            (r, g, b)=self.getRGB(image, x,  y)
            if r!=162 and g!=1 and b!=1:
                return y

    def doLeftMousePressed(self, event):
        ctrl  = ((event.state & 0x0004) != 0)
        shift = ((event.state & 0x0001) != 0)
        if event.x>=25 and event.x<=125 and event.y>=575 and event.y<=675:
            #when the fire button is clicked
            self.mouseClicked=True
            self.pPower=0
            self.projectileReset()
        if self.nSpecial>0 and self.Weapon=="Special" and self.pFire:
            #when you have special available and during the fire
            self.nSpecial-=1
            self.specialW=True
            #make sure that the bullet goes straight to the target when clicked
            if self.cx>event.x:
                self.pVx=-50
            else:
                self.pVx=50
            #get gradient of the straight travel to the target
            slope=-(event.y-self.cy)/(event.x-self.cx)
            self.pVy=slope*(self.pVx)
            
    def doLeftMouseReleased(self, event):
        ctrl  = ((event.state & 0x0004) != 0)
        shift = ((event.state & 0x0001) != 0)
        self.setPic()
        if self.mouseClicked:
            self.pFire=self.p1INIT=True
            self.mouseClicked=False
    
    def isLegalMove(self, image, x0):
        if x0<10 or x0>1190:
            return False
        return True
    
    def getPyDown(self, image, pY, x):
        #gives the y coord of terrain in the future move checked downwards
        for y in xrange(pY, 700):
            (r, g, b)=self.getRGB(image, x,  y)
            if r==162 and g==1 and b==1:
                return y

    def getPyUp(self, image, pY, x):
        #gives the y coord of terrain in the future move checked upwards
        for y in xrange(pY, 0, -1):
            (r, g, b)=self.getRGB(image, x, y)
            if r!=162 and g!=1 and b!=1:
                return y
    
    def setPy(self, image, pY, x):
        PyUp=self.getPyUp(image, pY, x)
        PyDown=self.getPyDown(image, pY, x)
        TyDown=self.getTy(image, x)
        TyUp=self.getTopTy(image, x)
        if PyDown==TyDown:
            #"going Down while at bottom"
            return TyDown
        elif TyUp>PyUp:
            #"going Down while on top"
            return TyUp
        elif TyDown<PyDown:
            #"going Up while at below"
            return TyDown
        elif TyUp==PyDown:
            #"going Up while on top"
            return TyUp
        else: return TyDown

    def doLeftMove(self):
        self.moved+=1
        self.setPic()
        if self.headLeft==True and self.oil>0 and\
                         self.isLegalMove(self.terrain, self.pLeft-5):
            self.pLeft-=5 #move left by five
            self.pY=self.setPy(self.terrain, self.pY, self.pLeft+self.pWidth/2)
            self.oil-=20 #stamina loss
        else: #you need to turn left before moving left
            self.headLeft=True
            self.turnPlayerAngle()
        self.projectileReset()
        self.calcRotation()
        self.p=self.p.rotate(math.degrees(self.deltaA))
    
    def doRightMove(self):
        self.moved+=1
        self.setPic()
        if self.headLeft==False and self.oil>0 and\
                         self.isLegalMove(self.terrain, self.pLeft+5):
            self.pLeft+=5 #move right by five
            self.pY=self.setPy(self.terrain, self.pY, self.pLeft+self.pWidth/2)
            self.oil-=20
        if self.headLeft: #turn right first
            self.headLeft=False
            self.turnPlayerAngle()
        self.projectileReset()
        self.calcRotation()
        self.p=self.p.rotate(math.degrees(self.deltaA))

    def doKeyPressed(self, event):
        if event.keysym=="Left" and not self.pFire: #move left
            self.doLeftMove()
        elif event.keysym == "Right" and not self.pFire: #move right
            self.doRightMove()
        elif event.keysym=="Up":#increase angle
            self.pAngle+=math.radians(1)
        elif event.keysym=="Down":#decrease angle
            self.pAngle-=math.radians(1)
        self.origin=(int(self.pLeft+(self.pWidth)/2.0), self.pY)

    def setUserA(self, left, right, top):
        if self.pMaxAngle<0 and self.pMinAngle<0:#when both angles are negative
            if abs(self.pAngle)>=abs(self.pMaxAngle):
                self.pAngle=self.pMaxAngle
            if abs(self.pAngle)<=abs(self.pMinAngle):
                self.pAngle=self.pMinAngle
        elif self.pMaxAngle*self.pMinAngle<0 and self.pMaxAngle>0:
            #when max and min have different signs and max is positive
            if self.pAngle>=self.pMaxAngle:
                self.pAngle=self.pMaxAngle
            if self.pAngle<=self.pMinAngle:
                self.pAngle=self.pMinAngle
        elif self.pMaxAngle*self.pMinAngle<0 and self.pMaxAngle<0:
            #when max and min have different signs and min is positive
            if self.pAngle<=self.pMaxAngle:
                self.pAngle=self.pMaxAngle
            if self.pAngle>=self.pMinAngle:
                self.pAngle=self.pMinAngle
        else:
            if self.pAngle>=self.pMaxAngle:
                self.pAngle=self.pMaxAngle
            if self.pAngle<=self.pMinAngle:
                self.pAngle=self.pMinAngle
    
    def convertUserA(self, left, right, top):
        self.setUserA(left, right, top)
        if self.headLeft:
            center=(left,top)
            maxAngle=self.pMaxAngle
            minAngle=self.pMinAngle
            shotAngle=self.pAngle
        if not self.headLeft:
            center=(right, top)
            maxAngle=math.radians(90)-self.pMaxAngle
            minAngle=math.radians(90)-self.pMinAngle
            shotAngle=math.radians(90)-self.pAngle
        return (center, maxAngle, minAngle, shotAngle)
    
    def setAIA(self, left, right, top):
        if self.headLeft:
            center=(left,top)
            maxAngle=self.pMaxAngle
            minAngle=self.pMinAngle
            shotAngle=self.pAngle
        else:
            center=(right, top)
            maxAngle=math.radians(90)-self.pMaxAngle
            minAngle=math.radians(90)-self.pMinAngle
            shotAngle=math.radians(90)-self.pAngle
        return (center, maxAngle, minAngle, shotAngle)

    def drawAs(self,center, maxAngle, minAngle, shotAngle, length):
        #draw max
        self.canvas.create_line(center[0]+length*math.sin(maxAngle)*1/2.0,\
                center[1]-length*math.cos(maxAngle)*1/2.0,\
                center[0]+length*math.sin(maxAngle),\
                center[1]-length*math.cos(maxAngle), fill="Turquoise")
        #draw min
        self.canvas.create_line(center[0]+length*math.sin(minAngle)*1/2.0,\
                center[1]-length*math.cos(minAngle)*1/2.0,\
                center[0]+length*math.sin(minAngle),\
                center[1]-length*math.cos(minAngle), fill="Turquoise")
        #draw the actual angle
        self.canvas.create_line(center[0]+length*math.sin(shotAngle)*1/4.,\
                center[1]-length*math.cos(shotAngle)*1/4,\
                center[0]+length*math.sin(shotAngle),\
                center[1]-length*math.cos(shotAngle), fill="gold")

    def drawAngle(self, pwidth, pheight, pleft, ptop):
        if self.turn and self.pHP>0:
            width=self.pWidth
            height=self.pHeight
            left=self.pLeft
            bottom=self.pY
            right=left+width
            top=bottom-height
            length=width
            bodyAngle=math.radians(90)-self.bodyAngle
            if self.user:
                center, maxAngle, minAngle, shotAngle=\
                                self.convertUserA(left, right, top)   
            else:
                center, maxAngle, minAngle, shotAngle=\
                                self.setAIA(left, right, top)
            self.drawAs(center, maxAngle, minAngle, shotAngle,length)

    def turnPlayerAngle(self):
        if self.headLeft==True: #turn left
            self.pAngle=-math.pi/2+self.pAngle
            self.pMaxAngle=-math.pi/2+self.pMaxAngle
            self.pMinAngle=-math.pi/2+self.pMinAngle
            self.setPic()
        else: #turn right
            self.pAngle=math.pi/2+self.pAngle
            self.pMaxAngle=math.pi/2+self.pMaxAngle
            self.pMinAngle=math.pi/2+self.pMinAngle
            self.setPic()

    def doDrawRange(self, left, top, right, bottom):
        #draws the oil left
        if self.user and self.pHP>0:
            if self.oil<0:
                self.oil=0
            self.canvas.create_rectangle(left, top, left+self.oil,\
                                         bottom, fill="Dark Violet")

    def doDrawPowerBar(self, left, right, top, bottom):
        #draw the power built in so far
        if self.pPower<=self.pPowermax and self.pHP>0:
            self.canvas.create_rectangle(left, top, left+self.pPower*5,\
                                         bottom, fill="red")

    def doDrawFireButton(self):
        if self.mouseClicked:
            self.canvas.create_rectangle(50, 600, 100, 650, fill="dark red")
            self.canvas.create_text(75, 625, text="FIRE",  \
                                    font="comicsans 20 bold", fill="white")
        else:
            self.canvas.create_rectangle(25, 575, 125, 675, fill="red")
            self.canvas.create_text(75, 625, text="FIRE",  \
                                    font="comicsans 30 bold")
    
    def drawTimer(self):
        #draws the time spent so far before shooting at this turn
        if self.pHP>0:
            left=self.canvasWidth/1.1
            top=self.canvasHeight/10
            if self.counter<20:
                self.canvas.create_text(left, top, text=self.counter,\
                                        font="comicsans 120 italic bold")
                self.canvas.create_text(left, top, text=self.counter,\
                            fill="white", font="comicsans 100 italic bold")
            else:
                self.canvas.create_text(left, top, text=self.counter,\
                            fill="Black", font="comicsans 120 italic bold")
                self.canvas.create_text(left, top, text=self.counter,\
                            fill="Red", font="comicsans 100 italic bold")
    
    def hexColor(self, red, green, blue):
        return ("#%02x%02x%02x" % (red, green, blue))
    
    def getRGB(self, image, x, y):
        try:
            if x>0 and x<image.width():
                value = image.get(int(x), int(y))
                return tuple(map(int, value.split(" ")))
            else: return (0, 0, 0)
        except: return (0,0,0)
        
    def setRGB(self, image, x, y, red, green, blue):
        (r, g, b)=self.getRGB(image, x, y)
        if r==162 and g==1 and  b==1:
            color = self.hexColor(red, green, blue)
            image.put(color, to=(x,y))
            
    def getPixelsC(self, cx, cy):
        #gets the pixels of a circle at cx, cy (for groove purpose)
        pixel=[]
        for d in xrange(360):
            for i in xrange(self.bulletR*2):
                x=int(cx+round(i*math.cos(math.radians(d))))
                y=int(cy+round(i*math.sin(math.radians(d))))
                if (x, y) not in pixel:
                    pixel.append((x, y))
        return pixel
    
    def drawGroove(self, bk, terrain, cx, cy, pHeight):
        pixels=self.getPixelsC(cx, cy)
        #insert the background pixels at each pixel from getPixelsC onto the
        #terrain at the same position
        for pixel in pixels:
                x=pixel[0]
                y=pixel[1]
                (red, green, blue)=self.getRGB(bk, x, y)
                self.setRGB(terrain, x, y, red, green, blue)
    
    def calcHitXY(self, image, cx, cy, ncx, ncy):
        dx=ncx-cx
        dy=ncy-cy
        #check every point in the direction til the next point
        if dx>0: #if headed right,
            for d in xrange(int(dx+1)):
                x=int(cx+d)
                if d!=0: y=int(((dy/dx*1.0)*d)+cy)
                else: y=cy
                r, g, b=self.getRGB(image, x, y)
                if r==162 and g==1 and b==1: #check if you've hit the terrain
                    return (x, y)
        else:#if headed left
            for d in xrange(abs(int(dx+1))):
                d*=-1
                x=int(cx+d)
                if d!=0: y=int(((dy/dx*1.0)*d)+cy)
                else: y=cy
                r, g, b=self.getRGB(image, x, y)
                if r==162 and g==1 and b==1: 
                    return (x, y)
        return (cx, cy)

    def isLegalProjectile(self, cx, cy):
        if cx<0 or cx>1200:
            self.cx=1200
            self.cy=-100 #draws explosion outside the canvas
            return (False, self.cx, self.cy)
        cx=int(cx)
        cy=int(cy)
        ncx=int(cx+self.pVx)
        ncy=int(cy-self.pVy)
        HitXY=self.calcHitXY(self.terrain, cx, cy, ncx, ncy)
        r, g, b=self.getRGB(self.terrain, HitXY[0], HitXY[1])
        if (r, g, b) == (162, 1, 1):
            return (False, HitXY)
        return (True, HitXY)
    
    def drawExplosion(self, cx, cy, r):
        colors=["white", "yellow"]
        j= random.randint(0, 1)
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=colors[j])
    
    def doAftermath(self, isLegalProjectile):
        self.specialW=False
        self.Weapon="Normal"
        self.explosion=True
        self.setPic()
        self.calcRotation()
        self.p=self.p.rotate(math.degrees(self.deltaA))
        if self.cy>0: self.cx, self.cy=isLegalProjectile[1]
        if not self.user: #in drawing grooves
            d=((self.cx-self.target[0])**2+(self.cy-self.target[1])**2)**0.5
            #if the target is near the bomb sight, teleport the bomb to target
            if d<30: self.drawGroove(self.bk, self.terrain, \
                    self.target[0]-self.pWidth/2, self.cy, self.pHeight)
            else: self.drawGroove(self.bk, self.terrain, self.cx,\
                                  self.cy, self.pHeight)
        else:self.drawGroove(self.bk, self.terrain, self.cx, self.cy,\
                            self.pHeight)
        self.HPreduction(self.cx, self.cy) #reduce HP accordingly
        if not self.user: self.pPower=0
        self.pFire=False
    
    def doProjectile(self, Wx, Wy):
        terrain=self.terrain
        cx=self.cx
        cy=self.cy
        if not self.specialW:
            self.cx+=(self.pVx+Wx)
        else:
            self.cx+=(self.pVx)
        self.cy-=self.pVy
    
    def calcProjectile(self):
        if self.p1INIT:
            self.p1ProjectileINIT() #after the original cx, cy, add pVx and pVy
            self.windINIT()
            self.p1INIT=False
        Wx=self.WindX
        Wy=self.WindY
        if not self.specialW:
            if self.user:
                self.pVy+=(GRAVITY+Wy)
            if not self.user:
                self.pVy+=GRAVITY
        isLegalProjectile=self.isLegalProjectile(self.cx, self.cy)
        if isLegalProjectile[0]:
            self.doProjectile(Wx, Wy)
        else:
            self.doAftermath(isLegalProjectile)

    def drawProjectile(self, cx, cy, r):
        if not self.specialW:
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="red")
        else:
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="black")
            r-=5
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="blue")
            cx-=10; cy+=10
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="turquoise")

    def calcRotation(self):
        prevCx=self.pLeft+self.pWidth/2-3
        prevCy=self.pY
        futuCx=self.pLeft+self.pWidth/2+3
        futuCy=self.setPy(self.terrain, prevCy, futuCx)
        difference=abs(self.pMaxAngle-self.pAngle)
        #find the slope at -3 and +3 x the position the player is at
        #calculate the angle of the change
        self.deltaA=math.atan((prevCy-futuCy)/6.0)
        if not self.headLeft:
            self.bodyAngle=self.deltaA
            if self.user:
                self.pMaxAngle=self.bodyAngle+math.radians(80)
                self.pMinAngle=self.bodyAngle+math.radians(30)
        else:
            self.bodyAngle=-self.deltaA
            if self.user:
                self.pMaxAngle=-math.radians(80)+self.bodyAngle
                self.pMinAngle=self.bodyAngle-math.radians(30)

    def AIisLegalMove(self, travelD, sLocal):
        eLocalx=sLocal[0]+travelD #desitionat
        eLocaly=self.getTopTy(self.terrain, eLocalx) #destination y at eLocalx
        try:
            #now check that there is no pit that can get the player killed
            if travelD<0:
                for path in xrange(eLocalx, sLocal[0]): 
                    if self.getTopTy(self.terrain, path)>690:
                        return False
            elif travelD>0:
                for path in xrange(sLocal[0], eLocalx):
                    if self.getTopTy(self.terrain, path)>690:
                        return False
            if eLocalx<30 or eLocalx>1150 or eLocaly>self.canvasHeight:
                return False
        except: return False
        return True
    
    def AImoveLimit(self):
        possibleMoves=self.possibleMoves
        sign=random.randint(0, 1)
        i=random.randint(0, len(possibleMoves)-1)
        move=possibleMoves[i]
        #until a legal move is found
        while not self.AIisLegalMove(move, self.origin):
            i=random.randint(0, len(possibleMoves)-1)
            move=possibleMoves[i]
        xDest=self.pLeft+self.pWidth/2+move
        yDest=self.getTy(self.terrain, xDest)
        self.destination=(xDest, yDest)
        self.move=move

    def doAILeftMove(self):
        #similar idea to doLeftMove but for AI
        self.setPic()
        if self.headLeft==True:
            self.moved+=1
            self.pLeft-=5
            self.pY=self.setPy(self.terrain, self.pY, self.pLeft+self.pWidth/2)
        else:
            self.headLeft=True
            self.turnPlayerAngle()
        self.calcRotation()
        self.projectileReset()
        self.p=self.p.rotate(math.degrees(self.deltaA))

    def doAIRightMove(self):
        #similar idea to doRightMove but for AI
        self.setPic()
        if self.headLeft==False:
            self.moved+=1
            self.pLeft+=5
            self.pY=self.setPy(self.terrain, self.pY, self.pLeft+self.pWidth/2)
        if self.headLeft:
            self.headLeft=False
            self.turnPlayerAngle()
        self.calcRotation()
        self.projectileReset()
        self.p=self.p.rotate(math.degrees(self.deltaA))

    def moveAI(self):
        move=self.move
        if move<0:
            self.doAILeftMove()
        elif move>0:
            self.doAIRightMove()
        self.origin=(int(self.pLeft+self.pWidth/2), self.pY)

    def calculateAIpower(self):
        self.oppCoord=[] #define alive opponents
        for opponent in self.opponents:
            if opponent.pHP>0:
                self.oppCoord.append(opponent.origin)
        nOpp=len(self.oppCoord)
        self.shortestD=self.canvasWidth
        for i in xrange(nOpp):
            Ocx=self.oppCoord[i][0]
            Ocy=self.oppCoord[i][1]
            Pcx=self.origin[0]
            Pcy=self.origin[1]
            D=(((Pcx-Ocx)**2)+((Pcy-Ocy)**2))**0.5
            if self.shortestD>=D: #find the closest target from opponents
                self.shortestD=D
                self.target=self.oppCoord[i]
        x=(self.target[0]-self.origin[0])
        y=(self.target[1]-self.origin[1])
        try: #physics calculation to find the sufficient power to attack
            self.AIpower=(abs((9.81*(x**2))/((x*math.tan(self.pAngle)-y)\
                *(math.cos(2*self.pAngle)+1))))**0.5
            if self.AIpower<10:
                return random.randint(10, 50)
        except:
            return random.randint(5, 50) #at failure shoot randomly
    
    def setExplosion(self):
        if self.explosionTime==0:
            self.explosion=False
            self.explosionTime=10
            self.explosionR=5
            self.turn=False
    
    def playAI(self):
        if self.pPower<self.AIpower:
            if self.pPower<=18: #AI recharge to 18 until its turn is over...
                self.setPic()#set back to original after shooting
                self.calcRotation()
                self.p=self.p.rotate(math.degrees(self.deltaA))
            else: self.setShotPic()
            self.pPower+=2
            if self.pPower>self.AIpower:#ready to shoot
                self.p1INIT=True
                self.pFire=True
                self.projectileReset()
        if self.pFire:
            self.calcProjectile()
        if self.target[0]<self.origin[0] and not self.headLeft:
            self.headLeft=True #if the target is at the left
            self.turnPlayerAngle()
        elif self.target[0]>self.origin[0] and self.headLeft:
            self.headLeft=False #if the target is at the right
            self.turnPlayerAngle()
           
    def AITimerFired(self):
        self.calculateAIpower()
        self.pY=self.setPy(self.terrain, self.pY, self.pLeft+self.pWidth/2)
        if self.origin[0]!=self.destination[0]:
            if self.headLeft: self.moveAI()
            else: self.moveAI()
        else:
            self.playAI()
        if self.explosion:
            self.setExplosion()
        
    def doTimerFired(self):
        if self.counter==25:#after 25 seconds, your turn is over
            self.turn=False
        if self.mouseClicked and self.pPower<self.pPowermax:
            self.setShotPic()#bazooka!
            self.pPower+=4
        if self.pFire:
            self.calcProjectile()
            if self.headLeft and self.user:
                self.pastA=-math.pi/2-self.pAngle
            if not self.headLeft and self.user:
                self.pastA=self.pAngle
        if self.explosion:
            self.setExplosion()
    
    def doRedrawAll(self):
        if self.user: self.drawTimer()
        if self.turn:
            width=self.pWidth
            height=self.pHeight
            left=self.pLeft
            bottom=self.pY
            top=bottom-height
            self.drawAngle(width, height, left, top)
            if self.pFire:
                self.drawProjectile(self.cx, self.cy, self.bulletR)
            if self.explosion:
                self.explosionR+=5
                self.drawExplosion(self.cx, self.cy, self.explosionR)
                self.explosionTime-=1


#class used to call an input dialogue to set user's name
class MyDialog(tkSimpleDialog.Dialog):
    def body(self, master):
        self.Result= None
        Label(master, text="User:").grid(row=0)
        self.e1 = Entry(master)
        self.e1.grid(row=0, column=1)
        return self.e1 # initial focus
    def apply(self):
        first = self.e1.get()
        self.Result = (first)

############################################################################
#Game class is where the basic information regarding the game is put and
#the different screens that should be displayed(Main Page, instructions, etc...)
#For the convenience of the game, the terrain will always have a color
# r=162, g=1, and b=1

class Game(object):

    #set-up of the game
    ############################################################################
    #Main Page
    #Buttons and their functions
    def Mode1ButtonPressed(self):
        self.mode="Normal"
        #set AI moves such that it usually stays on its position (easier to hit)
        self.AIpossibleMoves=[-150, -100, -50, 0, 0, 0, 0, 0, 50, 100, 150]
    
    def Mode2ButtonPressed(self):
        self.mode="CatchMeIfYouCan"
        #This mode is hard so the AI moves around after each turn
        self.AIpossibleMoves=[-250, -200, -150, -100, -50, 50, 100, 150, 200, 250]
    
    def InstructionPressed(self):
        self.openMain=False
        self.openInstruction=True

    def Instruction2Pressed(self):
        self.openInstruction=False
        self.openInstruction2=True
    
    def nPlayersAddPressed(self):
        if self.nPlayers<10:
            self.nPlayers+=1
    
    def nPlayersSubPressed(self):
        if self.nPlayers>2:
            self.nPlayers-=1
    
    def NextPressed(self):
        if self.openMain:
            self.openSelectMap=True
            self.openMain=False
        elif self.openInstruction:
            self.openInstruction=False
            self.openInstruction2=True
        
    def showDialog(self):
        # calls the class Mydialog and returns the entered name of the user
        Mydialog=MyDialog(self.canvas)
        return Mydialog.Result
    
    def EnterName(self):
        self.uName = str(self.showDialog())

    def setMainButtons(self):
        NormalModeB=PhotoImage(file="NormalModeButton.gif")
        b1 = Button(self.canvas, image=NormalModeB, width=200, height=77, anchor=SW, command=self.Mode1ButtonPressed)
        b1.image=NormalModeB
        self.Mode1B = b1
        CatchMeB=PhotoImage(file="CatchMeButton.gif")
        b2 = Button(self.canvas, image=CatchMeB, width=200, height=77, command=self.Mode2ButtonPressed)
        b2.image=CatchMeB
        self.Mode2B = b2
        InstructButton=PhotoImage(file="InstructionButton.gif")
        b3 = Button(self.canvas, image=InstructButton, width=200, height=77, command=self.InstructionPressed)
        b3.image=InstructButton
        self.InstructB = b3
        UpArrow=PhotoImage(file="UpArrow.gif")
        b4 = Button(self.canvas, image=UpArrow, width=60, height=60, command=self.nPlayersAddPressed)
        b4.image=UpArrow
        self.nPlayersAddB = b4
        DownArrow=PhotoImage(file="DownArrow.gif")
        b5 = Button(self.canvas, image=DownArrow, width=60, height=60, command=self.nPlayersSubPressed)
        b5.image=DownArrow
        self.nPlayersSubB= b5
        NextB=PhotoImage(file="nextButton.gif")
        b6 = Button(self.canvas, image=NextB, width=150, height=77, bg="white", command=self.NextPressed)
        b6.image=NextB
        self.nextB = b6
        b7=Button(self.canvas, text="Enter Your User Name", command=self.EnterName)
        self.EnterNameB=b7

    def mainInit(self):
        self.MainBK=PhotoImage(file="MainBk.gif")
        #Default Game Set Up
        self.AIpossibleMoves=[-150, -100, -50, 0, 0, 0, 0, 0, 50, 100, 150]
        self.mode="Normal"
        self.uName="You"
        self.nPlayers=2
        #Buttons on main page
        self.setMainButtons()
    
    ##############################################################################
    #selectMap Page
    #T=terrain, BK=background
    
    def selectT1(self):
        self.terrain=self.t1
    
    def selectT2(self):
        self.terrain=self.t2
    
    def selectT3(self):
        self.terrain=self.t3
    
    def selectBK1(self):
        self.bk=self.bk1
    
    def selectBK2(self):
        self.bk=self.bk2
    
    def selectBK3(self):
        self.bk=self.bk3
        
    def selectDraw(self):
        self.openSelectMap=False
        self.openDraw=True
        #allows a quicker redraw
        self.timerDelay=1

    def prevPressed(self):
        if self.openSelectMap:
            self.openMain=True
            self.openSelectMap=False
        elif self.openDraw:
            self.openSelectMap=True
            self.openDraw=False
            self.terrain=self.t1
        elif self.openInstruction:
            self.openMain=True
            self.openInstruction=False
        elif self.openInstruction2:
            self.openInstruction=True
            self.openInstruction2=False
        
    def playPressed(self):
        #Let's play some game!
        if self.openDraw:
            self.terrain=self.emptyMap
        self.setPlayers(self.nPlayers)
        self.timerDelay=50
        self.openMain=False
        self.openSelectMap=False
        self.openDraw=False
        self.openInstruction=False
        self.openGame=True
    
    def setMiniSamples(self):
        #set minis of each terriains and background for display
        self.t1mini=PhotoImage(file="Terrain1mini.gif")
        self.t2mini=PhotoImage(file="Terrain2mini.gif")
        self.t3mini=PhotoImage(file="Terrain3mini.gif")
        self.bk1mini=PhotoImage(file="BK1mini.gif")
        self.bk2mini=PhotoImage(file="GameBK2mini.gif")
        self.bk3mini=PhotoImage(file="GameBk3mini.gif")
    
    def setMapButtons(self):
        b1 = Button(self.canvas, text="Terrain 1", command=self.selectT1)
        self.selectT1B = b1
        drawButton=PhotoImage(file="DrawButton.gif")
        b2 = Button(self.canvas, image=drawButton, width=400, height=77, command=self.selectDraw)
        b2.image=drawButton
        self.selectDrawB = b2
        prevButton=PhotoImage(file="prevButton.gif")
        b3 = Button(self.canvas, image=prevButton, width=150, height=77, command=self.prevPressed)
        b3.image=prevButton
        self.prevB = b3
        playButton=PhotoImage(file="playButton.gif")
        b4 = Button(self.canvas, image=playButton, width=150, height=77, command=self.playPressed)
        b4.image=playButton
        self.playB = b4
        b5 = Button(self.canvas, text="Terrain 2", command=self.selectT2)
        self.selectT2B = b5
        b6 = Button(self.canvas, text="Terrain 3", command=self.selectT3)
        self.selectT3B = b6
        b7 = Button(self.canvas, text="Background 1", command=self.selectBK1)
        self.selectBK1B = b7
        b8 = Button(self.canvas, text="Background 2", command=self.selectBK2)
        self.selectBK2B = b8
        b9 = Button(self.canvas, text="Background 3", command=self.selectBK3)
        self.selectBK3B = b9

    def mapInit(self):
        #Buttons on the selet Terrain page
        self.setMapButtons()
        self.setMiniSamples()

    
    ##############################################################################
    #set init for the game itself

    def setPictures(self):
        self.arrow=PhotoImage(file="arrow.gif")
        #p has information that is used for p1, which is actually drawn in game
        self.p=PIL.Image.open("worm.gif").convert("RGBA")
        self.p1=ImageTk.PhotoImage(self.p)
        #terrains and backgrounds
        self.t1=PhotoImage(file="Terrain1.gif")
        self.t2=PhotoImage(file="Terrain2.gif")
        self.t3=PhotoImage(file="Terrain3.gif")
        self.bk1=PhotoImage(file="BK1.gif")
        self.bk2=PhotoImage(file="GameBk2.gif")
        self.bk3=PhotoImage(file="GameBK3.gif")
        
    def setGameButtons(self):
        ExitB=PhotoImage(file="Exit.gif")
        b1 = Button(self.canvas, image=ExitB, width=140, height=50, command=self.exit)
        b1.image=ExitB
        self.ExitB = b1
        PauseB=PhotoImage(file="pause.gif")
        b2 = Button(self.canvas, image=PauseB, width=140, height=50, command=self.pause)
        b2.image=PauseB
        self.PauseB = b2
        b3=Button(self.canvas, text="Normal Weapon", command=self.NormalW)
        self.NormalWB=b3
        b4=Button(self.canvas, text="Special Weapon", command=self.SpecialW)
        self.SpecialWB=b4
    
    def gameInit(self):
        self.deathMatch=self.gameOver=self.user=self.win=self.paused=False
        self.setPictures()
        self.tHeight=223 #used for user interface in the game
        self.oil=743 #stamina of the worm
        #WindA is the angle of the wind
        self.windAlist=[0, 30, 45, 60, 90, 120, 135, 150, 180, 210,\
                        225, 240, 270, 300, 315, 330]
        self.windA=math.radians(self.windAlist[random.randint(0, 15)])
        self.windV=random.randint(0, 9) #the magnitude of the wind
        self.pFire=False
        #turnCounter is counted every timerFired, and gameTurn counts the rounds
        self.currentP=self.turnCounter=self.gameTurn=0
        self.terrain=self.t1 #default terrain
        self.bk=self.bk1 #default background
        self.setGameButtons()
  
    def NormalW(self): #Chose normal weapon
        player=self.players[self.currentP]
        if player.user:
            player.Weapon="Normal"
        
    def SpecialW(self): #Chose speical weapon
        player=self.players[self.currentP]
        if player.user:
            player.Weapon="Special"
    
    def drawWeapon(self): #in the user interaction
        player=self.players[self.userIndex]
        cx=830; cy=600; r=player.bulletR
        if player.Weapon=="Normal":
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="red")
            self.canvas.create_text(cx+35, cy, text="x999", font="fixedsys 15")
        else:
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="black")
            r-=5
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="blue")
            cx-=10; cy+=10
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="turquoise")
            self.canvas.create_text(cx+25, cy, text="x%d"%player.nSpecial, font="fixedsys 15")
        self.canvas.create_text(800, 600, text="Current Weapon=%s"%player.Weapon, anchor=E, font="fixedsys 20")
        
    def exit(self):
        self.openMain=True
        self.openGame=False
        self.initWrapper() #sets to the new game

    def pause(self):
        if self.paused:
            self.paused=False
        else: self.paused=True
    
    ##############################################################################
    #draw Page- user can draw the terrain

    def drawInit(self):
        self.emptyMap =PhotoImage(file="emptyMap.gif")
        self.draw=self.done=False
        redrawButton=PhotoImage(file="RedrawButton.gif")
        b1= Button(self.canvas, image=redrawButton, width=200, height=77, command=self.selectRedraw)
        b1.image=redrawButton
        self.redrawB=b1
        
    def selectRedraw(self):
        #refresh the map image
        self.emptyMap=PhotoImage(file="emptyMap.gif")
    
    def getRGB(self, image, x, y):
        try:
            if x>0 and x<image.width():
                value = image.get(int(x), int(y))
                return tuple(map(int, value.split(" ")))
            else: return (0, 0, 0)
        except: return (0,0,0)
        
    def setDrawRGB(self, image, x, y):
        if x>0 and y>0:
            #for pixel at (x,y), fill in the color below
            color = self.hexColor(162, 1, 1)
            image.put(color, to=(x,y))
    
    def floodFill(self, image):
        for x in xrange(1, 1200): #go through the width
            Ty=self.getTopTy(image, x) #find the y-coordinate of the drawn line
            for y in xrange(Ty, 750):
                #fill in bottom to up til the y-coord
                self.setDrawRGB(image, x, y)
        self.done=False
    
    def drawPencil(self, image, cx, cy):
        pixel=set([])
        #fill in a circle with radius 10 in order to draw
        for d in xrange(360):
            for i in xrange(10):
                x=int(cx+round(i*math.cos(math.radians(d))))
                y=int(cy+round(i*math.sin(math.radians(d))))
                if (x, y) not in pixel:
                    pixel.add((x, y))
                    self.setDrawRGB(self.emptyMap, x, y)
 
    def leftDrawMousePressed(self, event):
        if not self.done:
            self.draw=True
    
    def leftMouseMoved(self, event):
        #draw while the mouse is being moved
        if self.openDraw:
            if self.draw:
                self.drawPencil(self.emptyMap, event.x, event.y)
        
    def leftDrawMouseReleased(self, event):
        self.draw=False
    
    def keyDrawPressed(self, event):
        if event.keysym=="space":
            self.done=True #... and we start filling
    
    def InstructionInit(self):
        self.Instruction1=PhotoImage(file="Instruction1.gif")
        self.Instruction2=PhotoImage(file="Instruction2.gif")
    
    #InitWrapper
    def initWrapper(self):
        self.openMain=True
        self.openSelectMap=self.openDraw=self.openInstruction=self.openGame=self.openInstruction2=False
        self.timerDelay=50
        self.mainInit()
        self.InstructionInit()
        self.gameInit()
        self.drawInit()
        self.mapInit()

    ##############################################################################
    #Game things
    ##############################################################################

    def getTopTy(self, image, x):
        #check up to bottom the most top terrain (y) at x
        for y in xrange(700):
            (r, g, b)=self.getRGB(image, x,  y)
            if r==162 and g==1 and b==1:
                return y
    
    def leftMousePressed(self, event):
        if self.openGame and not self.paused:
            if self.players[self.currentP].user:
                self.players[self.currentP].doLeftMousePressed(event)
        elif self.openDraw:
            self.leftDrawMousePressed(event)

    def leftMouseReleased(self, event):
        if self.openGame:
            if self.players[self.currentP].user:
                self.players[self.currentP].doLeftMouseReleased(event)
        elif self.openDraw:
            self.leftDrawMouseReleased(event)

    def keyPressed(self, event):
        if self.openGame and not self.paused:
            if self.players[self.currentP].user:
                self.players[self.currentP].doKeyPressed(event)
        elif self.openDraw:
            self.keyDrawPressed(event)

    def run(self, width=1200, height=700):
        self.root=Tk()
        self.canvas = Canvas(self.root, width=width, height=height)
        self.root.resizable(width=FALSE, height=FALSE)
        self.canvas.pack(fill=BOTH, expand=YES)
        self.margin2=margin=5
        canvasWidth=self.canvasWidth=width-margin*2
        canvasHeight=self.canvasHeight=height-margin*2
        self.initWrapper()
        def redrawAllWrapperC():
            self.canvas.delete(ALL)
            self.redrawAllWrapper()
        def mousePressedWrapper(event):
            self.leftMousePressed(event)
            redrawAllWrapperC()
        def keyPressedWrapper(event):
            self.keyPressed(event)
            redrawAllWrapperC()
        def leftMouseMovedWrapper(event):
            self.leftMouseMoved(event)
            redrawAllWrapperC()
        def leftMouseReleasedWrapper(event):
            self.leftMouseReleased(event)
        self.root.bind("<Key>", keyPressedWrapper)
        self.root.bind("<Button-1>", mousePressedWrapper)
        self.root.bind("<B1-Motion>", leftMouseMovedWrapper)
        self.root.bind("<B1-ButtonRelease>", leftMouseReleasedWrapper)
        self.timerFired() # set up timerFired events
        self.root.mainloop() # and launch the app

    def setPlayers(self, nPlayers):
        self.players=[] #add instances of Player
        for i in xrange(nPlayers):
            pWidth=self.p1.width()
            pHeight=self.p1.height()
            pLeft=random.randint(0, self.canvasWidth-pWidth)#set position
            windV=self.windV
            windA=self.windA
            headLeft=False
            bk=self.bk
            if i%2==0: ally=False
            else: ally=True
            terrain=self.terrain
            canvasWidth=self.canvasWidth
            canvasHeight=self.canvasHeight
            possibleMoves=self.AIpossibleMoves
            playerName="player%s" %(str(i+1))
            self.players.append(Player(possibleMoves, self.p, self.p1, bk,\
            playerName, self.canvas, pWidth, pHeight, pLeft, windV, windA,\
            headLeft, canvasWidth, canvasHeight, terrain, ally, self.oil))
        self.setPspecifics()

    def setPspecifics(self):
        self.userIndex=random.randint(0, len(self.players)-1) #chose the user
        self.players[self.userIndex].user=True
        self.players[self.currentP].turn=True
        self.players[self.userIndex].pName=self.uName
        for player in self.players: #set opponents
            for i in xrange(self.nPlayers):
                if player.ally!=self.players[i].ally:
                    player.opponents.append(self.players[i])
                player.players.append(self.players[i])
        self.players[self.currentP].AImoveLimit()
    
    def drawFinale(self, text):
        cx=self.canvasWidth/2
        cy=self.canvasHeight/2
        if text=="WIN":
            self.canvas.create_text(cx, cy, text=text,\
                                    font="Comicsans 100 bold", fill="red")
        else:   
            self.canvas.create_text(cx, cy, text=text,\
                                    font="Comicsans 100 bold", fill="green")
    
    def drawTurn(self, player): #draw the turn indicator
        height=player.pY-player.pHeight-20
        self.canvas.create_image(player.pLeft+player.pWidth/2.0,\
                                 height, image=self.arrow)                

    def drawWind(self):
        WindV=self.windV
        WindA=self.windA-math.pi*3/2 #set it to the Tkinter standard
        cWidth=self.canvasWidth
        cHeight=self.canvasHeight
        cx=cWidth/2.0
        cy=cHeight/20.0
        r=30
        minuteHand=26
        Windx=minuteHand*math.sin(WindA)
        Windy=minuteHand*math.cos(WindA)
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="white", width=5)
        self.canvas.create_line(cx, cy, cx+Windx, cy+Windy, fill="red", width=5)
        self.canvas.create_text(cx, cy, text=WindV, fill="Blue", \
                                font="ComicSans 20")

    def drawRange(self):
        terrain=self.terrain
        left=self.canvasWidth/6.0
        right=left+int(self.canvasWidth/1.6)
        top=self.canvasHeight-20
        bottom=top+20
        self.canvas.create_rectangle(left, top, right, bottom, fill="grey")
        if self.players[self.currentP].user:
            self.players[self.currentP].doDrawRange(left, top, right, bottom)

    def drawPowerBar(self):
        terrain=self.terrain
        left=self.canvasWidth/6.0
        right=left+int(self.canvasWidth/1.6)
        top=self.canvasHeight-70
        bottom=top+50
        self.canvas.create_rectangle(left, top, right, bottom, fill="grey")
        if self.players[self.currentP].user:
            self.players[self.currentP].doDrawPowerBar(left, right, top, bottom)
        for i in xrange(4): #draw margins on the gauge
            Left=left+(right-left)/4.0*i
            self.canvas.create_line(Left, top, Left, bottom)
    
    def setDrawAngle(self, player):
        #set angles to Tkinter standard and to users'
        if player.headLeft: 
            currentAngle=int(90-abs(math.degrees(player.pAngle)))
        else: currentAngle=int(math.degrees(player.pAngle))
        if currentAngle>90: currentAngle=180-currentAngle
        return currentAngle

    def drawPlayer(self):
        for player in self.players:
            if player.pHP>0:#draw them if they are alive
                player.p1=ImageTk.PhotoImage(player.p)
                width=player.pWidth
                height=player.pHeight
                left=player.pLeft
                bottom=player.setPy(self.terrain, player.pY,\
                                    player.pLeft+player.pWidth/2)
                top=bottom-height
                self.canvas.create_image(left, bottom, anchor=SW, \
                                image=player.p1)
                currentAngle=self.setDrawAngle(player)
                if player.user: #show the current angle
                    self.canvas.create_text(left+width/2*3, bottom-height/2,\
                    text=currentAngle, fill="Turquoise", font="comicsans 15")
                if player.turn: self.drawTurn(player)
                self.drawHPbar(player.pHP, width, height, left, bottom)
                self.drawName(width, height, left, player.pName, player.ally,\
                              bottom)

    def drawHPbar(self, pHP, Width, Height, Left, bottom):
        FullHP=100
        HP=pHP
        width=Width
        height=Height/5
        left=Left
        top=bottom+20
        right=left+width
        bottom=top+height
        center=(left+right)/2.0
        self.canvas.create_rectangle(center-FullHP/2.0, top, \
                                     center+FullHP/2.0, bottom, fill="grey")
        self.canvas.create_rectangle(center-FullHP/2.0, top,\
                                     center+HP-FullHP/2.0, bottom, fill="red")

    def drawName(self, Width, Height, Left, pName, ally, bottom):
        width=Width
        height=Height/2
        left=Left
        top=bottom+10
        right=left+width
        center=(left+right)/2.0
        name=pName
        if ally:
            self.canvas.create_text(center, top, text=name, fill="blue")
        else:
            self.canvas.create_text(center, top, text=name, fill="violet")

    def setAngleMemory(self, userI):
        if self.players[userI].headLeft:
            currentAngle=str(int(90-abs(math.degrees(self.players[userI].pAngle))))
            pastAngle=str(int(abs(math.degrees(self.players[userI].pastA))))
        else:
            currentAngle=str(int(abs(math.degrees(self.players[userI].pAngle))))
            pastAngle=str(int(abs(math.degrees(self.players[userI].pastA))))
        return (currentAngle, pastAngle)
    
    def drawAngleMemory(self, left, top):
        userI=self.userIndex
        right=self.canvasWidth/5.0
        bottom=self.canvasHeight-75
        self.canvas.create_rectangle(left, top, right, bottom, fill="black")
        currentAngle=self.setAngleMemory(userI)[0]
        pastAngle=self.setAngleMemory(userI)[1]
        self.canvas.create_text(left+10, top, text="LAST", anchor=NW,\
                                fill="white")
        self.canvas.create_text(left+15, top+15, text=pastAngle, anchor=NW,\
                                fill="white", font="comicsans")
        self.canvas.create_text(left+50, top+15, text=currentAngle,\
                    anchor=W, fill="white", font="comicsans 24 italic")

    def drawFireButton(self):
        if not self.players[self.currentP].user:
            self.canvas.create_rectangle(25, 575, 125, 675, fill="red")
            self.canvas.create_text(75, 625, text="FIRE",\
                                    font="comicsans 30 bold")
        if self.players[self.currentP].user:
            self.players[self.currentP].doDrawFireButton()
    
    def drawDeathMatch(self):
        terrain=self.terrain
        left=self.canvasWidth/6.0+int(self.canvasWidth/1.6)
        right=self.canvasWidth/8.0+int(self.canvasWidth/1.3)
        top=self.canvasHeight-70
        bottom=self.canvasHeight
        self.canvas.create_rectangle(left, top, right, bottom, fill="green")
        if self.deathMatch:
            self.canvas.create_text(left, top, text="DEATH",\
                                    anchor=NW, font="Times 25 bold")
            self.canvas.create_text(left, bottom, text="MATCH",\
                                    anchor=SW, font="Times 25 bold")
        else:
            self.canvas.create_text(left, top, text="Normal",\
                                    anchor=NW, font="Times 28 bold")
            self.canvas.create_text(left+15, bottom, text="Mode",\
                                    anchor=SW, font="Times 30 bold")

    def drawUserInteraction2(self):
        canvasWidth=self.canvasWidth
        canvasHeight=self.canvasHeight
        terrain=self.terrain
        UI2left=canvasWidth/8.0
        UI2right=UI2left+int(canvasWidth/1.3)
        UI2top=canvasHeight-111
        UI2bottom=canvasHeight
        self.canvas.create_rectangle(UI2left, UI2top, UI2right, UI2bottom,\
                                     fill="Light Cyan")
        self.drawPowerBar()
        self.drawRange()
        self.drawAngleMemory(UI2left, UI2top)
        self.drawDeathMatch()
    
    def hexColor(self, red, green, blue):
        return ("#%02x%02x%02x" % (red, green, blue))

    def checkGameOver(self):
        Home=[]
        Away=[]
        uI=self.userIndex
        for player in self.players:
            if player.pHP>0 and player.user: #user is in home team
                Home.append(player)
            elif player.pHP>0 and not player.user and\
                    player.ally==self.players[uI].ally:
                #user's allies are in home, too
                Home.append(player)
            elif player.pHP>0 and not player.user and\
                    player.ally!=self.players[uI].ally:
                #all the rest is opponent
                Away.append(player)
        if len(Home)==0: #when there is no longer home players
            self.gameOver=True
            self.win=False
        elif len(Away)==0: #other wise,
            self.gameOver=True
            self.win=True

    def setGame(self):
        if self.currentP==len(self.players)-1:
            self.currentP=0#when every player each had one turn
            self.gameTurn+=1#one round has passed
            if self.gameTurn%4==0: #after every four rounds, reset wind
                self.windA=math.radians(self.windAlist[random.randint(0, 15)])
                self.windV=random.randint(0, 9)
                for player in self.players:
                    player.windA=self.windA
                    player.windV=self.windV
        else:
            self.currentP+=1
        self.players[self.currentP].turn=True
        self.players[self.currentP].oil=self.oil
        self.players[self.currentP].AImoveLimit()
        if self.currentP!=self.userIndex: #for AI, reset the projectile
            self.players[self.currentP].projectileReset()

    def playGame(self):
        cP=self.players[self.currentP]
        self.checkGameOver()
        for player in self.players:
            #at death match, the bullet and its power increases
            if self.deathMatch: 
                player.bulletR=18
            if player.pHP<1: #the player is dead
                player.pHP=0
                player.turn=False
        if cP.turn==False:# when the turn is over, move to the next player
            self.setGame()
        if self.gameTurn==15:#after 15rounds, start deathMatch
            self.deathMatch=True
    
    ##############################################################################
    #RedrawAlls
    ##############################################################################    
    def drawMainRedrawAllButtons(self):
        b1 = self.Mode1B
        self.canvas.create_window(450, 250, window=b1)
        b2 = self.Mode2B
        self.canvas.create_window(750, 250, window=b2)
        b3 = self.InstructB
        self.canvas.create_window(600, 410, window=b3)
        b4 =  self.nPlayersAddB
        self.canvas.create_window(500, 510, window=b4)
        b5 = self.nPlayersSubB
        self.canvas.create_window(500, 570, window=b5)
        b6=self.nextB
        self.canvas.create_window(1100, 620, window=b6)
        b7=self.EnterNameB
        self.canvas.create_window(600, 640, window=b7)

    def doMainRedrawAll(self):
        # background (fill canvas)
        self.canvas.create_image(0, 700, anchor=SW, image=self.MainBK)
        self.drawMainRedrawAllButtons()
        self.canvas.create_text(600, 330, text="Mode=%s"%self.mode, \
                                font="fixedsys 30", fill="white")
        self.canvas.create_text(620, 540, text="players=%d"%self.nPlayers, \
                                font="fixedsys 20", fill="white")
        self.canvas.create_text(600, 170, text="Select Mode", \
                                font="fixedsys 40", fill="white")
        self.canvas.create_text(600, 70, text="Space Worms", \
                                font="fixedsys 80", fill="yellow")
    
    def showInstruct2(self):
        b3 = self.prevB
        self.canvas.create_window(100, 650, window=b3)
        self.canvas.create_image(0, 700, anchor=SW, image=self.Instruction2)
        
    def doGameRedrawAll(self):
        self.canvas.create_image(0, 750, anchor=SW, image=self.bk)
        self.canvas.create_image(0, 750, anchor=SW, image=self.terrain)
        self.drawUserInteraction2()
        self.drawPlayer()
        self.drawWind()
        self.drawFireButton()
        self.players[self.currentP].doRedrawAll()
        b1 = self.ExitB
        self.canvas.create_window(1135, 660, window=b1)
        b2= self.PauseB
        self.canvas.create_window(1135, 610, window=b2)
        b3=self.NormalWB
        self.canvas.create_window(300, 600, window=b3)
        b4=self.SpecialWB
        self.canvas.create_window(400, 600, window=b4)
        self.drawWeapon()
        
    def drawMinis(self):
        self.canvas.create_image(50, 300, anchor=SW, image=self.t1mini)
        self.canvas.create_image(450, 300, anchor=SW, image=self.t2mini)
        self.canvas.create_image(850, 300, anchor=SW, image=self.t3mini)
        self.canvas.create_image(50, 550, anchor=SW, image=self.bk1mini)
        self.canvas.create_image(450, 550, anchor=SW, image=self.bk2mini)
        self.canvas.create_image(850, 550, anchor=SW, image=self.bk3mini)
    
    def drawMapRedrawAllButtons(self):
        b1 = self.selectT1B
        self.canvas.create_window(200, 300, window=b1)
        b2 = self.selectDrawB
        self.canvas.create_window(600, 650, window=b2)
        b3 = self.prevB
        self.canvas.create_window(100, 650, window=b3)
        b4 = self.playB
        self.canvas.create_window(1100, 650, window=b4)
        b5= self.selectT2B
        self.canvas.create_window(600, 300, window=b5)
        b6= self.selectT3B
        self.canvas.create_window(1000, 300, window=b6)
        b7=self.selectBK1B
        self.canvas.create_window(200, 550, window=b7)
        b8=self.selectBK2B
        self.canvas.create_window(600, 550, window=b8)
        b9=self.selectBK3B
        self.canvas.create_window(1000, 550, window=b9)
    
    def doMapRedrawAll(self):
        self.canvas.create_image(0, 700, anchor=SW, image=self.MainBK)
        self.drawMapRedrawAllButtons()
        self.canvas.create_text(600, 50, text="Select Map",\
                                font="fixedsys 80", fill="white")
        self.drawMinis()

    def showInstruct1(self):
        self.canvas.create_image(0, 700, anchor=SW, image=self.Instruction1)
        b1 = self.prevB
        self.canvas.create_window(100, 650, window=b1)
        b6=self.nextB
        self.canvas.create_window(1100, 620, window=b6)

    def doDrawRedrawAll(self):
        b1 = self.playB
        self.canvas.create_window(1100, 650, window=b1)
        b2 = self.prevB
        self.canvas.create_window(100, 650, window=b2)
        b3=self.redrawB
        self.canvas.create_window(1100, 50, window=b3)
        self.canvas.create_text(600, 50, \
            text="Draw and then press spacebar to fill", font="ComicSans 15")
        self.canvas.create_text(600, 80, \
        text="Please wait while the terrain is filled", font="ComicSans 15")
        image = self.emptyMap
        self.canvas.create_image(0, 750, anchor=SW, image=image)

    def redrawAllWrapper(self):
        self.canvas.delete(ALL)
        if self.openMain:
            self.doMainRedrawAll()
        elif self.openGame:
            self. doGameRedrawAll()
        elif self.openSelectMap:
            self.doMapRedrawAll()
        elif self.openInstruction:
            self.showInstruct1()
        elif self.openInstruction2:
            self.showInstruct2()
        elif self.openDraw:
            self.doDrawRedrawAll()
    
    ##############################################################################
    #timerFireds
    ##############################################################################      
    def doDrawTimerFired(self):
        if self.done: #when you are done drawing
            self.floodFill(self.emptyMap)
    
    def doGameTimerFired(self):
        if not self.gameOver:
            if not self.paused:
                self.turnCounter+=1
                if self.turnCounter%20==0:
                    self.players[self.currentP].counter+=1#time limit for user
                if self.players[self.currentP].user:
                    self.players[self.currentP].doTimerFired()
                else:
                    self.turnCounter=0
                    self.players[self.userIndex].counter=0
                    self.players[self.currentP].AITimerFired()
                self.playGame()
            else:
                self.canvas.create_text(600, 350, text="PAUSED", fill="red",\
                                        font="fixedsys 100")
        else:
            if self.win:
                self.drawFinale("WIN")
            else: self.drawFinale("LOSE")
    
    def timerFired(self):
        if self.openGame:
            self.doGameTimerFired()
        elif self.openDraw:
            self.doDrawTimerFired()
        if not self.paused and not self.gameOver:
            self.redrawAllWrapper()
        delay = self.timerDelay # milliseconds
        def f():
            self.timerFired()
        self.canvas.after(delay, f)

def main():
    app=Game()
    app.run()
#Bazooka is out all times,
#the pY is not working entirely for calc rotation in drawPlayer
main()
