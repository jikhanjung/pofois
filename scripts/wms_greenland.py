#!/usr/bin/env python
from osgeo import gdal
from osgeo import osr
import numpy as np
import os, sys
import os,requests
from PIL import Image
from numpy import asarray,array
import rasterio
import time
# load the image
def convert_geotiff( from_filename,to_filename ):
    image = Image.open(from_filename)
    # convert image to numpy array
    data = array(image)
    print(type(data))
    # summarize shape
    print(data.shape)

    # create Pillow image
    image2 = Image.fromarray(data)
    print(type(image2))

    # summarize image details
    print(image2.mode)
    print(image2.size)
    Z = data
    print(Z.shape)

    R =Z[:,:,0]; G = Z[:,:,1]; B = Z[:,:,2]
    sum_rgb = R+G+B
    R[sum_rgb==0]=255
    G[sum_rgb==0]=255
    B[sum_rgb==0]=255
    #lat = [84,57]
    #lon = [-77,-2]

    lat = [y1,y2]
    lon = [x1,x2]


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


def download(url):
    get_response = requests.get(url,stream=True)
    file_name  = 'temp.png'
    with open(file_name, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return file_name

# bbox: -10973919.93019722588,7807973.989965946414,1966547.860455812654,20701362.16523269936

def get_average(val1,val2):
    return (val1+val2)/2.0


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
print(x_width, y_height, x_center, y_center)
print(x1,x2,y1,y2)
wh_ratio = x_width / y_height * 1.0
print(wh_ratio)

url_string = "https://data.geus.dk/geusmap/ows/32624.jsp?whoami=honestjung@gmail.com&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&BBOX={},{},{},{}&SRS=EPSG:{}&WIDTH={}&HEIGHT={}&LAYERS=grl_geus_500k_geology_map&STYLES=&FORMAT=image/png&DPI=96&MAP_RESOLUTION=96&FORMAT_OPTIONS=dpi:96&TRANSPARENT=TRUE"
l_url = url_string.format(x1,y1,x2,y2,epsg,width,height)



download_filename = download(l_url)

x_val = [x1,x2]
y_val = [y1,y2]

for i in range(1):
    for idx in range(len(x_val)-1,0,-1):
        x_val.insert(idx,get_average(x_val[idx],x_val[idx-1]))
        y_val.insert(idx,get_average(y_val[idx],y_val[idx-1]))
        print(x_val,y_val)

    for x_idx in range(len(x_val)-1):
        for y_idx in range(len(y_val)-1):
            print(x_idx,y_idx)
            print(url_string.format(x_val[x_idx],y_val[y_idx],x_val[x_idx+1]-1,y_val[y_idx+1]-1,epsg,width,height))
            time.sleep(3)
