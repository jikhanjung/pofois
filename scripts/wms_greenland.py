#!/usr/bin/env python
from osgeo import gdal
from osgeo import osr
import numpy as np
import os, sys
from PIL import Image
from numpy import asarray,array
import rasterio
import time
import os,requests
from os import path

# load the image
def convert_geotiff( from_filename,to_filename,a_xval, a_yval ):
    image = Image.open(from_filename)
    # convert image to numpy array
    data = array(image)
    #print(type(data))
    # summarize shape
    #print(data.shape)

    # create Pillow image
    image2 = Image.fromarray(data)
    #print(type(image2))

    # summarize image details
    #print(image2.mode)
    #print(image2.size)
    Z = data
    #print(Z.shape)

    R =Z[:,:,0]; G = Z[:,:,1]; B = Z[:,:,2] ; A = Z[:,:,3]
    sum_rgb = R+G+B
    
    R[A==0]=255
    G[A==0]=255
    B[A==0]=255
    #lat = [84,57]
    #lon = [-77,-2]

    lat = a_yval#[y1,y2]
    lon = a_xval#[x1,x2]


    # set geotransform
    nx = Z.shape[0]
    ny = Z.shape[1]
    xmin, ymin, xmax, ymax = [min(lon), min(lat), max(lon), max(lat)]
    xres = (xmax - xmin) / float(nx)
    yres = (ymax - ymin) / float(ny)
    geotransform = (xmin, xres, 0, ymax, 0, -yres)

    # create the 3-band raster file
    dst_ds = gdal.GetDriverByName('GTiff').Create(to_filename, ny, nx, 3, gdal.GDT_Byte)

    dst_ds.SetGeoTransform(geotransform)    # specify coords
    srs = osr.SpatialReference()            # establish encoding
    srs.ImportFromEPSG(3857)                # WGS84 lat/long
    dst_ds.SetProjection(srs.ExportToWkt()) # export coords to file
    dst_ds.GetRasterBand(1).WriteArray(R)   # write r-band to the raster
    dst_ds.GetRasterBand(2).WriteArray(G)   # write g-band to the raster
    dst_ds.GetRasterBand(3).WriteArray(B)   # write b-band to the raster
    dst_ds.FlushCache()                     # write to disk
    dst_ds = None
    
def download(url,file_name):
    get_response = requests.get(url,stream=True)
    with open(file_name, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def get_average(val1,val2):
    return (val1+val2)/2.0

# bbox: -10973919.93019722588,7807973.989965946414,1966547.860455812654,20701362.16523269936

x1 = -12873920
x2 = 3866548
y1 = 7807974
y2 = 20701362
width=2048
height=2048
epsg=3857
x_width = x2 - x1
y_height = y2 - y1
x_center = ( x1 + x2 ) / 2.0
y_center = ( y1 + y2 ) / 2.0
half_width = 8388608
print(x_width, y_height, x_center, y_center)
x1 = x_center - half_width
x2 = x_center + half_width
y1 = y_center - half_width
y2 = y_center + half_width
x_width = x2 - x1
y_height = y2 - y1
# print(x_width, y_height, x_center, y_center)
print(x1,x2,y1,y2)

url_string = "https://data.geus.dk/geusmap/ows/32624.jsp?whoami=honestjung@gmail.com&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&BBOX={},{},{},{}&SRS=EPSG:{}&WIDTH={}&HEIGHT={}&LAYERS=grl_geus_500k_geology_map&STYLES=&FORMAT=image/png&DPI=96&MAP_RESOLUTION=96&FORMAT_OPTIONS=dpi:96&TRANSPARENT=TRUE"

x_val = [x1,x2]
y_val = [y1,y2]
xy_vals = {}

from_level = 1
to_level = 6

for level in range(from_level,to_level+1):
    xy_vals[level] = [x_val.copy(),y_val.copy()]
    print(level,xy_vals[level])
    for idx in range(len(x_val)-1,0,-1):
        x_val.insert(idx,get_average(x_val[idx],x_val[idx-1]))
        y_val.insert(idx,get_average(y_val[idx],y_val[idx-1]))
    #print(x_val,y_val)
#print(xy_vals)


def get_map(a_level, a_x_val, a_y_val, a_epsg, a_width, a_height,a_refresh=False,a_sleeptime=10):
    #x_val, y_val = xy_vals[level]
    for x_idx in range(len(a_x_val)-1):
        for y_idx in range(len(a_y_val)-1):
            l_x1 = a_x_val[x_idx]
            l_y1 = a_y_val[y_idx]
            l_x2 = a_x_val[x_idx+1]-1
            l_y2 = a_y_val[y_idx+1]-1
            l_url = url_string.format(l_x1,l_y1,l_x2,l_y2,a_epsg,a_width,a_height)
            print(a_level,x_idx,y_idx,l_url)
            fname = "{}_{}_{}".format(a_level,x_idx,y_idx)
            fname1 = "data/png/" + fname+".png"
            fname2 = "data/tif/" + fname+".tif"
            #print(fname1,fname2)
            if not path.exists(fname2) or a_refresh:
                if not path.exists(fname1) or a_refresh:
                    download(l_url,fname1)
                convert_geotiff(fname1,fname2,[l_x1,l_x2],[l_y1,l_y2])
                time.sleep(a_sleeptime)

map_levels = [2]
                
for level in map_levels:
    x_val, y_val = xy_vals[level]
    get_map( level, x_val, y_val, epsg, width, height )

    