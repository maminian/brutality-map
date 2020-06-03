import pandas

df_cases = pandas.read_csv('cases-2june2020.tsv', delimiter='\t', usecols=range(1,7))
