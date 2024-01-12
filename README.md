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



- Löschfunktion für Gruppen?



Zukunft:

- Auslesen der aktuellen Datenbank von z.B. den eingetragenen Urlaubstagen, etc. um diese vielleicht auch abzugleichen.

- Automatische Aktualisierung der Seite, wenn was an der Datenbank verändert wird.

# -- SETUP ENV --

1. python3 -m venv venv

2. . venv/bin/activate

3. python3 -m pip install --upgrade pip

4. python3 -m pip install flask

5. python3 -m flask --app ./main.py run

# -- DATABASE --

INSERT INTO users (user_id, first_name, last_name, work_field) VALUES (1, "Thorsten", "Flathmann", "Schlosser"), (2, "Timo", "B.", "Schlosser"), (3, "Adama", "Adama", "Schlosser"), (4, "Daniel", "X.", "Schlosser"), (5, "Albert", "Litau", "Schlosser"), (6, "Horst", "Wendelken", "Schlosser"), (7, "Szymon", "Minda", "Dreher & Fräser"), (8, "Hans-Peter", "XY.", "Dreher & Fräser"), (9, "Igor", "Giswein", "Elektriker"), (10, "Marcel", "Krüger", "Elektriker"), (11, "Michael", "van Hoorn", "Elektriker"), (12, "Tim", "XY.", "Elektriker"), (13, "Ray", "XY.", "Elektriker"), (14, "Matthias", "Gerke", "Freie Mitarbeiter"), (15, "Franco", "Miraglia", "Büro"), (16, "Sabrina", "Miraglia", "Büro"), (17, "Raphael", "Schlameuß", "Büro"), (18, "Marc", "Rönick", "Büro"), (19, "Frank", "Böttcher", "Büro"), (20, "Frank", "Moser", "Büro"), (21, "Jenris", "Pfabe", "Büro"), (22, "Matthias", "Korn", "Büro"), (23, "Timo", "Wohltorf", "Büro"), (24, "Daniel", "Maul", "Büro"), (25, "Sinan", "Morina", "Hauswart");

INSERT INTO cars (car_id, car_name) VALUES (1, "T11 () HB-BE 384"), (2, "T13 (5/24) HB-SL 344"), (3, "T14 (4/23) HB-SL 554"), (4, "T15 (7/23) HB-SL 25"), (5, "BMW (2/24) HB-SL 133");
