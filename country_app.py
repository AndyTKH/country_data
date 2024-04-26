import streamlit as st
import pandas as pd
import math
from pathlib import Path
import base64



# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Country Data',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.ss


def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def full_page_background_image_base64():
    image_path = Path(__file__).parent/'image/world_un_img.jpg'  # Update this path
    encoded_image = get_base64_encoded_image(image_path)
    css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)

full_page_background_image_base64()


@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """
   
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    DATA_FILENAME2 = Path(__file__).parent/'data/population_data.csv'
    #DATA_FILENAME = "C:/Users/HUAWEI/Documents/gdp/gdp_data.csv"
    #DATA_FILENAME2 = "C:/Users/HUAWEI/Documents/gdp/population_data.csv"
    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    raw_population_df = pd.read_csv(DATA_FILENAME2)

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

    pop_df = raw_population_df.melt(
        ['Country Name'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'Population',
    )


    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    pop_df['Year'] = pd.to_numeric(pop_df['Year'])


    return gdp_df, pop_df

gdp_df, pop_df = get_gdp_data()

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

filtered_pop_df = pop_df[
    (pop_df['Country Name'].isin(selected_countries))
    & (pop_df['Year'] <= to_year)
    & (from_year <= pop_df['Year'])
]


st.header('GDP', divider='gray')

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


first_year_pop = pop_df[pop_df['Year'] == from_year]
last_year_pop = pop_df[pop_df['Year'] == to_year]


''


st.header('Population', divider='gray')


''


st.bar_chart(filtered_pop_df, y = 'Population', x='Year', color='Country Name')


''
''

st.header(f'Country statistics in {to_year}', divider='gray')
cols = st.columns(5)
cols[0].write(f"GDP increase ( in USD Billion) since {from_year}: ")

for i, country in enumerate(selected_countries):
    col_index = 1 + (i % (len(cols) - 1))
    col = cols[col_index]

    with col:
        first_gdp = first_year[gdp_df['Country Name'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[gdp_df['Country Name'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{(last_gdp-first_gdp):,.1f} B'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f} B',
            delta=growth,
            delta_color=delta_color
        )


''
cols = st.columns(5)
cols[0].write(f"Population percentage growth (%) increase since {from_year}: ")

for i, country in enumerate(selected_countries):
    col_index = 1 + (i % (len(cols) - 1))
    col = cols[col_index]

    with col:
        first_pop = first_year_pop[pop_df['Country Name'] == country]['Population'].iat[0] / 1000000
        last_pop = last_year_pop[pop_df['Country Name'] == country]['Population'].iat[0] / 1000000

        if math.isnan(first_pop):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{((last_pop-first_pop)/first_pop)*100:,.1f} %'
            delta_color = 'normal'

        st.metric(
            label=f'{country} Population',
            value=f'{last_pop:,.0f} M',
            delta=growth,
            delta_color=delta_color
        )

