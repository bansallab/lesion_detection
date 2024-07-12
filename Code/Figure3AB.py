# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 09:47:25 2023

@author: []

Generates figures 3A and 3B (effect of number of photos per dolphin on 
performance). For each lesion class and each value for number of photos (1,2,3+)
the prevalence estimate has been bootstrapped (n_resamples=500) and the distribution
was saved to a file which this program loads and has been provided in the
datafiles folder. 
"""

import numpy as np
import pandas as pd

bootstrapped = {"1 Photo":{"Spots":[], "Fringes":[]}, "2 Photos":{"Spots":[], \
                "Fringes":[]}, "3+ Photos":{"Spots":[], "Fringes":[]}}
for numPhoto in bootstrapped:
    for lesionClass in bootstrapped[numPhoto]:
        dist=np.loadtxt('datafiles/Model_PPD_Dist_'+lesionClass+"_"+numPhoto+'_v2.txt')
        confInt=np.loadtxt('datafiles/Model_PPD_CI_'+lesionClass+"_"+numPhoto+"_v2.txt")
        bootstrapped[numPhoto][lesionClass] = {"Dist": dist, "Mean": np.mean(dist),\
                                               "Conf":confInt}
        print(numPhoto, lesionClass, bootstrapped[numPhoto][lesionClass]["Mean"],\
              bootstrapped[numPhoto][lesionClass]["Conf"])
    
#Now for violin plots? I'll also do bar graphs later I guess but for now this'll do
data1 = pd.DataFrame(columns=['S1p', 'S2p', 'S3+p'])
data1['S1p'] = bootstrapped["1 Photo"]["Spots"]["Dist"].tolist()
data1['S2p'] = bootstrapped["2 Photos"]["Spots"]["Dist"].tolist()
data1['S3+p'] = bootstrapped["3+ Photos"]["Spots"]["Dist"].tolist()
data1.to_csv("datafiles/PPD_Spots_v2.csv")
data2 = pd.DataFrame(columns=['F1p', 'F2p', 'F3+p'])
data2['F1p'] = bootstrapped["1 Photo"]["Fringes"]["Dist"].tolist()
data2['F2p'] = bootstrapped["2 Photos"]["Fringes"]["Dist"].tolist()
data2['F3+p'] = bootstrapped["3+ Photos"]["Fringes"]["Dist"].tolist()
data2.to_csv("datafiles/PPD_Fringes_v2.csv")
mypal = {'S1p':"#A30000", 'S2p':"#BD4040", 'S3+p':"#D68080", \
         'F1p':"#1A84B8", 'F2p':"#59B5CE", 'F3+p':"#97E5E4", \
         'L1p':"#7203B3", 'L2p':"#8130B0", 'L3+p':"#905DAD"}
    
import seaborn
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (7,5)
#Spot
ax = seaborn.boxplot(data1, palette=mypal)
ax.set_xticklabels(['1 Photo', '2 Photos', '3+ Photos'], \
                   fontsize=14, rotation=15, ha="right")
ax.set_title('Spot', fontsize=18)
ax.set_ylabel('Accuracy', fontsize=16)
ax.set_xlabel('Photos Per Dolphin', fontsize=16)
ax.set_ylim([0.4,1.05])
plt.tight_layout()
figObj = plt.gcf()
figAddress = 'generatedFigures/Figure3A.jpg'
figObj.savefig(figAddress, bbox_inches='tight', dpi=1200)
plt.show()
plt.clf()

#Fringe
ax = seaborn.boxplot(data2, palette=mypal)
ax.set_xticklabels(['1 Photo', '2 Photos', '3+ Photos'], \
                   fontsize=14, rotation=15, ha="right")
ax.set_title('Fringe', fontsize=18)
ax.set_ylabel('Accuracy', fontsize=16)
ax.set_xlabel('Photos Per Dolphin', fontsize=16)
ax.set_ylim([0.3,1.05])
plt.tight_layout()
figObj = plt.gcf()
figAddress = 'generatedFigures/Figure3B.jpg'
figObj.savefig(figAddress, bbox_inches='tight', dpi=1200)
plt.show()
plt.clf()
