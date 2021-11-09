import numpy as np
import pandas as pd
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import TapTool, CustomJS, ColumnDataSource, HoverTool
pd.set_option('max_columns', None)

#%%
df = pd.read_csv('data/owid-co2-data.csv')

#%%
print(df.columns)
print(df['country'].unique())
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
# I don't know what theses labels means so I comment them out for now.
#  'primary_energy_consumption',
#  'energy_per_capita',
#  'energy_per_gdp',
 'population',
 'gdp']]

# =============================================================================
# # select important columns
# ## Need to remove Bhutan and Suriname as they already reached net-zero.
# International transport
# Kuwaiti Oil Fires
# Panama Canal Zone
# French Equatorial Africa
# French West Africa
# =============================================================================

print(df.head())
#%%
df1990 = df[df['year']>=1990]
#df1990 = df1990[df1990['country']=='World']
#df1990 = df1990.groupby(('country'))

print(df1990.head())

#%%
print(df1990[pd.isnull(df1990['co2'])==True]) #There is missing data for CO2

#%%
df1990temp = df1990[df1990['year'].isin([2015,2019])]
print(df1990temp[df1990temp['co2'].isna()])

#%%
#Ivory Coast and Palau have missing data for 2015.
#They have for 2017, so I might add them back later.
df1990 = df1990[-df1990['country'].isin(["Cote d'Ivoire","Palau"])]
print(df1990)

#%%
df2019 = df[df['year']==2019]
df2019temp = df2019[['country','year','co2']]

print(df1990[pd.isnull(df1990['co2'])==True])

# =============================================================================
# #missing values
# "Cote d'Ivoire" #no data
# Palau #no data
# Eritrea #no data
# Marshall Islands #no data
# Micronesia #no data
# Namibia #no data
# =============================================================================

#%%
dftemp = df1990[pd.isnull(df1990['co2'])==True]
print(dftemp['country'].unique())

#%%
#transform pandas df into ColumnDataSource 
source = ColumnDataSource(df1990)
hover = HoverTool(tooltips=[("Country", "@country"),])
callback = CustomJS(code="alert('you tapped a circle!')")
tap = TapTool(callback=callback)

# create a new plot (with a title) using figure
p = figure(plot_width=1200, plot_height=550, tools=[hover,tap], title="World Co2 emissions")

# add a line renderer
p.line("year", "co2" , line_width=2, source=source)
p.xaxis.axis_label = 'Year'
p.yaxis.axis_label = 'Co2'

show(p) # show the results

#%%
print(df1990)