import numpy as np
import pandas as pd
import re

cols_to_keep = ['ticket_id','fine_amount','late_fee','compliance','inspector_name', 
				'violator_name','agency_name','ticket_issued_date','disposition',
				'violation_code','hearing_date']

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


#extract the month, day and weekday from the features that are in  date/time format:

def get_time_features(index,label_flag, data):

	datetime = pd.to_datetime(data[ index ].astype(str), infer_datetime_format = True).dt

	data[label_flag+'_month'] = datetime.month
	data[label_flag+'_day'] = datetime.day
	data[label_flag+'_weekday'] = datetime.weekday
	data.drop(columns = index, inplace = True)

get_time_features('ticket_issued_date', 'issued', blight_data)
get_time_features('hearing_date', 'hearing', blight_data)



#standardize the string data by making everything lowercase and removing punctuation

def standardize_text(index, data):

	standard = data[ index ].astype(str).map(lambda x: x.lower().strip())
	standard = standard.map(lambda x: re.sub(r'[^\w\s]','', x))

	data[ index ] = standard


standardize_text('agency_name', blight_data)
standardize_text('inspector_name', blight_data)
standardize_text('violator_name', blight_data)




X = blight_data.drop(labels= 'compliance', axis  = 1)
Y = blight_data['compliance']


from sklearn.preprocessing import OrdinalEncoder

enc = OrdinalEncoder()
fit_data = enc.fit_transform(X[['disposition','violation_code','inspector_name','violator_name','agency_name']])
X[['disposition','violation_code','inspector_name','violator_name','agency_name']] = fit_data


print("End preprocessing, doing grid search for best parameters...")

#end preprocessing; Do grid search:
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier

grid_values = {'n_estimators': [3,4,5,6,7,8,9,10], 'learning_rate': [1,0.1,0.01]}

gbc = GradientBoostingClassifier()

roc_grid = GridSearchCV(gbc, param_grid = grid_values, scoring = 'roc_auc', cv = 5)

roc_grid.fit(X,Y)

grid_data = pd.DataFrame(roc_grid.cv_results_)
mean_test_scores = grid_data.set_index('params')['mean_test_score']

print(mean_test_scores.values.reshape(8,3))
