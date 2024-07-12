# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 15:47:19 2022

@author: []

Code to generate Figure 2. Loads data from the bplotdata excel sheet storing
the post-train mAP values obtained from Roboflow after training the models
used in the one step and two step processes.

"""


import pandas as pd
from matplotlib import pyplot as plt

plotdatafile = pd.ExcelFile('datafiles/bplotdata.xlsx')
df1 = pd.read_excel(plotdatafile, 'OneStep')
df2 = pd.read_excel(plotdatafile, 'TwoStep')
plotdatafile.close()

control = df1['Control']
crop = df1['Crop']
spots = df2['Spots']
bspots = df2['Bspots']
dspots = df2['Dspots']
fringes = df2['Fringes']
bfringes = df2['Bfringes']
dfringes = df2['Dfringes']


modelsA = [control, crop, spots, fringes]
modelsB = [bspots, dspots, bfringes, dfringes]
plt.figure(dpi=1200)
plt.rcParams['figure.figsize'] = (15,6)
fig, (ax1, ax2) = plt.subplots(1,2)
boxprops = dict(linewidth=2)
box1 = ax1.boxplot(modelsA, boxprops=boxprops)
for median in box1['medians']:
    median.set_color('black')
ax1.set_xticks([1,2,3,4])
ax1.set_xticklabels(['Uncropped', 'Cropped', 'Cropped Spots', 'Cropped Fringes'], \
                    fontsize=12, rotation=-45)
ax1.set_ylim([0,100])
ax1.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
ax1.set_ylabel('Mean Average Precision (mAP)', fontsize=18)
ax1.text(-0.1, 1.15, "A", transform=ax1.transAxes,
      fontsize=16, fontweight='bold', va='top', ha='right')


box2 = ax2.boxplot(modelsB, boxprops=boxprops)
for median in box2['medians']:
    median.set_color('black')
ax2.set_xticks([1,2,3,4])
ax2.set_xticklabels(['Body Spots', 'Dorsal Spots', 'Body Fringes',\
                     'Dorsal Fringes'], fontsize=16, rotation=-45)
ax2.set_ylim([0,100])
ax2.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
ax2.text(-0.1, 1.15, "B", transform=ax2.transAxes,
      fontsize=16, fontweight='bold', va='top', ha='right')

ax1.set_title("One Step Models", fontsize=20)
ax2.set_title("Two Step Models", fontsize=20)


plt.tick_params(axis='x', which='major', labelsize=12)
fig = plt.gcf()
figAddress = 'generatedFigures/Figure2.jpg'
fig.savefig(figAddress, bbox_inches='tight', dpi=1200)
plt.show()