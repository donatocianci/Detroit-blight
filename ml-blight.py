import numpy as np
import pandas as pd

cols_to_keep = ['ticket_id','fine_amount','late_fee','compliance']

blight_data = pd.read_csv( 'train.csv', encoding = "ISO-8859-1" , \
    usecols = cols_to_keep).sort_index()
address_data =  pd.read_csv( 'addresses.csv' )
gps_data = pd.read_csv( 'latlons.csv' )

#remove zip-code from the gps_data:
gps_data.address = gps_data.address.apply(lambda x: x.split(',')[0])
#remove zip-code from the address:
address_data.address = address_data.address.apply(lambda x: x.split(',')[0])
gps_data.set_index( 'address', inplace = True )
# add missing lat and lon for test data:
gps_data.loc['20424 bramford']['lat'] = 42.446540
gps_data.loc['20424 bramford']['lon'] = -83.023300

gps_data.dropna(axis = 0, inplace = True)


address_data = address_data.merge(gps_data, how = 'inner', left_on = 'address', \
    right_on = 'address',  copy = False)

address_data.drop_duplicates(subset = 'ticket_id', inplace = True)
address_data.drop(labels = 'address', axis = 1, inplace = True)


blight_data.dropna(axis = 0,inplace = True)

blight_data = blight_data.merge(address_data, how = 'inner', left_on = 'ticket_id',\
     right_on = 'ticket_id', copy = False)

blight_data.set_index('ticket_id', inplace = True)
X = blight_data.drop(labels= 'compliance', axis  = 1)
Y = blight_data['compliance']

#End pre-processing; Do cross-validation:

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

cols_to_keep = ['ticket_id','fine_amount','late_fee']
test_data = pd.read_csv( 'test.csv', usecols = cols_to_keep )
gbc = GradientBoostingClassifier(n_estimators = 7, learning_rate = 1).fit(X,Y)

test_data = test_data.merge(address_data, how = 'left', left_on = 'ticket_id',\
     right_on = 'ticket_id', copy = False)

for i in range(len(test_data['ticket_id'])):
    if np.isnan(test_data['lat'].iloc[i]):
        print(test_data.iloc[i])

test_data.set_index('ticket_id', inplace = True)

test_probs = gbc.predict_proba(test_data)

test_data['test_probs'] = test_probs[:,1]
