# Big Data Analyseprojekt - Tchibo Sentimentanalyse

Folgende Services sind aktuell Teil dieses Projekts:
- Scraper für [otto.de](https://otto.de) via RESTful API
- PostgreSQL Datenbank
- Adminer SQL Webclient für Zugriff auf PostgreSQL Datenbank
- Web Applikation für die Darstellung erster Auswertungen zu Rezensionen

Vorraussetzung zum Starten des Systems ist [Docker Desktop](https://www.docker.com/get-started) in der Version 2.4.0.0 oder höher.

Die Services können gestartet werden über ``docker-compose up -d``.

Wurden Änderungen an einer der Komponenten vorgenommen, müssen die Docke rImages und Container neu erzeugt werden. Dies kann über den Befehl ``docker-compose up --build`` erfolgen.

Nach erfolgreichem Start der Komponenten, ist die Web Applikation für erste Auswertungen unter ``localhost:8501`` erreichbar. 
Um die Daten in der Datenbank zu untersuchen steht unter ``localhost:8081`` die Adminer Weboberfläche zur Verfügung.
Der Scraper für die Bewertungen von [otto.de ](https://otto.de) kann per REST-Schnittstelle gestartet werden.
Aufgerufen werden kann das Scraping zum Beispiel via ``cURL`` unter ``localhost:9080``.
Dabei muss die Produkt-URL und der Name des Scrapers (otto_reviews) übergeben werden.
Ein beispielhafter Request via `cURL` sieht wie folgt aus: 
```cURL
curl --location --request POST 'http://localhost:9080/crawl.json' \
--header 'Content-Type: application/json' \
--data-raw '{
    "request": {
        "url": "https://www.otto.de/product-customerreview/reviews/presentation/product/898416526"
    },
    "spider_name": "otto_reviews"
}'
```