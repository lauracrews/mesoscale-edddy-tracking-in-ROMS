%Creates a mask of all patches active on a particular day
% Patches = matlab structure with data about all patches
% Day = the day we would like to make a patch mask for 
% sz = used for sizing mask

function allPatches = patchesActiveToday(patches, day, sz)
    
    allPatches = zeros(sz); % Initially empty mask   
    for patch = 1:length(patches) % Iterates through all patches to check if they are active on the day       
        allDays = patches(patch).day;
        for obsNum = 1:length(allDays)
            if allDays(obsNum) == day %If a patch is active on the day, its mask is included in the allPatches mask
                allPatches(cell2mat(patches(patch).patchMask(obsNum)) == 1) = 1; 
            end
        end
    end
    
end
                
        
        


