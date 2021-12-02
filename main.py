# Packages used are numpy, pandas and bokeh. They can be found on pip and conda.
from os.path import dirname, join

import numpy as np
import pandas as pd
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import TapTool, CustomJS, ColumnDataSource, HoverTool
from bokeh.models import BasicTicker, Label, Span, Range, Range1d, CustomJS
from bokeh.models import Select
from bokeh.models.tools import PanTool, SaveTool, WheelZoomTool, ResetTool, HoverTool
from bokeh.layouts import column

pd.set_option('max_columns', None)

#%%
#pd.read_csv(join(dirname(__file__), 'data/2015_weather.csv'))
df = pd.read_csv(join(dirname(__file__),'data','owid-co2-data.csv'))

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
# select important columns
dfgraph = df[['country', 'year', 'co2']]

print(dfgraph.head())

#%%
print(dfgraph[pd.isnull(dfgraph['co2'])==True]) 
dfgraphtemp = dfgraph[pd.isnull(dfgraph['co2'])==True]
print('-------')
print(dfgraphtemp['country'].unique())

# =============================================================================
# # Countries with missing values
# "Cote d'Ivoire" #no data
# Palau #no data
# Eritrea #no data
# Marshall Islands #no data
# Micronesia #no data
# Namibia #no data
# =============================================================================
print('-------')
dfgraphtemp = dfgraph[dfgraph['year'].isin([2015,2019])]
print(dfgraphtemp[dfgraphtemp['co2'].isna()])

#%%
#Ivory Coast and Palau have missing data for 2015.
#They have for 2017, so I might add them back later.
dfgraph = dfgraph[-dfgraph['country'].isin(["Cote d'Ivoire","Palau"])]
# dfgraph = dfgraph.groupby('country')

#%%
#create the new rows for the forecast
dfgraphcolumns_list = list(dfgraph)
list_countries = list(dfgraphtemp['country'].unique())
current_year = dfgraph['year'].max()
nb_years = 2050-current_year+1 #number of years to forecast
dfgraphfc = dfgraph.copy()
data = []

for country in list_countries: #list_countries:
    print(country)
    for i in range(nb_years):
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
        zipped = zip(dfgraphcolumns_list, values)
        row_dict = dict(zipped)
        data.append(row_dict)
dfgraphfc = dfgraphfc.append(data, True)
print(dfgraphfc)

#%%
#Bokeh

#Default
#dfgraphfc = dfgraphfc[dfgraphfc['country']=='World']

#transform pandas df into ColumnDataSource 
title = "World"
source = ColumnDataSource(dfgraphfc)
render = ColumnDataSource(
    {
        "year": dfgraphfc[dfgraphfc['country']=='World']["year"],
        "co2": dfgraphfc[dfgraphfc['country']=='World']["co2"],
    }
)

# create a new plot (with a title) using figure
p = figure(plot_width=1200, plot_height=550, title=title,
           x_range=Range1d(1980, 2050, bounds=(None,2050)),
           tools=[PanTool(dimensions='width'), SaveTool(), WheelZoomTool(), ResetTool()])

# add a line renderer
p.line("year", "co2", source=render, line_width=2, legend_label='CO2 emissions', line_alpha=0.5)
#p.line([2015, 2050], [dfgraphfc.loc[dfgraphfc['year'] == 2015]['co2'],0],
#       line_width=2, color = 'red', legend_label='Path to netzero in 2050')
COP21 = Span(location=2015, dimension='height', line_color='green',
             line_dash='dotted', line_width=2)
p.add_layout(COP21)

p.xaxis.ticker = BasicTicker(base=5)
p.xaxis.axis_label = 'Year'
p.yaxis.axis_label = 'CO2 emissions [mio of tons]'
p.add_layout(Label(x=2016, text='COP21', text_color='green'))
    
#dropdown     
select = Select(title="Country:", value="World", options=list_countries, width = 300)

#def update_plot(attr, old, new):
#    p.title.text = dfgraphfc[dfgraphfc['country']==select.value]
#    country_selected = select.value
#    select.options = list(df[country_selected].values)

callback_data = CustomJS( args = dict(render=render, source=source, select=select),
code="""
//Filter the countries
var data=source.data;
var country=data['country'];

var a=data['year'];
var b=data['co2'];

var f=select.value;

var x=[];
var y=[];

for(var i=0;i<a.length; i++){
        if(country[i]==f){
                         x.push(a[i]);
                         y.push(b[i]);
                    }
        }

render.data['year']=x;
render.data['co2']=y;

// Apply change
render.change.emit();
""")

select.js_on_change("value", callback_data)
select.js_link('value', p.title, 'text')
    
layout = column(select, p)

show(layout)
#curdoc().add_root(layout) # show the results
