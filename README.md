# Big Data Analyseprojekt - Tchibo Sentimentanalyse

Folgende Services sind aktuell Teil dieses Projekts:

-   Scraper für [otto.de](https://otto.de) via RESTful API
-   Web Applikation zur Ausführung der Scraping API
-   PostgreSQL Datenbank
-   Adminer SQL Webclient für Zugriff auf PostgreSQL Datenbank
-   Web Applikation für die Darstellung erster Auswertungen zu Rezensionen

Vorraussetzung zum Starten des Systems ist [Docker Desktop](https://www.docker.com/get-started) in der Version `2.4.0.0` oder höher, welches auf dem lokalen Computer installiert werden muss.

Die Services können über den Kommandozeilenbefehl `docker-compose up -d` gestartet werden, wenn man sich im Verzeichnis `bdap-tchibo-sentiment-master` befindet. Das erstmalige Starten des Systems installiert alle benötigten Komponenten und Services. Dies kann bis zu 15 Minuten dauern und erfordert eine Internetverbindung. Nach dieser initialen Installation erfolgt ein erneutes Hochfahren des Systems innerhalb von ca. 10 Sekunden.
Ein Herunterfahren des Systems kann über den Kommandozeilenbefehl `docker-compose stop`erfolgen, wenn man sich im Verzeichnis `bdap-tchibo-sentiment-master` befindet.

Wurden Änderungen an einer der Komponenten vorgenommen, müssen die Docker Images und Container neu erzeugt werden. Dies kann über den Befehl `docker-compose up --build` erfolgen.

Nach erfolgreichem Start der Komponenten, ist die Web Applikation für eine explorative Datenanalyse unter `localhost:8501` erreichbar.

Um die Daten in der Datenbank zu untersuchen steht unter `localhost:8081` die Adminer Weboberfläche zur Verfügung.

Der Scraper für die Bewertungen von [otto.de ](https://otto.de) kann per REST-Schnittstelle gestartet werden.

Der Zugriff auf die Scraping-Schnittstelle kann über eine Weboberfläche erfolgen.
Die Weboberfläche steht unter `localhost:8502` zur Verfügung.
Nach dem Scrapen werden alle neuen Daten, die noch nicht in der Datenbank vorhanden sind, dort gespeichert.

Die Sentimentanalyse kann über eine Webbapp gestartet werden. Diese ist unter `localhsot:8503` aufrufbar. Zuerst muss ein Lekixon in Form einer `.csv`-Datei eingelesen werden. Hierzu kann die mitgelieferte Datei unter `/analysis/sentiment-analysis/term_aspect_dict.csv` verwendet werden. Naschließend ist ein Produkname einzugeben z.B. 'Esperto' oder 'Cafissimo' und mit `Enter` zu bestätigen. Dies startet die Analyse, welche bis zu 2 Minuten dauern kann. Das Ergebnis wird in der Webapp dargestellt und repräsentiert den Datensatz, welcher in dem Tableau Dashboard zur Ableitung der Handlungsempfehlungen genutzt wurde.
