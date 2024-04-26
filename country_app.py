import streamlit as st
import pandas as pd
import math
from pathlib import Path
import base64



# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP Dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.


def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


IMAGE_FILENAME = Path(__file__).parent/'image/country_explorer_img.jpg'


# CSS to inject contained in a Python multiline string
background_image_style = f"""
<style>
html, body, [class*="ViewContainer"] {{background-image: url("data:image/jpeg;base64,{get_base64_encoded_image(IMAGE_FILENAME)}");
    background-size: cover;
    background-repeat: no-repeat;
    height: 100%;
}}
</style>
"""


st.markdown(background_image_style, unsafe_allow_html=True)

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """
   
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    #DATA_FILENAME = "C:/Users/HUAWEI/Documents/gdp/gdp_data.csv"
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 2002
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Name'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: Country Data Explorer

All data is collected from [World Bank Open Data](https://data.worldbank.org/) website.
'''

# Add some spacing
''


min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()



countries = gdp_df['Country Name'].unique()

if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Select countries:',
    countries,
    ['China', 'India', 'United Kingdom', 'United States', 'Japan'])

from_year, to_year = st.slider(
    'Range of years',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])


''
''
''
''


# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Name'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Name',
)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(5)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[gdp_df['Country Name'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[gdp_df['Country Name'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f} B',
            delta=growth,
            delta_color=delta_color
        )
