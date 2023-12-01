# einsatzplan
Einsatzplan Management


# -- Anforderungen -- #

- Mitarbeiter an Wochentagen zuweisen
- Mitarbeiter zu Projekten zuweisen
- Datum über Wochentag
- Zwischen den Kalenderwochen wechseln können (vlt. mit Button für direkt zur derzeitigen KW)
- Löschfunktion für Einträge
- 3-4 KW sichtbar
- Zeiten für 1 Jahr
- Gruppenfunktion mit Verschiebung -> Farbige Hinterlegen
- Hotel + Stundenzettel (Buchstaben)
- Kunden hinzufügen/löschen können
- Projekt -- "" --
- Auto -- "" --
- Detailansicht wenn man auf ein Feld draufklickt z.B. Ort
- Vor-Ort oder in der Firma (Buchstaben)
- Personalnummer
- Bei Gruppen jeweils Auto zuweisen bzw. mehrere Autos
- Hinweisfeld zum Eintragen

- FREI eintragen wodurch dann die restlichen Datenbanksachen auf "no" gesetzt werden und nur "FREI" angezeigt wird

- Legende


Zukunft:
- Auslesen der aktuellen Datenbank von z.B. den eingetragenen Urlaubstagen, etc. um diese vielleicht auch abzugleichen.

- Automatische Aktualisierung der Seite, wenn was an der Datenbank verändert wird.


# -- SETUP ENV -- #

1. python3 -m venv venv

2. . venv/bin/activate

3. python3 -m pip install --upgrade pip

4. python3 -m pip install flask

5. python3 -m flask --app ./main.py run



# -- DATABASE -- #
INSERT INTO users (user_id, first_name, last_name, work_field) VALUES (1, "Thorsten", "Flathmann", "Schlosser"), (2, "Timo", "B.", "Schlosser"), (3, "Adama", "Adama", "Schlosser"), (4, "Daniel", "X.", "Schlosser"), (5, "Albert", "Litau", "Schlosser"), (6, "Horst", "Wendelken", "Schlosser"), (7, "Szymon", "Minda", "Dreher & Fräser"), (8, "Hans-Peter", "XY.", "Dreher & Fräser"), (9, "Igor", "Giswein", "Elektriker"), (10, "Marcel", "Krüger", "Elektriker"), (11, "Michael", "van Hoorn", "Elektriker"), (12, "Tim", "XY.", "Elektriker"), (13, "Ray", "XY.", "Elektriker"), (14, "Matthias", "Gerke", "Freie Mitarbeiter"), (15, "Franco", "Miraglia", "Büro"), (16, "Sabrina", "Miraglia", "Büro"), (17, "Raphael", "Schlameuß", "Büro"), (18, "Marc", "Rönick", "Büro"), (19, "Frank", "Böttcher", "Büro"), (20, "Frank", "Moser", "Büro"), (21, "Jenris", "Pfabe", "Büro"), (22, "Matthias", "Korn", "Büro"), (23, "Timo", "Wohltorf", "Büro"), (24, "Daniel", "Maul", "Büro"), (25, "Sinan", "Morina", "Hauswart");

INSERT INTO cars (car_id, car_name) VALUES (1, "T11 () HB-BE 384"), (2, "T13 (5/24) HB-SL 344"), (3, "T14 (4/23) HB-SL 554"), (4, "T15 (7/23) HB-SL 25"), (5, "BMW (2/24) HB-SL 133");

