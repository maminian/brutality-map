def fetch(entries, verbosity=1):
    '''
    looks up tuples of (city,state) strings coming from load_data,
    and returns a latitude/longitude pair of the "expected" center
    of the city.

    Input:
        entries: list-like; each entry must itself be a list-like of the form of
            two strings ["city", "state"]; e.g. ["flint", "mi"]. I expect
            the format can be flexible, but this is up to the OpenCage API.
    Output:
        latlon: numpy array shape (n,2) of the center of the bounding box
            for each location.

    Loosely follows https://amaral.northwestern.edu/blog/getting-long-lat-list-cities

    '''
    if isinstance(entries,str):
        print('Warning: expecting list-like of cities; will return a list of a single tuple.')
        entries = [entries]
    #
    from opencage.geocoder import OpenCageGeocode
    import opencage_apikey # get your own.
    import numpy as np

    geocoder = OpenCageGeocode(opencage_apikey.key)

    import pdb
    #pdb.set_trace()
    latlons = np.zeros((len(entries), 2), dtype=float)
    for j,query in enumerate(entries):
#        query = ', '.join(cs)
        try:
            results = geocoder.geocode(query)
        except:
            results=[]
        #
        if len(results)==0:
            print("Warning: failed to find data for entry %s, using NaN coordinates."%query)
            latlon = np.array([np.nan,np.nan])
        else:
            ne = results[0]['bounds']['northeast']
            sw = results[0]['bounds']['southwest']
            latlon = np.mean([[ne['lat'], ne['lng']],[sw['lat'],sw['lng']]], axis=0)
        #
        latlons[j] = latlon
        if verbosity>0:
            print(query, latlon)
    #
    return latlons
#

def create_lookup(entries,fname='city_latlon.tsv', verbosity=1):
    '''
    Calls fetch() in the same module, and
    saves the result in a simple tab-separated file for future use.
    Makes sure the queries are unique.

    Uses pandas to deal with mixed types.
    '''
    import os
    if os.path.exists(fname):
        i = input('lookup table %s already exists; are you sure you want to continue? file will be overwritten (y/n)'%fname)
        if i.lower()!='y':
            print('Aborting.')
            return
    #
    import pandas
    import numpy as np
    queries = [', '.join(cs) for cs in entries]
    unique_queries = np.unique(queries)

    results = fetch(unique_queries, verbosity=verbosity)

    # split city and state up again...
    citystates = np.array([[e.strip() for e in uq.split(',')] for uq in unique_queries])

    latlon_data = np.hstack([citystates, results])

    df = pandas.DataFrame(data=latlon_data, columns=['city','state', 'lat', 'lon'])
    df.to_csv('latlon_lookup.tsv', sep='\t', index=None)
    return
#

if __name__=="__main__":
    '''
    Create the lookup table.
    '''
    import load_data
    create_lookup(load_data.citystates)
