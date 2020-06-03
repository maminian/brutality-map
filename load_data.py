import pandas
import numpy as np

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

citystates = df_cases[['City', 'State']].values



# State ID numbers
df_statecodes = pandas.read_excel('state-geocodes-v2016.xls', skiprows=5).iloc[:,2:]
# convert to dictionary
fp2state = {
    str(row[0]).zfill(2) : row[1] for row in df_statecodes.values
}

# https://www.census.gov/geographies/reference-files/time-series/geo/name-lookup-tables.2010.html
