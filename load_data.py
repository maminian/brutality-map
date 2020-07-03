import pandas
import numpy as np
import os

# TODO: switch from Basemap to cartopy
from mpl_toolkits.basemap import Basemap

# load data
df_orig = pandas.read_excel('GeorgeFloyd Protest - police brutality videos on Twitter.xlsx', skiprows=6)
df_cases = pandas.read_excel('GeorgeFloyd Protest - police brutality videos on Twitter.xlsx', skiprows=6)


end_idx = 1159 # manual; temporary while spreadsheet is non-rectangular.
df_cases = df_cases.iloc[:end_idx]

# TODO: replace city abbreviations, irregularities to help with lookups.

df_cases['City'] = df_cases['City'].str.lower()
df_cases['State'] = df_cases['State'].str.lower()

#######
# clean up some of the cases.....

# sorry Alaska, Hawaii, Puerto Rico, Canada :(
# Still need to get a better mapping tool to include them.
# excluding those two is bad!
excludes = ['uk', 'ak', 'hi', 'pr', 'mp', 'vi', 'as', 'gu', 'quebec canada', 'national']

for e in excludes:
    mask = np.where(df_cases['State'].values!=e)[0]
    df_cases = df_cases.iloc[mask]
#
mask = np.where(df_cases['City'].values!='Nationwide')

df_cases = df_cases.iloc[mask]



# string "NA" and similar should be replaced by np.nan to support later code.
df_cases['TGD Number'].replace('NA', np.nan, inplace=True)
df_cases['TGD Number'].replace('NA.1', np.nan, inplace=True)
df_cases['TGD Number'].replace('NA2', np.nan, inplace=True)




# strip any leading/trailing white space
df_cases['City'] = df_cases['City'].apply(lambda x: x.strip() if isinstance(x, str) else x)
df_cases['State'] = df_cases['State'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# a bunch of not-inline-replacements
df_cases.replace('nyc', 'new york city', inplace=True)
df_cases.replace('los angeles (van nuyes)', 'los angeles', inplace=True)
df_cases.replace('long beach', 'los angeles', inplace=True)
df_cases.replace('hollywood', 'los angeles', inplace=True)
df_cases.replace('altanta', 'atlanta', inplace=True)
df_cases.replace('west philadelphia', 'philadelphia', inplace=True)
df_cases.replace('cincinnatti', 'cincinnati', inplace=True)
df_cases.replace('cincinatti','cincinnati',inplace=True)
df_cases.replace(':as vegas', 'las vegas', inplace=True)
df_cases.replace('fredricksburg', 'fredericksburg', inplace=True)
df_cases.replace('atlanda', 'atlanta', inplace=True)
df_cases.replace('philaeslphia', 'philadelphia', inplace=True)
df_cases.replace('shanandoah county', 'shenandoah county', inplace=True)
df_cases.replace('albequrque', 'albuquerque', inplace=True)
df_cases.replace('cinciatti', 'cincinnati', inplace=True)
df_cases.replace('cinciatti', 'cincinnati', inplace=True)
df_cases.replace('for lauderdale', 'fort lauderdale', inplace=True)
df_cases.replace('for wayne', 'fort wayne', inplace=True)
df_cases.replace('minneaplois', 'minneapolis', inplace=True)


df_cases.replace('fairfax county', 'fairfax', inplace=True)


# incorrect states...
idx = (df_cases['City'].values=='charlotte')
df_cases.iloc[idx] = df_cases.iloc[idx].replace('nv','nc')
df_cases.iloc[idx] = df_cases.iloc[idx].replace('ca','nc')

idx = (df_cases['City'].values=='albuquerque')
df_cases.iloc[idx] = df_cases.iloc[idx].replace('nw','nm', inplace=True)




df_cases.replace('cd', 'dc', inplace=True)
df_cases.replace('k', 'ky', inplace=True)
df_cases['Doucette Text'].replace(np.nan, '[no description]', inplace=True)

# group by incident
def fetch_incident(ind):
    gdn = df_cases.loc[ind]['TGD Number']
    if not np.isnan(gdn):
        candidate = str(gdn).split('.')[0]
    else:
        # seems to work universally; but can catch any quirk cases as "other" for now.
        candidate = 'other'
    #
    return candidate
#

grouper = df_cases.groupby(fetch_incident)

# just remake manually, dataframe index being a pain.

#incidents = np.tile('', (df_cases.shape[0],))
#df_cases['incident'] = incidents
#for g,df_s in grouper:
#    df_cases.loc[df_s.index]['incident'] = g
##

incidents = [str(gdn).split('.')[0] if not np.isnan(gdn) else 'other' for gdn in df_cases['TGD Number'].values]
df_cases['incident'] = incidents

###################
#
# get latlon lookup table if it exists, and make a dictionary.
# (you need to run fetch_location.py manually if it does not exist.)
#
if os.path.exists('latlon_lookup.tsv'):
    import pandas
    df = pandas.read_csv('latlon_lookup.tsv', delimiter='\t')
    latlon_lookup = {', '.join((c,s)) : (x,y) for (c,s,x,y) in df.values}
else:
    latlon_lookup = {}

##################
#
# Replace missing/lack of youtube  links with np.nan so that 
# the HTML generator (correctly) ignores them.
#
has_youtubes = np.zeros(df_cases.shape[0], dtype=bool)
for j,v in enumerate(df_cases['YouTube'].values):
    if isinstance(v,str):
        if 'http' in v:
            has_youtubes[j] = True
#
df_cases['YouTube'][np.logical_not(has_youtubes)] = np.nan

######################
#
# load basemap files for county/state level outlines.
#
from mpl_toolkits.basemap import Basemap
state_map = Basemap()
state_map.readshapefile('state_shp/cb_2018_us_state_20m', 'states', drawbounds=False)
# for now don't care about which state is which; just draw boundaries.
state_xs = []
state_ys = []

for si,info in zip(state_map.states,state_map.states_info):
    if info['STUSPS'].lower() in excludes:
        continue
    _xs = [sii[0] for sii in si]
    _ys = [sii[1] for sii in si]
    state_xs.append(_xs)
    state_ys.append(_ys)
#

county_map = Basemap()
county_map.readshapefile('county_shp/cb_2018_us_county_20m', 'counties', drawbounds=False)
# for now don't care about which state is which; just draw boundaries.
county_xs = []
county_ys = []

# for ci,info in zip(county_map.counties,county_map.counties_info):
#     if info['STUSPS'].lower() in excludes:
#         continue
#     _xs = [sii[0] for sii in si]
#     _ys = [sii[1] for sii in si]
#     county_xs.append(_xs)
#     county_ys.append(_ys)

# misc
citystates = df_cases[['City', 'State']].values
