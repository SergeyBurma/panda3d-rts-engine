
import direct.directbase.DirectStart
from CameraHandler import CameraHandler
from direct.task import Task 
from direct.actor import Actor
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject


import math 


class RTSEngine(DirectObject):
    
    def __init__(self):
        from pandac.PandaModules import loadPrcFileData
        loadPrcFileData("", "want-directtools #t")
        loadPrcFileData("", "want-tk #t")
        self.camHandler = None
        self.environ = None
        self.isMoving = False
        self.trav = CollisionTraverser()
        self.cHandler = CollisionHandlerQueue()
        self.picked = None
        self.selected = None
        

        self.setupEnvironment()
        self.setupCamera()
        self.setupActors()
        self.setupLighting()
        self.setupMouseCollision()
        self.accept("mouse1",self.selectObject) 
        taskMgr.add(self.handleCursor,"HandleMouse")
        taskMgr.add(self.handleRalphCollision,"HandleRalphCollision")
        
        
   
   
   
    def run(self):
        run()
  
    

    def setupMouseCollision(self):
        
        
        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.trav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)
 
        
        
        pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        pickerNode.addSolid(self.pickerRay)
        self.trav.addCollider(self.pickerNP ,self.cHandler)
        self.trav.showCollisions(render)
        z=0
        self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, z)) 

        
    def setupCamera(self):
        self.camHandler = CameraHandler()
        self.camHandler.setTarget(self.environ.getX(),self.environ.getY(),self.environ.getZ())
        
    def setupActors(self):
        # Create the main character, Ralph
        ralphStartPos = self.environ.find("**/start_point").getPos()
        self.ralph = Actor.Actor("/home/focus/svn/panda3d-rts-engine/models/ralph",{"run":"models/ralph-run","walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(.2)
        self.ralph.setPos(1,1,1)
        self.ralph.setTag("pickable","1")
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.setPos(self.ralph.getPos())
        self.floater.reparentTo(render)
        
        self.pointer = loader.loadModel("/home/focus/svn/panda3d-rts-engine/models/box")
        self.pointer.setPos(5,5,1)
        self.pointer.setColor(1,0,0)
        self.pointer.setScale(.5)
        self.pointer.reparentTo(render)
        
        
        cmfg = CardMaker('fg') 
        cmfg.setFrame(0, 1, -1, 0) 
        self.bar = render2d.attachNewNode(cmfg.generate())
        self.bar.setColor(0,1,0,.5)
        self.bar.setTransparency(1)
        

        
    
        
        
        
        
    def setupLighting(self):
        #Setup the lighting and the shader to make it look cartoony
        plightnode = PointLight("point light")
        plightnode.setAttenuation(Vec3(1,0,0))
        plight = render.attachNewNode(plightnode)
        plight.setPos(30,-50,0)
        alightnode = AmbientLight("ambient light")
        alightnode.setColor(Vec4(0.8,0.8,0.8,1))
        alight = render.attachNewNode(alightnode)
        render.setLight(alight)
        render.setLight(plight)
        self.lastMousePos = None
        
        alight = AmbientLight("alight")
        alight.setColor(VBase4(0.5,0.5,0.5,0.5))
        self.alnp = self.ralph.attachNewNode(alight)
        
        self.floater.attachNewNode(alight)
        self.floater.setLight(self.alnp)
        
        
        
    def setupEnvironment(self):
        self.environ = loader.loadModel("/home/focus/svn/panda3d-rts-engine/models/world") 
        self.environ.reparentTo(render)
        self.environ.setScale(0.25,0.25,0.25) 
        self.environ.setPos(0,0,0)
        
    def mover(self):
        return
        
        
    def selectObject(self):
        if(base.mouseWatcherNode.hasMouse()):
            
            if(selected == None):
                return
            
            mpos = base.mouseWatcherNode.getMouse() 
            pos3d = Point3() 
            nearPoint = Point3() 
            farPoint = Point3() 
            base.camLens.extrude(mpos, nearPoint, farPoint) 
            if self.plane.intersectsLine(pos3d, 
                render.getRelativePoint(camera, nearPoint), 
                render.getRelativePoint(camera, farPoint)):
                self.floater.setPos(render, pos3d.getX(),pos3d.getY(),self.pickerNP.getZ())
            
        
        
    def handleRalphCollision(self,task):
        
        entries = []
        for i in range(self.ralphGroundHandler.getNumEntries()):
            entry = self.ralphGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.ralph.setPos(startpos)

        return task.cont
    
                            
                
                
    def handleCursor(self,task):
        if base.mouseWatcherNode.hasMouse(): 
            # We're going to use the mouse, so we have to make sure it's in the game window. If it's not and we try to use it, we'll get 
            # a crash error. 
            mpos = base.mouseWatcherNode.getMouse()
            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()
            self.pickerRay.setFromLens(base.camNode,mpos.getX(),mpos.getY())
            self.trav.traverse(render)
            
            if(self.cHandler.getNumEntries > 0):
                self.cHandler.sortEntries()
                try:
                    picked = self.cHandler.getEntry(0).getIntoNodePath()
                    picked = picked.findNetTag("pickable")
                    if not picked.isEmpty():
                        picked.setLight(self.alnp)
                        self.picked = picked
                    else:
                        if not (self.picked == None):
                            self.picked.clearLight(self.alnp)
                            self.picked= None
                    

                except:
                    pass
                

                
        return task.cont


        



if __name__ == "__main__":
    
    rts = RTSEngine()
    rts.run()