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

	return data

blight_data = get_time_features('ticket_issued_date', 'issued', blight_data)
blight_data = get_time_features('hearing_date', 'hearing', blight_data)



#standardize the string data by making everything lowercase and removing punctuation

def standardize_text(index, data):

	standard = data[ index ].astype(str).map(lambda x: x.lower().strip())
	standard = standard.map(lambda x: re.sub(r'[^\w\s]','', x))

	data[ index ] = standard

	return data

blight_data = standardize_text('agency_name', blight_data)
blight_data = standardize_text('inspector_name', blight_data)
blight_data = standardize_text('violator_name', blight_data)

#change `neighborhood city halls` to `department of public works` in `agency_name` feature
index_ = blight_data[blight_data['agency_name']=='neighborhood city halls'].index[0]
blight_data.at[index_, 'agency_name'] = 'department of public works'

#bin infrequenct violation codes into an `other` category
codes_to_keep = blight_data['violation_code'].value_counts().sort_values()[-14:].index.values
blight_data['violation_code'] = blight_data['violation_code'].apply(lambda x: x if x in codes_to_keep else 'other' )


#for inspectors that gave out more than 200 tickets, replace the `inspector_name` feature with 
#that inspectors percent compliance. For inspectors who gave out at most 200 tickets, just 
#replace their compliance percentage with the compliance percentage of all tickets.
val_counts =  blight_data['inspector_name'].value_counts()
grouping = blight_data.groupby('inspector_name')

inspector_compliance_perc = grouping['compliance'].mean()
blight_data['inspector_perc_success'] = blight_data['inspector_name'].apply(lambda x: inspector_compliance_perc.loc[x] if (val_counts.loc[x]>200) else 0.07)
blight_data.drop(columns = 'inspector_name', inplace = True)


#use count encoding to replace `violator_name` feature with the count of violations from that 
#particular violator. 
val_counts =  blight_data['violator_name'].value_counts()

blight_data['violator_count'] = blight_data['violator_name'].apply(lambda x: val_counts.loc[x])
blight_data.drop(columns = 'violator_name', inplace = True)


X = blight_data.drop(labels= 'compliance', axis  = 1)
Y = blight_data['compliance']

#use one-hot encoding for `agency_name` and `disposition`. 
X = pd.get_dummies(X, columns = ['agency_name', 'disposition','violation_code'])



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



