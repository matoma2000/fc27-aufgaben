# Aufgaben-Companion für FC 27 (Deutsch, inoffiziell)

Checkliste aller FC-27-Aufgaben auf Deutsch, mit Ablaufzeiten. Inoffizielles Fan-Projekt ohne Bilder von EA oder FIFA (Karten und Symbole sind eigene Nachbildungen). Quelle der Aufgaben: https://fcdata.io/objectives

## Einmalig einrichten: täglich automatisch aktuell + iPad-App (ca. 10 Minuten)

Ergebnis: Eine feste Internetadresse, die sich jeden Morgen von selbst aktualisiert. Danach musst du nie wieder etwas starten.

1. **GitHub-Konto** anlegen (kostenlos): https://github.com/signup
2. **Neues Repository** anlegen: https://github.com/new
   - Name z. B. `fc27-aufgaben`, Sichtbarkeit **Public** (nötig für kostenloses Hosting; es stehen keine privaten Daten drin)
   - Nichts ankreuzen (kein README), „Create repository“ klicken
3. **Projekt hochladen** (Terminal im Projektordner, `DEIN-NAME` ersetzen):
   ```
   git init -b main
   git add -A
   git commit -m "Start"
   git remote add origin https://github.com/DEIN-NAME/fc27-aufgaben.git
   git push -u origin main
   ```
4. **Hosting einschalten:** im Repository *Settings → Pages → Source: „GitHub Actions“*.
5. **Ersten Lauf starten:** Reiter *Actions → „Täglich aktualisieren und veröffentlichen“ → Run workflow*. Nach 1–2 Minuten steht die Adresse
   `https://DEIN-NAME.github.io/fc27-aufgaben/` unter *Settings → Pages*.
6. **Täglich:** läuft ab jetzt automatisch (ca. 5:30 Uhr deutscher Zeit): neue Aufgaben holen, Bilder laden, veröffentlichen.

### Optional: neue Aufgaben automatisch auf Deutsch
Ohne Zusatz erscheinen **neue** Aufgabentexte zunächst auf Englisch (alles Bestehende bleibt Deutsch).
Für automatische Übersetzung: API-Key unter https://console.anthropic.com anlegen (kostet bei dieser Textmenge nur Cent-Beträge pro Monat), dann im Repository *Settings → Secrets and variables → Actions → New repository secret*, Name `ANTHROPIC_API_KEY`.

## Auf dem iPad
1. In **Safari** die Adresse oben öffnen.
2. Teilen-Symbol → **„Zum Home-Bildschirm“**. Fertig, die App hat ein eigenes Icon und öffnet sich ohne Browserleiste.
3. Haken-Fortschritt wird auf dem iPad gespeichert (nicht mit anderen Geräten geteilt; Safari-Daten nicht löschen).

## Funktionen
- Aufgabengruppen mit Einzelaufgaben, abhakbar, Fortschritt je Gruppe und gesamt
- Ablauf-Countdown (Ortszeit), „Läuft bald ab“ zuerst
- Spielerkarten (eigene Nachbildung), Packs, Münzen usw. als Symbole
- Suche, Kategorien, „Erledigte ausblenden“

## Lokal / von Hand
- Ansehen: `index.html` doppelklicken.
- Daten sofort aktualisieren: `python3 data/update.py` (danach ggf. `python3 data/translate.py`, braucht `ANTHROPIC_API_KEY`).
- Fehlende Übersetzungen stehen in `data/missing.json`.
