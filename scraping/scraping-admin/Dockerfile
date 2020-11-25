FROM python:3.7.4-slim-stretch

WORKDIR /app

ADD requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

COPY scraping-admin.py /app.py

COPY wait-for-it.sh ./

RUN chmod +x wait-for-it.sh 

EXPOSE 8501

CMD ["./wait-for-it.sh", "database:5432", "--", "streamlit", "run", "/app.py"]