# einsatzplan

Einsatzplan Management

# -- Anforderungen --

- Mitarbeiter an Wochentagen zuweisen
- Mitarbeiter zu Projekten zuweisen
- Datum über Wochentag
- 3-4 KW sichtbar
- Hotel + Stundenzettel (Buchstaben)
- Kunden hinzufügen/löschen können
- Projekt -- "" --
- Auto -- "" --
- Vor-Ort oder in der Firma (Buchstaben)
- Personalnummer
- Hinweisfeld zum Eintragen
- Detailansicht wenn man auf ein Feld draufklickt z.B. Ort/Hinweis
  => JS
- Bei Gruppen jeweils Auto zuweisen bzw. mehrere Autos
- Aktuelle KW hervorheben
- Zwischen den Kalenderwochen wechseln können (vlt. mit Button für direkt zur derzeitigen KW)
- nur helle Farben bei den Gruppen
- 2 KW aufeinmal rest scrollen
- Feiertage Bremen
- Nord und Südfeiertage
- Info icon (Bei verfügbaren Hinweis)
- Neue Reihenfolge: Elektriker, Schlosser, Sinan, Büro, Dreher & Fräser, extern
- Legende
- Zeiten für 1 Jahr
- Abwesendheit, Urlaub & Gleizeit, Schule mit Farbe (Schwarz oder Rot)
- -> Dafür einen Button dass das Eingetragen wird und bei Project ID iwie 00001 ist was dann als z.B. "Schule" angezeigt wird oder einfach nur Farben je nach Project ID
- Wechseln der Seiten und weiterhin in Admin-Bereich drinne bleiben ermöglichen
- Wenn an einem Tag schon was belegt ist bei der user_id & date, dann sollte eine Meldung kommen, dass der Tag schon zugewiesen wurde (einfach Abfrage, bevor es in die Datenbank gesetzt wird if else oder so)
- Auto pro Tag zuweisen und dann für die anderen nicht erlauben
- Check if car is assigned to another group_id between the dates
- Löschfunktion für Einträge (Am besten anwählen und löschen)
- Extra Besprechungsliste als Seite wo man Manuell den Raum Auswählen kann und die Bewirtung anklicken sowie Die Teilnehmer, Uhrzeit + Datum
- Besprechungsliste als QuickView oben rechts mit vlt. den heutigen 3 und dann als Button um die Liste aufzurufen woanders.
- Logos oben und unten weg
- Login vor die Seite



Zukunft:

- Auslesen der aktuellen Datenbank von z.B. den eingetragenen Urlaubstagen, etc. um diese vielleicht auch abzugleichen.

- Automatische Aktualisierung der Seite, wenn was an der Datenbank verändert wird.


# -- SETUP ENV --

1. python3 -m venv venv

2. . venv/bin/activate

3. python3 -m pip install --upgrade pip

4. python3 -m pip install --verbose -r requirements.txt
# Run testing env
5. python3 -m flask --app ./main.py run

# Run with uwsgi (within venv)
1. uwsgi_python3 --http-socket 0.0.0.0:5000 -w wsgi:app

# -- DATABASE --

datenbank.db

Tabellen:

CalenderWeek
assignment_table
cars
customers
extras
group
meetings
projects
users

npm install jquery
npm install unpkg.com/react@16.7.0/umd/react.production.min.js
npm install unpkg.com/react-dom@16.7.0/umd/react-dom.production.min.js

