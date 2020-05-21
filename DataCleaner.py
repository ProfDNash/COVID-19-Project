"""
Created on Wed May 20 10:08:45 2020

@author: David A. Nash
"""
import numpy as np
import pandas as pd

fileName = r'C:\Users\ProfN\Downloads\daily (1).csv'
data = pd.read_csv(fileName)
##delete unused columns
unused = ['pending','hospitalizedCurrently','hospitalizedCumulative','inIcuCurrently','inIcuCumulative',
          'onVentilatorCurrently','onVentilatorCumulative','dataQualityGrade','hash','dateChecked',
          'hospitalized','total','posNeg','fips', 'hospitalizedIncrease']
for col in unused:
    del data[col]

##delete U.S. territories 'AS', 'GU', 'MP', 'PR', 'VI'
territories = ['AS','GU','MP','PR','VI']
for terr in territories:
    data = data[data.state != terr]

##
stateList = set(data.state)
for state in stateList:
    currStateData = data[data.state==state]
    currStateData = currStateData.sort_values('date')
    counter = 0 ##count number of days with no reported data
    for i in range(len(currStateData)):
        if currStateData.iloc[i,11] == 0:   ##then no new test results were reported
            counter = counter+1
        elif counter > 0: ##next time results are reported, split them over the previous days
            for j in range(1,counter+1):
                currStateData.iloc[i-j,2] += (counter+1-j)*int(currStateData.iloc[i,10]/(counter+1)) ##positive cases
                currStateData.iloc[i-j,10] += int(currStateData.iloc[i,10]/(counter+1)) ##positive cases increase
                currStateData.iloc[i-j,3] += (counter+1-j)*int(currStateData.iloc[i,9]/(counter+1)) ##negative cases
                currStateData.iloc[i-j,9] += int(currStateData.iloc[i,9]/(counter+1)) ##negative cases inc
                currStateData.iloc[i-j,6] += (counter+1-j)*int(currStateData.iloc[i,8]/(counter+1)) ##deaths
                currStateData.iloc[i-j,8] += int(currStateData.iloc[i,8]/(counter+1)) ##deaths increase
                currStateData.iloc[i-j,7] += (counter+1-j)*int(currStateData.iloc[i,11]/(counter+1)) ##totalTests
                currStateData.iloc[i-j,11] += int(currStateData.iloc[i,11]/(counter+1)) ##totalTests inc
            ##update the current date by changing only the "increase" columns
            currStateData.iloc[i,11] -= int(currStateData.iloc[i,11]/(counter+1))*counter ##total inc
            currStateData.iloc[i,10] -= int(currStateData.iloc[i,10]/(counter+1))*counter ##pos inc
            currStateData.iloc[i,9] -= int(currStateData.iloc[i,9]/(counter+1))*counter ##neg inc
            currStateData.iloc[i,8] -= int(currStateData.iloc[i,8]/(counter+1))*counter ##death 
            counter = 0 ##reset counter after distributing data
        else:
            pass
    ##write new values back into the table
    data.update(currStateData, join='left', overwrite=True)


##write edited table to file for use in Tableau
outputName = r'C:\Users\ProfN\Downloads\dailyCleaned.csv'
data.to_csv(outputName)


