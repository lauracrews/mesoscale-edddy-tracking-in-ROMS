%Plots the eddy grid and the contour outlining the eddy to make sure they align correctly
%If they do not, it is likely a day number indexing error 
%The assignment currentDay = fileNumber + 1 in patch_identificaion.py may need to be changed to e.g. currentDay = fileNumber + 2 (if starting on day 2)

function testOverlap(center_x, center_y, center_lon, center_lat, lon, lat, patchGrid, patchMask)
    radius = 15; %Number of cells around the patch center to plot
    lon = lon(center_x - radius:center_x + radius, center_y - radius:center_y + radius);
    lat = lat(center_x - radius:center_x + radius, center_y - radius:center_y + radius);
   
    figure
    contourf(lon, lat, patchGrid(center_x - radius:center_x + radius, center_y - radius:center_y + radius), 'linestyle', 'none'); 
    hold on; 
    contour(lon, lat, patchMask(center_x - radius:center_x + radius, center_y - radius:center_y + radius), 'g')
    hold on;
    colormap gray
    scatter(center_lon, center_lat, 70, 'r', 'filled')

end