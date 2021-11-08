import numpy as np
import pandas as pd
from bokeh.io import show
from bokeh.plotting import figure

#%%
df = pd.read_csv('data/owid-co2-data.csv')

#%%
# select important columns
df = df[['iso_code',
 'country',
 'year',
 'co2',
 'co2_growth_prct',
 'co2_growth_abs',
 'co2_per_capita',
 'co2_per_gdp',
 'share_global_co2',
 'cumulative_co2',
 'share_global_cumulative_co2',
 'ghg_per_capita',
 'methane',
 'methane_per_capita',
 'nitrous_oxide',
 'nitrous_oxide_per_capita',
 'primary_energy_consumption',
 'energy_per_capita',
 'energy_per_gdp',
 'population',
 'gdp']]

print(df)
#%%
df1990 = df[df['year']>=1990]

print(df1990)

#%%
df2019 = df[df['year']==2019]

print(df2019)
print(df2019[['country','co2_growth_prct']])

#%%
# create a new plot (with a title) using figure
p = figure(plot_width=1200, plot_height=550, title="My Line Plot")

# add a line renderer
p.line(df1990["year"], df1990["co2"] , line_width=2)
p.xaxis.axis_label = 'Year'
p.yaxis.axis_label = 'Co2'

show(p) # show the results

#%%
print(df1990["year"])