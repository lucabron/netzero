import numpy as np
import pandas as pd
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import TapTool, CustomJS, ColumnDataSource, HoverTool, BasicTicker, Label

pd.set_option('max_columns', None)

#%%
df = pd.read_csv('data/owid-co2-data.csv')

#%%
print(df.columns)
print(df['country'].unique())
print(df.isnull().sum())

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
 'total_ghg',
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
# # delete irelevant countries
# ## Need to remove Bhutan and Suriname as they already reached net-zero.
# International transport
# Kuwaiti Oil Fires
# Panama Canal Zone
# French Equatorial Africa
# French West Africa
# =============================================================================
excluded = df[df['country'].isin(['Kuwaiti Oil Fires','Panama Canal Zone'])].index
df.drop(excluded, inplace=True)

print(df.head())
print(df.isnull().sum()) #There is missing data for CO2

df['value_type'] = 'observed' #as opposed to the forecast one's

#%%
df80 = df[df['year']>=1980]
# select important columns
df80 = df80[['country', 'year', 'co2']]

print(df80.head())

#%%
print(df80[pd.isnull(df80['co2'])==True]) 
df80temp = df80[pd.isnull(df80['co2'])==True]
print(df80temp['country'].unique())

# =============================================================================
# # Countries with missing values
# "Cote d'Ivoire" #no data
# Palau #no data
# Eritrea #no data
# Marshall Islands #no data
# Micronesia #no data
# Namibia #no data
# =============================================================================

df80temp = df80[df80['year'].isin([2015,2019])]
print(df80temp[df80temp['co2'].isna()])

#%%
#Ivory Coast and Palau have missing data for 2015.
#They have for 2017, so I might add them back later.
df80 = df80[-df80['country'].isin(["Cote d'Ivoire","Palau"])]
# df80 = df80.groupby('country')

#%%
#create the new rows for the forecast
df80columns_list = list(df80)
list_countries = df80temp['country'].unique()
current_year = df80['year'].max()
nb_years = 2050-current_year+1 #number of years to forecast
new_df = df80.copy()
data = []

for country in ['South Korea']: #list_countries:
    print(country)
    for i in range(nb_years):
        print(i)
        values = [ #'iso_code',
            country, #'country',
            current_year+i,#'year',
            #'co2',
            #'co2_growth_prct',
            #'co2_growth_abs',
            #'co2_per_capita',
            #'co2_per_gdp',
            #'share_global_co2',
            #'cumulative_co2',
            #'share_global_cumulative_co2',
            #'ghg_per_capita',
            #'methane',
            #'methane_per_capita',
            #'nitrous_oxide',
            #'nitrous_oxide_per_capita',
            #'population',
            #'gdp',
            #'value_type'
            ]
        zipped = zip(df80columns_list, values)
        row_dict = dict(zipped)
        data.append(row_dict)
df80fc = new_df.append(data, True)
print(df80fc)

#%%
df80fc = df80fc[df80fc['country']=='Switzerland']

#%%
#transform pandas df into ColumnDataSource 
source = ColumnDataSource(df80fc)
hover = HoverTool(tooltips=[("Country", "@country"),])
callback = CustomJS(code="alert('you tapped a circle!')")
tap = TapTool(callback=callback)

# create a new plot (with a title) using figure
p = figure(plot_width=1200, plot_height=550, title="Switzerland CO2 emissions")

# add a line renderer
p.line("year", "co2" , line_width=2, source=source, legend_label='CO2 emissions')
p.line([2015, 2050], [df80fc.loc[df80fc['year'] == 2015]['co2'],0],
       line_width=2, color = 'red', legend_label='Path to netzero in 2050')
COP21 = Span(location=2015, dimension='height', line_color='green',
             line_dash='dotted', line_width=2)
p.add_layout(COP21)
p.xaxis.ticker = BasicTicker(base=5)
p.xaxis.axis_label = 'Year'
p.yaxis.axis_label = 'CO2 emissions [mio of tons]'
p.add_layout(Label(x=2016, text='COP21', text_color='green'))

show(p) # show the results

#%%
print(df80)