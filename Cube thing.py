import pygame,math,random,sys,os,copy,numpy,time
from UIpygame import PyUI as pyui
pygame.init()
screenw = 900
screenh = 600
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
ui.styleload_teal()

class Render_3D:
    def __init__(self):
        #x,y,z, xr,yr,zr
        self.camera = [0,0,-200,0,0,0]
        self.focallength = 1000
        self.fov = 45
        self.selected = -1


        self.mesh = []
        self.lightvector = [20,10,30]
        self.refreshdisplay()
        
    def projectpoly(self,poly):
        adjustedpoly = []
        for a in poly[1]:
            adjustedpoly.append(self.rotatepoint(a,self.camera))
            
        projectedpoly = []
        for a in adjustedpoly:
            projectedpoly.append([(self.focallength)/(a[2])*(a[0])+ui.screenw/2,(self.focallength )/(a[2])*(a[1])+ui.screenh/2])
            
        angle = poly[4]
        col = (poly[0][0]*angle,poly[0][1]*angle,poly[0][2]*angle)
        return [col,projectedpoly,poly[2],poly[3],poly[4]]
    def rotatepoint(self,point,cam):
        x0 = point[0]-cam[0]
        y0 = point[1]-cam[1]
        z0 = point[2]-cam[2]
        #rotates for left/right turning
        x1 = x0*math.cos(-cam[4])+z0*math.sin(-cam[4])
        y1 = y0
        z1 = z0*math.cos(-cam[4])-x0*math.sin(-cam[4])
        #rotates for up/down turning
        x2 = x1
        y2 = y1*math.cos(-cam[3])-z1*math.sin(-cam[3])
        z2 = y1*math.sin(-cam[3])+z1*math.cos(-cam[3])
        #rotates world clockwise/anticlockwise
        x3 = x2*math.cos(-cam[5])-y2*math.sin(-cam[5])
        y3 = x2*math.sin(-cam[5])+y2*math.cos(-cam[5])
        z3 = z2
        return [x3,y3,z3]
        
    def refreshdisplay(self):
        for mesh in self.mesh:
            for a in range(len(mesh)):
                mesh[a][3] = self.avpoint(mesh[a][1])
                if mesh[a][2]<100000000: mesh[a][2] = self.pythag3d(self.camera,mesh[a][3])
                mesh[a][4] = self.lightcalc(mesh[a][1])
            mesh.sort(key=lambda x: x[2],reverse=True)
        self.mesh.sort(key=lambda x: self.pythag3d(self.camera,self.avpoint([m[3] for m in x])),reverse=True)
        self.projected = []
        for b in self.mesh:
            for a in b:
                poly = self.projectpoly(a)
                if poly[2]>40 and self.getclockwise(poly):
                    self.projected.append(self.projectpoly(a))
    def refreshselected(self):
        self.selected = -1
        for a in range(len(self.projected)):
            if pyui.polycollide(ui.mpos,self.projected[a][1]):
                self.selected = a
        self.selected  = -1
    def pythag3d(self,p1,p2):
        return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)**0.5
    def avpoint(self,points):
        if len(points) == 0: return (0,0,0)
        tot = [0,0,0]
        for a in points:
            tot[0]+=a[0]
            tot[1]+=a[1]
            tot[2]+=a[2]
        tot[0]/=len(points)
        tot[1]/=len(points)
        tot[2]/=len(points)
        return tot
    def getclockwise(self,poly):
        points = copy.deepcopy(poly[1])
        yvals = [a[1] for a in points]
        index = yvals.index(min(yvals))
        while index!=0:
            points.append(points.pop(0))
            index-=1
##        if points[1][0] == points[2][0]:
##            if 
##        if points[1][0]>points[2][0]:
##            return True

##        if (points[0][0]-points[1][0])<0:
##            if points[2][0]-points[0][0] < (points[0][1]-points[1][1])/(points[0][0]-points[1][0])*(points[2][1]-points[0][1]):
##                return True
##        elif (points[0][0]-points[1][0]) == 0:
##            if points[2][1]<points[1][1]:
##                return True
##        elif points[2][0]-points[0][0] > (points[0][1]-points[1][1])/(points[0][0]-points[1][0])*(points[2][1]-points[0][1]):
##            return True
##        print(points,math.atan2(points[0][1]-points[1][1],points[0][0]-points[1][0]),math.atan2(points[0][1]-points[2][1],points[0][0]-points[2][0]))

        if points[0][1] == points[2][1]:
            return points[0][0]>points[2][0]
        elif points[0][1] == points[1][1]:
            return points[0][0]<points[1][0]
        elif math.atan2(points[0][1]-points[1][1],points[0][0]-points[1][0])<math.atan2(points[0][1]-points[2][1],points[0][0]-points[2][0]):
            return True
    
        
        return False
        
            
    def lightcalc(self,poly):
        light = self.lightvector
        v1 = [poly[1][0]-poly[0][0],poly[1][1]-poly[0][1],poly[1][2]-poly[0][2]]
        v2 = [poly[2][0]-poly[0][0],poly[2][1]-poly[0][1],poly[2][2]-poly[0][2]]
        n = [v1[1]*v2[2]-v1[2]*v2[1],
             v1[2]*v2[0]-v1[0]*v2[2],
             v1[0]*v2[1]-v1[1]*v2[0]]
        try:
            costheta = (n[0]*light[0]+n[1]*light[1]+n[2]*light[2])/(pythag3d([0,0,0],n)*pythag3d([0,0,0],light))
        except:
            costheta = 1

        return (costheta+1)/2

    def polypreprocess(self,poly):
        npoly = []
        for a in poly:
            if len(a[1]) == 3:
                npoly.append([a[0],a[1],0])
            elif len(a[1]) == 4:
                temp = copy.deepcopy(a[1])
                del temp[3]
                npoly.append([a[0],temp,0])
                temp2 = copy.deepcopy(a[1])
                del temp2[1]
                npoly.append([a[0],temp2,0])
            else:
                print(len(a[1]),a)
        for a in range(len(npoly)):
            npoly[a].append(self.avpoint(npoly[a][1]))
            npoly[a].append(self.lightcalc(npoly[a][1]))
        return npoly

    def cameracontroller(self):
        precam = self.camera[:]
        speed = 3
        kprs = pygame.key.get_pressed()
        rel = pygame.mouse.get_rel()
        mprs = pygame.mouse.get_pressed()
##        if not mprs[1]: rel = [0,0]
        if kprs[pygame.K_UP]:
            self.camera[2]+=speed*math.cos(self.camera[4])
            self.camera[0]+=speed*math.sin(self.camera[4])
        elif kprs[pygame.K_DOWN]:
            self.camera[2]-=speed*math.cos(self.camera[4])
            self.camera[0]-=speed*math.sin(self.camera[4])
        if kprs[pygame.K_LEFT]:
            self.camera[2]+=speed*math.cos(self.camera[4]-math.pi/2)
            self.camera[0]+=speed*math.sin(self.camera[4]-math.pi/2)
        elif kprs[pygame.K_RIGHT]:
            self.camera[2]+=speed*math.cos(self.camera[4]+math.pi/2)
            self.camera[0]+=speed*math.sin(self.camera[4]+math.pi/2)
        if kprs[pygame.K_SPACE]: self.camera[1]-=5
        elif kprs[pygame.K_LSHIFT]: self.camera[1]+=5

        self.camera[3]-=rel[1]/1000
        self.camera[4]+=rel[0]/1000
        if self.camera[3]>math.pi/2: self.camera[3] = math.pi/2
        elif self.camera[3]<-math.pi/2: self.camera[3] = -math.pi/2

        if self.camera!=precam:
            self.refreshdisplay()
            
    def cubecameracontroller(self):
        precam = self.camera[:]
        speed = 10
        kprs = pygame.key.get_pressed()
        rel = pygame.mouse.get_rel()
        mprs = pygame.mouse.get_pressed()

        # Up/down, left/right
        inpu = [0,0]
        inpu[0]+=int(kprs[pygame.K_DOWN])
        inpu[0]-=int(kprs[pygame.K_UP])
        inpu[1]+=int(kprs[pygame.K_RIGHT])
        inpu[1]-=int(kprs[pygame.K_LEFT])

        if mprs[0]:
            inpu[0]-=rel[1]/10
            inpu[1]-=rel[0]/10
        
        self.camera[2]+=speed*math.cos(self.camera[4]-math.pi/2)*math.cos(self.camera[3])*inpu[1]
        self.camera[0]+=speed*math.sin(self.camera[4]-math.pi/2)*math.cos(self.camera[3])*inpu[1]

        self.camera[1]-=speed*inpu[0]

        
        
        self.camera[3] = math.atan2(self.camera[1],((self.camera[0]**2+self.camera[2]**2)**0.5))
        self.camera[4] = math.atan2(self.camera[0],self.camera[2])-math.pi

        distance = 350/self.pythag3d((0,0,0),self.camera)
        self.camera[0]*=distance
        self.camera[1]*=distance
        self.camera[2]*=distance
         
        if self.camera!=precam:
            self.refreshdisplay()
        self.refreshselected()

    def drawmesh(self,screen):
        for a in self.projected:
            pyui.draw.polygon(screen,a[0],a[1])
        if self.selected!=-1:
            pygame.draw.polygon(screen,(255,255,255),self.projected[self.selected][1],4)

    def makecube(self,x,y,z,side,angles=(0,0,0),cols=(150,150,150),border=-1,bordercol=(0,0,0),refresh=False,fillback=False):
        if border == -1:
            border = int(side/10)
            
        if type(cols) == list:
            if len(cols) == 6:
                ncols = []
                for a in cols:
                    ncols+=[a,a]
                cols = ncols
        elif type(cols) == tuple:
            cols = [cols for a in range(12)]
            
        mesh = []
        sid = side/2
        corners = [(x+sid,y+sid,z+sid),(x-sid,y+sid,z+sid),(x-sid,y+sid,z-sid),(x+sid,y+sid,z-sid),
                   (x+sid,y-sid,z+sid),(x-sid,y-sid,z+sid),(x-sid,y-sid,z-sid),(x+sid,y-sid,z-sid)]
        connections = [(5,4,6),(7,6,4),(3,2,7),(6,7,2),(2,1,6),(5,6,1),(1,0,5),(4,5,0),(0,3,4),(7,4,3),(0,1,3),(2,3,1)]
        for i,a in enumerate(connections):
            if cols[i] != -1:
                if border == 0:
                    mesh.append([cols[i],[corners[a[0]],corners[a[1]],corners[a[2]]]])
                else:

                    c0 = corners[a[0]]
                    c1 = corners[a[1]]
                    c2 = corners[a[2]]
                    a = numpy.array(c1)
                    b = numpy.array(c2)
                    c = numpy.array(c0)
                    b0 = border
                    b1 = b0/self.pythag3d(a-b,(0,0,0))
                    p0 = c+(b0/self.pythag3d(a+b-2*c,(0,0,0)))*(a+b-2*c)
                    p1 = a+b1*(b-a)
                    p2 = b+b1*(a-b)

                    mesh.append([cols[i],[p0,p1,p2]])
                    mesh.append([bordercol,[b,p0,p2]])
                    mesh.append([bordercol,[b,c,p0]])
                    mesh.append([bordercol,[c,a,p0]])
                    mesh.append([bordercol,[a,p1,p0]])
            elif fillback:
                mesh.append([bordercol,[corners[a[0]],corners[a[1]],corners[a[2]]]])

        for a in range(len(mesh)):
            mesh[a] = [mesh[a][0],[self.rotatepoint(b,[0,0,0]+list(angles)) for b in mesh[a][1]],float('inf')]
                
        self.mesh.append(self.polypreprocess(mesh))
        if refresh:
            self.refreshdisplay()
        

class Cube:
    def __init__(self,height=4,width=-1,depth=-1):
        if width == -1: width = height
        if depth == -1: depth = height
        self.height = height
        self.width = width
        self.depth = depth
        
        # 0 top white,
        # 1 front green
        # 2 right red
        # 3 back blue
        # 4 left orange
        # 5 bottom yellow
        
        self.colkey = {0:(255,255,255),1:(0,200,0),2:(255,0,0),3:(0,0,255),4:(255,107,0),5:(255,242,0)}
        self.n = height
        self.reset(False)
        self.animation = ['',0,False]
        self.animationlength = 15

        self.si_moves = {'R':[self.makemovemapouter([(1,'R',True,n,self.height),(0,'R',True,n,self.depth),(3,'R',False,self.width-n-1,self.height),(5,'R',True,n,self.depth)]) for n in range(self.width)],
                         'F':[self.makemovemapouter([(0,'U',False,n,self.width),(2,'R',False,self.depth-n-1,self.height),(5,'U',True,self.depth-n-1,self.width),(4,'R',True,n,self.height)]) for n in range(self.depth)],
                         'U':[self.makemovemapouter([(1,'U',True,n,self.width),(4,'U',True,n,self.depth),(3,'U',True,n,self.width),(2,'U',True,n,self.depth)]) for n in range(self.height)]}
        self.si_moves['R'][0]+=self.movemapflip(self.makemovemapinner(4))
        self.si_moves['R'][-1]+=self.makemovemapinner(2)
        self.si_moves['F'][0]+=self.movemapflip(self.makemovemapinner(3))
        self.si_moves['F'][-1]+=self.makemovemapinner(1)
        self.si_moves['U'][-1]+=self.movemapflip(self.makemovemapinner(5))
        self.si_moves['U'][0]+=self.makemovemapinner(0)

        self.movemap = {'R':self.si_moves['R'][-1],'L':self.si_moves['R'][0],
                        'F':self.si_moves['F'][-1],'B':self.si_moves['F'][0],
                        'D':self.si_moves['U'][-1],'U':self.si_moves['U'][0],
                        'M':[],'E':[],'S':[],'X':[],'Y':[],'Z':[]}

        slices = {'L':self.width,'R':self.width,'U':self.height,'D':self.height,'F':self.depth,'B':self.depth}
        
        for w in [('L','R'),('B','F'),('U','U')]:
            for n in range(1,slices[w[0]]):
                self.movemap[str(n+1)+w[0]] = self.si_moves[w[1]][n]
                self.movemap[str(n+1)+w[0]+'w'] = []
                for m in self.si_moves[w[1]][:n+1]: self.movemap[str(n+1)+w[0]+'w']+=m
        for w in [('R','R'),('F','F'),('D','U')]:
            for n in range(1,slices[w[0]]):
                nf = len(self.si_moves[w[1]])-n-1
                self.movemap[str(n+1)+w[0]] = self.si_moves[w[1]][nf]
                self.movemap[str(n+1)+w[0]+'w'] = []
                for m in self.si_moves[w[1]][nf:]: self.movemap[str(n+1)+w[0]+'w']+=m

        for a in self.movemap.keys():
            if sum([a.count(s) for s in 'LDB']):
                self.movemap[a] = self.movemapflip(self.movemap[a])
            
        for m in self.si_moves['R'][1:-1]:
            self.movemap['M']+=self.movemapflip(m)
        for m in self.si_moves['F'][1:-1]:
            self.movemap['E']+=m
        for m in self.si_moves['U'][1:-1]:
            self.movemap['S']+=m
            
        for m in self.si_moves['R']:
            self.movemap['X']+=m
        for m in self.si_moves['F']:
            self.movemap['Z']+=m
        for m in self.si_moves['U']:
            self.movemap['Y']+=m

        new = {}
        for m in self.movemap.keys():
            if 'w' in m:
                char = m[m.index('w')-1]
                new[m.replace(f'{char}w',char.lower())] = self.movemap[m]
        self.movemap.update(new)
        new = {}
        for m in self.movemap.keys():
            if m[0] == '2':
                new[m[1:]] = self.movemap[m]
        for a in new:
            if not a in self.movemap:
                self.movemap[a] = new[a]
        


##        self.movemap = {'U':self.makemovemapinner(0)+self.makemovemapouter([(1,'u',True),(4,'u',True),(3,'u',True),(2,'u',True)]),
##                        'F':self.makemovemapinner(1)+self.makemovemapouter([(0,'d',False),(2,'l',False),(5,'u',True),(4,'r',True)]),
##                        'R':self.makemovemapinner(2)+self.makemovemapouter([(1,'r',True),(0,'r',True),(3,'l',False),(5,'r',True)]),
##                        'B':self.makemovemapinner(3)+self.makemovemapouter([(0,'u',True),(4,'l',False),(5,'d',False),(2,'r',True)]),
##                        'L':self.makemovemapinner(4)+self.makemovemapouter([(1,'l',False),(5,'l',False),(3,'r',True),(0,'l',False)]),
##                        'D':self.makemovemapinner(5)+self.makemovemapouter([(1,'d',False),(2,'d',False),(3,'d',False),(4,'d',False)]),
##                        'M':self.makemovemapouter([(1,'v',False),(5,'v',False),(3,'v',True),(0,'v',False)]),
##                        'E':self.makemovemapouter([(1,'h',False),(2,'h',False),(3,'h',False),(4,'h',False)]),
##                        'S':self.makemovemapouter([(0,'h',False),(2,'v',False),(5,'h',True),(4,'v',True)])}
##        self.movemap['X'] = self.movemap['R']+self.movemapflip(self.movemap['L'])+self.movemapflip(self.movemap['M'])
##        self.movemap['Y'] = self.movemap['U']+self.movemapflip(self.movemap['E'])+self.movemapflip(self.movemap['D'])
##        self.movemap['Z'] = self.movemap['F']+self.movemap['S']+self.movemapflip(self.movemap['B'])
##        self.movemap['r'] = self.movemap['R']+self.movemapflip(self.movemap['M'])
##        self.movemap['l'] = self.movemap['L']+self.movemap['M']
##        self.movemap['u'] = self.movemap['U']+self.movemapflip(self.movemap['E'])
##        self.movemap['d'] = self.movemap['D']+self.movemap['E']
##        self.movemap['b'] = self.movemap['B']+self.movemapflip(self.movemap['S'])
##        self.movemap['f'] = self.movemap['F']+self.movemap['S']
        
        primes = {m+"'":self.movemapflip(copy.deepcopy(self.movemap[m])) for m in self.movemap}
        doubles = {m+"2":self.movemapdouble(copy.deepcopy(self.movemap[m])) for m in self.movemap}
        self.movemap.update(primes)
        self.movemap.update(doubles)

        self.decoder = [[[[-1,-1,-1,(3,0,2),(4,0,0),(0,0,0)],[-1,-1,-1,(3,0,1),-1,(0,0,1)],[-1,-1,(2,0,2),(3,0,0),-1,(0,0,2)]],
                        [[-1,-1,-1,-1,(4,0,1),(0,1,0)],[-1,-1,-1,-1,-1,(0,1,1)],[-1,-1,(2,0,1),-1,-1,(0,1,2)]],
                        [[-1,(1,0,0),-1,-1,(4,0,2),(0,2,0)],[-1,(1,0,1),-1,-1,-1,(0,2,1)],[-1,(1,0,2),(2,0,0),-1,-1,(0,2,2)]]],
                       
                       [[[-1,-1,-1,(3,1,2),(4,1,0),-1],[-1,-1,-1,(3,1,1),-1,-1],[-1,-1,(2,1,2),(3 ,1,0),-1,-1]],
                        [[-1,-1,-1,-1,(4,1,1),-1],[-1,-1,-1,-1,-1,-1],[-1,-1,(2,1,1),-1,-1,-1]],
                        [[-1,(1,1,0),-1,-1,(4,1,2),-1],[-1,(1,1,1),-1,-1,-1,-1],[-1,(1,1,2),(2,1,0),-1,-1,-1]]],
                       
                       [[[(5,2,0),-1,-1,(3,2,2),(4,2,0),-1],[(5,2,1),-1,-1,(3,2,1),-1,-1],[(5,2,2),-1,(2,2,2),(3,2,0),-1,-1]],
                        [[(5,1,0),-1,-1,-1,(4,2,1),-1],[(5,1,1),-1,-1,-1,-1,-1],[(5,1,2),-1,(2,2,1),-1,-1,-1]],
                        [[(5,0,0),(1,2,0),-1,-1,(4,2,2),-1],[(5,0,1),(1,2,1),-1,-1,-1,-1],[(5,0,2),(1,2,2),(2,2,0),-1,-1,-1]]]]
        self.decoder = [[[[-1 for a in range(6)] for x in range(self.width)] for z in range(self.depth)] for y in range(self.height)]
        self.implantdecoder(0,-1,-1,0,False,False)
        self.implantdecoder(1,-1,self.depth-1,-1,False,False)
        self.implantdecoder(2,self.width-1,-1,-1,True,False)
        self.implantdecoder(3,-1,0,-1,True,False)
        self.implantdecoder(4,0,-1,-1,False,False)
        self.implantdecoder(5,-1,-1,self.height-1,False,True)
        
            
        self.makeeffectedmap()

        simpleanglemap = {'U':(0,1,0),'F':(0,0,-1),'R':(-1,0,0),
                         'B':(0,0,1),'L':(1,0,0),'D':(0,-1,0),
                         'M':(1,0,0),'E':(0,1,0),'S':(0,0,-1),
                         'X':(-1,0,0),'Y':(0,1,0),'Z':(0,0,-1)}
        self.anglemap = {}
        for m in self.movemap.keys():
            for c in m:
                if c.upper() in simpleanglemap:
                    self.anglemap[m] = simpleanglemap[c.upper()]
                    if m[-1] == "'": self.anglemap[m] = (self.anglemap[m][0]*-1,self.anglemap[m][1]*-1,self.anglemap[m][2]*-1)
                    elif m[-1] == "2": self.anglemap[m] = (self.anglemap[m][0]*2,self.anglemap[m][1]*2,self.anglemap[m][2]*2)
                    break
        
##        primes = {m+"'":(self.anglemap[m][0]*-1,self.anglemap[m][1]*-1,self.anglemap[m][2]*-1) for m in self.anglemap}
##        self.anglemap.update({m+"2":(self.anglemap[m][0]*2,self.anglemap[m][1]*2,self.anglemap[m][2]*2) for m in self.anglemap})
##        self.anglemap.update(primes)
        
        self.renderer = Render_3D()
        self.resetcamera()
        self.genmesh()
        
    def reset(self,update=True):
        self.cube = {s:[[s for x in range(self.n)] for y in range(self.n)] for s in range(6)}
        self.undo = []
        if update:
            self.resetcamera()
            self.genmesh()
    def resetcamera(self):
        self.renderer.camera = [-80,80,-200,0,0,math.pi]
        
### Move map functions ###                    
    def makemovemapinner(self,face):
        base = [[(face,y,x) for x in range(self.n)] for y in range(self.n)]
        reverse = [[(face,y,self.n-x-1) for x in range(self.n)] for y in range(self.n)]
        rotated = [[reverse[x][y] for x in range(len(reverse[y]))] for y in range(len(reverse))]

        loops = []
        marked = []
        for y in range(len(rotated)):
            for x in range(len(rotated)):
                moving = rotated[y][x]
                if not(y == moving[1] and x == moving[2]):
                    loops.append([])
                    while not (moving in marked):
                        marked.append(moving)
                        loops[-1].append(moving)
                        moving = rotated[moving[1]][moving[2]]
                    if loops[-1] == []: del loops[-1]
                else:
                    loops.append([moving,moving])
        return loops
##        return [[(face,0,0),(face,0,2),(face,2,2),(face,2,0)],[(face,0,1),(face,1,2),(face,2,1),(face,1,0)],[(face,1,1),(face,1,1)]]
    
    def makemovemapouter(self,sides):
        info = []
        for s in sides:
            if s[1] == 'R': new = [(s[0],n,s[3]) for n in range(s[4])]
            elif s[1] == 'U': new = [(s[0],s[3],n) for n in range(s[4])]
            
            elif s[1] == 'r': new=[(s[0],0,2),(s[0],1,2),(s[0],2,2)]
            elif s[1] == 'l': new=[(s[0],0,0),(s[0],1,0),(s[0],2,0)]
            elif s[1] == 'u': new=[(s[0],0,0),(s[0],0,1),(s[0],0,2)]
            elif s[1] == 'd': new=[(s[0],2,0),(s[0],2,1),(s[0],2,2)]
            elif s[1] == 'v': new=[(s[0],0,1),(s[0],1,1),(s[0],2,1)]
            elif s[1] == 'h': new=[(s[0],1,0),(s[0],1,1),(s[0],1,2)]
            if s[2]:
                new.reverse()
            info+=new
        n = int(len(info)/len(sides))
        finals = [[] for a in range(n)]
        for s in range(n):
            for b in range(4):
                finals[s].append(info[b*n+s])  
        return finals
    def movemapflip(self,moves):
        c = copy.deepcopy(moves)
        for a in c:
            a.reverse()
        return c
    def movemapdouble(self,moves):
        nmoves = []
        for b in moves:
            nmoves.append([a for i,a in enumerate(b) if i%2==0])
            nmoves.append([a for i,a in enumerate(b) if i%2==1])
        return nmoves
    def implantdecoder(self,face,xmov,zmov,ymov,flipx,flipy):
        if face in [0,5]: area,mod = self.depth*self.width,self.width
        elif face in [1,3]: area,mod = self.height*self.width,self.width
        elif face in [2,4]: area,mod = self.depth*self.height,self.depth
        data = [[face,n//mod,n%mod] for n in range(area)]
        for a in data:
            if flipy: a[1] = mod-a[1]-1
            if flipx: a[2] = mod-a[2]-1

        if xmov == -1: xr = range(0,self.width)
        else: xr = range(xmov,xmov+1)
        if ymov == -1: yr = range(0,self.height)
        else: yr = range(ymov,ymov+1)
        if zmov == -1: zr = range(0,self.depth)
        else: zr = range(zmov,zmov+1)
        index = 0

        for y in yr:
            for z in zr:
                for x in xr:
                    f = data[index][0]
                    if f == 0: f = 5
                    elif f == 5: f = 0
                    self.decoder[y][z][x][f] = data[index]
                    index+=1
        
        
    ## generate
    def makeeffectedmap(self):
        self.effectmap = []
        for y in range(len(self.decoder)):
            self.effectmap.append([])
            for z in range(len(self.decoder[y])):
                self.effectmap[-1].append([])
                for x in range(len(self.decoder[y][z])):
                    self.effectmap[-1][-1].append([])
                    for m in self.movemap:
                        sides = []
                        for s in self.movemap[m]: sides+=s
                        for d in self.decoder[y][z][x]:
                            if d!=-1 and tuple(d) in sides:
                                self.effectmap[y][z][x].append(m)
                                break
                            

### Moving cube functions ###
    def move(self,move,update=True):
        if not self.animation[2]: self.undo.append(move)
        for cycle in self.movemap[move]:
            storeprev = self.getat(cycle[-1])
            for loc in cycle:
                store = self.getat(loc)
                self.setat(loc,storeprev)
                storeprev = store
        if update:
            self.genmesh()
    def slowmove(self,move,undo=False):
        if self.animation[1]<1 and self.animation[0]!='':
            self.move(self.animation[0])
        self.animation = [move,0,undo]
    def undomove(self):
        if len(self.undo)>0:
            move = self.undo.pop(-1)
            if len(move) == 1: move = move+"'"
            elif move[1] == "'": move = move[0]
            self.slowmove(move,True)
    def animate(self):
        if self.animation[0] != '':
            if self.animation[0][-1] == '2': self.animation[1]+=ui.deltatime/self.animationlength/2
            else: self.animation[1]+=ui.deltatime/self.animationlength
            if self.animation[1]>1:
                self.move(self.animation[0],self.animation[2])
                self.animation = ['',0,False]
            self.genmesh()
    
    def getat(self,location):
        return self.cube[location[0]][location[1]][location[2]]
    def setat(self,location,value):
        self.cube[location[0]][location[1]][location[2]] = value
    def scramble(self):
        scram = self.makescramble()
        st = ''
        for a in scram:
            st+=a+' '
            self.move(a,False)
        ui.IDs['scramble text'].settext(st)
        self.resetcamera()
        self.genmesh()
        self.undo = []

    def makescramble(self):
        lengthkey = [0,0,11,20,45,60,80,100]
        length = lengthkey[self.n]
        self.reset(False)
        if self.n == 2: basics = ['R','U','F']
        else: basics = ['R','L','U','F','D','B']
        moves = [a for a in self.movemap if a[0] in basics]
        trim = []
        if self.n == 4: trim = ['Dw','Lw','Bw']
        elif self.n == 6: trim = ['3Dw','3Lw','3Bw']
        torem = []
        for a in moves:
            for t in trim:
                if t in a:
                    torem.append(a)
        for a in torem:
            moves.remove(a)
        
        scramble = []
        for a in range(length):
            move = random.choice(moves)
            while move[0] in [m[0] for m in scramble[len(scramble)-2:]]:
                move = random.choice(moves)
            scramble.append(move)
        return scramble
    
    def output(self):
        for s in self.cube:
            print(f'-- {s} --')
            for y in self.cube[s]:
                for x in y:
                    print(x,end='')
                print()
    def inputkey(self):
        key = ui.IDs['cube input'].text
        if key in self.movemap:
            self.slowmove(key)
            ui.IDs['cube input'].settext()
##        elif len(key)>0:
##            if key[0] in self.movemap:
##                self.slowmove(key[0])
##                ui.IDs['cube input'].settext(key[1])
##            elif len(key)>1 and key[1] in self.movemap:
##                self.slowmove(key[1])
##                ui.IDs['cube input'].settext(key[0])
            
### Rendering Functions ###
    def genmesh(self,posx=0,posy=0,posz=0):
        sides = 40*3/max([self.width,self.height,self.depth])*(ui.dirscale[1]**0.6)
        border = 0
        if self.n<=4: border = -1
        self.renderer.mesh = []
        
        cols = [self.colkey[5],self.colkey[1],self.colkey[2],self.colkey[3],self.colkey[4],self.colkey[0]]

        drawbackkey = {0:[2,4],1:[0,5],2:[1,3]}
        if self.animation[0]!='':
            angleffect = self.anglemap[self.animation[0]]
        else: angleffect = (0,0,0)
        for y in range(len(self.decoder)):
            for z in range(len(self.decoder[y])):
                for x in range(len(self.decoder[y][z])):
                    cols = []
                    for a in self.decoder[y][z][x]:
                        if a == -1:
                            cols.append(-1)
                        else:
                            cols.append(self.colkey[self.getat(a)])
                    angles = (0,0,0)
                    if self.animation[0] in self.effectmap[y][z][x]:
                        angles = self.anglemap[self.animation[0]]
                    for a in range(3):
                        if angleffect[a]!=0:
                            if cols[drawbackkey[a][0]] == -1: cols[drawbackkey[a][0]] = (0,0,0)
                            if cols[drawbackkey[a][1]] == -1: cols[drawbackkey[a][1]] = (0,0,0)
                    self.renderer.makecube(posx-(x-(self.width-1)/2)*sides,posy-(y-(self.height-1)/2)*sides,posz-(z-(self.depth-1)/2)*sides,sides,[angles[0]*self.animation[1]*math.pi/2,angles[1]*self.animation[1]*math.pi/2,angles[2]*self.animation[1]*math.pi/2],cols,border)
        self.renderer.refreshdisplay()
                    
    def update(self,screen):
        self.animate()
        self.renderer.cubecameracontroller()
        self.renderer.drawmesh(screen)

    
cube = Cube()
ui.makebutton(10,10,'Scramble',40,cube.scramble)
ui.makebutton(10,55,'Reset',40,cube.reset)
ui.makebutton(10,100,'Center',40,cube.resetcamera)
ui.maketext(155,15,'',30,ID='scramble text',maxwidth=700)
ui.maketextbox(10,145,'',70,1,textsize=40,verticalspacing=4,command=cube.inputkey,ID='cube input',chrlimit=4)
ui.makebutton(10,195,'Undo',40,cube.undomove)


while not done:
    for event in ui.loadtickdata():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.VIDEORESIZE:
            cube.renderer.refreshdisplay()
            cube.genmesh()
    
    screen.fill(pyui.Style.wallpapercol)
    cube.update(screen)

    
    ui.rendergui(screen)
    ui.write(screen,20,ui.screenh-15,str(int(clock.get_fps())),30)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 











