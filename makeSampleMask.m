% Makes a mask to sample a random subset of points within a patch

% patchMask is a mask (dimensions = model domain dimensions) of points within the patch
% numCells is the number of cells in the patch
% percentToSample is the number of cells to sample as a percent of all cells in the patch
% minNumCells is the minimum number of cells to sample. Will be used if numCells * percentToSample < minNumCells

function sampleMask = makeSampleMask(patchMask, numCells, percentToSample, minNumCells)

    if numCells * percentToSample < minNumCells 
        numSamplePoints = minNumCells;
    else
        numSamplePoints = numCells * percentToSample;
    end
    randomPoints = randi([1 numCells],floor(numSamplePoints), 1);
    
    sz = size(patchMask);
    sampleMask = zeros(sz);
    
    pointNum = 1;
    for i = 1:sz(1)
        for j = 1:sz(2)          
            if patchMask(i,j) == 1 %Cell is in the patch
                if any(pointNum == randomPoints) %We're interested in subsampling this particular point within the patch 
                    sampleMask(i, j) = 1;
                end
                pointNum = pointNum + 1;
            end
        end
    end
    
end
