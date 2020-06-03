import pandas
import numpy as np
import os

df_cases = pandas.read_csv('cases-2june2020.tsv', delimiter='\t', usecols=range(1,7))

# clean up some of the cases
mask = np.where(df_cases['City']!='Nationwide')

df_cases = df_cases.iloc[mask]

# TODO: replace city abbreviations, irregularities to help with lookups.

df_cases['City'] = df_cases['City'].str.lower()
df_cases['State'] = df_cases['State'].str.lower()

# a bunch of not-inline-replacements
df_cases.replace('nyc', 'new york city', inplace=True)
df_cases.replace('los angeles (van nuyes)', 'los angeles', inplace=True)
df_cases.replace('altanta', 'atlanta', inplace=True)
df_cases.replace('west philadelphia', 'philadelphia', inplace=True)

citystates = df_cases[['City', 'State']].values

# get latlon lookup table if it exists, and make a dictionary.
if os.path.exists('latlon_lookup.tsv'):
    import pandas
    df = pandas.read_csv('latlon_lookup.tsv', delimiter='\t')
    latlon_lookup = {', '.join((c,s)) : (x,y) for (c,s,x,y) in df.values}
else:
    latlon_lookup = {}
