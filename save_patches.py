import numpy as np
import os, sys
import cv2
import csv
import pickle
from patchClass import patch

#Locations of data sets to be loaded
baseDirectory = '/where python list of patches made by patch_identification.py is stored'
saveDirectory_summaries = '/where to save the summary file for each patch'
saveDirectory_masks = '/where to save the mask files for each patch'

#Load data created by patch_identification.py
os.chdir(baseDirectory)
fileObject = open('Patches', 'r')
patches = pickle.load(fileObject)

#Constants
MIN_LIFESPAN = 10 #Minimum number of days 
DOMAIN_DIMENSIONS = (1301, 1151) #This should be updated to reflect the size of the model domain 

save_number = 1; #Used to number each patch when its data is saved
for currentPatch in patches:
	 
	if (currentPatch.getLifespan() >= MIN_LIFESPAN):
		
		os.chdir(saveDirectory_summaries)
		with open('patch' + str(save_number)  + '_summary.csv', 'w') as csvfile:
   			patchwriter = csv.writer(csvfile)
			currentPatch_data = []
			
			#Data archives for each patch
			activeDays = currentPatch.getActiveDays()
			centerArchive = currentPatch.getCenterArchive()
			areaArchive = currentPatch.getAreaArchive()	
			velocityArchive = currentPatch.getVelocityArchive()	
			contourArchive = currentPatch.getContourArchive() #Used to determine which points are in the patch	
		
			#Iterates through all days the patch was active
			#Extracts and saves the data for the patch on each day
			daysOffEdge = 0 
			for dayNum, contour in enumerate(contourArchive):
				day = activeDays[dayNum]
				center = centerArchive[dayNum]
				area = areaArchive[dayNum]
				velocity = velocityArchive[dayNum]	
				
				#Finds which cells were within the patch, saves a mask for for each day
				#Will not use patches that are on the model edge - some of their data may be outside the domain
				#Note - this step is very slow and likely could be more efficient!
				mask = np.zeros(DOMAIN_DIMENSIONS)
				pts = []
				onEdge = 0
				for coordinate, pixel in np.ndenumerate(mask):
					if cv2.pointPolygonTest(contour, coordinate, 0) >= 0: #Point is within the patch
						if (coordinate[0] == 0) or (coordinate[1] == 0) or (coordinate[0] == DOMAIN_DIMENSIONS[0]) or (coordinate[1] == DOMAIN_DIMENSIONS[1]):
							onEdge = 1 #Patch is on the edge of model domain - don't use it
							break
						else:
							pts.append([coordinate[1], coordinate[0]]) 				
				
				if not onEdge: #Patch is wholly within the model domain - save its data
					daysOffEdge = daysOffEdge + 1
					currentPatch_data.append([day, center[1], center[0], area, velocity]) #Note center saved as (y,x) to align with matlab indexing
					os.chdir(saveDirectory_masks)
					np.savetxt('patch' + str(save_number) + '_day' + str(day) + '_mask.csv', pts, delimiter=",")
			
			#Saves data for all the days the patch was active. Check that the number of days the patch is wholly within the model domain exceeds the minimum number of days
			if daysOffEdge >= MIN_LIFESPAN:
				patchwriter.writerows(currentPatch_data)												
				save_number = save_number + 1		