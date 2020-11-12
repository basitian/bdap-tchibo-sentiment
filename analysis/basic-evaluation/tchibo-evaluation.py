import streamlit as st
from helpers import create_db_connection, create_charts, get_reviews_for_product, get_sources

st.title('Auswertung Tchibo Produktbewertungen')

dbConnection = create_db_connection()

st.sidebar.title('Settings')

st.sidebar.subheader('Additional Stopwords')
additional_stopwords = st.sidebar.text_input('Add additional stopwords seperated by a comma')

st.sidebar.subheader('Product Selection')

available_sources = get_sources(dbConnection)
sources = st.sidebar.multiselect('Select the data sources to use', options = available_sources)

product_title = st.sidebar.text_input('Type a product title')

if len(sources) < 1:
    st.warning('Please select one or more sources')
    st.stop()

if not product_title:
    st.warning('Please select a product')
    st.stop()

# get data an process it
with st.spinner('Processing all requested data...'):
    product_reviews = get_reviews_for_product(product_title.lower(), dbConnection, sources, [x.lower().strip() for x in additional_stopwords.split(',')]).copy()

product_names = product_reviews.ProductName.unique()

st.sidebar.write('- ' + '\n- '.join(product_names))
st.sidebar.write('{} reviews in total for "{}"'.format(len(product_reviews), product_title))

create_charts(product_reviews, product_title)