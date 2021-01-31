# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 07:08:04 2021
COVID-19 DEATHS BY COUNTY ANIMATED VIZ
@author: ProfN
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import geopandas as gpd
from shapely.geometry import Point  ##to check if a point is inside
#from scipy.ndimage.filters import gaussian_filter
from matplotlib.animation import FuncAnimation
#import plotly.express as px  #doesn't look like this will work
#from plotly.offline import plot 

filepath = r'C:\Users\ProfN\Downloads\covid_deaths_usafacts.csv'
total_deaths_df = pd.read_csv(filepath)

##process the total_deaths_df to get a count of *new* deaths each day
new_deaths_df = total_deaths_df.copy()
skip = ['countyFIPS','County Name', 'State', 'stateFIPS']
date_cols = list(new_deaths_df.columns)[4:]

new_deaths_df[date_cols] = new_deaths_df[date_cols].diff(axis=1)
##drop all dates in January 2020 as the first recorded death was on Feb. 6th
new_deaths_df.drop(columns=date_cols[:10], inplace=True)

##convert differenced columns back to integers
new_deaths_df[date_cols[10:]] = new_deaths_df[date_cols[10:]].astype(int)

##randomly distribute the unallocated deaths from each state to different
##counties within the state
unknown = new_deaths_df[new_deaths_df['County Name']=='Statewide Unallocated']
new_deaths_df = new_deaths_df[new_deaths_df['County Name']!='Statewide Unallocated']

##remove all columns that are entirely zeros
unknown = unknown[unknown.columns[(unknown != 0).any()]]

   

##load county shape files from Census Bureau
county_filepath = r'C:\Users\ProfN\Downloads\cb_2018_us_county_500k\cb_2018_us_county_500k.shp'
counties = gpd.read_file(county_filepath)
state_filepath = r'C:\Users\ProfN\Downloads\cb_2018_us_state_500k\cb_2018_us_state_500k.shp'
states = gpd.read_file(state_filepath)
states.STATEFP = states.STATEFP.astype(int)
counties.STATEFP = counties.STATEFP.astype(int)
##drop territories
Ccounties = counties[counties.STATEFP<60]
Cstates = states[states.STATEFP<60]
##drop Alaska and Hawaii
Ccounties = Ccounties[Ccounties.STATEFP!=2] ##Alaska
Cstates = Cstates[Cstates.STATEFP!=2] ##Alaska
Ccounties = Ccounties[Ccounties.STATEFP!=15] ##Hawaii
Cstates = Cstates[Cstates.STATEFP!=15] ##Hawaii

##to plot just the continental US
def plotBoundaries(shape):
    sns.set_palette('magma')
    fig, ax = plt.subplots(figsize=(20,10))
    g = shape.plot(ax=ax)
    sns.despine(left=True, bottom=True)
    ##xlim and ylim zoom in on the contiguous US only
    #g.set(xlim=(-125,-67),ylim=(25,50),xticks=(),yticks=())
    ##NY only
    g.set(xlim=(-80,-72),ylim=(40.3,45.3),xticks=(),yticks=())
    plt.show()


def randCoord(county, num_coords=1):
    ##generate num_coords random coordinates inside the county geometry
    rand_coords = []
    xmin, ymin, xmax, ymax = county.bounds
    xdiff, ydiff = xmax-xmin, ymax-ymin
    while len(rand_coords)<num_coords:
        rand_x, rand_y = 0,0
        rand_pt = Point(rand_x, rand_y)
        while rand_pt.within(county)==False:
            rand_x = xmin+xdiff*np.random.rand()
            rand_y = ymin+ydiff*np.random.rand()
            rand_pt = Point(rand_x, rand_y)
        rand_coords.append([rand_x, rand_y])
    rand_df = pd.DataFrame(rand_coords, columns=['latitude','longitude'])
    return rand_df

#def myplot(df, s, bins=1000): ##cool heatmap, but not super useful given wide range
#    heatmap, xedges, yedges = np.histogram2d(df.latitude, df.longitude, bins=bins)
#    heatmap = gaussian_filter(heatmap, sigma=s)
#
#    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
#    return heatmap.T, extent

def allCoords(counties, deaths):
    ##Take in a collection of counties and find random points within each county
    ##First, merge counties and total deaths
    ##This requires adjusting the County names
    deaths['County Name'] = deaths['County Name'].apply(
        lambda x: x.replace(' County', ''))
    deaths['County Name'] = deaths['County Name'].apply(
        lambda x: x.replace(' Parish', ''))
    counties = counties.merge(deaths[['stateFIPS','County Name','1/27/21']], left_on=['STATEFP','NAME'],
                              right_on=['stateFIPS','County Name'], how='left')
    allCoords = []
    np.random.RandomState(seed=42) ##for reproducibility
    for idx, row in counties.iterrows():
        if idx%100==0:
            print(idx)
        county_geom = row['geometry']
        county_deaths = row['1/27/21']
        county_df = randCoord(county_geom, county_deaths)
        if len(allCoords)==0 and len(county_df)>0:
            allCoords = county_df
        elif len(county_df)>0:
            allCoords = allCoords.append(county_df)
    
    ##add color choices
    allCoords.reset_index(inplace=True)
    allCoords['color']=allCoords['index'].apply(
        lambda x: 'Deaths<1000' if x<1000 
        else ('1000<Deaths<2000' if x<2000 
              else ('2000<Deaths<3000' if x<3000 
                   else ('3000<Deaths<4000' if x<4000 
                         else ('4000<Deaths<5000' if x<5000 
                               else 'Deaths>5000')
                         )
                   )
              )
        )
    return allCoords

def plotAll(states, coords):
    fig, ax = plt.subplots(figsize=(20,10))
    states.plot(color='white',edgecolor='grey', markersize=1, ax=ax)
    sns.despine(left=True,bottom=True)
    ax.set(xticks=(), yticks=())
    sns.scatterplot(x='latitude', y='longitude', hue='color', 
                    palette=sns.color_palette('YlOrRd_r', 7)[1:], #as_cmap=True), 
                    data=coords,edgecolor='k', ax=ax, alpha=0.4, s=2)
    plt.legend(fontsize=15, loc='lower left')
    plt.title('U.S. Deaths from COVID-19 (as of 1-27-21)', fontsize=20)
    plt.show()
    
def createAnimation(states, coords):
    fig, ax = plt.subplots()
    ax = states.plot(color='white',edgecolor='grey', markersize=1)
    sns.despine(left=True, bottom=True)
    ax.set(xticks=(), yticks=())
    
    def animate(i):
        pass