import pandas


df = pandas.read_csv('data/snooker/players_r.csv')

countries = df['country'].unique()

with open('data/snooker/countries.txt', 'w') as f:
    for country in countries:
        f.write(country + '\n')