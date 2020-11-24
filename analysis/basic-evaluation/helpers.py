import streamlit as st
import pandas as pd
import csv
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
import psycopg2

import nltk
from nltk.corpus import stopwords
import spacy

import altair as alt
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from collections import Counter

@st.cache(allow_output_mutation=True)
def create_db_connection():
    # Create an engine instance
    alchemyEngine = create_engine('postgresql+psycopg2://postgres:password@database:5432/postgres', pool_recycle=3600)
    # Connect to PostgreSQL server
    dbConnection = alchemyEngine.connect()
    return dbConnection

@st.cache(hash_funcs={Connection: id})
def get_sources(connection):
    return pd.read_sql('SELECT DISTINCT "Source" FROM "Reviews";', connection)

@st.cache(hash_funcs={Connection: id}, show_spinner=False)
def get_reviews_for_product(product_name, connection, sources, additional_stopwords = None):
    if len(sources) > 1:
        query = 'SELECT * FROM "Reviews" WHERE "ProductName" ILIKE \'%{}%\' AND "Source" IN {};'.format(product_name, tuple(sources))
    else:
        query = 'SELECT * FROM "Reviews" WHERE "ProductName" ILIKE \'%{}%\' AND "Source" = \'{}\';'.format(product_name, sources[0])
    data = pd.read_sql(query, connection)
    data['CreatedAt'] = pd.to_datetime(data['CreatedAt'], format= "%Y-%m-%d")
    data = process_reviews(data, additional_stopwords)
    return data

@st.cache(allow_output_mutation=True, show_spinner=False)
def get_nlp_model():
    return spacy.load('de')

@st.cache(show_spinner=False)
def lemmatize(text):
    nlp_model = get_nlp_model()
    doc = nlp_model(text, disable=["tagger", "parser", "ner", "textcat"])
    result = ' '.join([x.lemma_.strip().lower() for x in doc]) 
    return result

@st.cache(show_spinner=False)
def clean_text(text, additional_stopwords = None):
    # Erstellung einer Liste von deutschen Stopwords
    german_stopwords = stopwords.words('german')

    german_stopwords.remove('nicht')
    german_stopwords.remove('nichts')

    if additional_stopwords:
        german_stopwords.extend(additional_stopwords)

    text = text.str.replace('[^\w\s]', ' ')
    text = text.apply(lambda x: " ".join(x.strip() for x in x.split()))
    text = text.str.replace('\d+', '')
    text = text.apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in (german_stopwords)]))
    text = text.astype(str)
    return text

@st.cache(show_spinner=False)
def get_nouns(data):
    nlp_model = get_nlp_model()
    req_tag = ['NN']
    extracted_words = []
    try:
        for x in data['REVIEW_PROCESSED']:
            doc = nlp_model(x)
            for token in doc:
                if token.tag_ in req_tag:
                    extracted_words.append(token.lemma_)
        return extracted_words
    except Exception as e:
        return extracted_words

@st.cache(show_spinner=False)
def process_reviews(reviews, additional_stopwords = None):
    reviews['REVIEW'] = reviews['ReviewTitle'] + '. ' + reviews['ReviewText']
    reviews['TEXT_LENGTH'] = reviews['REVIEW'].apply(lambda text: len(text))
    reviews['REVIEW_PROCESSED'] = clean_text(reviews['REVIEW'], additional_stopwords)
    reviews['REVIEW_LEMMATIZED'] = reviews['REVIEW_PROCESSED'].apply(lemmatize)
    return reviews

@st.cache
def get_product_names(title, reviews):
    return reviews.ProductName.unique()

def create_charts(product_records, product_title):
    st.subheader('Statistics for "{}":'.format(product_title))

    # Verteilung der Ratings (1-5 Sterne)
    st.write('Rating Distribution (mean: {:.2f})'.format(np.mean(product_records['Rating'])))
    product_ratings = pd.DataFrame.from_records(Counter(product_records['Rating']).most_common(), columns=['Rating', 'Count'])
    chart1 = alt.Chart(product_ratings).mark_bar().encode(
        alt.X('Rating:O', title = 'Rating'),
        alt.Y('Count:Q', title='Number of Reviews')
    ).properties(
        height=350
    )
    st.altair_chart(chart1, use_container_width=True)

    # Verteilung der Textlänge (Anzahl Wörter je Text)
    st.write('Review Text Length Distribution (mean: {:.2f})'.format(np.mean(product_records['TEXT_LENGTH'])))
    chart2 = alt.Chart(product_records).mark_bar().encode(
        alt.X('TEXT_LENGTH:Q', bin=True, title='Text Length'),
        alt.Y('count()', title='Number of Reviews')
    ).properties(
        height=350
    )
    st.altair_chart(chart2, use_container_width=True)

    # Anzahl Ratings je Monat
    df_time = product_records.filter(items=['Rating', 'CreatedAt'])
    df_month = df_time.set_index('CreatedAt')
    df_month = df_month.groupby(pd.Grouper(freq='M')).count()
    df_month = df_month.reset_index()
    st.write('Number of Reviews Over Time (mean: {:.2f})'.format(np.mean(df_month['Rating'])))
    chart3 = alt.Chart(df_month).mark_bar().encode(
        alt.X('yearmonth(CreatedAt):O', title='Creation Date'),
        alt.Y('Rating:Q', title='Number of Reviews')
    ).properties(
        height=350
    )
    st.altair_chart(chart3, use_container_width=True)

    # Wordcloud für Texte mit positiver Bewertung >= 4
    st.write('Wordcloud for Positive Reviews')
    product_positive_reviews = product_records[product_records['Rating'] >= 4]
    product_positive_text = " ".join(product_positive_reviews['REVIEW_LEMMATIZED'])

    product_wordcloud_positive = WordCloud(background_color="white", width=1920, height=1080, colormap='summer').generate(product_positive_text)

    fig, ax = plt.subplots()
    ax.imshow(product_wordcloud_positive, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # Wordcloud für Texte mit negativer Bewertung < 4
    st.write('Wordcloud for Negative Reviews')
    product_negative_reviews = product_records[product_records['Rating'] < 4]
    product_negative_text = " ".join(product_negative_reviews['REVIEW_LEMMATIZED'])

    product_wordcloud_negative = WordCloud(background_color="white", width=1920, height=1080, colormap='hot').generate(product_negative_text)

    fig, ax = plt.subplots()
    ax.imshow(product_wordcloud_negative, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # Häufigste Wörter nach Anzahl Auftreten
    product_all_text = ' '.join(product_records['REVIEW_LEMMATIZED'])
    product_common_words = pd.DataFrame.from_records(Counter(product_all_text.split()).most_common(20), columns=['Words', 'Count'])
    st.write('Most Common Words')
    chart4 = alt.Chart(product_common_words).mark_bar().encode(
        alt.X('Words:O', title='Commmon Words', sort='-y'),
        alt.Y('Count:Q', title='Frequency')
    ).properties(
        height=350
    )
    st.altair_chart(chart4, use_container_width=True)

    # Häufigste Nomen nach Anzahl Auftreten
    most_common_nouns = pd.DataFrame.from_records(Counter(get_nouns(product_records)).most_common(15), columns=['Words', 'Count'])
    st.write('Most Common Nouns')
    chart5 = alt.Chart(most_common_nouns).mark_bar().encode(
        alt.X('Words:O', title='Common Nouns', sort='-y'),
        alt.Y('Count:Q', title='Frequency')
    ).properties(
        height=350
    )
    st.altair_chart(chart5, use_container_width=True)