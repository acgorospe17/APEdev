from glob import glob
import re
import os
import shutil
import cv2
import numpy as np
from skimage import filters
from skimage.morphology import disk
from skimage.morphology import remove_small_objects, closing
from scipy.ndimage import binary_fill_holes


SAMPLE_NAME = 'sample'

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def move_images(images, img_class):
    new_dir = os.path.join(base_dir, img_class)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    for img in images:
        shutil.move(os.path.join(base_dir, img), os.path.join(new_dir, img))


# -----ORGANIZE IMAGES-----
base_dir = os.getcwd()
<<<<<<< HEAD
base_dirname = os.path.basename(base_dir)
=======
>>>>>>> 900cc4c488cc2aa68f627bcbc39914302ff14303

images = {}
for ls in ['Initial@E30', 'E30', 'E45', 'E60', 'W30', 'W45', 'W60']:
    imgs = glob('*{}.tif'.format(ls))
    move_images(imgs, ls)
    images[ls] = glob('{}/*.tif'.format(ls))
    images[ls] = natural_sort(images[ls])

naming_convention = '({})(.*)'.format(SAMPLE_NAME)
masks = []

final_dir = os.path.join(base_dir, 'Final/')
if not os.path.exists(final_dir):
    os.makedirs(final_dir)

# -----EXTRACT LINE FROM E30 IMAGES USING BACKGROUND-----
for line in zip(images['E30'], images['Initial@E30']):
    gray_fgd = cv2.imread(line[0], 0)
    gray_bgd = cv2.imread(line[1], 0)
    height, width = gray_fgd.shape
    cropped_fgd = gray_fgd[height//3:2*height//3, width//5:4*width//6]
    cropped_bgd = gray_bgd[height//3:2*height//3, width//5:4*width//6]

    diff = cv2.absdiff(cropped_fgd, cropped_bgd)
    med = filters.median(diff, disk(25))

    binary_adaptive = cv2.adaptiveThreshold(med, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 1.05)
    binary_adaptive = cv2.bitwise_not(binary_adaptive)
    thresh = remove_small_objects(np.array(binary_adaptive, bool), 20, connectivity=1)
    thresh = closing(thresh, selem=disk(7))
    thresh = binary_fill_holes(thresh).astype(int)*255
    masks.append(thresh)
    
    result = cropped_fgd*thresh.astype(bool)
    final = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
    
    g = re.search(naming_convention, line[0])
<<<<<<< HEAD
    cv2.imwrite(final_dir+base_dirname+g.group(2), final)
=======
    cv2.imwrite(final_dir+g.group(2), final)
>>>>>>> 900cc4c488cc2aa68f627bcbc39914302ff14303

# -----EXTRACT LINEs FROM REMAINING IMAGES-----   
for ls in ['E45', 'E60', 'W30', 'W45', 'W60']:
    for idx,line in enumerate(images[ls]):
        gray_fgd = cv2.imread(line, 0)
        height, width = gray_fgd.shape
        cropped_fgd = gray_fgd[height//3:2*height//3, width//5:4*width//6]
        thresh = masks[idx]
        
        result = cropped_fgd*thresh.astype(bool)
        final = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
        
        g = re.search(naming_convention, line)
<<<<<<< HEAD
        cv2.imwrite(final_dir+base_dirname+g.group(2), final)
=======
        cv2.imwrite(final_dir+g.group(2), final)
>>>>>>> 900cc4c488cc2aa68f627bcbc39914302ff14303
