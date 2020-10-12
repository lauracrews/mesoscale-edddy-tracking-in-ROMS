%The portion of the model domain to be studied
firstRow = 1; lastRow = 1301; firstCol = 1; lastCol = 1147;

%The depth used for making patch grids (assumes model has been interpolated to constant z-layers
zlay = 1;

%The size of a model grid cell - to convert units for area and velocity
gridSize = 0.8;

%Used to subsample points within the eddy
minNumCells = 10; %Minimum number of cells to sample
percentToSample = 0.2; %Percent of cells to sample

%Initialize empty data structure. Adjust 'other property' here and below to temperature, salinity, etc.
patches = repmat(struct('day',{}, 'lat',{},'lon',{}, ...
    'j',{},'i',{}, 'area', {}, 'velocity', {},  'patchGrid', {}, ... 
    'patchMask', {}, 'meanOtherProperty', {}),1, 10);

ncFile = 'name of file used to make patch masks';
cd /where the .nc file is stored
depth = ncread(ncFile, 'depth');
lat = ncread(ncFile, 'lat', [firstRow firstCol], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1], [1 1]);
lon  = ncread(ncFile, 'lon', [firstRow firstCol], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1], [1 1]);

numPatches = 1; %Adjust this by looking at the patch numbers in the names of the patch summaries created by save_patches.py
for patch = 1:numPatches
    cd '/where the patch summaries made by save_patches.py are stored'
    patchFile = strcat('patch', int2str(patch), '_summary.csv');
    patchData = csvread(patchFile);
    
    %Copy data from the csv file made by save_patches.py to the matlab data structure
    patches(patch).day = patchData(:, 1);
    patches(patch).i = patchData(:, 2);
    patches(patch).j = patchData(:, 3);
    patches(patch).area = patchData(:, 4) .* gridSize^2; %To convert from grid cell units to km^2
    patches(patch).velocity = patchData(:, 5) .* gridSize; %To convert from grid cells/day to km/day
    
    %Iterate through each day a patch is active, save data for that day
    for obsNum = 1:length(patchData(:, 1))
        day = patchData(obsNum, 1); %Day in the .nc file
        
        patches(patch).lon(obsNum) = lon(patchData(obsNum, 2), patchData(obsNum, 3)); 
        patches(patch).lat(obsNum) = lat(patchData(obsNum, 2), patchData(obsNum, 3));
        
        %Create mask of patch location
        cd /where the masks made by save_patches.py are stored
        maskFile = strcat('patch', int2str(patch), '_day', int2str(day), '_mask.csv');
        pointsInPatch = csvread(maskFile); numCells = length(pointsInPatch(:,1));
        patchMask = zeros(size(lat));
        for i = 1:numCells
            xloc = pointsInPatch(i, 1); yloc = pointsInPatch(i, 2);
            patchMask(xloc, yloc) = 1;
        end        
        patches(patch).patchMask(obsNum) = {patchMask};
        
        %This is optional - it's useful to plot the patch grid with the patch mask overlaid to make sure they align correctly
        %If they do not align correctly, change currentDay = fileNumber + 1 in patch_identification.py
        cd /where the patch grids created using makePatchGrids.m are stored
        if day < 10
            patchGridFile = strcat('00', int2str(day), '_patchGrid_', int2str(depth(zlay)), 'm.csv'); 
        elseif day < 100
            patchGridFile = strcat('0', int2str(day), '_patchGrid_', int2str(depth(zlay)), 'm.csv'); 
        else
            patchGridFile = strcat(int2str(day), '_patchGrid_', int2str(depth(zlay)), 'm.csv');
        end       
        patchGrid = csvread(patchGridFile);
        patches(patch).patchGrid(obsNum) = {patchGrid};
        
        %Plots patchGrid and patchMask to check overlap
        %testOverlap(patches(patch).i(obsNum), patches(patch).j(obsNum), patches(patch).lon(obsNum), patches(patch).lat(obsNum), lon, lat, patchGrid, patchMask)        
        
        sampleMask = patchMask;        
        %sampleMask = makeSampleMask(patchMask, numCells, percentToSample, minNumCells); %Use to sample a random subset of points in the patch 
        
        %Use the sampleMask to calculate properties within the patch. Adjust 'propertyName' and 'otherProperty'
        cd /where the .nc file is      
        %If it's a 2D property
        otherProperty = ncread(ncFile, 'propertyName', [firstRow firstCol day], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1, 1], [1 1 1]);       
        %If it's a 3D property
        otherProperty = ncread(ncFile, 'propertyName', [firstRow firstCol zlay day], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1, 1, 1], [1 1 1 1]);   
       
        patches(patch).meanOtherProperty(obsNum) = mean(otherProperty(logical(sampleMask))); %Average of pixels within the patch
        
    end
end

cd /where you want to save the patches .mat structure
save('patches', 'patches')