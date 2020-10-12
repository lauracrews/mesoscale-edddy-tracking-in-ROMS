#Defines the patch class. 
#Allows patch objects to be made 
#Most important function is patch.update, which updates a patch's characteristics when it is matched with a newer patch

import numpy as np
import os
import cv2
import math

#############
#Constants
TIMESTEP = 1 #Time in days elapsed between each images. Used in vortex velocity calculations

###############
#Function definitions
def to_bool(s):
    return 1 if s == 'true' else 0

#################
#Class definition
class patch:
	 def __init__(self, contour, currentDay): #Needs a contour to create a patch object
	 
	 	M = cv2.moments(contour)
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])
		center = (cx, cy)
	 	area = cv2.contourArea(contour)
	 	circCenter, radius = cv2.minEnclosingCircle(contour)
	 	
	 	#Sets characteristics
	 	self.contour = contour
	 	self.x = cx
	 	self.y = cy
	 	self.center = center
	 	self.area = area
	 	self.radius = radius
	 	self.points = []
	 	
	 	self.active = 'false'
	 	self.new = 'true'
	 	self.tracked = 'false'
	 	
	 	self.matches = []
	 	
	 	self.activeDays = [currentDay]
	 	
	 	self.contourArchive = [contour]
	 	self.centerArchive = [center]
	 	self.areaArchive = [area]
	 	self.velocityArchive = [0] #Setting first value to 0 means that it has not moved from its initial position. Ensures len(velocityArcive) = patch lifespan
	 	
################# Functions to assign and return information about the patch 		 
	 def getContour(self):
	 	return self.contour
	 	
	 def getX(self):
	 	return self.x 	
	 	
	 def getY(self):
	 	return self.y
	 		 
	 def getCenter(self):
	 	return self.center
	 	
	 def getArea(self):
	 	return self.area
	 	
	 def getRadius(self):
	 	return self.radius
	 	
	 def getActiveDays(self):
	 	return self.activeDays
	 	
	 def getLifespan(self):
	 	allDays = self.getActiveDays()	 	
	 	return allDays[-1] - allDays[0] + 1 
	 
	 def getContourArchive(self):
	 	return self.contourArchive
	 	
	 def getAreaArchive(self):
	 	return self.areaArchive
	 
	 def getCenterArchive(self):
	 	return self.centerArchive
	 	
	 def getVelocityArchive(self):
	 	return self.velocityArchive
	 
	 def isActive(self):
	 	return to_bool(self.active)
	 	
	 def isNew(self):
	 	return to_bool(self.new)
	 		 
	 def getMatches(self):
	 	return self.matches
	 
	 def activate(self):
	 	self.active = 'true'
	 	
	 def deactivate(self):
	 	self.active = 'false'
	 
	 def notNew(self):
	 	self.new = 'false'
	 	
	 def addMatch(self, match):
	 	self.matches.append(match)
	 	
	 def clearMatches(self):
	 	self.matches = []
	 	
################ Most important function - updates patch with new information 
	 def update(self, updatedPatch, currentDay):
	 	oldx = self.getX()
	 	oldy = self.getY()
	 	
	 	self.contour = updatedPatch.getContour()
	 	self.contourArchive.append(updatedPatch.getContour())
		
		self.activeDays.append(currentDay)
		
	 	self.radius = updatedPatch.getRadius() 
	 	
	 	self.area = updatedPatch.getArea()
	 	self.areaArchive.append(updatedPatch.getArea())

		self.x = updatedPatch.getX()
		self.y = updatedPatch.getY()

		self.center = (self.getX(), self.getY())
		self.centerArchive.append(self.getCenter())
	 		 	
	 	self.velocityArchive.append(math.hypot(oldx - self.getX(), oldy - self.getY()) / TIMESTEP) 
############### end update function