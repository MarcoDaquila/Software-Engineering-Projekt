# Cyber Defenders

Lernspiel für Java und IT-Sicherheit aus zwei Sichten

## Team

* Felix Hagino
* Marco Daquila
* Leonie Röse
* Dominik Stengele

## Beschreibung

Link zum Projekt-Board: https://github.com/users/MarcoDaquila/projects/3/views/1

Als Team von **FMLD-Studios** werden wir das Lernspiel **Cyber Defenders** entwickeln. Dabei wird ein virtueller Escape Room mit einem Detektiv- und Rätselspiel kombiniert. 
Die Nutzer lernen darin spielerisch fortgeschrittene Java-Programmierung und grundlegende Prinzipien der IT-Sicherheit.
Gespielt wird in einzelnen Missionen, zum Beispiel in einem gehackten Serverraum oder einem Firmennetzwerk. 
Vor dem Start wählen die Spieler eine Rolle (Cyber-Defender oder White-Hat-Hacker) und lernen IT-Sicherheit so aus zwei Blickwinkeln.

- **Nutzer:** Studierende und Einsteiger, die Java und IT-Sicherheit lernen wollen.
- **Mindestumfang:** eine spielbare Mission mit Code-Editor, automatischer Prüfung der Lösung und gespeichertem Fortschritt.

## Tech-Stack

* Frontend: Angular (TypeScript), Tailwind CSS
* Backend: TypeScript mit Express
* Datenbank: Neon (PostgreSQL)

## Lokal starten

> Der lokale Start soll über die Ports 3100 und 4100 erfolgen, jedoch befindet sich das Projekt noch in Arbeit.
1. `git clone` des Repos
2. `npm install` im Frontend- und Backend-Ordner
3. `npx supabase start` für die lokale Datenbank (benötigt Docker) (Muss überarbeitet werden)
4. `npm run start` im Backend (Express, http://localhost:3100)
5. `ng serve` im Frontend (http://localhost:4100)

