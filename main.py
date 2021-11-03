import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# import plotly.express as px
# import seaborn as sns
# import plotnine

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
df2019 = df[df['year']==2019]

print(df2019)