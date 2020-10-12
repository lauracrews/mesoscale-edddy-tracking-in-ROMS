%The portion of the model domain to be studied
firstRow = 1; lastRow = 1301; firstCol = 1; lastCol = 1147;

%The depth used for making patch grids (assumes model has been interpolated to constant z-layers
zlay = 1;

%For example, minTemp = 2; 
threshold1 = x; %Adjust these
threshold2 = x;

%Creates patch true/false grid as csv files to be used in Python. 
cd /Where the .nc file is located
ncFile = 'name of nc file';
days = ncread(ncFile, 'time');
depth = ncread(ncFile, 'depth');
lat = ncread(ncFile, 'lat', [firstRow firstCol], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1], [1 1]);
lon = ncread(ncFile, 'lon', [firstRow firstCol], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1], [1 1]);

for day = 1:length(days)
    
    patchGrid = zeros(size(lat));
    cd /Where the .nc file is located

    %For two-dimensional properties (i.e. bathymetry, sea surface height)
    property1 = ncread(ncFile, 'propertyName', [firstRow firstCol day], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1, 1], [1 1 1]);   
    %For three-dimensional properties (i.e. temperature, salinity)
    property2 = ncread(ncFile, 'propertyName', [firstRow firstCol zlay day], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1, 1, 1], [1 1 1 1]);   
  
    patchGrid(property1 >= threshold1) = 1;
    patchGrid(property2 >= threshold2) = 1;
    
    cd /where the patch grid files to be read by patch_identification.py are stored
    if day < 10 %This naming convention makes sure python will read files in correct order (including leading zeroes makes it 'alphebetical')
        saveName = strcat('00', int2str(day), '_patchGrid_', int2str(depth(zlay)), 'm.csv'); 
    elseif day < 100
        saveName = strcat('0', int2str(day), '_patchGrid_', int2str(depth(zlay)), 'm.csv'); 
    else
        saveName = strcat(int2str(day), '_patchGrid_', int2str(depth(zlay)), 'm.csv');
    end
    csvwrite(saveName, patchGrid); 
end