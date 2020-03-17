import requests
import pandas as pd
import csv


def get_lat_lons(address):

    '''
    Returns the latitude and longitude of an address by using the Google maps
    API.

    Accesses Google Map's API. Requires you to replace your Google Maps API key
    in the 'ID' string. Uses the requests library to pull the geocode information
    for the address in the string 'address', which can be in an address format
    that you would use in a google search for an address.

    Args:
        address: string of an address whose latitude and longitude coordinates
        we want to find.

    Returns:
        Tuple of coordinates. Latitude is the first component and longitude is
        the second component.

    Example:
        get_lat_lons('18309 evergreen, Detroit MI')
        out: (42.423913,-83.238867)
    '''

    geocode_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    ID = 'your_google_maps_ID_key_here'

    print('Retrieving latitude and longitude from ', address)
    req = requests.get(geocode_URL, params = {'address':address, 'key':ID})
    data = req.json()

    lat = data['results'][0]['geometry']['location']['lat']
    lon = data['results'][0]['geometry']['location']['lng']
    return (lat, lon)


def get_geocoded_addresses():

    '''
    Pulls current addresses for which we have saved latitude/longitude data.

    Looks up currently saved addresses which have latitude/longitude data in the
    file 'latlons.csv' and appends them to a list.

    Returns:
        List of strings containing addresses that have already been geocoded.
    '''

    addresses = []
    with open('latlons.csv') as csvfile:
        for row in csvfile:
            comps = row.split(',')
            address = comps[0]+','+comps[1]
            addresses.append(address[1:-1])

    addresses = addresses[1:]
    return addresses

def get_addresses_to_geocode(old_adds):

    '''
    Creates a list of addresses which we will iterate over to find corresponding
    latitude/longitude coordinates.

    Uses the file 'addresses.csv' to create a list of addresses that we want to
    geocode. Some of these addresses have already been geocoded. Therefore, we 
    must remove these from the current list. We prune the list by converting 
    it to a set and take the set difference with the addresses for which the lat 
    lon data is known. Then we return this list of addresses which we want to 
    geocode. 

    Args:
        old_adds: a list of strings which contain addresses that we want to purge 
        from the current list of addresses. 

    Returns:
        addresses: a list of strings containing addresses which we want to geocode 
        and have not already done so. 

    '''

    addresses = set()
    with open('addresses.csv') as csvfile:
        for row in csvfile:
            comps = row.split(',')
            address = comps[-2]+','+comps[-1]
            addresses.add(address[1:-2])

    addresses = addresses.difference(set(old_adds))
    addresses = list(addresses)

    return addresses

def initialize():

    '''
    Returns an empty Pandas dataframe with columns given by 'address', 'lat', and 
    'lon' which will hold the corresponding address string, latitude, and 
    longitude of the address, respectively. 

    Also initializes the count to zero.
    '''

    df = pd.DataFrame(columns = ['address', 'lat', 'lon'])
    count = 0

    return (count, df)


geocoded_adds = get_geocoded_addresses()
addresses = get_addresses_to_geocode(geocoded_adds)
(count, to_save) = initialize()

#parameters used to control access to Google's API
address_per_save = 10
number_of_addresses = 1000

for address in addresses:
    count = count+1
    try:
        (lat, lon) = get_lat_lons(address)
        to_save = to_save.append({'address':address,'lat': lat, 'lon': lon},ignore_index = True)
    except:
        print('Error trying to geocode: '+address)
        break

    if count == address_per_save:
        print('Saving geocoded addresses...')
        to_save.to_csv('my_latlons.csv',header = False,index = False,
                                mode = 'a')
        (count, to_save) = initialize()
