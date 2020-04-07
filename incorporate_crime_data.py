import numpy as np
import pandas as pd
from math import pi

#import the processed data
blight_data = pd.read_csv( 'processed_blight_data.csv').set_index('ticket_no')

blight_data.drop(columns = 'parcelno', inplace = True)


avg_lat = blight_data['Y'].median()*(pi/180.0)

#these two variables give the instantaneous rate of change the distance (in m) as a function of latitude
delta_lat = 111132.92 - 559.822*np.cos(2*avg_lat)+1.175*np.cos(4*avg_lat)-0.0023*np.cos(6*avg_lat)
delta_lon =  111412.84*np.cos(avg_lat)-93.5*np.cos(3*avg_lat)+0.118*np.cos(5*avg_lat)

crime_data = pd.read_csv('Reported_Major_Crimes_2011_to_2014.csv', usecols = ['LOCATION'])

#clean crime data to obtain only latitude and longitude information. 
crime_data['lat'] = crime_data['LOCATION'].str.extract(r'\(([0-9,.]+),').astype(float)
crime_data['lon'] = crime_data['LOCATION'].str.extract(r', ([0-9,.,-]+)\)').astype(float)
crime_data.drop(columns = ['LOCATION'], inplace = True)

tot_crimes = crime_data['lat'].size

blight_data['loc'] =  list( zip(blight_data.Y, blight_data.X) ) 
crime_lat = crime_data['lat'].to_numpy()
crime_lon = crime_data['lon'].to_numpy()

def crime_tally(loc):
    return np.sum( delta_lat*np.absolute( (loc[0])*np.ones(tot_crimes) - crime_lat )+ \
    delta_lon*np.absolute( (loc[1])*np.ones(tot_crimes) - crime_lon ) <= 1000.0 )

blight_data['crime_totals'] = blight_data['loc'].apply(crime_tally)

blight_data.drop(columns = 'loc', inplace = True)

blight_data.to_csv(path_or_buf = 'processed_blight_data_with_crime.csv')