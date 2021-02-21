import streamlit as st
import pandas as pd
from analysis import SentimentAnalyzer, Lexicon, Topic, LexiconEntry
import de_core_news_lg

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
import psycopg2

# function to create a Aspect-Term-Lexicon from a csv file
@st.cache(hash_funcs={Lexicon: id})
def createLexiconFromFile(file_path):
    term_aspects = pd.read_csv(file_path, header=None, names=['term', 'aspect'], sep=';')
    lexicon = Lexicon()

    for index, row in term_aspects.iterrows():
        lexicon.append(row['term'], Topic(row['aspect']))

    return lexicon

@st.cache(allow_output_mutation=True)
def create_db_connection():
    # Create an engine instance
    alchemyEngine = create_engine('postgresql+psycopg2://postgres:password@database:5432/postgres', pool_recycle=3600)
    # Connect to PostgreSQL server
    dbConnection = alchemyEngine.connect()
    return dbConnection

@st.cache(allow_output_mutation=True, show_spinner=False)
def get_nlp_model():
    return de_core_news_lg.load()

def get_reviews_for_product(product_name):
    alchemyEngine = create_engine('postgresql+psycopg2://postgres:password@database:5432/postgres', pool_recycle=3600)
    # Connect to PostgreSQL server
    dbConnection = alchemyEngine.connect()
    query = 'SELECT * FROM "Reviews" WHERE "ProductName" ILIKE \'%%{}%%\';'.format(product_name)
    data = pd.read_sql(query, dbConnection)
    data['CreatedAt'] = pd.to_datetime(data['CreatedAt'], format= "%Y-%m-%d")
    return data

st.title('Analyse starten')

product_name = st.text_input("Product name")
if product_name != '':
    reviews = get_reviews_for_product(product_name).copy()
    st.write("Found {} reviews for {}".format(len(reviews), product_name))

    uploaded_file = st.file_uploader('Select lexicon file as CSV', type=['csv'], )
    if uploaded_file is not None:
        lexicon = createLexiconFromFile(uploaded_file)
        st.write('Created Lexicon with {} entries from uploaded file.'.format(len(lexicon.entries)))

        analyzing_state = st.text("Analyzing... This might take some time")
        model = get_nlp_model()
        analyzer = SentimentAnalyzer(lexicon, model)
        analyzed = analyzer.analyzeReviews(reviews)
        analyzing_state.text("Analyzing complete.")
        st.write(analyzed)


