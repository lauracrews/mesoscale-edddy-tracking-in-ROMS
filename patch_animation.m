%This makes an animation of model data with patch contours overlain.
%Calls patchesActiveToday to create a mask of all patches active on a particular day

cd /where you want to save the animation
close all
v1 = VideoWriter('patch_animation.mp4', 'MPEG-4'); %Video writer objct which writes images into an animation
v1.FrameRate = 5; 
open(v1)

%The portion of the model domain to be studied
firstRow = 1; lastRow = 1301; firstCol = 1; lastCol = 1147;

%The depth used for making patch grids (assumes model has been interpolated to constant z-layers
zlay = 1;

cd /where patches.mat is stored
load patches

cd /where the .nc file is stored
ncFile = 'name of file used to make patch masks';
depth = ncread(ncFile, 'depth');
time = ncread(ncFile, 'time');
lat = ncread(ncFile, 'lat', [firstRow firstCol], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1], [1 1]);
lon  = ncread(ncFile, 'lon', [firstRow firstCol], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1], [1 1]);
landmask = ncread(ncFile, 'mask3d', [firstRow firstCol 1], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1, Inf], [1 1 1]); landmask = landmask(:, :, 1);
bathy = ncread(ncFile, 'h', [firstRow firstCol], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1], [1 1]);
sz = size(lat);

%Projection
hFig = figure(1);
set(hFig, 'Position', [50 50 800 1000])
latlims = [min(lat(:)), max(lat(:))];
lonlims = [min(lon(:)), max(lon(:))];
m_proj('lambert','lon',lonlims,'lat',latlims);

%Used to title each day - adjust for date range 
d1 = datenum('jan-1-2006');
d2 = datenum('dec-31-2007');
dailyDates = d1:d2; 

for day = 1:length(time)
    close all
    hFig = figure(1);
    set(hFig, 'Position', [50 50 800 1000])   
    
    allPatches = patchesActiveToday(patches, day, sz);
    
    %For two-dimensional properties (i.e. bathymetry, sea surface height)
    property1 = ncread(ncFile, 'propertyName', [firstRow firstCol day], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1, 1], [1 1 1]);   
    %For three-dimensional properties (i.e. temperature, salinity)
    property2 = ncread(ncFile, 'propertyName', [firstRow firstCol zlay day], [(lastRow - firstRow) + 1, (lastCol - firstCol) + 1, 1 1], [1 1 1 1]);   

    m_pcolor(lon, lat, property2); hold on; shading flat;
    caxis([]) %Adjust this
    m_contour(lon, lat, allPatches, 'k', 'lineWidth', 3); hold on;
    m_contour(lon, lat, landmask, 'k'); hold on;  % Coastline shortcut - faster than calling m_gshhs_i 
    cint = 500 * [0:1:5];
    m_contour(lon, lat, bathy, cint, 'color', 0.8 .*[1 1 1]) %Bathymetry contours
  
    set(gca, 'color', 0.8 .*[1 1 1]) %Background color
    colorbar()
    title(strcat('Property at ', int2str(depth(zlay)), 'm,  ', datestr(dailyDates(day), 'mmm.dd,yyyy')), 'fontSize', 16, 'fontWeight', 'bold')  
    set(gca, 'fontsize', 18, 'xtick', [0], 'xticklabel', {''}, 'ytick', [0], 'yticklabel',{''}) %Adjust to label lat/lon
    
    F1 = getframe(gcf);
    writeVideo(v1, F1)
    
end
close(v1)
    