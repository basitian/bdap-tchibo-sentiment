import streamlit as st
import requests
import pandas as pd

def scrape_otto(product_id):

    url = "http://otto-scraper:9080/crawl.json"

    product_link = "https://www.otto.de/product-customerreview/reviews/presentation/product/{}".format(product_id)

    payload='{\"request\": {\"url\":\"' + product_link + '\"},\"spider_name\": \"otto_reviews\"\n}'
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()

st.title('Scraping Administration')

product_id = st.text_input('Enter otto.de product id (e.g. 898416526)')

if st.button('Scrape Data'):
    with st.spinner('Scraping Data...'):
        response = scrape_otto(product_id)
    if response['status'] == 'ok':
        df = pd.DataFrame(response['items'])
        count = response['stats']['item_scraped_count']
        st.success('Done scraping {} items.'.format(count))
        st.write(df)
    else:
        st.error('Error scraping data')
        
    

