FROM python:3.7.4-slim-stretch

WORKDIR /app

ADD requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

RUN python -m spacy download de_core_news_lg

COPY /SentiWS_v2.0 /SentiWS_v2.0

COPY webapp.py /app.py
COPY analysis.py /analysis.py

COPY wait-for-it.sh ./

RUN chmod +x wait-for-it.sh 

EXPOSE 8501

CMD ["./wait-for-it.sh", "database:5432", "--", "streamlit", "run", "/app.py"]
