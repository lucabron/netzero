# Packages used are numpy, pandas and bokeh. They can be found on pip and conda.
from os.path import dirname, join
import statistics as s

import numpy as np
import pandas as pd
from bokeh.plotting import show, figure, output_file
from bokeh.models import CustomJS, ColumnDataSource,BasicTicker, Label, Span
from bokeh.models import Range1d, Select
from bokeh.models.tools import SaveTool, HoverTool
from bokeh.layouts import column

# pd.set_option('max_columns', None)

#%%
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

#%%
# Delete irelevant countries by only keeping the ones who ratified the agreement
# and the ones with data
excluded = df[df['country'].isin(['Africa', 'Africa (GCP)', 'Aland Islands',
                                  'Anguilla',
                                  'Antarctica','Aruba', 'Asia',
                                  'Asia (GCP)', 'Asia (excl. China and India)',
                                  'Bermuda', 'Bonaire Sint Eustatius and Saba',
                                  'British Virgin Islands',
                                  'Central America (GCP)', 'Christmas Island',
                                  'Curacao', 'Eritrea', 'EU-28', 'Europe',
                                  'Europe (GCP)',
                                  'European Union (27) (GCP)',
                                  'Europe (excl. EU-28)',
                                  'Europe (excl. EU-27)',
                                  'European Union (28)',
                                  'Faeroe Islands','French Equatorial Africa',
                                  'French Guiana', 'French Polynesia',
                                  'French West Africa', 'Greenland',
                                  'Guadeloupe', 'High-income countries',
                                  'Hong Kong',
                                  'International shipping', 'International aviation'
                                  , 'Iran', 'Kosovo',
                                  'Kuwaiti Oil Fires', 'Kuwaiti Oil Fires (GCP)',
                                  'Leeward Islands',
                                  'Libya', 'Low-income countries',
                                  'Lower-middle-income countries',
                                  'Macao', 'Martinique', 'Mayotte',
                                  'Micronesia','Middle East (GCP)',
                                  'Montserrat', 'New Caledonia',
                                  'North America', 'North America (excl. USA)',
                                  'Non-OECD (GCP)',
                                  'North America (GCP)', 'OECD (GCP)','Oceania',
                                  'Oceania (GCP)', 'Panama Canal Zone',
                                  'Puerto Rico', 'Reunion', 'Ryukyu Islands',
                                  'Saint Helena', 'St. Kitts-Nevis-Anguilla',
                                  'St. Kitts-Nevis-Anguilla (GCP)',
                                  'Saint Pierre and Miquelon',
                                  'Sint Maarten (Dutch part)','South America',
                                  'South America (GCP)',
                                  'Taiwan', 'Turks and Caicos Islands',
                                  'Upper-middle-income countries',
                                  'Wallis and Futuna', 'Yemen'
                                  ])].index
df.drop(excluded, inplace=True)

# change Micronesia name to make it smart
df = df.replace('Micronesia (country)','Micronesia')

print(df.isnull().sum()) #There is missing data for CO2

#%%
# select most important columns
dfgraph = df[['country', 'year', 'co2']]

#the graph will only use the data from 1980, so filter here already.
dfgraph = dfgraph[dfgraph['year']>=1980] 

print(dfgraph.head())

#%%
# Countries with missing values for co2
dfgraphtemp = dfgraph[pd.isnull(dfgraph['co2'])==True]
print('-------')
print(dfgraphtemp['country'].unique())

#%%
# Some countries don't have data from 1980
dfgraph = dfgraph.dropna() #this will drop them

#%%
# This code can reduce the number of countries displayed.
selected_countries = dfgraph['country'].unique()
#['World','Australia','Brazil','Canada','China','EU-27',
#                      'India','Indonesia','Japan','Mexico','Nigeria','Russia',
#                      'Saudi Arabia','South Africa','South Korea',
#                      'Switzerland','Turkey','United Kingdom','United States',]
#dfgraph = dfgraph[dfgraph['country'].isin(selected_countries)]

#%%
#create the new rows for the forecast
dfgraphcolumns_list = list(dfgraph)
list_countries = list(selected_countries)
current_year = dfgraph['year'].max()
nb_years = 2050-current_year+1 #number of years to forecast
dfgraphfc = dfgraph.copy()

data = []

for country in list_countries: 
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
# dfgraphfc = dfgraphfc.append(pd.DataFrame(data), True)
dfgraphfc = pd.concat([dfgraphfc, pd.DataFrame(data)], ignore_index=True)
print(dfgraphfc)

#%%
#Create column with co2 path for each country.
#Yearly reduction needed from 2015 to 2050
aim_reduction = 1/(2050-2015)

# Cleanup
dfgraphfc = dfgraphfc.sort_values(by=['country','year'])
dfgraphfc = dfgraphfc.reset_index(drop=True)

# Create new column and get 2015 value
dfgraphfc['co2_path'] = dfgraphfc[dfgraphfc['year']==2015]['co2']
# Creating a temporary dataframe to only get the value for forecast and
# loop more easily.
dfgraphfctemp = dfgraphfc[dfgraphfc['year']>=2015]

aim_reduction_abs = 0

# Calculating the 2016 to 2050 values based on the aim reduction.
for i in range(0,dfgraphfctemp.index.size):
    if pd.notnull(dfgraphfctemp.iat[i,3]):
        aim_reduction_abs = dfgraphfctemp.iat[i,3]*aim_reduction
    else:
        dfgraphfctemp.iat[i,3] = dfgraphfctemp.iat[i-1,3]-aim_reduction_abs
        
# Merge dfgraphfctemp into dfgraphfc
dfgraphfc['co2_path'] = dfgraphfctemp['co2_path']

#%%
# linear regression
# Create new column and get 2015 value
dfgraphfctemp2 = dfgraphfc.copy()
dfgraphfctemp2['co2_OLS'] = dfgraphfctemp2[dfgraphfctemp2['year']==2015]['co2']

# Creating a temporary dataframe to only get the value for forecast and
# loop more easily.
dfgraphfctemp2 = dfgraphfctemp2[(dfgraphfctemp2['year']<=current_year) &
                          (dfgraphfctemp2['year']>= 2015)]

# Selects sub-graphs based on countries, find the OLS values and regroup
# them together in a big graph. It might need to be refactored in a better way.
dfgraphfctemp3 = []
dfgraphfctemp4 = []
    
for country in list_countries:
    dfgraphfctemp3 = dfgraphfctemp2[dfgraphfctemp2['country']==country]
    alpha = dfgraphfctemp3.iloc[0,2]
    X = dfgraphfctemp3['year'][0:6]-2015
    Y = dfgraphfctemp3['co2'][0:6]

    # To find beta, need to minimize the residuals which is the same as finding
    # the minimum of the sum of (Y - alpha - beta*X)**2
    # it is the same as solving (s.mean(Y)-alpha)/s.mean(X)
    
    beta = (s.mean(Y)-alpha)/s.mean(X)

    # Calculating the 2016 to current year values based on beta.
    for i in range(1,dfgraphfctemp3.index.size):
        dfgraphfctemp3.iat[i,4] = alpha+(dfgraphfctemp3.iat[i,1]-2015)*beta

    dfgraphfctemp4.append(dfgraphfctemp3)

dfgraphfctemp5 = pd.concat(dfgraphfctemp4, ignore_index=True)

# Merge dfgraphfctemp into dfgraphfc
dfgraphfc = pd.merge(dfgraphfc, dfgraphfctemp5, how='left',
                      on=['year','country','co2','co2_path'])

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
        "co2_path": dfgraphfc.loc['World']["co2_path"],
        "co2_OLS": dfgraphfc.loc['World']["co2_OLS"],})

title = 'World'

# create a new plot (with a title) using figure
p = figure(title=title, sizing_mode="stretch_height", aspect_ratio=2,
           x_range=Range1d(1980, 2050, bounds=(1980,2050)),
           tools=[SaveTool()]) 

# add four lines renderer
plot1 = p.line("year", "co2", source=render, line_width=5,
                  legend_label='CO2 emissions', line_alpha=0.9)
p.add_tools(HoverTool(renderers=[plot1], tooltips=[
        ('Year', '@year'),
        ('CO2 emissions', '@co2{0.0}')]))    
plot2 = p.line("year", "co2_OLS", source=render, line_width=5,
       color = 'red', legend_label='CO2 trend (regression)', line_alpha=0.9)
p.add_tools(HoverTool(renderers=[plot2], tooltips=[
        ('Year', '@year'),
        ('CO2 Trend', '@co2_OLS{0.0}'),]))
plot3 = p.line("year", "co2_path", source=render, line_width=5, color = 'red',
       line_dash='dashed', legend_label='Target to reach net zero',
       line_alpha=0.8)
p.add_tools(HoverTool(renderers=[plot3], tooltips=[
        ('Year', '@year'),
        ('CO2 Target', '@co2_path{0.0}')]))
COP21 = Span(location=2015, dimension='height', line_color='green',
             line_dash='dotted', line_width=4)
p.add_layout(COP21)

# Appearance
p.xaxis.ticker = BasicTicker(base=5, max_interval = 5)
p.xaxis.axis_label = 'Year'
p.yaxis.axis_label = 'Net CO2 emissions [mio of tons]'
p.xaxis.axis_label_text_font_size = "1.5em"
p.yaxis.axis_label_text_font_size = "1.5em"
p.xaxis.major_label_text_font_size = "1.3em"
p.yaxis.major_label_text_font_size = "1.3em"
p.add_layout(Label(x=2016, y=0.0001, text='COP21', text_color='green'))
    
# Dropdown     
select = Select(title="Country:", value="World", options=list_countries,
                width = 300)

# Interactively change the lines. It uses javascript callbacks
callback_df = CustomJS(args = dict(render=render, source=source, select=select),
code="""
//Filter the countries
var data=source.data;
var country=data['country'];

var a=data['year'];
var b=data['co2'];
var c=data['co2_path'];
var d=data['co2_OLS'];

var f=select.value;

var x=[];
var y=[];
var z=[];
var q=[];

for(var i=0;i<a.length; i++){
        if(country[i]==f){
                         x.push(a[i]);
                         y.push(b[i]);
                         z.push(c[i]);
                         q.push(d[i]);
                    }
        }

render.data['year']=x;
render.data['co2']=y;
render.data['co2_path']=z;
render.data['co2_OLS']=q;

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

layout = column(children = [select,p], aspect_ratio=2, sizing_mode="stretch_height") 
# layout = column(children = [select,p], sizing_mode="scale_height") 

output_file(join(dirname(__file__),'graph.html'), title='Bokeh plot: Objective net zero carbon emissions 2050')

show(layout) #use this for development
#curdoc().add_root(layout) # show the results if using a bokeh server

#%%
# graph html export
# Generate the table based on the current_year
dflastyear = dfgraphfc[dfgraphfc['year']==current_year]
dflastyear = dflastyear.drop('year', axis=1)                

# Rearrange columns
dflastyear = dflastyear[['co2','co2_OLS','co2_path']]

# Add a column for the difference between current path an target path
dflastyear['Difference'] = dflastyear['co2_OLS']-dflastyear['co2_path']
dflastyear['Percent Diff.'] = (dflastyear['co2_OLS']/dflastyear['co2_path']-1)*100
dflastyear = dflastyear.round({'co2': 2, 'co2_path': 2, 'co2_OLS': 2,
                               'Difference': 2, 'Percent Diff.': 1})

dflastyear = dflastyear.rename(columns={"co2": "CO2", "co2_path": "CO2 Path",
                                        "co2_OLS": "Current Path"})
dflastyear['Percent Diff.'] = dflastyear['Percent Diff.'].map("{:,.2f}%".format)

html = dflastyear.to_html()
 
# write html to file
html_file = open("table.html", "w")
html_file.write(html)
html_file.close()