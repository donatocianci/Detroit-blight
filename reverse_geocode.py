import requests
import pandas as pd
import csv


def get_address(lat, lng):

    '''
    Returns the formatted address of the nearest property with GPS coordinates
    given by (lat, lng) using Google Map's API.

    Accesses Google Map's API. Requires you to replace your Google Maps API key
    in the 'ID' string. Uses the requests library to pull the formatted address
    information for the nearest address with coordinates (lat, lon).

    Args:
        lat: float of the latitude of the location (in degrees)
        lng: float of the longitude of the location (in degrees)

    Returns:
        String of formatted address nearest the location (lat, lon)

    Example:
        get_address(42.326055136000036, -83.06475928299993)
        out: '1628 Howard St, Detroit, MI 48216, USA'
    '''
    
    geocode_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    ID = 'your_google_API_key_here'

    #print statement for debugging
    #print('Retrieving address for ', (lat, lng))
    
    gps = str(lat)+','+str(lng)
    req = requests.get(geocode_URL, params = {'latlng': gps, 'key': ID, 'result_type': 'street_address'})
    data = req.json()
    

    return data['results'][0]['formatted_address']

def get_geocoded_tickets():

    '''
    Pulls current tickets for which we have saved address data.

    Looks up currently saved ticket IDs which have address data in the
    file 'address_to_parcel.csv' and appends them to a list.

    Returns:
        List of strings containing ticket IDs that have already been reverse geocoded.
    '''

    tickets = []
    with open('address_to_parcel.csv') as csvfile:
        for row in csvfile:
            comps = row.split(',')
            ticket = comps[0]
            tickets.append(ticket)

    return tickets


def get_tickets_to_geocode(old_tics):

    '''
    Creates a list of ticket IDs which we will iterate over to find corresponding
    address data.

    Uses the file 'need_parcels.csv' to create a list of ticket IDs which we want to 
    reverse geocode. Some of these IDs have already been reverse geocoded. Therefore, we 
    must remove these from the current list. We prune the list by converting 
    it to a set and take the set difference with the ticket ID for which the address
     data is known. Then we return this list of addresses which we want to 
    geocode. 

    Args:
        old_tics: a list of strings which contain ticket IDs that we want to purge 
        from the current list of IDs. 

    Returns:
        a list of strings containing ticket IDs which we want to reverse geocode
        and have not already done so.

    '''
    tickets = set()

    with open('need_parcels.csv') as csvfile:
        for row in csvfile:
            comps = row.split(',')
            ticket = comps[0]
            tickets.add(ticket)

    tickets = tickets.difference(set(old_tics))
    tickets.remove('ticket_id')
    
    return list(tickets)

def initialize():

    '''
    Returns an empty Pandas dataframe with columns given by 'ticket_id' and 
    'address' which will hold the corresponding address string for a given 
    ticket_id. 

    Also initializes the count to zero.
    '''

    df = pd.DataFrame(columns = ['ticket_id', 'address'])
    count = 0

    return (count, df)

geocoded_tickets = get_geocoded_tickets()
ticket_to_gps = pd.read_csv('need_parcels.csv').set_index('ticket_id')
tickets = get_tickets_to_geocode(geocoded_tickets)
(count, to_save) = initialize()

#parameters used to control access to Google's API
address_per_save = 199
number_of_addresses = 2000

if number_of_addresses > len(tickets):
    if len(tickets) == 0:
        print("No more tickets left to decode.")
        quit()
    
    else: 
        print("Only "+str(len(tickets))+" addresses left to be reverse geocoded")
        number_of_addresses = len(tickets)

for ticket in tickets[:number_of_addresses]:
    count = count+1
    try:
        lat = ticket_to_gps.loc[ int(ticket), 'Y']
        lng = ticket_to_gps.loc[ int(ticket), 'X']
        add = get_address(lat, lng)
        to_save = to_save.append({'ticket_id':ticket,'address': add}, ignore_index = True)
    except:
        print('Error trying to reverse geocode: '+ticket)
        break

    if count == address_per_save:
        print('Saving addresses...')
        to_save.to_csv('address_to_parcel.csv',header = False,index = False,
                                mode = 'a')
        (count, to_save) = initialize()

if to_save.size > 0:
    print('Saving last of addresses...')
    to_save.to_csv('address_to_parcel.csv',header = False,index = False,
                                mode = 'a')

