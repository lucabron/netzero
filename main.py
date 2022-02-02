# Packages used are numpy, pandas and bokeh. They can be found on pip and conda.
from os.path import dirname, join

import numpy as np
import pandas as pd
from bokeh.plotting import show, figure, output_file
from bokeh.models import CustomJS, ColumnDataSource
from bokeh.models import BasicTicker, Label, Span, Range1d
from bokeh.models import Select
from bokeh.models.tools import PanTool, SaveTool, WheelZoomTool, ResetTool
from bokeh.layouts import column

pd.set_option('max_columns', None)

#%%
#pd.read_csv(join(dirname(__file__), 'data/2015_weather.csv'))
df = pd.read_csv(join(dirname(__file__),'data','owid-co2-data.csv'))

#%%
# Exploration
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
 'trade_co2',
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
 'population',
 'gdp']]

# # delete irelevant countries
# ## Need to remove Bhutan and Suriname as they already reached net-zero.
# International transport
# Kuwaiti Oil Fires
# Panama Canal Zone
# French Equatorial Africa
# French West Africa

excluded = df[df['country'].isin(['Kuwaiti Oil Fires','Panama Canal Zone'])].index
df.drop(excluded, inplace=True)

print(df.head())
print(df.isnull().sum()) #There is missing data for CO2

#%%
# select most important columns
dfgraph = df[['country', 'year', 'co2']]

print(dfgraph.head())

#%%
# Countries with missing values for co2
print(dfgraph[pd.isnull(dfgraph['co2'])==True]) 
dfgraphtemp = dfgraph[pd.isnull(dfgraph['co2'])==True]
print('-------')
print(dfgraphtemp['country'].unique())

# # Countries with missing values
# "Cote d'Ivoire" #no data
# Palau #no data
# Eritrea #no data
# Marshall Islands #no data
# Micronesia #no data
# Namibia #no data

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
    for i in range(1,nb_years):
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
#Create column with co2 path for each country.
#Yearly reduction needed from 2015 to 2050
aim_reduction = 1/(2050-2015)

# Cleanup
dfgraphfc = dfgraphfc.sort_values(by=['country','year'])
dfgraphfc = dfgraphfc.reset_index(drop=True)

# Getting the 2015 value
dfgraphfc['co2_path'] = dfgraphfc[dfgraphfc['year']==2015]['co2']
# Creating a temporary dataframe to only get the value for forecast and loop easier.
dfgraphfctemp = dfgraphfc[dfgraphfc['year']>=2015]

aim_reduction_abs = 0

# Calculating the 2016 to 2050 values based on the aim reduction.
for i in range(1,dfgraphfctemp.index.size):
    if pd.notnull(dfgraphfctemp.iat[i,3]):
        aim_reduction_abs = dfgraphfctemp.iat[i,3]*aim_reduction
    else:
        dfgraphfctemp.iat[i,3] = dfgraphfctemp.iat[i-1,3]-aim_reduction_abs

# get the value for each 2015 and complete the next 36 lines based on it.
#for y2015 in dfgraphfctemp[pd.notnull(dfgraphfctemp['co2_path'])==True]:
#    print(y2015)
        
# Merge dfgraphfctemp into dfgraphfc
dfgraphfc['co2_path'] = dfgraphfctemp['co2_path']

#%%
#Create Index (Maybe I should have created before. Lazy to refactor now.)
dfgraphfc = dfgraphfc.set_index('country')

#%%
#Bokeh
#transform pandas df into ColumnDataSource
source = ColumnDataSource(dfgraphfc)
render = ColumnDataSource({
        "year": dfgraphfc.loc['World']["year"],
        "co2": dfgraphfc.loc['World']["co2"],
        "co2_path": dfgraphfc.loc['World']["co2_path"],}
)

title = 'World'

# create a new plot (with a title) using figure
p = figure(aspect_ratio=2, sizing_mode='scale_height', title=title,
           x_range=Range1d(1980, 2050, bounds=(None,2050)),
           tools=[PanTool(dimensions='width'), SaveTool(), ResetTool()])

# add three lines renderer
p.line("year", "co2", source=render, line_width=2, legend_label='CO2 emissions', line_alpha=0.9)
p.line("year", "co2_path", source=render, line_width=2, color = 'red',
       legend_label='Path to netzero in 2050', line_alpha=0.9)
COP21 = Span(location=2015, dimension='height', line_color='green',
             line_dash='dotted', line_width=2)
p.add_layout(COP21)

# Appearance
p.xaxis.ticker = BasicTicker(base=5, max_interval = 5)
p.xaxis.axis_label = 'Year'
p.yaxis.axis_label = 'CO2 emissions [mio of tons]'
p.add_layout(Label(x=2016, text='COP21', text_color='green'))
    
# Dropdown     
select = Select(title="Country:", value="World", options=list_countries, width = 300)

# Interactively change the lines. It uses javascript callbacks
callback_df = CustomJS(args = dict(render=render, source=source, select=select),
code="""
//Filter the countries
var data=source.data;
var country=data['country'];

var a=data['year'];
var b=data['co2'];
var c=data['co2_path'];

var f=select.value;

var x=[];
var y=[];
var z=[];

for(var i=0;i<a.length; i++){
        if(country[i]==f){
                         x.push(a[i]);
                         y.push(b[i]);
                         z.push(c[i]);
                    }
        }

render.data['year']=x;
render.data['co2']=y;
render.data['co2_path']=z;

// Apply change
render.change.emit();
""")

select.js_on_change("value", callback_df)
select.js_link('value', p.title, 'text')

# This code can replace js callback if bokeh server is ever used
#def update_plot(attr, old, new):
#    p.title.text = dfgraphfc[dfgraphfc['country']==select.value]
#    country_selected = select.value
#    select.options = list(df[country_selected].values)
    
layout = column(select, p)

output_file(join(dirname(__file__),'graph.html'), title='Bokeh plot: Objective net zero carbon emissions 2050')

show(layout)
#curdoc().add_root(layout) # show the results if using a bokeh server
