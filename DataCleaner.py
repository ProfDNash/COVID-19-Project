"""
Created on Wed May 20 10:08:45 2020

@author: David A. Nash
"""
import numpy as np
import pandas as pd

filename = r'C:\Users\ProfN\Downloads\daily (1).csv'
data = pd.read_csv(filename)
##delete unused columns
unused = ['pending','hospitalizedCurrently','hospitalizedCumulative','inIcuCurrently','inIcuCumulative',
          'onVentilatorCurrently','onVentilatorCumulative','dataQualityGrade','hash','dateChecked',
          'hospitalized','total','posNeg','fips']
for col in unused:
    del data[col]

##write edited table to file for use in Tableau
outputname = r'C:\Users\ProfN\Downloads\daily.csv'
data.to_csv(outputname)


