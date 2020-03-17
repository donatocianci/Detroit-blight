import pandas as pd
import numpy as np
import re

'''
This script is used to pull the addresses from each blight ticket and collate them 
into a csv file. 

This script uses the training data and test data to pull all the addresses in the 
dataset and save them to a CSV titled "my_addresses.csv". 
'''


def make_address_string(row):

    address_parts = row.values

    address = str(int(address_parts[1]))+' '+address_parts[2].lower()+', Detroit MI'

    if not re.search('[a-zA-Z]',str(address_parts[3])) and not np.isnan(float(address_parts[3])):
        address = address+' '+str(address_parts[3])

    return address



cols_to_keep = ['ticket_id', 'violation_street_number', 'violation_street_name',
                    'violation_zip_code']

training_addresses = pd.read_csv( 'train.csv', encoding = "ISO-8859-1" , \
                                    usecols = cols_to_keep)

test_addresses = pd.read_csv( 'test.csv', encoding = "ISO-8859-1", \
                                usecols = cols_to_keep)

address_data = pd.concat([training_addresses,test_addresses])

address_data['address'] = address_data.apply(make_address_string,
                                                            axis = 1)

address_data.to_csv(path_or_buf = 'my_addresses.csv',
                    columns = ['ticket_id', 'address'], index = False)
