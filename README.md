# aoi-portal

Dieses Projekt soll die signup+login flows für die österreichische Informatikolympiade verbessern.

Ziel sind einerseits moderne Register/Login flows (mit change password/email, passwort vergessen functionality), single-sign-on für das CMS system, sowie manche aktionen für Administratoren (contest aufsetzen etc) zu verbessern.

Tech Stack:
- Flask backend
- Vue.js (2.x) frontend
- Bulma/Buefy CSS framework

Das Frontend ist eine single page applikation (gebaut mit Vue.js), und kommuniziert über JSON APIs mit dem Backend.

Zusätzlich gibt es eine cms-bridge, die interaktionen zwischen dem backend und dem cms system ermöglicht (direkt ins portal backend ist nicht möglich, da die dependencies inkompatibel sind).

## Dev Installation

### MacOS or Unix

```bash
$ cd backend/
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -e .
$ python3 run.py createdb  # create db
$ python3 run.py addadmin --first-name John --last-name Smith --password password1 --email me@example.org
$ python3 run.py wsgi  # start server
```

```bash
$ cd cms-bridge/
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -e .
$ python3 run.py wsgi  # start server
```

```bash
$ cd frontend
$ npm install
$ npm run serve
```

### Windows

Make sure to run the powershell as admin.

```bash
$ cd backend/
$ python3 -m venv venv
$ venv/Scripts/activate.bat
$ pip3 install -e .
$ python3 run.py createdb  # create db
$ python3 run.py addadmin --first-name John --last-name Smith --password password1 --email me@example.org
$ python3 run.py wsgi  # start server
```

```bash
$ cd cms-bridge/
$ python3 -m venv venv
$ venv/Scripts/activate.bat
$ pip3 install -e .
$ python3 run.py wsgi  # start server
```

```bash
$ cd frontend
$ npm install
$ npm run serve
```

Dann die URL die von `npm run serve` gezeigt wird aufrufen. Das setup sollte automatisch die APIs an das backend weiterleiten.
