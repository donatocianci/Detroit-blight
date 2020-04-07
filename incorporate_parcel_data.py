import pandas as pd

parcel_cols_to_keep = ['address', 'parcel_number']
parcel_data = pd.read_csv('Parcels.csv', usecols = parcel_cols_to_keep)
parcel_data.drop_duplicates(inplace = True)
parcel_data.set_index('parcel_number', inplace = True)

parcel_data['address'] = parcel_data['address'].astype(str).map(lambda x: x.lower().strip())
parcel_data['address_no'] = parcel_data['address'].str.extract(r'^([0-9]+)')
parcel_data.dropna(inplace = True)
parcel_data['address_no'] = parcel_data['address_no'].astype(int)

tickets_no_parcel = pd.read_csv('address_to_parcel.csv', names = ['ticket_id', 'address'])
tickets_no_parcel['address'] = tickets_no_parcel['address'].astype(str).map(lambda x: x.lower().strip())

tickets_no_parcel['address_no'] = tickets_no_parcel['address'].str.extract(r'^([0-9]+)')
tickets_no_parcel['address'] = tickets_no_parcel['address'].astype(str).map(lambda x: x.split(',')[0])
tickets_no_parcel['address'] = tickets_no_parcel['address'].str.replace('^[0-9]+','',regex = True).str.strip()
tickets_no_parcel['address'] = tickets_no_parcel['address'].str.replace('[a-z]{1,3}$','',regex = True).str.strip()
tickets_no_parcel['address'] = tickets_no_parcel['address'].str.replace('^[a-z]{1} ','',regex = True).str.strip()

def find_nearby_parcel(row):
	index = row
	street_name = tickets_no_parcel['address'].loc[index]
	street_num = tickets_no_parcel['address_no'].loc[index]
	street_parcels = parcel_data[ parcel_data['address'].str.contains(street_name) ]
	
	if street_parcels.size>0:
		return street_parcels.loc[:,'address_no'].apply(lambda x: abs(x - int(street_num))).idxmin()
	else:
		return 'No_parcel_found'


tickets_no_parcel['parcel_no'] = tickets_no_parcel.index.map(find_nearby_parcel)
tickets_no_parcel.set_index('ticket_id', inplace = True)
tickets_no_parcel.drop(columns = ['address_no','address'], inplace = True)

tickets_no_parcel.to_csv(path_or_buf = 'ticket_id_to_parcel_dict.csv')
