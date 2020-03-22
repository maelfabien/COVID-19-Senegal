import streamlit as st

# Base packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import altair as alt

# Find coordinates
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="myapp2")
import time

# Plot static maps
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Plot interactive maps
import geopandas as gpd
from shapely import wkt
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, ColumnDataSource
import json
from bokeh.models import HoverTool

import math
from scipy.optimize import curve_fit
import plotly.express as px

st.header("Cas de COVID-19 au Sénégal 🇸🇳")

st.markdown("*Dernière mise à jour: 22/03/2020*")

st.markdown("Si vous avez des symptômes, appelez les urgences au 70 717 14 92, 76 765 97 31 ou 78 172 10 81. Un numéro vert a été mis en place par le Ministère de la Santé au 800 00 50 50. En cas d'urgence, appelez le SAMU au 1515.")
st.markdown("Si vous avez des doutes, vous pouvez tester vos symptomes sur Prevcovid19: http://www.prevcovid19.com/#/teste")

st.write("La table de donnée ci-dessous a été contruite à partir des tweets du Ministère de la Santé et de l'Action Sociale du Sénégal. La source peut être trouvée ici: https://twitter.com/MinisteredelaS1")
st.write("Le code et la base de données peuvent être trouvés ici: https://github.com/maelfabien/COVID-19-Senegal")
# I. Dataframe

df = pd.read_csv("COVID_Dakar.csv", sep=";")
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

st.write(df)

evol_cases = df[['Date', 'Positif', 'Negatif', 'Décédé', 'Guéri']].groupby("Date").sum().cumsum()

st.subheader("En bref")

total_positif = evol_cases.tail(1)['Positif'][0]
total_negatif = evol_cases.tail(1)['Negatif'][0]
total_decede = evol_cases.tail(1)['Décédé'][0]
total_geuri = evol_cases.tail(1)['Guéri'][0]
st.write("Nombre de malades: ", total_positif - total_geuri)
st.write("Nombre de décès: ", total_decede)
st.write("Nombre de guérisons: ", total_geuri)
st.write("Pourcentage de guerison: ", np.round(total_geuri / total_positif, 3) * 100, " %")
st.write("Nombre total de cas positifs: ", total_positif)
st.write("Nombre de cas negatifs: ", total_negatif)
st.write("Nombre de tests réalisés: ", total_positif + total_negatif)
st.write("Pourcentage de tests positifs: ", np.round(total_positif / (total_positif + total_negatif), 3) * 100, " %")

# II. Map
st.markdown("---")
st.subheader("Carte des cas positifs")
shapefile = 'app/ne_110m_admin_0_countries.shp'

#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']
gdf = gdf[gdf['country']=="Senegal"]
grid_crs=gdf.crs
gdf_json = json.loads(gdf.to_json())
grid = json.dumps(gdf_json)

cities = pd.read_csv("city_coordinates.csv", index_col=0)

def find_lat(x):
    try:
        return float(cities[cities['Ville'] == x]['Latitude'])
    except TypeError:
        return None

def find_long(x):
    try:
        return float(cities[cities['Ville'] == x]['Longitude'])
    except TypeError:
        return None

summary = df[['Positif', 'Ville']].groupby("Ville").sum().reset_index()
summary['latitude'] = summary['Ville'].apply(lambda x: find_lat(x))
summary['longitude'] = summary['Ville'].apply(lambda x: find_long(x))

geosource = GeoJSONDataSource(geojson = grid)
pointsource = ColumnDataSource(summary)

hover = HoverTool(
    tooltips = [('Ville', '@Ville'), ('Nombre de cas positifs', '@Positif')]
)

#Create figure object.
p = figure(plot_height = 550 , plot_width = 700, tools=[hover, 'pan', 'wheel_zoom'])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.xaxis.visible = False
p.yaxis.visible = False
p.outline_line_color = None

patch = p.patches('xs','ys', source = geosource, fill_color = '#fff7bc',
          line_color = 'black', line_width = 0.35, fill_alpha = 1, 
                hover_fill_color="#fec44f")

#Add patch renderer to figure. 
patch = p.patches('xs','ys', source = geosource, fill_color = 'lightgrey',
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

p.circle('longitude','latitude',source=pointsource, size='Positif')

st.bokeh_chart(p)

# III. Map
st.markdown("---")
st.subheader("Evolution du nombre de cas positifs au Sénégal")

highlight = alt.selection(type='single', on='mouseover',
                          fields=['Positif'], nearest=True)

chart = alt.Chart(evol_cases.reset_index()).mark_line(color="#FFAA00").encode(
    x='Date:T',
    y='Positif:Q',
    tooltip='Positif:Q'
).properties(height=400, width=700)

points = chart.mark_circle().encode(
    opacity=alt.value(0)
).add_selection(
    highlight
)

lines = chart.mark_line().encode(
    size=alt.condition(~highlight, alt.value(1), alt.value(3))
)

st.write(points + lines)

# IV. Contamination
st.markdown("---")
st.subheader("Contamination")

st.write("Nous distinguon les cas importés (voyageurs en provenance de l'extérieur) des cas contact qui ont été en contact avec une personne malade. Les cas Communauté sont des cas dont les contacts directs ne peuvent être établis, et donc les plus dangereux.")

facteur = df[['Date', 'Facteur']].dropna()
facteur['Count'] = 1

importe = facteur[facteur['Facteur'] == "Importé"].groupby("Date").sum().cumsum().reset_index()
voyage = facteur[facteur['Facteur'] == "Contact"].groupby("Date").sum().cumsum().reset_index()
communaute = facteur[facteur['Facteur'] == "Communauté"].groupby("Date").sum().cumsum().reset_index()

df_int = pd.merge(importe, voyage, left_on='Date', right_on='Date', how='outer')
df_int = pd.merge(df_int, communaute, left_on='Date', right_on='Date', how='outer')

df_int['Date'] = pd.to_datetime(df_int['Date'], dayfirst=True)
df_int = df_int.sort_values("Date").ffill().fillna(0)
df_int.columns = ["Date", "Importes", "Contact", "Communauté"]

ch0 = alt.Chart(df_int).transform_fold(
    ['Importes', 'Contact', 'Communauté'],
).mark_line().encode(
    x='Date:T',
    y='value:Q',
    color='key:N'
).properties(title="Evolution des cas contacts, communauté et importés", height=500, width=700)

st.altair_chart(ch0)

st.write("Les cas importés, ayant ensuite crée des cas contact, proviennent des pays suivants:")

ch3 = alt.Chart(df.dropna(subset=['Source/Voyage'])).mark_bar().encode(
	x = 'Source/Voyage:N',
    y=alt.Y('count()', title='Nombre de patients')
).properties(title="Provenance des malades", height=300, width=700)

st.write(ch3)

# Interactive Map
st.write("Visualisation interactive de la provenance des cas de COVID-19:")

df3 = px.data.gapminder().query("year == 2007")
df2 = df3[(df3['country']=="Italy") | (df3['country']=="Senegal") | (df3['country']=="United Kingdom") | (df3['country']=="France") | (df3['country']=="Spain")]

fig = px.line_geo(df2, locations="iso_alpha",
                  projection="orthographic")

st.plotly_chart(fig)

# V. Population
st.markdown("---")
st.subheader("Population touchée")
st.write("Les chiffres présentés ci-dessous tiennent compte des publication du Ministère de la Santé et de l'Action Sociale. Certaines données sont manquantes, et nous n'affichons que les valeurs connues à ce jour.")

st.write("1. L'age moyen des patients est de ", np.mean(df['Age'].dropna()), " ans")

ch = alt.Chart(df).mark_bar().encode(
	x = 'Age:Q',
    y=alt.Y('count()', title='Nombre de patients')
).properties(title="Age des patients", height=300, width=700)

st.write(ch)

st.write("2. La plupart des patients connus sont des hommes")

st.write(pd.DataFrame(df[['Homme', 'Femme']].dropna().sum()).transpose())

st.write("3. La plupart des cas sont concentrés à Dakar")

ch2 = alt.Chart(df.dropna(subset=['Ville'])).mark_bar().encode(
	x = 'Ville:N',
    y=alt.Y('count()', title='Nombre de patients')
).properties(title="Ville connue du patient", height=300, width=700)

st.write(ch2)

st.write("4. La plupart des personnes malades résident au Sénégal")

st.write(df['Resident Senegal'].dropna().value_counts())

st.write("5. La plupart des personnes malades résident au Sénégal")

st.write(df['Resident Senegal'].dropna().value_counts())

st.write("6. Le temps d'hospitalisation moyen pour le moment est de : ", np.mean(df['Temps Hospitalisation (j)'].dropna()), " jours")

st.markdown("---")

st.write("Réalisé par Maël Fabien pour Dakar Institute of Technology: https://dit.sn/")
