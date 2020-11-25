# Big Data Analyseprojekt - Tchibo Sentimentanalyse

Folgende Services sind aktuell Teil dieses Projekts:
- Scraper für [otto.de](https://otto.de) via RESTful API
- Web Applikation zur Ausführung der Scraping API
- PostgreSQL Datenbank
- Adminer SQL Webclient für Zugriff auf PostgreSQL Datenbank
- Web Applikation für die Darstellung erster Auswertungen zu Rezensionen

Vorraussetzung zum Starten des Systems ist [Docker Desktop](https://www.docker.com/get-started) in der Version 2.4.0.0 oder höher.

Die Services können gestartet werden über `docker-compose up -d`.

Wurden Änderungen an einer der Komponenten vorgenommen, müssen die Docke rImages und Container neu erzeugt werden. Dies kann über den Befehl `docker-compose up --build` erfolgen.

Nach erfolgreichem Start der Komponenten, ist die Web Applikation für erste Auswertungen unter `localhost:8501` erreichbar. 
Um die Daten in der Datenbank zu untersuchen steht unter `localhost:8081` die Adminer Weboberfläche zur Verfügung.
Der Scraper für die Bewertungen von [otto.de ](https://otto.de) kann per REST-Schnittstelle gestartet werden.
Der Zugriff auf die Scraping-Schnittstelle kann über eine Weboberfläche erfolgen. 
Die Weboberfläche steht unter `localhost:8052` zur Verfügung. 
Nach dem Scrapen werden alle neuen Daten, die noch nicht in der Datenbank vorhanden sind, dort gespeichert.
Danach stehen diese zur Auswertung unter `localhost:8501` zur Verfügung.