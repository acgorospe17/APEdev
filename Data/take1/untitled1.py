#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 05:07:07 2018

@author: crush
"""

<<<<<<< HEAD
base_dir = os.getcwd()
base_dirname = os.path.basename(base_dir)
print(base_dirname)
=======
final_dir = os.path.join(base_dir, 'Final/')
if not os.path.exists(final_dir):
    os.makedirs(final_dir)
print(final_dir)
>>>>>>> 900cc4c488cc2aa68f627bcbc39914302ff14303
