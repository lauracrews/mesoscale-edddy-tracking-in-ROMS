import numpy as np
import os
import cv2
import math
import pickle
from patchClass import patch #This is another script I sent you defining what a patch object is

#############
#Constants

#This should match TIMESTEP in the patch class definition script! It corresponds to the number of 
#days elapsed between images, to be used in calculating patch velocity
TIMESTEP = 1 

#Filter contours by radius or area
MIN_AREA = 20
MAX_RADIUS = 40

#### Parameters used for tracking ####
#These should all be Order 100. Otherwise the calculated 'match goodness' between patches would need to be treated as a double (currently treated as an int, 'match goodness' values of Order 1 can be rounded to the same int so tracking doesn't work)
#Distance a patch can move between frames as a percent of its radius
MAX_TRAVEL = 400

#Importance given to movement when ranking matches
MOVE_WEIGHT = 100 

#Percent change in patch area permitted between frames
MAX_SIZECHANGE = 300

#Importance given to size change when ranking matches
SIZE_WEIGHT = 100 

############
#Directories
baseDirectory = '/where code is'
inputDataDirectory = '/where patch grid files are'
imageDirectory = '/if patch grid have been converted to images - not initially the case' #more about this below

#################
#Functions called (main execution script below)

#Converts true/false strings to boolean
def to_bool(s):
    return 1 if s == 'true' else 0
    
#Loads patch grid from a CSV. 
#This step is not necessary if using already processed image files (see data structures section, below)
#Erosion/dilation smoothes rough edges. If kernel size is consistent, shouldn't change patch area
#Can adjust erode/dilate kernel size here (larger size - more 'blurred' edges). 
def loadImage(file):
	os.chdir(inputDataDirectory)	
	#imports patch grid files with true/false as 1/0
	img = np.genfromtxt(file, dtype=np.uint8, delimiter=',')
	
	#Rescale the image color to the 0-255 color scale so that we can plot it. 
	img[img!=0] = 127

	#Erosion and dilation operations to clean up breaks within patches
	kernel = np.ones((2,2),np.uint8)
	img = cv2.dilate(img,kernel,iterations = 1)
	img = cv2.erode(img,kernel,iterations = 1)

	return img

#This can be used to show all patches identified in an image
#Use to check that patch identification is working correctly
def showAllPatches(patches, img):
	patchToShow = [p.getContour() for p in patches]
	img[img!=0] = 127
	cv2.drawContours(img, patchToShow, -1, (255), -1)
	cv2.imshow('All Patches',img)
	cv2.waitKey(0) #Close when you press a keyboard key

#Add a patch to the array of patches active in the current frame. 
#Only called when a patch is observed for the first time
def add2Active(p):
	p.activate()
	activePatches.append(p)

#Once a match has been found for a patch from the previous frame, we need to update
#it with information from its match	
def updatePatch(old, new, currentDay):

	#Because the previous frame's patch has a match in the current frame, it remains active
	old.activate()  
	
	#Will update the previous frame's patch with information from its match in the current frame
	#Brings the patch 'up to date' with the current frame
	old.update(new, currentDay) 

	#Now that the patch in the new frame has been matched with a patch from the previous
	#frame, it is not available to match with any other patches from the previous frame
	new.notNew()  

#Returns a metric of how well two patches 'match', indicating whether one might represent the evolution of the other
def measureMatch(patch1, patch2):
	
	#matchWeight is equal to move weight * distance moved + size weight * percent change in size
	matchWeight = MOVE_WEIGHT * (math.sqrt((patch1.getX() - patch2.getX())**2 + (patch1.getY() - patch2.getY())**2)/patch1.getRadius()) + SIZE_WEIGHT * abs((patch1.getArea() - patch2.getArea())/patch2.getArea())	 	
	return int(matchWeight)

#Determines if a patch from the previous frame is the best match for a patch in the current frame 
#activePatch is the patch from the previous frame
#bestMatch is the patch from the current frame
def checkIfBest(activePatch, bestMatch): 			

	matchBaseline = measureMatch(activePatch, bestMatch) 	
	competitors = bestMatch.getMatches() #The other patches from the previous frame that also match with the patch in the new frame	
	isBest = 'true' #Default: it is the best match. Check if another patch is a better match. 
	for otherPatch in competitors:
		if measureMatch(otherPatch, bestMatch) < matchBaseline:
			isBest = 'false'
			break	
	return to_bool(isBest)

#Moves an active patch to the archive
def archive(p):
	archivedPatches.append(p)
	activePatches.remove(p)

#####################
#Main execution script

#All patches that were active in the previous frame 
activePatches = []

#All patches that are no longer active. 
archivedPatches = []

#Use this if eddy grid files have not yet been processed by loadImage() (function defined above)
#Once these have been loaded, can be saved as a python list (end of main script, below) to be read more quickly later
#Slow - only needed if images haven't previously been saved
imgs = []
os.chdir(inputDataDirectory)
for data_file in sorted(os.listdir(inputDataDirectory)):
	if not data_file.startswith('.'): #indicative of a hidden file - check printed-out file names to make sure no hidden files are being processed
		print "Current File Being Processed is: " + data_file
		img = loadImage(data_file)
		imgs.append(img)

#Save all processed eddy grids as a python list that can be loaded later
os.chdir(baseDirectory) 
saveName = 'Patch Grids'
fileObject = open(saveName, 'wb')
pickle.dump(imgs, fileObject)
fileObject.close()

#If eddy grids have been processed and saved (above), load them here
#os.chdir(baseDirectory)
#fileObject = open('Patch Grids','r')
#imgs = pickle.load(fileObject)

for fileNumber, img in enumerate(imgs):

	print fileNumber #Just to monitor progress through the data processing. 
	
	#Adjusted to currentDay = fileNumber + 1 to fix indexing errors between 0-indexed python and 1-indexed matlab
	#Similarly, this should be adjusted if the first file doesn't correspond to Day 1 (e.g. if first file is Day 3, adjust to currentDay = fileNumber + 4)
	#The accuracy of indexing can be checked by plotting the eddy grid and eddy masks after eddy identification is complete (part of patchData.m)
	currentDay = fileNumber + 1
	
	#Find all contours in the current frame
	_, contours, _  = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	#Filter all contours for the correct size range
	smallCont = []
	for c in contours: 
		center, radius = cv2.minEnclosingCircle(c)		
		if radius < MAX_RADIUS and cv2.contourArea(c) > 0:
			smallCont.append(c)				

	#Creates patch objects from contours						
	patches = [patch(c, currentDay) for c in smallCont]			
	print len(patches), 'patches identified in this frame'
	#showAllPatches(patches, img) #Can use this to show all patches in the image
	
	#Will be called only for the first frame, before any patches are active
	#Adds all patches in the first frame to the list of active patches
	#This step is necessary to create a pool of patches to compare patches in the subsequent frames against
	if not len(activePatches):
		for p in patches:
			add2Active(p)
			p.notNew() #This ensures it won't mistakenly be double-added later
	
	#If not the first frame, then there are already patches from the previous frame 
	else:
		
		#Deactivates all activePatches. At this point, activePatches were active in the previous frame.
		#We will now see if these previous frame patches have matches in the current frame.
		#If so, they will be re-activated at will survive to the next frame
		#If not, they will remain deactivated at the end of this loop iteration and will be archived
		for ap in activePatches:
			ap.deactivate()
			ap.clearMatches()
		
		#Iterate through all patches identified in the previous frame. 
		#Determine if any of the patches in the current frame are a plausible match
		for ap in activePatches:			
			for p in patches:
				#Checks that the distance traveled from the previous frame and the percent change in patch area from the previous frame do not exceed thresholds 
				if 100 * (math.sqrt((p.getX() - ap.getX())**2 + (p.getY() - ap.getY())**2) / ap.getRadius())  < MAX_TRAVEL and 100 * abs((p.getArea() - ap.getArea())/ap.getArea()) < MAX_SIZECHANGE:
					#The two are a potential match
					p.addMatch(ap)
					ap.addMatch(p)	
		
		#Iterate through all patches identified in the previous frame. 
		#We determined all possible matches in the previous step
		#Now we must determine which match is best
		#This match finding must not advantage patches coming earlier in the list
		for ap in activePatches:
			
			#List of all the current frame's patches that match with a patch from the previous frame
			matches = ap.getMatches() 
			
			#If no match found (len(matches) == 0), the patch from the previous frame
			#has no plausible matches in the current frame. It stays marked as deactivated 
			#and will be archived.
			if len(matches) == 0: continue
			
			#Only one potential match among the current frame's patches. 
			#That potential match also only has one match. 
			#We have identified a unique pair. 
			#ap is the patch from the previous frame, matches[0] is the patch in the current frame.  
			elif len(matches) == 1 and len(matches[0].getMatches()) == 1: 				
				updatePatch(ap, matches[0], currentDay)
					
			#Another patch from the previous frame also matches with the only potential match in the current frame 
			#We must determine which patch from the previous frame is a better match for the patch in the current frame
			#ap is the patch from the previous frame, matches[0] is the patch in the current frame.  
			elif len(matches) == 1 and len(matches[0].getMatches()) > 1:
												
				#In checkIfBest() is true, the patch from the previous frame will compete against 
				#other potentially matching patch from the previous frame to see 
				#if it is the best possible match for the new patch							
				#ap is the patch from the previous frame, matches[0] is the patch in the current frame.  
				if checkIfBest(ap, matches[0]):
					updatePatch(ap, matches[0], currentDay)					
					
			#The patch from the previous frame has multiple potential matches in the current frame.
			#We must determine which of these potential matches is best. 
			#Once the best match has been found, we must see if that match is actually better matched to a different patch in the previous frame. 
			#If it is, we will check the next-best match, and so on. 
			elif len(matches) > 1:
				
				#Creates array of match measurements for each potential match in the current frame
				matchGoodness = [measureMatch(ap, m) for m in matches]
				
				#This loop will determine which of the potential matches the previous frame the patch should be paired with
				noMatch = 'false'
				bestMatch = []
				while(1):					
					#This arises if none of the potential matches prove suitable because they are already matched
					#to a different patch from the previous frame					
					if len(matchGoodness) == 0:
						noMatch = 'true'
						break
					
					#Chooses the best match in the current frame					
					bestScore = min(matchGoodness)
					minIndex = matchGoodness.index(bestScore)
					bestMatch = matches[minIndex]
				
					#Patch from the previous frame will compete with other patch from the previous frame to keep its match in the current frame
					#bestMatch.isNew() will be false if the best match has already been paired up with a different patch from the previous frame
					isBest = 'false'					
					if bestMatch.isNew():
						#If bestMatch.getMatches()) == 1, there are no other patches from the 
						#previous frame that could match with the bestMatch patch, so the 
						#patch from the previous frame that we are presently interested in wins by default 			
						if len(bestMatch.getMatches()) == 1 or checkIfBest(ap, bestMatch):
							isBest = 'true'					
					if to_bool(isBest): break
						
					#The patch from the previous frame lost the competition for the match. 
					#We'll remove that match and try the next-best match									
					matches.remove(bestMatch)
					matchGoodness.remove(bestScore)
				
				if not to_bool(noMatch): #Once the best match has been identified
					updatePatch(ap, bestMatch, currentDay)

	#Remove any previously active patches that are no longer active
	#Want to work backward through loop to remove patches from the end of the array
	for ap in reversed(activePatches):
		if not ap.isActive():
			archive(ap)

	#If any patches in the current frame were not matched up with a patch from the previous
	#frame, they have just formed in this frame. We will add them to the list of active patches
	for p in patches:
		if p.isNew() and p.getArea() > MIN_AREA:
			add2Active(p)
							
	os.chdir(inputDataDirectory)

#Archive all patches still active at the end of the run
for ap in reversed(activePatches):
	archive(ap)

#Save all patches as a python list that can be loaded later. List will be used by save_patches.py
os.chdir(baseDirectory) 
saveName = 'Patches'
fileObject = open(saveName, 'wb')
pickle.dump(archivedPatches, fileObject)
fileObject.close()	