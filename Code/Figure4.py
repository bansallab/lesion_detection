# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 19:38:36 2023

@author:[]

Code responsible for generating Figure 4 (Violin plots comparing manual estimates
of lesion presence to model estimates of lesion presence).

For manual estimates, loads the BASE_dist file for the correct lesion class and
year. This is a bootstrap distribution resulting from bootstrapping the manual
prediction of the selected lesion class' prevalence for the selected year with
n_resamples=999

For model estimates, each replicate was run with the data and predictions of
prevalence by year were collected. 
"""

import seaborn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dataS = pd.DataFrame(columns=['SMo15', 'SMo16', 'SMo17', 'SMa15', 'SMa16', 'SMa17'])
    
dataS['SMo15'] = pd.Series([0.8311688312, 0.8181818182, 0.7402597403, \
                           0.8311688312, 0.8571428571, 0.8051948052, \
                           0.7272727273, 0.8181818182, 0.7662337662, 0.8701298701])
dataS['SMo16'] = pd.Series([0.7115384615, 0.6730769231, 0.5961538462, \
                           0.7115384615, 0.7307692308, 0.6538461538, \
                               0.7307692308, 0.5769230769, 0.75, 0.7115384615])
dataS['SMo17'] = pd.Series([0.7840909091, 0.6363636364, 0.6363636364, \
                           0.7159090909, 0.6477272727, 0.6022727273, \
                               0.7272727273, 0.6590909091, 0.6022727273, 0.7045454545])
dataS['SMa15'] = pd.Series(np.loadtxt('datafiles/BASE_SpotDist2015.txt').tolist())
dataS['SMa16'] = pd.Series(np.loadtxt('datafiles/BASE_SpotDist2016.txt').tolist())
dataS['SMa17'] = pd.Series(np.loadtxt('datafiles/BASE_SpotDist2017.txt').tolist())

dataF = pd.DataFrame(columns=['FMo15', 'FMo16', 'FMo17', 'FMa15', 'FMa16', 'FMa17'])
dataF['FMo15'] = pd.Series([0.3766233766, 0.3116883117, 0.2337662338, \
                           0.2597402597, 0.3376623377, 0.2337662338, \
                           0.2597402597, 0.2857142857, 0.3376623377, 0.2987012987])
dataF['FMo16'] = pd.Series([0.3269230769, 0.2692307692, 0.4038461538, \
                           0.3653846154, 0.3653846154, 0.3269230769, \
                           0.2884615385, 0.3076923077, 0.3846153846, 0.3846153846])
dataF['FMo17'] = pd.Series([0.2272727273, 0.1590909091, 0.1931818182, \
                           0.1704545455, 0.1931818182, 0.1363636364, \
                               0.1931818182, 0.2045454545, 0.1704545455, 0.1818181818])
dataF['FMa15'] = pd.Series(np.loadtxt('datafiles/BASE_FringeDist2015.txt').tolist())
dataF['FMa16'] = pd.Series(np.loadtxt('datafiles/BASE_FringeDist2016.txt').tolist())
dataF['FMa17'] = pd.Series(np.loadtxt('datafiles/BASE_FringeDist2017.txt').tolist())   
 
###Violin Plots
plt.figure(dpi=1200, figsize=(11,4))
fig, (ax1, ax2) = plt.subplots(1,2)
data2a = pd.DataFrame(columns=['pResS', 'modelPS'])
data2b = pd.DataFrame(columns=['pResF', 'modelPF'])
data2b['pResF'] = pd.concat([dataF['FMa15'].dropna(), dataF['FMa16'].dropna(), dataF['FMa17'].dropna()], ignore_index=True)
data2a['pResS'] = pd.concat([dataS['SMa15'].dropna(), dataS['SMa16'].dropna(), dataS['SMa17'].dropna()], ignore_index=True)
data2b['modelPF'] = pd.concat([dataF['FMo15'].dropna(), dataF['FMo16'].dropna(), dataF['FMo17'].dropna()], ignore_index=True)
data2a['modelPS'] = pd.concat([dataS['SMo15'].dropna(), dataS['SMo16'].dropna(), dataS['SMo17'].dropna()], ignore_index=True)
data2a['modelPS'].to_csv('datafiles/Model_Spot_Predictions.csv')
data2b['modelPF'].to_csv('datafiles/Model_Fringe_Predictions.csv')
print(data2a['pResS'].mean())
print(data2b['pResF'].mean())
mypal = {'pResF':'#1a84b8', 'pResS':'#A30000', 'modelPF':'#1aa4b8', 'modelPS':'#EF1910'}
seaborn.violinplot(data2a, palette=mypal, ax=ax1)
ax1.set_xticklabels(['Manual', 'Model'], fontsize=12, rotation=0, ha="right")
ax1.set_yticklabels([0, 0.2, 0.4, 0.6, 0.8, 1], fontsize=12)
ax1.set_ylabel('Yearly Prevalence', fontsize=16)
ax1.set_title('Spots', fontsize=20)
ax1.set_ylim([0,1])
ax1.text(-0.1, 1.15, "A", transform=ax1.transAxes,
      fontsize=16, fontweight='bold', va='top', ha='right')
seaborn.violinplot(data2b, palette=mypal, ax=ax2)
ax2.set_xticklabels(['Manual', 'Model'], fontsize=12, rotation=0, ha="right")
ax2.set_yticklabels([0, 0.2, 0.4, 0.6, 0.8, 1], fontsize=12)
ax2.set_ylabel('Yearly Prevalence', fontsize=16)
ax2.set_ylim([0,1])
ax2.set_title("Fringes", fontsize=20)
ax2.text(-0.1, 1.15, "B", transform=ax2.transAxes,
      fontsize=16, fontweight='bold', va='top', ha='right')
figObj = plt.gcf()
figAddress = 'generatedFigures/Figure4.jpg'
plt.tight_layout()
figObj.savefig(figAddress, bbox_inches='tight', dpi=1200)

plt.show()