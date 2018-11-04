import json
import re
import numpy as np
import pandas as pd
import os


SAMPLE_NAME = 'sample'


def calc_heights(h):
    h1 = h[1] - np.mean([h[3], h[6]])
    h2 = h[0] - np.mean([h[4], h[7]])
    h3 = h[2] - np.mean([h[5], h[8]])
    return h1, h2, h3


# -----LOAD DATA FROM JSON-----
with open('heights.json') as f:
    raw_data = json.load(f)
    
# -----EXTRACT DATA FROM JSON-----
raw_heights = []
raw_locations = []

naming_convention = '({})(.*)'.format(SAMPLE_NAME)

for sample in raw_data:
    for k,v in sample.items():
        if k.startswith(SAMPLE_NAME):
            raw_heights.append(v[0])
            g = re.search(naming_convention, k)
            raw_locations.append(g.group(2))

# -----PARSE DATA-----
bgd_heights = raw_heights[:len(raw_heights)//2]
fgd_heights = raw_heights[len(raw_heights)//2:]

empty_heights = []
for sample in bgd_heights:
    empty_heights.append( calc_heights(sample) )
    
printed_heights = []
for sample in fgd_heights:
    printed_heights.append( calc_heights(sample) )
    
heights = np.abs( np.array(printed_heights) - np.array(empty_heights) )

locations = raw_locations[:len(raw_locations)//2]

base_dir = os.getcwd()
base_dirname = os.path.basename(base_dir)

filenames = []
for loc in locations:
    filenames.append([base_dirname+loc+ls+'.tif' for ls in ['E30', 'E45', 'E60', 'W30', 'W45', 'W60']])

# -----ORGANIZE DATA-----
data = {}
for h,fn_set in zip(heights, filenames):
    for fn_item in fn_set:
        data[fn_item] = h

df = pd.DataFrame(data).T

# -----SAVE DATA-----
df.to_csv('data.csv')

