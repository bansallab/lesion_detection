# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 09:47:25 2023

@author: []

Generates figures 3C and 3D (effect of image quality per dolphin on 
performance). For each lesion class and each value for image quality (2 star,
3 star) the prevalence estimate has been bootstrapped (n_resamples=500) and the 
distribution was saved to a file which this program loads and has been provided 
in the datafiles folder.  
"""


import pandas as pd
import numpy as np

bootstrapped = {"2Star":{"Spots":[], "Fringes":[]},  \
                "3Star":{"Spots":[], "Fringes":[]}}
    
for stars in bootstrapped:
    for lesionClass in bootstrapped[stars]:
        dist=np.loadtxt('datafiles/Model_IQ_Dist_'+lesionClass+"_"+stars+'.txt')
        confInt=np.loadtxt('datafiles/Model_IQ_CI_'+lesionClass+"_"+stars+".txt")
        bootstrapped[stars][lesionClass] = {"Dist": dist, "Mean": np.mean(dist),\
                                               "Conf":confInt}
        print(stars, lesionClass, bootstrapped[stars][lesionClass]["Mean"],\
              bootstrapped[stars][lesionClass]["Conf"])
            
data1 = pd.DataFrame(columns=['S2s', 'S3s'])
data1['S2s'] = bootstrapped["2Star"]["Spots"]["Dist"].tolist()
data1['S3s'] = bootstrapped["3Star"]["Spots"]["Dist"].tolist()
data1.to_csv("datafiles/IMQ_Spots.csv")
data2 = pd.DataFrame(columns=['F2s', 'F3s'])
data2['F2s'] = bootstrapped["2Star"]["Fringes"]["Dist"].tolist()
data2['F3s'] = bootstrapped["3Star"]["Fringes"]["Dist"].tolist()
data2.to_csv("datafiles/IMQ_Fringes.csv")

mypal = {'S2s':"#A30000", 'S3s':"#D68080", 'F2s':"#1A84B8", 'F3s':"#97E5E4"}

import seaborn
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (7,5)

#Spot
ax = seaborn.boxplot(data1, palette=mypal)
ax.set_xticklabels(['2 Stars', '3 Stars'], \
                   fontsize=14, rotation=15, ha="right")
ax.set_title('Spot', fontsize=18)
ax.set_ylabel('Accuracy', fontsize=16)
ax.set_xlabel('Photo Quality', fontsize=16)
ax.set_ylim([0.35,1.05])
plt.tight_layout()
figObj = plt.gcf()
figAddress = 'generatedFigures/Figure3C.jpg'
figObj.savefig(figAddress, bbox_inches='tight', dpi=1200)
plt.show()
plt.clf()

#Fringe
ax = seaborn.boxplot(data2, palette=mypal)
ax.set_xticklabels(['2 Stars', '3 Stars'], \
                   fontsize=14, rotation=15, ha="right")
ax.set_title('Fringe', fontsize=18)
ax.set_ylabel('Accuracy', fontsize=16)
ax.set_xlabel('Photo Quality', fontsize=16)
ax.set_ylim([0.35,1.05])
plt.tight_layout()
figObj = plt.gcf()
figAddress = 'generatedFigures/Figure3D.jpg'
figObj.savefig(figAddress, bbox_inches='tight', dpi=1200)
plt.show()
plt.clf()