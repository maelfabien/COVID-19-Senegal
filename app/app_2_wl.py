import streamlit as st

# Base packages
import pandas as pd
import numpy as np
import datetime
import altair as alt
import matplotlib.pyplot as plt

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

st.header(" Xibaar yu aju ci Jangorëy Koronaa ci Senegal 🇸🇳")

st.sidebar.markdown("*yeesal gu muj: 25/03/2020*")
st.sidebar.markdown("---")
st.sidebar.header("Ressources utiles")

st.sidebar.markdown("Numero guir woté bu jamp bu jeuk: **78 172 10 81**")
st.sidebar.markdown("Numero guir woté bu jamp ñaaréle: **76 765 97 31**")
st.sidebar.markdown("Numero guir woté bu jamp ñeetéle: **70 717 14 92**")
st.sidebar.markdown("Numero boye woté té do fayye bu ministere: **800 00 50 50**")
st.sidebar.markdown("Samu: **1515**")
st.sidebar.markdown("Besel ci sa telefone : **#2121#**")
st.sidebar.markdown("[Saytul say sa yarame ci Jangoroji ci Prevcovid19](http://www.prevcovid19.com/#/teste)")
st.sidebar.markdown("[Tweetru ministre gui eub walu wergu yaram ](https://twitter.com/MinisteredelaS1)")
st.sidebar.markdown("[Booleb xéeti mbir ak màndargaay jumtukaayu ](https://github.com/maelfabien/COVID-19-Senegal)")
st.sidebar.markdown("---")

st.sidebar.header("Jokko ak wa ministere")

st.sidebar.markdown("Ministre gui eub walu wergu yaram ak boolem boko / Fann Residence")
st.sidebar.markdown("Rue Aimé Césaire, Dakar, Senegal")
st.sidebar.markdown("+221 800 00 50 50 - contact@sante.gouv.sn")

st.sidebar.markdown("---")
st.sidebar.markdown("Ñi ka derale moye  [Maël Fabien](https://maelfabien.github.io/) ak [Dakar Institute of Technology](https://dit.sn/)")

# I. Dataframe

df = pd.read_csv("COVID_Dakar.csv", sep=";")
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

#st.write(df)

evol_cases = df[['Date', 'Positif', 'Negatif', 'Décédé', 'Guéri']].groupby("Date").sum().cumsum()

st.subheader("Ci tënkk")

total_positif = evol_cases.tail(1)['Positif'][0]
total_negatif = evol_cases.tail(1)['Negatif'][0]
total_decede = evol_cases.tail(1)['Décédé'][0]
total_geuri = evol_cases.tail(1)['Guéri'][0]

st.markdown("Limu ñi feebar: <span style='font-size:1.5em;'>%s</span>"%(total_positif - total_geuri), unsafe_allow_html=True)
st.markdown("Limu ñi faatu: <span style='font-size:1.5em;'>%s</span>"%(total_decede), unsafe_allow_html=True)
st.markdown("Limu ñi wer: <span style='font-size:1.5em;'>%s</span>"%(total_geuri), unsafe_allow_html=True)
st.markdown("dayob ñi wer : <span style='font-size:1.5em;'>%s</span>"%(np.round(total_geuri / total_positif, 3) * 100), unsafe_allow_html=True)
st.markdown("dàyob yoqute ñi feebar bis bu ay : <span style='font-size:1.5em;'>%s</span>"%(np.round(pd.DataFrame(np.sqrt(evol_cases['Positif'].pct_change(periods=2)+1)-1).tail(1)['Positif'][0] * 100, 2)), unsafe_allow_html=True)
st.markdown("Mboolem ñi ame Koronaa: <span style='font-size:1.5em;'>%s</span>"%(total_positif), unsafe_allow_html=True)
st.markdown("Mboolem ñi ñu saytu te ñu mùcc ci feebar bi: <span style='font-size:1.5em;'>%s</span>"%(total_negatif), unsafe_allow_html=True)
st.markdown("Mboolem ñi ñu saytu: <span style='font-size:1.5em;'>%s</span>"%(total_positif + total_negatif), unsafe_allow_html=True)
st.markdown("dayob ñi ame feebar bi ci ñi ñu saytu: <span style='font-size:1.5em;'>%s</span>"%(np.round(total_positif / (total_positif + total_negatif), 3) * 100), unsafe_allow_html=True)


# II. Map
st.markdown("---")
st.subheader("ñi ame feebar bi fu ñu féete")
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
    tooltips = [('Ville', '@Ville'), ('Limu ñi ame Koronaa ', '@Positif')]
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

p.circle('longitude','latitude',source=pointsource, size=15)

st.bokeh_chart(p)

# III. Map
st.markdown("---")
st.subheader(" Yoqute limu ñi ame Koronaa ci Senegal")

highlight = alt.selection(type='single', on='mouseover',
                          fields=['Positif'], nearest=True)

chart = alt.Chart(evol_cases.reset_index()).mark_line(point=True, strokeWidth=5).encode(
    x='Date:T',
    y='Positif:Q',
    tooltip='Positif:Q'
).add_selection(
    highlight
).properties(height=400, width=700)


st.write(chart.interactive())

st.markdown("---")
st.subheader("Mingalé rewu Pays-Bas")

st.write("Senegaal rewle bigua xamanetané limu way-dëkké dafa méggo ak rewu Pays-bas (Fukk ak jurrom benn million), ba taxna ab mégele meuna dox di diganté ñaari dëkk yoyé. Doneté yoqute Jangorëy Koronaa gui ci rewum Senegaal la geune yéxé ci sinu dioni yalla taye, luñu setlu ci ni Jangoro gui di doxé diarna bayi xel wayé itameu lathe na niou xalate ci.Fi gua xamené mome leu rewu Senegaal tolu ci Jangorëy Koronaa dafa mengo ci fukki fan ak juroom ci guinaw fi rew mi di Pays-Bas Tolone,wayé xayma gogu boye seteu juroom ñaari faney le guir rew pays-bas té Senegaal fukki fan ak juroom ñeet. Lim yi aju ci rewu  Pays-Bas ñuguike jeulé ci Wikipedia: https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_the_Netherlands")

df_nl = pd.read_csv("df_nl.csv")

plt.figure(figsize=(16,10))
plt.plot(df_nl['Netherlands'], linestyle="--", linewidth=5, label="Pays-Bas")
plt.plot(df_nl['Senegal'],label="Sénégal", linewidth=5)
plt.figtext(.5,.9,'Evolution des cas au Sénégal et aux Pays-Bas', fontsize=30, ha='center')
plt.legend()
st.pyplot(plt)

# IV. Contamination
st.markdown("---")
st.subheader("Tassarok Jangorogui")

st.write("Ñugui xamé ñeneu ñu jeulé Jangoroji ci ñu jugué bimeu rew, ci niit ñu feebar yigua xamené ño waleu ñeni niit.Limu ñigua xamné ño ameu Jangoroji té jeuléko ci biir rewmi, moye waleu gui geuna ragalu ci walanté Jangoroji..")

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
).mark_line(size=5).encode(
    x='Date:T',
    y='value:Q',
    color='key:N'
).properties(height=500, width=700)

st.altair_chart(ch0)

st.write("Ñu dieulé Jangoroji bitimeu rew, té waleu Jangoroji ñeneu ñu dëkk Senegaal, Ñugui jugué ci rew yi :")

ch3 = alt.Chart(df.dropna(subset=['Source/Voyage'])).mark_bar().encode(
	x = 'Source/Voyage:N',
    y=alt.Y('count()', title='Nombre de patients')
).properties(title="Provenance des malades", height=300, width=700)

st.write(ch3)

# Interactive Map
st.write("Natalu feega xamené fila jangorey koronaa bi jugué:")

df3 = px.data.gapminder().query("year == 2007")
df2 = df3[(df3['country']=="Italy") | (df3['country']=="Senegal") | (df3['country']=="United Kingdom") | (df3['country']=="France") | (df3['country']=="Spain")]

fig = px.line_geo(df2, locations="iso_alpha",
                  projection="orthographic")

st.plotly_chart(fig)

# V. Population
st.markdown("---")
st.subheader("Way-dëkk ñu feebar daleu.")
st.write("Les chiffres présentés ci-dessous tiennent compte des publication du Ministère de la Santé et de l'Action Sociale. Certaines données sont manquantes, et nous n'affichons que les valeurs connues à ce jour.")

st.write("1. At ñu eupe  ci yi Jangoroji di diap ", np.mean(df['Age'].dropna()), " ans")

ch = alt.Chart(df).mark_bar().encode(
	x = 'Age:Q',
    y=alt.Y('count()', title='Nombre de patients')
).properties(title="Atu aji wop gui ", height=300, width=700)

st.write(ch)

st.write("2. Ñu eup ci aji-wop yi aye goor lañu")

st.write(pd.DataFrame(df[['Homme', 'Femme']].dropna().sum()).transpose())

st.write("3. Ñu eupe ci ñu feebar bi diapeu ndakaru lañu dëkké")

ch2 = alt.Chart(df.dropna(subset=['Ville'])).mark_bar().encode(
	x = 'Ville:N',
    y=alt.Y('count()', title='Nombre de patients')
).properties(title="Ville connue du patient", height=300, width=700)

st.write(ch2)

st.write("4. Ñu eupe ci niit ñu amé Jangoroji Senegaal lañu dëkk.")

st.write(df['Resident Senegal'].dropna().value_counts())

st.write("5. Ñu eupe ci niit ñu amé Jangoroji Senegaal lañu dëkk.")

st.write(df['Resident Senegal'].dropna().value_counts())

st.write("6. Faan ñigua xamné aji wop gui ci laye teud lalu opital : ", np.mean(df['Temps Hospitalisation (j)'].dropna()), " Faan")
