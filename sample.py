import pandas as pd

# Sample data with states and values
data = {
    'state': ['United States', 'Brazil', 'China', 'India'],
    'value': [39538223, 29145505, 21538187, 20201249]
}
df = pd.DataFrame(data)

geojson_url = 'https://raw.githubusercontent.com/PublicaMundi/GeoJSON-States/master/us-states.geo.json'

import folium
import streamlit as st

# Create a folium map centered around the U.S.
m = folium.Map(location=[37.0902, -95.7129], zoom_start=5)

# Add GeoJSON layer for state boundaries
folium.GeoJson(
    geojson_url,
    name='geojson',
    style_function=lambda feature: {
        'fillColor': 'white',
        'color': 'black',
        'weight': 1
    }
).add_to(m)

# Add a Choropleth layer to visualize values
folium.Choropleth(
    geo_data=geojson_url,
    data=df,
    columns=['state', 'value'],
    key_on='feature.properties.name',  # Key should match the property name in the GeoJSON file
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Value'
).add_to(m)

# Display the map in Streamlit
st.write("Map Visualization with State Data:")
st.components.v1.html(m._repr_html_(), height=500)
