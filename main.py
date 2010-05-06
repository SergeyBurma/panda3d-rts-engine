
import direct.directbase.DirectStart
from CameraHandler import CameraHandler
from direct.task import Task 
from direct.actor import Actor
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject


import math 


class RTSEngine(DirectObject):
    
    def __init__(self):
        self.camHandler = None
        self.environ = None
        self.isMoving = False
        self.trav = CollisionTraverser()
        self.cHandler = CollisionHandlerQueue()
        self.picked = None
        self.selected = None
        
        self.setupMouseCollision()

        self.setupEnvironment()
        self.setupCamera()
        self.setupActors()
        self.setupLighting()
        
        self.accept("mouse1",self.selectObject) 

        taskMgr.add(self.handleCursor,"HandleMouse")
        
        
   
   
   
    def run(self):
        run()
  
    
    def setupMouseCollision(self):
        pickerNode = CollisionNode('mouseRay')
        pickerNP = camera.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        pickerNode.addSolid(self.pickerRay)
        self.trav.addCollider(pickerNP ,self.cHandler)
        
    def setupCamera(self):
        self.camHandler = CameraHandler()
        self.camHandler.setTarget(self.environ.getX(),self.environ.getY(),self.environ.getZ())
        
    def setupActors(self):
        # Create the main character, Ralph
        ralphStartPos = self.environ.find("**/start_point").getPos()
        self.ralph = Actor.Actor("models/ralph",{"run":"models/ralph-run","walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(.2)
        self.ralph.setPos(1,1,1)
        self.ralph.setTag("pickable","1")
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.setPos(self.ralph.getPos())
        self.floater.reparentTo(render)
        
        
        
        
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
        
        
    def setupEnvironment(self):
        self.environ = loader.loadModel("models/world") 
        self.environ.reparentTo(render)
        self.environ.setScale(0.25,0.25,0.25) 
        self.environ.setPos(0,0,0)
        
    def selectObject(self):
        if(base.mouseWatcherNode.hasMouse()):
            mpos = mpos = base.mouseWatcherNode.getMouse()
            if not (self.picked == None):
                if (self.selected == None):
                    return
                self.selected =  self.picked
                return
            else:
                z = self.environ.getZ(mpos.getPos())
                self.floater.setPos(mpos.getX(),mpos.getY())
                
                
        
    def handleCursor(self,task):
        if(self.isMoving):
            self.ralph.loop("run")
        if base.mouseWatcherNode.hasMouse(): 
            # We're going to use the mouse, so we have to make sure it's in the game window. If it's not and we try to use it, we'll get 
            # a crash error. 
            mpos = base.mouseWatcherNode.getMouse()
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