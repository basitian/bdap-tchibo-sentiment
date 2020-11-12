# Dockerfile for PostgreSQL for Big Data Analyseprojekt - Tchibo
# by Bastian Hunecke
# 03.11.2020

# pull stable nginx image
FROM postgres:13.0
 
# copy the initial script into dir
COPY init/setup-database.sql /docker-entrypoint-initdb.d
ADD https://www.dropbox.com/s/jol8eiz6vcrgq6s/tchibo_reviews.csv?dl=1 /docker-entrypoint-initdb.d/tchibo_reviews.csv

RUN chmod +r /docker-entrypoint-initdb.d/tchibo_reviews.csv
 
# set locale
RUN localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8
 
# set lang 
ENV LANG de_DE.utf8