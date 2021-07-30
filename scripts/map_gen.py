from PIL import Image

width = 2048
height = 2048

n_width = 2
n_height = 4


whole_image = Image.new( mode = "RGBA", size = (width*n_width, height * n_height) )

for w_idx in range(n_width):
    for h_idx in range(n_height):
        img = Image.open("data/map_level3/3_{}_{}.tif".format(w_idx+1,h_idx))
        whole_image.paste(img,box=(width*(w_idx),height*(n_height-h_idx-1)))

whole_image.save('data/map_level3/whole_image.png')
